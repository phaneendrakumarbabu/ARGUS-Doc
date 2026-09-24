"""
ADFF - Report Generator Agent
Assembles the final ForensicReport object matching the required schema (§8)
and compiles an investigator-ready forensic docket in JSON and Markdown formats.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any
from backend.models.schemas import (
    ForensicReport,
    RiskLevel,
    ManipulationCategory,
    SuspiciousRegion,
    EvidenceItem,
    ExecutionLogEntry
)


class ReportGeneratorAgent:
    def __init__(self):
        self.disclaimer = (
            "These findings are indicators for further examination and do not independently "
            "establish legal proof of forgery. Final determination rests with a qualified human investigator."
        )

    def generate(
        self,
        document_id: str,
        risk_level: RiskLevel,
        risk_score: float,
        suspicious_regions: List[SuspiciousRegion],
        evidence_items: List[EvidenceItem],
        likely_manipulation_category: str,
        methods_executed: List[str],
        unresolved_conflicts: List[str],
        recommended_verification_steps: List[str],
        execution_trace: List[ExecutionLogEntry],
        page_artifacts: List[Dict[str, str]],
        document_type: str,
        output_dir: str,
        document_metadata: Optional[Dict[str, Any]] = None,
        forensic_signals: Optional[Dict[str, Any]] = None,
        chain_of_custody: Optional[List[Dict[str, Any]]] = None
    ) -> ForensicReport:
        """
        Creates and persists ForensicReport JSON and Markdown docket.
        """
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        report = ForensicReport(
            document_id=document_id,
            analysis_date=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            suspicious_regions=suspicious_regions,
            risk_level=risk_level,
            risk_score=risk_score,
            evidence=evidence_items,
            likely_manipulation_category=ManipulationCategory(likely_manipulation_category),
            methods_executed=methods_executed,
            unresolved_conflicts=unresolved_conflicts,
            recommended_verification_steps=recommended_verification_steps,
            disclaimer=self.disclaimer,
            execution_trace=execution_trace,
            page_artifacts=page_artifacts,
            document_type=document_type,
            document_metadata=document_metadata,
            forensic_signals=forensic_signals,
            chain_of_custody=chain_of_custody
        )

        # Save JSON report
        json_path = out_dir / "forensic_report.json"
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))

        # Save Markdown docket
        md_path = out_dir / "forensic_docket.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self._format_markdown_docket(report))

        return report

    def _format_markdown_docket(self, r: ForensicReport) -> str:
        """Formats an executive summary docket for human investigators."""
        md = []
        md.append(f"# Forensic Examination Docket — {r.document_id}")
        md.append(f"**Analysis Date:** {r.analysis_date}  ")
        md.append(f"**Document Type:** {r.document_type or 'General'}  ")
        md.append(f"**Risk Level:** **{r.risk_level.value.upper()}** (Score: {r.risk_score}/100)  ")
        md.append(f"**Likely Manipulation Category:** `{r.likely_manipulation_category.value}`  \n")
        
        md.append("## Methods Executed")
        md.append(", ".join([f"`{m}`" for m in r.methods_executed]) + "\n")

        if r.document_metadata:
            md.append("## File Metadata & Provenance")
            md.append(f"- **Filename:** {r.document_metadata.get('file_name', 'N/A')}")
            md.append(f"- **File Size:** {r.document_metadata.get('file_size', 0):,} bytes")
            md.append(f"- **SHA-256 Checksum:** `{r.document_metadata.get('sha256', 'N/A')}`")
            if r.document_metadata.get('creator'):
                md.append(f"- **Application/Creator:** {r.document_metadata.get('creator')}")
            if r.document_metadata.get('producer'):
                md.append(f"- **PDF Producer:** {r.document_metadata.get('producer')}")
            if r.document_metadata.get('creation_date'):
                md.append(f"- **Creation Timestamp:** {r.document_metadata.get('creation_date')}")
            if r.document_metadata.get('mod_date'):
                md.append(f"- **Modification Timestamp:** {r.document_metadata.get('mod_date')}")
            if r.document_metadata.get('software_flags'):
                md.append(f"- **Software Signatures Detected:** {', '.join(r.document_metadata.get('software_flags'))}")
            md.append("")

        if r.chain_of_custody:
            md.append("## Forensic Chain of Custody")
            md.append("| Step | Phase | Action / Verification | Timestamp |")
            md.append("|---|---|---|---|")
            for c in r.chain_of_custody:
                md.append(f"| {c.get('step')} | **{c.get('phase')}** | {c.get('description')} | {c.get('timestamp')} |")
            md.append("")

        md.append("## Suspicious Regions Localized")
        if r.suspicious_regions:
            md.append("| Page | Bounding Box [x0, y0, x1, y1] | Confidence | Reason |")
            md.append("|---|---|---|---|")
            for reg in r.suspicious_regions:
                box_str = f"[{reg.bbox[0]}, {reg.bbox[1]}, {reg.bbox[2]}, {reg.bbox[3]}]"
                md.append(f"| {reg.page} | `{box_str}` | {int(reg.confidence * 100)}% | {reg.reason} |")
        else:
            md.append("*No localized high-confidence anomalies identified.*\n")

        md.append("\n## Evidence Lineage (Observations & Interpretations)")
        md.append("### Observations (Raw Measurable Facts)")
        for ev in r.evidence:
            if ev.type == "observation":
                md.append(f"- **[{ev.id or 'OBS'}]** {ev.text}")

        md.append("\n### Interpretations (Deductions)")
        for ev in r.evidence:
            if ev.type == "interpretation":
                cite = f" *(Supported by: {', '.join(ev.supported_by)})*" if ev.supported_by else ""
                md.append(f"- **[{ev.id or 'INT'}]** {ev.text}{cite}")

        if r.unresolved_conflicts:
            md.append("\n## Unresolved Cross-Agent Conflicts")
            for conf in r.unresolved_conflicts:
                md.append(f"- ⚠️ {conf}")

        md.append("\n## Recommended Investigator Verification Steps")
        for idx, step in enumerate(r.recommended_verification_steps, 1):
            md.append(f"{idx}. {step}")

        md.append(f"\n---\n> **Disclaimer:** {r.disclaimer}\n")
        return "\n".join(md)
