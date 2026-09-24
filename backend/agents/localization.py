"""
ADFF - Localization Agent
Localizes suspicious document regions as bounding boxes, cross-references
them against OCR token coordinates, and generates visual overlay artifacts.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from backend.models.schemas import SuspiciousRegion


class LocalizationAgent:
    def __init__(self):
        pass

    def localize(
        self,
        forensics_pages: List[Dict[str, Any]],
        ocr_pages: List[Dict[str, Any]],
        page_image_paths: List[str],
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Coordinates pixel anomalies and OCR tokens, produces localized bounding boxes,
        and renders visual overlay images with bounding boxes.
        """
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        all_regions: List[SuspiciousRegion] = []
        page_overlays: List[str] = []

        for p_idx, page_img_path in enumerate(page_image_paths):
            p_forensic = forensics_pages[p_idx] if p_idx < len(forensics_pages) else {}
            p_ocr = ocr_pages[p_idx] if p_idx < len(ocr_pages) else {}

            clusters = p_forensic.get("anomalous_clusters", [])
            typography_anoms = p_ocr.get("typography_anomalies", [])
            tokens = p_ocr.get("tokens", [])

            # Load page image
            base_img = cv2.imread(page_img_path)
            if base_img is None:
                continue

            h, w = base_img.shape[:2]
            overlay_img = base_img.copy()

            page_regions: List[SuspiciousRegion] = []

            # 1. Process ELA / Image Forensic Clusters
            for c in clusters:
                c_bbox = c["bbox"]
                # Find associated OCR text in or near this bbox
                associated_tokens = self._find_enclosed_tokens(c_bbox, tokens)
                assoc_text = " ".join([t["text"] for t in associated_tokens]) if associated_tokens else None

                reason = f"High ELA compression residual (energy={c['mean_ela_energy']:.1f})"
                if assoc_text:
                    reason += f" overlapping text field: '{assoc_text}'"

                reg = SuspiciousRegion(
                    page=p_idx,
                    bbox=c_bbox,
                    confidence=float(c.get("confidence", 0.75)),
                    reason=reason,
                    associated_text=assoc_text,
                    source_method="ela_residual_clustering"
                )
                page_regions.append(reg)

            # 2. Process Typography Anomalies from OCR
            for t_anom in typography_anoms:
                t_bbox = t_anom.get("bbox", [0, 0, 0, 0])
                # Check if not already covered by an ELA cluster
                already_covered = any(self._iou(t_bbox, r.bbox) > 0.35 for r in page_regions)
                if not already_covered:
                    associated_tokens = self._find_enclosed_tokens(t_bbox, tokens)
                    assoc_text = " ".join([t["text"] for t in associated_tokens]) if associated_tokens else None

                    reg = SuspiciousRegion(
                        page=p_idx,
                        bbox=t_bbox,
                        confidence=0.70,
                        reason=f"Typographical anomaly: {t_anom.get('description', '')}",
                        associated_text=assoc_text,
                        source_method="typography_analysis"
                    )
                    page_regions.append(reg)

            # 3. Render Visual Overlays on Page Image
            overlay_path = out_dir / f"overlay_p{p_idx}.png"
            self._render_bounding_boxes(overlay_img, page_regions)
            cv2.imwrite(str(overlay_path), overlay_img)
            page_overlays.append(str(overlay_path))

            all_regions.extend(page_regions)

        return {
            "suspicious_regions": all_regions,
            "page_overlays": page_overlays
        }

    def _find_enclosed_tokens(self, bbox: List[int], tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Finds tokens that lie inside or significantly overlap with the bounding box."""
        x0, y0, x1, y1 = bbox
        matched = []
        for t in tokens:
            tb = t.get("bbox", [0, 0, 0, 0])
            # Center point of token
            cx = (tb[0] + tb[2]) / 2.0
            cy = (tb[1] + tb[3]) / 2.0
            if (x0 - 15) <= cx <= (x1 + 15) and (y0 - 15) <= cy <= (y1 + 15):
                matched.append(t)
        return matched

    def _render_bounding_boxes(self, img: np.ndarray, regions: List[SuspiciousRegion]) -> None:
        """Draws highlighted forensic bounding boxes and tags on the image."""
        for reg in regions:
            x0, y0, x1, y1 = reg.bbox
            conf = reg.confidence

            # Color coding: Red for high confidence, Amber for moderate
            if conf >= 0.75:
                color = (40, 40, 230)  # Bright Red/Crimson in BGR
                fill_color = (60, 60, 240)
            else:
                color = (30, 165, 255)  # Amber/Orange in BGR
                fill_color = (40, 180, 255)

            # Draw semi-transparent fill
            overlay = img.copy()
            cv2.rectangle(overlay, (x0, y0), (x1, y1), fill_color, -1)
            cv2.addWeighted(overlay, 0.22, img, 0.78, 0, img)

            # Draw thick border
            cv2.rectangle(img, (x0, y0), (x1, y1), color, 3)

            # Draw badge tag above box
            tag_text = f"SUSPECT [{int(conf * 100)}%]"
            font_scale = 0.55
            thickness = 1
            (text_w, text_h), baseline = cv2.getTextSize(tag_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
            
            tag_y1 = max(0, y0 - 8)
            tag_y0 = max(0, tag_y1 - text_h - 6)
            tag_x1 = min(img.shape[1], x0 + text_w + 10)
            
            cv2.rectangle(img, (x0, tag_y0), (tag_x1, tag_y1), color, -1)
            cv2.putText(img, tag_text, (x0 + 5, tag_y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    def _iou(self, boxA: List[int], boxB: List[int]) -> float:
        """Calculates Intersection over Union between two bounding boxes."""
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-5)
        return iou
