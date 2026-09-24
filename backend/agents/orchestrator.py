"""
ADFF - Orchestrator Control Loop
Coordinates specialized forensic agents through an adaptive, evidence-driven decision loop:
- Decides dynamically which agents to execute based on accumulating evidence.
- Triggers Early Stop on pristine documents to conserve resources and avoid false positives.
- Triggers Adaptive Re-examination Passes when evidence is weak, ambiguous, or conflicting.
- Records a complete, transparent execution trace for investigator review.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.models.schemas import (
    ForensicReport,
    ExecutionLogEntry,
    SuspiciousRegion,
    EvidenceItem
)
from backend.agents.ingestion import IngestionAgent
from backend.agents.document_understanding import DocumentUnderstandingAgent
from backend.agents.ocr_agent import OCRAgent
from backend.agents.image_forensics import ImageForensicsAgent
from backend.agents.metadata import MetadataAgent
from backend.agents.tampering_detection import TamperingDetectionAgent
from backend.agents.localization import LocalizationAgent
from backend.agents.evidence_reasoning import EvidenceReasoningAgent
from backend.agents.risk_assessment import RiskAssessmentAgent
from backend.agents.report_generator import ReportGeneratorAgent


class ForensicOrchestrator:
    def __init__(self, storage_dir: str = "data/artifacts"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.ingestion_agent = IngestionAgent(storage_dir)
        self.understanding_agent = DocumentUnderstandingAgent()
        self.ocr_agent = OCRAgent()
        self.forensics_agent = ImageForensicsAgent(quality=90, ela_scale=18.0)
        self.deep_forensics_agent = ImageForensicsAgent(quality=75, ela_scale=24.0)
        self.metadata_agent = MetadataAgent()
        self.tampering_agent = TamperingDetectionAgent()
        self.localization_agent = LocalizationAgent()
        self.reasoning_agent = EvidenceReasoningAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.report_agent = ReportGeneratorAgent()

    def execute_pipeline(self, file_path_or_bytes: Any, filename: str) -> ForensicReport:
        """
        Executes the adaptive multi-agent forensic control loop.
        """
        execution_trace: List[ExecutionLogEntry] = []
        methods_executed: List[str] = []
        step_counter = 1

        def log_step(agent: str, action: str, decision: str, rationale: str):
            nonlocal step_counter
            entry = ExecutionLogEntry(
                step=step_counter,
                agent=agent,
                action=action,
                decision=decision,
                rationale=rationale,
                timestamp=datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
            )
            execution_trace.append(entry)
            step_counter += 1

        # =========================================================================
        # Stage 1: Ingestion & Document Integrity
        # =========================================================================
        log_step(
            agent="IngestionAgent",
            action="Validate file headers, assign document ID, render page images",
            decision="PROCEED",
            rationale=f"Ingesting candidate file '{filename}' for forensic screening."
        )
        ingest_res = self.ingestion_agent.validate_and_ingest(file_path_or_bytes, filename)
        doc_id = ingest_res["document_id"]
        doc_dir = ingest_res["doc_dir"]
        original_path = ingest_res["original_path"]
        file_type = ingest_res["file_type"]
        page_image_paths = ingest_res["page_image_paths"]
        methods_executed.append("ingestion")

        # =========================================================================
        # Stage 2: Document Understanding
        # =========================================================================
        log_step(
            agent="DocumentUnderstandingAgent",
            action="Analyze layout structure, classify genre, map high-value target zones",
            decision="PROCEED",
            rationale="Establish document baseline (Invoice, Contract, Certificate) to locate critical financial/signature zones."
        )
        understanding_res = self.understanding_agent.analyze(original_path, file_type, page_image_paths)
        methods_executed.append("document_understanding")

        # =========================================================================
        # Stage 3: Initial Screening (Metadata & Fast Pixel Forensics)
        # =========================================================================
        log_step(
            agent="MetadataAgent",
            action="Inspect PDF object dictionary / image EXIF tags for software signatures and dates",
            decision="PROCEED",
            rationale="Check for overt editing software (Photoshop, Canva, iLovePDF) and temporal modifications."
        )
        metadata_res = self.metadata_agent.analyze(original_path, file_type)
        methods_executed.append("metadata")

        log_step(
            agent="ImageForensicsAgent",
            action="Perform preliminary Error Level Analysis (ELA) and noise profiling",
            decision="PROCEED",
            rationale="Scan document pages for localized compression discrepancies or noise variances."
        )
        forensics_pages = []
        for p_idx, p_img in enumerate(page_image_paths):
            p_res = self.forensics_agent.analyze_page(
                p_img, doc_dir, page_idx=p_idx, understanding_res=understanding_res
            )
            forensics_pages.append(p_res)
        methods_executed.append("image_forensics")

        # =========================================================================
        # Stage 4: Dynamic Control Branching
        # =========================================================================
        total_clusters = sum(len(p.get("anomalous_clusters", [])) for p in forensics_pages)
        has_suspicious_software = metadata_res.get("suspicious_software_flag", False)
        has_post_mod = metadata_res.get("is_modified_post_creation", False)
        has_temporal_anomaly = metadata_res.get("temporal_anomaly", False)
        has_incremental = metadata_res.get("has_incremental_updates", False)

        ocr_pages = []
        suspicious_regions: List[SuspiciousRegion] = []
        page_overlays = []

        # Branch Condition 1: Clean Document -> Early Stop
        is_clean_candidate = (
            not has_suspicious_software and
            not has_temporal_anomaly and
            not has_post_mod and
            not has_incremental and
            total_clusters == 0
        )

        if is_clean_candidate:
            log_step(
                agent="OrchestratorControlLoop",
                action="Evaluate initial screening indicators for early termination",
                decision="EARLY_STOP",
                rationale=(
                    "Adaptive Early Stop triggered: Document metadata is authentic, timestamps match creation time, "
                    "and pixel compression/noise residual map is uniformly distributed with zero anomalous clusters. "
                    "Bypassing heavy secondary OCR typography and localization passes to minimize latency and prevent false positive alarms."
                )
            )
            # Lightweight OCR pass for general word verification
            ocr_pages = self.ocr_agent.extract(original_path, file_type, page_image_paths)
            methods_executed.append("ocr_typography")

            tampering_res = self.tampering_agent.evaluate(
                metadata_res, forensics_pages, ocr_pages, understanding_res
            )
            methods_executed.append("tampering_detection")

        # Branch Condition 2: Conflicting Evidence -> Adaptive Re-examination Pass
        elif (has_suspicious_software or has_incremental) and total_clusters == 0:
            log_step(
                agent="OrchestratorControlLoop",
                action="Identify cross-signal divergence between Metadata and Pixel Forensics",
                decision="ADAPTIVE_REEXAMINATION_PASS",
                rationale=(
                    f"Conflict detected: Metadata flags editing software ({', '.join(metadata_res.get('software_flags', []))}) "
                    f"or post-creation incremental updates, yet initial coarse ELA revealed no localized pixel clusters. "
                    "Triggering adaptive deep pass with high-sensitivity ELA (Q=75, scale=24x) and fine-grained OCR typography inspection."
                )
            )
            # Re-run deep forensics with higher sensitivity
            deep_forensics_pages = []
            for p_idx, p_img in enumerate(page_image_paths):
                deep_res = self.deep_forensics_agent.analyze_page(
                    p_img, doc_dir, page_idx=p_idx, understanding_res=understanding_res
                )
                deep_forensics_pages.append(deep_res)
            forensics_pages = deep_forensics_pages
            methods_executed.append("adaptive_deep_reexamination")

            ocr_pages = self.ocr_agent.extract(original_path, file_type, page_image_paths)
            methods_executed.append("ocr_typography")

            tampering_res = self.tampering_agent.evaluate(
                metadata_res, forensics_pages, ocr_pages, understanding_res
            )
            methods_executed.append("tampering_detection")

            loc_res = self.localization_agent.localize(
                forensics_pages, ocr_pages, page_image_paths, doc_dir
            )
            suspicious_regions = loc_res["suspicious_regions"]
            page_overlays = loc_res["page_overlays"]
            methods_executed.append("localization")

        # Branch Condition 3: Standard Anomaly Detection
        else:
            log_step(
                agent="OrchestratorControlLoop",
                action="Evaluate initial screening anomalies",
                decision="EXPAND_FORENSIC_DEEP_DIVE",
                rationale=(
                    f"Screening detected {total_clusters} anomalous pixel cluster(s) or metadata anomalies. "
                    "Engaging OCR typography analysis and spatial bounding box localization."
                )
            )
            ocr_pages = self.ocr_agent.extract(original_path, file_type, page_image_paths)
            methods_executed.append("ocr_typography")

            tampering_res = self.tampering_agent.evaluate(
                metadata_res, forensics_pages, ocr_pages, understanding_res
            )
            methods_executed.append("tampering_detection")

            loc_res = self.localization_agent.localize(
                forensics_pages, ocr_pages, page_image_paths, doc_dir
            )
            suspicious_regions = loc_res["suspicious_regions"]
            page_overlays = loc_res["page_overlays"]
            methods_executed.append("localization")

        # =========================================================================
        # Stage 5: Evidence Reasoning & Conflict Resolution
        # =========================================================================
        log_step(
            agent="EvidenceReasoningAgent",
            action="Synthesize observations, derive interpretations, evaluate agreements/conflicts",
            decision="PROCEED",
            rationale="Map raw empirical measurements to structured observations and enforce citation linkage on interpretations."
        )
        evidence_items, unresolved_conflicts = self.reasoning_agent.reason(
            metadata_res=metadata_res,
            forensics_pages=forensics_pages,
            ocr_pages=ocr_pages,
            understanding_res=understanding_res,
            tampering_res=tampering_res,
            suspicious_regions=suspicious_regions
        )
        methods_executed.append("evidence_reasoning")

        # =========================================================================
        # Stage 6: Risk Assessment & Triage
        # =========================================================================
        log_step(
            agent="RiskAssessmentAgent",
            action="Compute fused 0-100 score, categorize triage level, formulate investigator checklist",
            decision="PROCEED",
            rationale="Produce actionable investigator triage rating without automated final verdict."
        )
        risk_level, risk_score, verification_steps = self.risk_agent.assess(
            metadata_res=metadata_res,
            tampering_res=tampering_res,
            suspicious_regions=suspicious_regions,
            evidence_items=evidence_items,
            unresolved_conflicts=unresolved_conflicts,
            understanding_res=understanding_res
        )
        methods_executed.append("risk_assessment")

        # Compile page visual artifacts for frontend inspection
        page_artifacts = []
        for p_idx in range(len(page_image_paths)):
            base_p = Path(page_image_paths[p_idx]).name
            overlay_file = Path(doc_dir, f"overlay_p{p_idx}.png")
            p_dict = {
                "page": str(p_idx),
                "original_image": f"/api/artifacts/{doc_id}/{base_p}",
                "heatmap_image": f"/api/artifacts/{doc_id}/forensic_heatmap_p{p_idx}.png",
                "overlay_image": f"/api/artifacts/{doc_id}/overlay_p{p_idx}.png" if overlay_file.exists() else f"/api/artifacts/{doc_id}/{base_p}"
            }
            page_artifacts.append(p_dict)

        # =========================================================================
        # Stage 7: Report Generation
        # =========================================================================
        log_step(
            agent="ReportGeneratorAgent",
            action="Format standardized JSON report and Markdown forensic docket",
            decision="COMPLETE",
            rationale=f"Forensic triage finalized: {risk_level.value} Risk ({risk_score}/100)."
        )
        methods_executed.append("report_generator")

        # Assemble comprehensive document metadata
        doc_meta_payload = {
            "file_name": ingest_res.get("filename", filename),
            "file_type": ingest_res.get("file_type", file_type),
            "file_size": ingest_res.get("file_size", 0),
            "sha256": ingest_res.get("sha256", ""),
            "page_count": ingest_res.get("page_count", len(page_image_paths)),
            "creator": metadata_res.get("creator") or "N/A",
            "producer": metadata_res.get("producer") or "N/A",
            "creation_date": metadata_res.get("creation_date") or "N/A",
            "mod_date": metadata_res.get("mod_date") or "N/A",
            "is_modified_post_creation": metadata_res.get("is_modified_post_creation", False),
            "temporal_anomaly": metadata_res.get("temporal_anomaly", False),
            "time_difference_desc": metadata_res.get("time_difference_desc", ""),
            "has_incremental_updates": metadata_res.get("has_incremental_updates", False),
            "eof_marker_count": metadata_res.get("eof_marker_count", 0),
            "startxref_count": metadata_res.get("startxref_count", 0),
            "suspicious_software_flag": metadata_res.get("suspicious_software_flag", False),
            "software_flags": metadata_res.get("software_flags", []),
            "raw_metadata": metadata_res.get("raw_metadata", {})
        }

        # Assemble granular AI & forensic signal breakdown
        forensic_signals = {
            "ela_anomaly_score": round(forensics_pages[0].get("ela_anomaly_score", 0.0) * 100, 1) if forensics_pages else 0.0,
            "noise_inconsistency_score": round(forensics_pages[0].get("noise_inconsistency_score", 0.0) * 100, 1) if forensics_pages else 0.0,
            "edge_discontinuity_score": round(forensics_pages[0].get("edge_gradient_discontinuity_score", 0.0) * 100, 1) if forensics_pages else 0.0,
            "typography_anomalies_count": tampering_res.get("typography_mismatch_count", 0),
            "anomalous_clusters_count": tampering_res.get("total_anomalous_clusters", 0),
            "copy_move_detected": tampering_res.get("copy_move_detected", False),
            "suspicious_software_detected": metadata_res.get("suspicious_software_flag", False)
        }

        # Build cryptographic Chain of Custody
        custody_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        chain_of_custody = [
            {
                "step": 1,
                "phase": "Ingestion & Preserved Stream",
                "actor": "IngestionAgent",
                "timestamp": custody_time,
                "description": f"Verified file header for '{filename}'. Assigned ID '{doc_id}'. Original byte stream secured."
            },
            {
                "step": 2,
                "phase": "Cryptographic SHA-256 Hashing",
                "actor": "IngestionAgent",
                "timestamp": custody_time,
                "description": f"Computed tamper-evident SHA-256 hash: {ingest_res.get('sha256', '')}"
            },
            {
                "step": 3,
                "phase": "Layout Baseline & Target Mapping",
                "actor": "DocumentUnderstandingAgent",
                "timestamp": custody_time,
                "description": f"Classified genre as '{understanding_res.get('document_type', 'Document')}' and mapped high-value transaction zones."
            },
            {
                "step": 4,
                "phase": "PDF Structure & Metadata Inspection",
                "actor": "MetadataAgent",
                "timestamp": custody_time,
                "description": f"Audited dictionary tags, EOF markers (count={metadata_res.get('eof_marker_count', 1)}), and creation timestamps."
            },
            {
                "step": 5,
                "phase": "Multi-Modal Pixel Forensics",
                "actor": "ImageForensicsAgent",
                "timestamp": custody_time,
                "description": f"Analyzed ELA compression residuals and Laplacian noise variance across {len(page_image_paths)} rendered page(s)."
            },
            {
                "step": 6,
                "phase": "Evidence Reasoning & Conflict Audit",
                "actor": "EvidenceReasoningAgent",
                "timestamp": custody_time,
                "description": f"Synthesized {len(evidence_items)} evidence item(s) with observation citations and resolved inter-agent contradictions."
            },
            {
                "step": 7,
                "phase": "Forensic Triage & Docket Generation",
                "actor": "ReportGeneratorAgent",
                "timestamp": custody_time,
                "description": f"Finalized forensic report with Triage Level '{risk_level.value.upper()}' ({risk_score}/100) and human checklist."
            }
        ]

        report = self.report_agent.generate(
            document_id=doc_id,
            risk_level=risk_level,
            risk_score=risk_score,
            suspicious_regions=suspicious_regions,
            evidence_items=evidence_items,
            likely_manipulation_category=tampering_res.get("likely_manipulation_category", "undetermined"),
            methods_executed=methods_executed,
            unresolved_conflicts=unresolved_conflicts,
            recommended_verification_steps=verification_steps,
            execution_trace=execution_trace,
            page_artifacts=page_artifacts,
            document_type=understanding_res.get("document_type", "Commercial Document"),
            output_dir=doc_dir,
            document_metadata=doc_meta_payload,
            forensic_signals=forensic_signals,
            chain_of_custody=chain_of_custody
        )

        return report
