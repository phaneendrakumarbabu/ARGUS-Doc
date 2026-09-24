"""
ADFF - Ingestion Agent
Validates file integrity, assigns unique analysis ID, computes cryptographic hash,
and converts document pages (PDF/JPG/PNG) into high-resolution standardized RGB images.
"""

import os
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Tuple
from PIL import Image
import pymupdf


class IngestionAgent:
    def __init__(self, storage_dir: str = "data/artifacts"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def validate_and_ingest(
        self, file_path_or_bytes: Any, filename: str
    ) -> Dict[str, Any]:
        """
        Validates file integrity, creates artifact folder, extracts pages to images.
        Returns document ID, metadata, page image paths, and page count.
        """
        # Read content
        if isinstance(file_path_or_bytes, (str, Path)):
            with open(file_path_or_bytes, "rb") as f:
                content = f.read()
        elif hasattr(file_path_or_bytes, "read"):
            content = file_path_or_bytes.read()
        elif isinstance(file_path_or_bytes, bytes):
            content = file_path_or_bytes
        else:
            raise ValueError("Unsupported input format for file ingestion.")

        file_size = len(content)
        if file_size == 0:
            raise ValueError("Input file is empty (0 bytes).")

        # Generate unique document ID
        timestamp_slug = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        unique_suffix = uuid.uuid4().hex[:6]
        doc_id = f"DOC_{timestamp_slug}_{unique_suffix}"

        # Setup artifact directory
        doc_dir = self.storage_dir / doc_id
        doc_dir.mkdir(parents=True, exist_ok=True)

        # Compute SHA-256 hash
        sha256_hash = hashlib.sha256(content).hexdigest()

        # Detect file type via magic bytes
        file_type = self._detect_file_type(content, filename)

        # Save original file
        original_ext = Path(filename).suffix.lower() or f".{file_type.lower()}"
        original_path = doc_dir / f"original{original_ext}"
        with open(original_path, "wb") as f:
            f.write(content)

        # Extract page images
        page_images, dimensions = self._extract_page_images(
            original_path, file_type, doc_dir
        )

        return {
            "document_id": doc_id,
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "sha256": sha256_hash,
            "page_count": len(page_images),
            "original_path": str(original_path),
            "page_image_paths": [str(p) for p in page_images],
            "dimensions": dimensions,
            "doc_dir": str(doc_dir),
        }

    def _detect_file_type(self, content: bytes, filename: str) -> str:
        """Determines file type using magic numbers with filename fallback."""
        if content.startswith(b"%PDF"):
            return "PDF"
        if content.startswith(b"\x89PNG\r\n\x1a\n"):
            return "PNG"
        if content.startswith(b"\xff\xd8\xff"):
            return "JPEG"
        if content.startswith(b"II*\x00") or content.startswith(b"MM\x00*"):
            return "TIFF"

        # Fallback to extension
        ext = Path(filename).suffix.lower()
        if ext in [".pdf"]:
            return "PDF"
        if ext in [".png"]:
            return "PNG"
        if ext in [".jpg", ".jpeg"]:
            return "JPEG"
        if ext in [".tif", ".tiff"]:
            return "TIFF"

        raise ValueError(
            f"Unsupported file format for '{filename}'. Allowed types: PDF, JPG, PNG, TIFF."
        )

    def _extract_page_images(
        self, file_path: Path, file_type: str, output_dir: Path
    ) -> Tuple[List[Path], List[Dict[str, float]]]:
        """Converts each page of the document into a high-res RGB image."""
        page_image_paths = []
        dimensions = []

        if file_type == "PDF":
            doc = pymupdf.open(file_path)
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                rect = page.rect
                dim = {"width": float(rect.width), "height": float(rect.height)}
                dimensions.append(dim)

                # Render page at 2.0x scale (~144-200 DPI standard for crisp forensic analysis)
                zoom_matrix = pymupdf.Matrix(2.0, 2.0)
                pix = page.get_pixmap(matrix=zoom_matrix, alpha=False)
                img_path = output_dir / f"page_{page_idx}.png"
                pix.save(str(img_path))
                page_image_paths.append(img_path)
            doc.close()
        else:
            # Single image file (PNG, JPG, TIFF)
            with Image.open(file_path) as img:
                rgb_img = img.convert("RGB")
                img_path = output_dir / "page_0.png"
                rgb_img.save(str(img_path), format="PNG")
                page_image_paths.append(img_path)
                dimensions.append({"width": float(img.width), "height": float(img.height)})

        return page_image_paths, dimensions
