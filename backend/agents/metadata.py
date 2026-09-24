"""
ADFF - Metadata Agent
Examines document file structures, PDF dictionary tags (/Creator, /Producer, /CreationDate, /ModDate),
incremental update chains, and image EXIF headers to detect tool signatures and temporal discrepancies.
"""

from typing import Dict, Any, List
from pathlib import Path
import re
from datetime import datetime
from PIL import Image, ExifTags
import pymupdf


class MetadataAgent:
    def __init__(self):
        self.suspicious_software_signatures = [
            "photoshop", "gimp", "canva", "ilovepdf", "sejda", "pdfill",
            "inkscape", "coreldraw", "paint.net", "foxit phantom", "nitro pro",
            "pdf architect", "pdf-xchange editor", "smallpdf", "adobe illustrator"
        ]

    def analyze(self, original_path: str, file_type: str) -> Dict[str, Any]:
        """
        Parses metadata, headers, structural incremental updates, and checks software indicators.
        """
        if file_type == "PDF":
            return self._analyze_pdf(original_path)
        else:
            return self._analyze_image(original_path, file_type)

    def _analyze_pdf(self, pdf_path: str) -> Dict[str, Any]:
        with open(pdf_path, "rb") as f:
            raw_bytes = f.read()

        doc = pymupdf.open(pdf_path)
        raw_meta = doc.metadata or {}
        doc.close()

        creator = raw_meta.get("creator", "") or ""
        producer = raw_meta.get("producer", "") or ""
        creation_date_str = raw_meta.get("creationDate", "") or ""
        mod_date_str = raw_meta.get("modDate", "") or ""
        title = raw_meta.get("title", "") or ""
        author = raw_meta.get("author", "") or ""

        # Detect suspicious software
        software_flags = []
        combined_text = f"{creator} {producer}".lower()
        for sig in self.suspicious_software_signatures:
            if sig in combined_text:
                software_flags.append(sig.title())

        # Check incremental updates: multiple 'startxref' or '%%EOF'
        eof_count = len(re.findall(rb"%%EOF", raw_bytes))
        startxref_count = len(re.findall(rb"startxref", raw_bytes))
        has_incremental_updates = (eof_count > 1 or startxref_count > 1)

        # Parse dates
        creation_dt = self._parse_pdf_date(creation_date_str)
        mod_dt = self._parse_pdf_date(mod_date_str)

        is_modified_post_creation = False
        temporal_anomaly = False
        time_difference_desc = "Timestamps match or no mod date found."

        if creation_dt and mod_dt:
            diff_seconds = (mod_dt - creation_dt).total_seconds()
            if diff_seconds > 60:  # modified more than 1 min after creation
                is_modified_post_creation = True
                time_difference_desc = f"Document modified {int(diff_seconds // 60)} minutes after original creation."
            elif diff_seconds < -5:  # modification date is before creation date!
                temporal_anomaly = True
                time_difference_desc = "CRITICAL: Modification date predates creation date (clock manipulation)."

        return {
            "file_type": "PDF",
            "creator": creator,
            "producer": producer,
            "title": title,
            "author": author,
            "creation_date": creation_dt.isoformat() if creation_dt else creation_date_str,
            "mod_date": mod_dt.isoformat() if mod_dt else mod_date_str,
            "is_modified_post_creation": is_modified_post_creation,
            "temporal_anomaly": temporal_anomaly,
            "time_difference_desc": time_difference_desc,
            "has_incremental_updates": has_incremental_updates,
            "eof_marker_count": eof_count,
            "startxref_count": startxref_count,
            "suspicious_software_flag": len(software_flags) > 0,
            "software_flags": software_flags,
            "raw_metadata": raw_meta
        }

    def _analyze_image(self, img_path: str, file_type: str) -> Dict[str, Any]:
        software_flags = []
        raw_meta = {}
        creation_date = None
        mod_date = None
        software = None

        try:
            with Image.open(img_path) as im:
                # Check PNG text info
                if file_type == "PNG" and hasattr(im, "text") and im.text:
                    raw_meta = dict(im.text)
                    software = raw_meta.get("Software") or raw_meta.get("software")

                # Check EXIF for JPEG/TIFF
                exif = im.getexif()
                if exif:
                    for tag_id, val in exif.items():
                        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                        raw_meta[tag_name] = str(val)

                    software = software or raw_meta.get("Software")
                    creation_date = raw_meta.get("DateTimeOriginal") or raw_meta.get("DateTime")
        except Exception:
            pass

        if software:
            s_lower = software.lower()
            for sig in self.suspicious_software_signatures:
                if sig in s_lower:
                    software_flags.append(sig.title())

        return {
            "file_type": file_type,
            "creator": None,
            "producer": software,
            "creation_date": creation_date,
            "mod_date": mod_date,
            "is_modified_post_creation": False,
            "temporal_anomaly": False,
            "time_difference_desc": "Image file EXIF inspection.",
            "has_incremental_updates": False,
            "suspicious_software_flag": len(software_flags) > 0,
            "software_flags": software_flags,
            "raw_metadata": raw_meta
        }

    def _parse_pdf_date(self, d_str: str) -> Any:
        """Parses PDF date format: D:YYYYMMDDHHmmSS[OHH'mm']"""
        if not d_str:
            return None
        clean_str = d_str.strip()
        if clean_str.startswith("D:"):
            clean_str = clean_str[2:]

        # Extract numeric core YYYYMMDDHHMMSS
        match = re.match(r"^(\d{4})(\d{2})(\d{2})(\d{2})?(\d{2})?(\d{2})?", clean_str)
        if match:
            year, month, day, hour, minute, sec = match.groups()
            try:
                return datetime(
                    int(year),
                    int(month),
                    int(day),
                    int(hour or 0),
                    int(minute or 0),
                    int(sec or 0)
                )
            except ValueError:
                return None
        return None
