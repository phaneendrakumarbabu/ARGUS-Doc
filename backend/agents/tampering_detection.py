"""
ADFF - Tampering Detection Agent
Evaluates cross-agent forensic signals (ELA, noise inconsistency, typography mismatch, metadata flags)
to estimate composite tampering probability and categorize the likely manipulation modality.
"""

from typing import Dict, Any, List, Tuple
from backend.models.schemas import ManipulationCategory


class TamperingDetectionAgent:
    def __init__(self):
        pass

    def evaluate(
        self,
        metadata_res: Dict[str, Any],
        forensics_pages: List[Dict[str, Any]],
        ocr_pages: List[Dict[str, Any]],
        understanding_res: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesizes metrics across pages, assesses anomaly z-scores,
        and classifies the likely manipulation category.
        """
        page_scores = []
        all_clusters = []
        copy_move_flag = False
        typography_mismatch_count = 0

        # Scan forensic pages
        for p_idx, p_forensic in enumerate(forensics_pages):
            clusters = p_forensic.get("anomalous_clusters", [])
            for c in clusters:
                c["page"] = p_idx
                all_clusters.append(c)

            if p_forensic.get("copy_move_detected", False):
                copy_move_flag = True

            p_ela_score = p_forensic.get("ela_anomaly_score", 0.0)
            p_noise_score = p_forensic.get("noise_inconsistency_score", 0.0)
            p_edge_score = p_forensic.get("edge_gradient_discontinuity_score", 0.0)

            # Combined page anomaly metric
            p_score = (p_ela_score * 0.45) + (p_noise_score * 0.35) + (p_edge_score * 0.20)
            page_scores.append(p_score)

        # Scan OCR pages for typography mismatches
        for p_ocr in ocr_pages:
            anoms = p_ocr.get("typography_anomalies", [])
            typography_mismatch_count += len(anoms)

        # Metadata signals
        suspicious_software = metadata_res.get("suspicious_software_flag", False)
        post_creation_mod = metadata_res.get("is_modified_post_creation", False)
        incremental_updates = metadata_res.get("has_incremental_updates", False)
        temporal_anomaly = metadata_res.get("temporal_anomaly", False)

        # Compute max page score
        max_page_score = max(page_scores) if page_scores else 0.0

        # Determine manipulation category
        category = self._classify_manipulation(
            all_clusters,
            copy_move_flag,
            typography_mismatch_count,
            suspicious_software,
            incremental_updates,
            understanding_res
        )

        return {
            "max_page_score": float(round(max_page_score, 3)),
            "page_scores": [float(round(s, 3)) for s in page_scores],
            "total_anomalous_clusters": len(all_clusters),
            "likely_manipulation_category": category.value,
            "copy_move_detected": copy_move_flag,
            "typography_mismatch_count": typography_mismatch_count,
            "metadata_signals": {
                "suspicious_software": suspicious_software,
                "post_creation_mod": post_creation_mod,
                "incremental_updates": incremental_updates,
                "temporal_anomaly": temporal_anomaly
            }
        }

    def _classify_manipulation(
        self,
        clusters: List[Dict[str, Any]],
        copy_move: bool,
        typography_count: int,
        suspicious_software: bool,
        incremental: bool,
        understanding: Dict[str, Any]
    ) -> ManipulationCategory:
        """Determines the most specific manipulation category based on evidence convergence."""
        if copy_move:
            return ManipulationCategory.COPY_MOVE

        if typography_count > 0 and len(clusters) > 0:
            return ManipulationCategory.TEXT_REPLACEMENT

        # Check if high-value zones (signatures, totals) intersect high ELA clusters
        if len(clusters) > 0:
            high_value_zones = understanding.get("high_value_zones", [])
            for c in clusters:
                c_box = c.get("bbox", [0, 0, 0, 0])
                for hvz in high_value_zones:
                    hv_box = hvz.get("bbox", [0, 0, 0, 0])
                    # Intersection check
                    if self._boxes_intersect(c_box, hv_box):
                        if "total" in hvz.get("zone_type", "") or "financial" in hvz.get("zone_type", ""):
                            return ManipulationCategory.TEXT_REPLACEMENT
                        if "signature" in hvz.get("zone_type", "") or "seal" in hvz.get("zone_type", ""):
                            return ManipulationCategory.SPLICING

            if suspicious_software:
                return ManipulationCategory.LOCAL_EDIT
            return ManipulationCategory.SPLICING

        if incremental and suspicious_software:
            return ManipulationCategory.INSERTION_DELETION

        if suspicious_software:
            return ManipulationCategory.LOCAL_EDIT

        return ManipulationCategory.UNDETERMINED

    def _boxes_intersect(self, boxA: List[int], boxB: List[int]) -> bool:
        """Checks if two bounding boxes [x0, y0, x1, y1] overlap."""
        return not (
            boxA[2] < boxB[0] or
            boxA[0] > boxB[2] or
            boxA[3] < boxB[1] or
            boxA[1] > boxB[3]
        )
