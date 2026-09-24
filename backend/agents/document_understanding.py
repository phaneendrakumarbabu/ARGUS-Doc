"""
ADFF - Document Understanding Agent
Classifies document type, structural layout, text density, embedded raster objects,
and identifies high-value target zones (amounts, signatures, dates, seals) prone to tampering.
"""

from typing import Dict, Any, List
from pathlib import Path
import pymupdf
from PIL import Image


class DocumentUnderstandingAgent:
    def __init__(self):
        self.doc_types = {
            "invoice": ["invoice", "tax invoice", "bill to", "subtotal", "amount due", "balance", "total amount", "gst"],
            "contract": ["agreement", "terms and conditions", "in witness whereof", "parties", "hereby agreed", "signature"],
            "certificate": ["certificate of", "certify that", "awarded to", "conferred upon", "completion", "achievement", "license"],
            "bank_statement": ["account statement", "opening balance", "closing balance", "transaction history", "withdrawal", "deposit"],
            "receipt": ["receipt", "cash receipt", "payment receipt", "change due", "subtotal"],
        }

    def analyze(self, original_path: str, file_type: str, page_image_paths: List[str]) -> Dict[str, Any]:
        """
        Analyzes document structure, extracts semantic regions, embedded image rects, and layout properties.
        """
        page_count = len(page_image_paths)
        raw_text = ""
        has_vector_text = False
        has_raster_images = False
        embedded_image_zones = []
        high_value_zones = []

        scale = 2.0  # matches 2.0x page rasterization

        if file_type == "PDF":
            doc = pymupdf.open(original_path)
            for page_idx, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    has_vector_text = True
                    raw_text += " " + text

                # Inspect embedded raster image objects
                img_list = page.get_images()
                if img_list:
                    has_raster_images = True
                    for img_item in img_list:
                        xref = img_item[0]
                        rects = page.get_image_rects(xref)
                        for r in rects:
                            scaled_bbox = [int(r.x0 * scale), int(r.y0 * scale), int(r.x1 * scale), int(r.y1 * scale)]
                            embedded_image_zones.append({
                                "page": page_idx,
                                "xref": xref,
                                "bbox": scaled_bbox
                            })

                # High-value target zones from text blocks
                blocks = page.get_text("blocks")
                for b in blocks:
                    block_text = b[4].lower()
                    bbox = [int(b[0] * scale), int(b[1] * scale), int(b[2] * scale), int(b[3] * scale)]

                    if any(term in block_text for term in ["total", "amount", "balance", "subtotal", "due"]):
                        high_value_zones.append({
                            "page": page_idx,
                            "zone_type": "financial_total",
                            "text_preview": b[4].strip()[:50],
                            "bbox": bbox
                        })
                    elif any(term in block_text for term in ["signature", "signed by", "signatory", "authorized"]):
                        high_value_zones.append({
                            "page": page_idx,
                            "zone_type": "signature_block",
                            "text_preview": b[4].strip()[:50],
                            "bbox": bbox
                        })
                    elif any(term in block_text for term in ["date", "dated", "issued"]):
                        high_value_zones.append({
                            "page": page_idx,
                            "zone_type": "date_field",
                            "text_preview": b[4].strip()[:50],
                            "bbox": bbox
                        })
            doc.close()
        else:
            has_raster_images = True
            # For pure image contracts, mark lower third as candidate signature zone
            with Image.open(original_path) as im:
                w_orig, h_orig = im.width, im.height
                high_value_zones.append({
                    "page": 0,
                    "zone_type": "signature_block",
                    "text_preview": "Signature & Seal Area",
                    "bbox": [int(w_orig * 0.1), int(h_orig * 0.55), int(w_orig * 0.9), int(h_orig * 0.85)]
                })

        # Classify document genre
        lower_content = raw_text.lower()
        scores = {}
        for d_type, keywords in self.doc_types.items():
            match_count = sum(1 for kw in keywords if kw in lower_content)
            scores[d_type] = match_count

        sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if sorted_types and sorted_types[0][1] > 0:
            detected_type = sorted_types[0][0].replace("_", " ").title()
        elif "contract" in original_path.lower() or "agreement" in original_path.lower():
            detected_type = "Contract Agreement"
        elif "certificate" in original_path.lower():
            detected_type = "Certificate"
        else:
            detected_type = "Commercial Document / Record"

        word_count = len(raw_text.split())
        if word_count > 300:
            density = "High"
        elif word_count > 50:
            density = "Medium"
        else:
            density = "Low"

        dims = []
        for p_img in page_image_paths:
            with Image.open(p_img) as im:
                dims.append({"width": im.width, "height": im.height})

        return {
            "document_type": detected_type,
            "page_count": page_count,
            "dimensions": dims,
            "text_density": density,
            "word_count": word_count,
            "has_vector_text": has_vector_text,
            "has_raster_images": has_raster_images,
            "embedded_image_zones": embedded_image_zones,
            "high_value_zones": high_value_zones,
        }
