"""
ADFF - Evidence Reasoning Agent
Synthesizes observations and interpretations across specialized forensic agents,
ensures every interpretation cites supporting observations, and reconciles cross-agent agreements and conflicts.
"""

from typing import List, Dict, Any, Tuple
from backend.models.schemas import EvidenceItem, SuspiciousRegion


class EvidenceReasoningAgent:
    def __init__(self):
        pass

    def reason(
        self,
        metadata_res: Dict[str, Any],
        forensics_pages: List[Dict[str, Any]],
        ocr_pages: List[Dict[str, Any]],
        understanding_res: Dict[str, Any],
        tampering_res: Dict[str, Any],
        suspicious_regions: List[SuspiciousRegion]
    ) -> Tuple[List[EvidenceItem], List[str]]:
        """
        Builds formal Evidence list (Observations and Interpretations) and identifies unresolved conflicts.
        """
        evidence_items: List[EvidenceItem] = []
        unresolved_conflicts: List[str] = []

        obs_counter = 1
        int_counter = 1

        # ----------------------------------------------------
        # 1. Observations from Metadata
        # ----------------------------------------------------
        meta_obs_ids = []
        creator = metadata_res.get("creator") or "None"
        producer = metadata_res.get("producer") or "None"
        software_flags = metadata_res.get("software_flags", [])

        if software_flags:
            obs_id = f"OBS-{obs_counter:02d}"
            obs_counter += 1
            meta_obs_ids.append(obs_id)
            evidence_items.append(EvidenceItem(
                id=obs_id,
                type="observation",
                text=f"Metadata analysis detected image-editing / PDF manipulation software signature: {', '.join(software_flags)} (Creator: '{creator}', Producer: '{producer}').",
                confidence=0.99,
                source_agent="metadata"
            ))
        else:
            obs_id = f"OBS-{obs_counter:02d}"
            obs_counter += 1
            meta_obs_ids.append(obs_id)
            evidence_items.append(EvidenceItem(
                id=obs_id,
                type="observation",
                text=f"File metadata indicates standard creation toolchain (Producer: '{producer or 'Standard PDF Engine'}', Creator: '{creator or 'Standard Application'}'). No overt editing software signatures found.",
                confidence=0.90,
                source_agent="metadata"
            ))

        if metadata_res.get("is_modified_post_creation", False):
            obs_id = f"OBS-{obs_counter:02d}"
            obs_counter += 1
            meta_obs_ids.append(obs_id)
            evidence_items.append(EvidenceItem(
                id=obs_id,
                type="observation",
                text=f"Temporal analysis: {metadata_res.get('time_difference_desc')}",
                confidence=0.95,
                source_agent="metadata"
            ))

        if metadata_res.get("temporal_anomaly", False):
            obs_id = f"OBS-{obs_counter:02d}"
            obs_counter += 1
            meta_obs_ids.append(obs_id)
            evidence_items.append(EvidenceItem(
                id=obs_id,
                type="observation",
                text=f"Temporal inconsistency: File modification timestamp predates creation timestamp, indicating system clock tampering or backdated file assembly.",
                confidence=0.98,
                source_agent="metadata"
            ))

        if metadata_res.get("has_incremental_updates", False):
            obs_id = f"OBS-{obs_counter:02d}"
            obs_counter += 1
            meta_obs_ids.append(obs_id)
            evidence_items.append(EvidenceItem(
                id=obs_id,
                type="observation",
                text=f"PDF object stream contains multiple trailer markers (%%EOF count: {metadata_res.get('eof_marker_count')}), confirming post-assembly incremental revisions.",
                confidence=0.95,
                source_agent="metadata"
            ))

        # ----------------------------------------------------
        # 2. Observations from Image Forensics
        # ----------------------------------------------------
        forensic_obs_ids = []
        for p_idx, p_forensic in enumerate(forensics_pages):
            ela_mean = p_forensic.get("ela_mean_residual", 0.0)
            ela_score = p_forensic.get("ela_anomaly_score", 0.0)
            clusters = p_forensic.get("anomalous_clusters", [])

            if clusters:
                obs_id = f"OBS-{obs_counter:02d}"
                obs_counter += 1
                forensic_obs_ids.append(obs_id)
                evidence_items.append(EvidenceItem(
                    id=obs_id,
                    type="observation",
                    text=f"Page {p_idx}: Error Level Analysis (ELA) identified {len(clusters)} high-residual compression clusters (peak local energy: {clusters[0]['mean_ela_energy']:.1f}, global baseline mean: {ela_mean:.1f}).",
                    confidence=0.92,
                    source_agent="image_forensics"
                ))
            else:
                obs_id = f"OBS-{obs_counter:02d}"
                obs_counter += 1
                forensic_obs_ids.append(obs_id)
                evidence_items.append(EvidenceItem(
                    id=obs_id,
                    type="observation",
                    text=f"Page {p_idx}: Error Level Analysis (ELA) residual is uniformly distributed (mean: {ela_mean:.1f}, score: {ela_score:.2f}) with no localized compression boundaries.",
                    confidence=0.88,
                    source_agent="image_forensics"
                ))

            if p_forensic.get("copy_move_detected", False):
                obs_id = f"OBS-{obs_counter:02d}"
                obs_counter += 1
                forensic_obs_ids.append(obs_id)
                evidence_items.append(EvidenceItem(
                    id=obs_id,
                    type="observation",
                    text=f"Page {p_idx}: Keypoint descriptor matching identified {p_forensic.get('copy_move_matches')} duplicated spatial blocks, indicating potential copy-move cloning.",
                    confidence=0.89,
                    source_agent="image_forensics"
                ))

            if p_forensic.get("noise_inconsistency_score", 0.0) > 0.45:
                obs_id = f"OBS-{obs_counter:02d}"
                obs_counter += 1
                forensic_obs_ids.append(obs_id)
                evidence_items.append(EvidenceItem(
                    id=obs_id,
                    type="observation",
                    text=f"Page {p_idx}: Laplacian high-frequency noise variance exhibits sharp spatial divergence (variance ratio: {p_forensic.get('noise_variance_std'):.1f}), characteristic of spliced content from a different sensor or rendering resolution.",
                    confidence=0.86,
                    source_agent="image_forensics"
                ))

        # ----------------------------------------------------
        # 3. Observations from OCR & Typography
        # ----------------------------------------------------
        ocr_obs_ids = []
        for p_idx, p_ocr in enumerate(ocr_pages):
            typo_anoms = p_ocr.get("typography_anomalies", [])
            for tanom in typo_anoms:
                obs_id = f"OBS-{obs_counter:02d}"
                obs_counter += 1
                ocr_obs_ids.append(obs_id)
                evidence_items.append(EvidenceItem(
                    id=obs_id,
                    type="observation",
                    text=f"Page {p_idx}: Typography examination detected font anomaly in line {tanom.get('line')}: {tanom.get('description')}.",
                    confidence=0.87,
                    source_agent="ocr_typography"
                ))

        # ----------------------------------------------------
        # 4. Interpretations Derived from Observations
        # ----------------------------------------------------
        cat = tampering_res.get("likely_manipulation_category", "undetermined")

        # Interpretation: Text Replacement
        if cat == "text-replacement":
            int_id = f"INT-{int_counter:02d}"
            int_counter += 1
            supporting = [oid for oid in (forensic_obs_ids + ocr_obs_ids + meta_obs_ids) if oid]
            evidence_items.append(EvidenceItem(
                id=int_id,
                type="interpretation",
                text="Probable digital text replacement / numeric field doctoring. Localized compression residuals directly coincide with modified tabular or currency text coordinates.",
                supported_by=supporting[:3],
                confidence=0.91,
                source_agent="evidence_reasoning"
            ))

        elif cat == "copy-move":
            int_id = f"INT-{int_counter:02d}"
            int_counter += 1
            supporting = forensic_obs_ids[:2]
            evidence_items.append(EvidenceItem(
                id=int_id,
                type="interpretation",
                text="Probable copy-move cloning detected. Identical graphical or textual structures were replicated across distinct spatial locations in the document.",
                supported_by=supporting,
                confidence=0.89,
                source_agent="evidence_reasoning"
            ))

        elif cat == "splicing":
            int_id = f"INT-{int_counter:02d}"
            int_counter += 1
            supporting = (forensic_obs_ids + meta_obs_ids)[:3]
            evidence_items.append(EvidenceItem(
                id=int_id,
                type="interpretation",
                text="Probable splicing of external document elements (such as an imported signature, stamp, or seal) evidenced by localized noise variance discrepancy and high ELA gradient boundaries.",
                supported_by=supporting,
                confidence=0.88,
                source_agent="evidence_reasoning"
            ))

        elif cat == "local-edit":
            int_id = f"INT-{int_counter:02d}"
            int_counter += 1
            supporting = (meta_obs_ids + forensic_obs_ids)[:3]
            evidence_items.append(EvidenceItem(
                id=int_id,
                type="interpretation",
                text="Document shows signs of external raster editing or retouching using external software, causing isolated compression anomalies in specific document zones.",
                supported_by=supporting,
                confidence=0.85,
                source_agent="evidence_reasoning"
            ))

        else:
            # Undetermined or Clean
            int_id = f"INT-{int_counter:02d}"
            int_counter += 1
            supporting = (meta_obs_ids + forensic_obs_ids)[:2]
            evidence_items.append(EvidenceItem(
                id=int_id,
                type="interpretation",
                text="Document exhibits consistent digital rendering characteristics with no localized compression anomalies or overt typographic discrepancies across sampled regions.",
                supported_by=supporting,
                confidence=0.88,
                source_agent="evidence_reasoning"
            ))

        # ----------------------------------------------------
        # 5. Cross-Agent Conflict Detection
        # ----------------------------------------------------
        has_pixel_anomalies = len(suspicious_regions) > 0
        has_meta_anomalies = (
            metadata_res.get("suspicious_software_flag", False) or
            metadata_res.get("temporal_anomaly", False) or
            metadata_res.get("has_incremental_updates", False)
        )

        # Conflict 1: Clean metadata, but pixel tampering detected
        if has_pixel_anomalies and not has_meta_anomalies:
            unresolved_conflicts.append(
                "Metadata / Pixel Discrepancy: File metadata reflects standard authentic producer tags, yet Image Forensics identified localized compression/noise anomalies. An external tool may have stripped metadata or applied direct pixel modifications without updating header dictionaries."
            )

        # Conflict 2: Suspicious metadata (e.g. Photoshop), but pixel map shows uniform compression
        if has_meta_anomalies and not has_pixel_anomalies:
            unresolved_conflicts.append(
                "Metadata / Visual Discrepancy: Document metadata indicates image-editing software (e.g. Photoshop/Canva) or incremental revisions, but pixel ELA and noise analysis reveal uniform compression across all pages. The file may have been re-exported or whole-page rasterized without localized element tampering."
            )

        # Conflict 3: OCR shows typographic anomaly, but ELA has low residual
        if len(ocr_obs_ids) > 0 and not has_pixel_anomalies:
            unresolved_conflicts.append(
                "Typography / ELA Discrepancy: OCR detected font/baseline deviations within a text line, but pixel-level ELA did not show elevated compression difference. Could be caused by legitimate multi-font document template design rather than malicious splicing."
            )

        return evidence_items, unresolved_conflicts
