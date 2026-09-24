"""
ADFF - Risk Assessment Agent
Calculates fused 0-100 numeric tampering risk score, assigns Low/Medium/High triage level,
and formulates investigator-oriented verification recommendations.
"""

from typing import List, Dict, Any, Tuple
from backend.models.schemas import RiskLevel, SuspiciousRegion, EvidenceItem


class RiskAssessmentAgent:
    def __init__(self):
        pass

    def assess(
        self,
        metadata_res: Dict[str, Any],
        tampering_res: Dict[str, Any],
        suspicious_regions: List[SuspiciousRegion],
        evidence_items: List[EvidenceItem],
        unresolved_conflicts: List[str],
        understanding_res: Dict[str, Any]
    ) -> Tuple[RiskLevel, float, List[str]]:
        """
        Computes weighted risk score, assigns triage rating, and derives verification actions.
        """
        score = 0.0

        # 1. Suspicious regions component (up to 45 pts)
        if suspicious_regions:
            max_conf = max(r.confidence for r in suspicious_regions)
            count_factor = min(len(suspicious_regions), 4) * 4.0
            score += (max_conf * 32.0) + count_factor

        # 2. Tampering score from forensic signals (up to 30 pts)
        max_page_score = tampering_res.get("max_page_score", 0.0)
        score += min(30.0, max_page_score * 30.0)

        # 3. Metadata component (up to 25 pts)
        meta_signals = tampering_res.get("metadata_signals", {})
        if meta_signals.get("suspicious_software"):
            score += 18.0
        if meta_signals.get("temporal_anomaly"):
            score += 20.0
        elif meta_signals.get("post_creation_mod"):
            score += 8.0
        if meta_signals.get("incremental_updates"):
            score += 10.0

        # 4. Typography anomalies (up to 15 pts)
        typo_count = tampering_res.get("typography_mismatch_count", 0)
        if typo_count > 0:
            score += min(15.0, typo_count * 8.0)

        # 5. Conflicting evidence adjustment:
        # If there are unresolved conflicts and suspicious metadata, ensure risk is at least Medium (>= 38.0)
        if unresolved_conflicts and (meta_signals.get("suspicious_software") or meta_signals.get("incremental_updates")):
            score = max(score, 42.0)

        # Cap score at 100.0
        score = min(100.0, max(0.0, score))
        score = float(round(score, 1))

        # Assign risk level based on thresholds:
        # Low: 0-35, Medium: 36-64, High: 65-100
        if score >= 65.0 or (len(suspicious_regions) > 0 and score >= 55.0):
            risk_level = RiskLevel.HIGH
        elif score >= 36.0:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        verification_steps = self._generate_recommendations(
            risk_level,
            tampering_res.get("likely_manipulation_category", "undetermined"),
            suspicious_regions,
            unresolved_conflicts,
            metadata_res,
            understanding_res
        )

        return risk_level, score, verification_steps

    def _generate_recommendations(
        self,
        risk_level: RiskLevel,
        category: str,
        regions: List[SuspiciousRegion],
        conflicts: List[str],
        metadata_res: Dict[str, Any],
        understanding: Dict[str, Any]
    ) -> List[str]:
        steps = []

        if risk_level == RiskLevel.HIGH:
            steps.append(
                "High Risk Triage: Immediately flag document for forensic senior review before financial disbursement, contract execution, or credential verification."
            )
            if category == "text-replacement":
                steps.append(
                    "Mathematical & Text Audit: Recalculate line item subtotals, tax figures, and stated grand total against vendor master records."
                )
                steps.append(
                    "Source Confirmation: Contact the issuing counterparty directly via verified directory channels (not contact details printed on this questioned document)."
                )
            elif category in ["splicing", "copy-move"]:
                steps.append(
                    "Signature & Seal Verification: Compare the questioned signature/stamp against genuine benchmark specimens on file with the organization."
                )
            if metadata_res.get("suspicious_software_flag"):
                steps.append(
                    f"Metadata Audit: Inquire why the file was created or resaved using raster manipulation software ({', '.join(metadata_res.get('software_flags', []))})."
                )

        elif risk_level == RiskLevel.MEDIUM:
            steps.append(
                "Moderate Risk Triage: Document exhibits isolated forensic anomalies or metadata conflicts. Secondary human verification is advised prior to critical operational decisions."
            )
            if conflicts:
                steps.append(
                    "Resolve Forensic Conflicts: Review conflicting evidence items identified in the report to rule out standard multi-tool scanning or non-malicious PDF re-exporting."
                )
            steps.append(
                "Request First-Generation Native File: Request the counterparty provide the original digital vector PDF or scanned original at 300+ DPI without intermediate re-compression."
            )

        else:
            steps.append(
                "Standard Low Risk Clearance: No significant forensic anomalies detected across examined indicators. Proceed with routine operational verification."
            )
            steps.append(
                "Periodic Spot-Check: Maintain standard audit trail and archival retention according to organizational document policy."
            )

        return steps
