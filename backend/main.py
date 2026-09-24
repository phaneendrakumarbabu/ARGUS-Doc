"""
ADFF - Backend Application
FastAPI REST API exposing forensic agents, orchestrator control loop,
synthetic sample runner, and static frontend hosting.
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.models.schemas import ForensicReport
from backend.agents.orchestrator import ForensicOrchestrator
from backend.samples.generator import SampleGenerator

app = FastAPI(
    title="ADFF - Agentic AI Document Tampering Detection & Forensic Analysis",
    version="1.0.0",
    description="Multi-agent document forensics coordination platform with adaptive control loop."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = BASE_DIR / "data" / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

SAMPLES_DIR = BASE_DIR / "data" / "samples"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

orchestrator = ForensicOrchestrator(storage_dir=str(ARTIFACTS_DIR))
sample_gen = SampleGenerator(output_dir=str(SAMPLES_DIR))

# Ensure sample files exist on startup
sample_paths = sample_gen.generate_all()


@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "service": "ADFF Forensic Orchestrator",
        "agents": [
            "ingestion",
            "document_understanding",
            "metadata",
            "image_forensics",
            "ocr_typography",
            "tampering_detection",
            "localization",
            "evidence_reasoning",
            "risk_assessment",
            "report_generator",
            "orchestrator"
        ]
    }


@app.get("/api/samples")
async def list_samples():
    """Lists pre-configured synthetic forensic test cases."""
    return [
        {
            "id": "clean_invoice",
            "title": "Clean Corporate Invoice (Authentic)",
            "file_name": "clean_invoice.pdf",
            "format": "PDF",
            "expected_behavior": "Orchestrator triggers Early Stop; authentic metadata and uniform ELA baseline; Low Risk.",
            "description": "Authentic enterprise services tax invoice. Demonstrates compute-saving early termination."
        },
        {
            "id": "edited_amount_invoice",
            "title": "Doctored Invoice Total ($5,403 -> $95,403)",
            "file_name": "edited_amount_invoice.pdf",
            "format": "PDF",
            "expected_behavior": "Local-edit & text-replacement; high ELA anomaly & typography mismatch; High Risk; localized bbox.",
            "description": "Invoice with modified total due. Demonstrates localized raster patch detection and OCR coordinate alignment."
        },
        {
            "id": "spliced_contract",
            "title": "Spliced Contract Agreement (Imported Signature & Seal)",
            "file_name": "spliced_contract.png",
            "format": "PNG",
            "expected_behavior": "Splicing / copy-move; sensor noise variance disparity & edge halo; High Risk; signature bbox.",
            "description": "Scanned legal agreement with spliced signature block. Demonstrates multi-sensor noise discrepancy detection."
        },
        {
            "id": "conflicting_certificate",
            "title": "Conflicting Evidence Certificate (Photoshop Meta vs Clean Pixels)",
            "file_name": "conflicting_certificate.pdf",
            "format": "PDF",
            "expected_behavior": "Orchestrator triggers Adaptive Re-examination Pass; reconciles conflict; Medium Risk triage.",
            "description": "Certificate with Adobe Photoshop producer metadata but uniform visual pixels. Demonstrates conflict handling."
        }
    ]


@app.post("/api/analyze", response_model=ForensicReport)
async def analyze_document(file: UploadFile = File(...)):
    """Uploads and executes the adaptive multi-agent forensic pipeline."""
    filename = file.filename or "uploaded_document"
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        report = orchestrator.execute_pipeline(contents, filename)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forensic pipeline error: {str(e)}")


@app.post("/api/analyze-sample/{sample_id}", response_model=ForensicReport)
async def analyze_sample(sample_id: str):
    """Executes the pipeline directly against a pre-generated sample."""
    sample_mapping = {
        "clean_invoice": SAMPLES_DIR / "clean_invoice.pdf",
        "edited_amount_invoice": SAMPLES_DIR / "edited_amount_invoice.pdf",
        "spliced_contract": SAMPLES_DIR / "spliced_contract.png",
        "conflicting_certificate": SAMPLES_DIR / "conflicting_certificate.pdf"
    }

    if sample_id not in sample_mapping:
        raise HTTPException(status_code=404, detail=f"Sample '{sample_id}' not found.")

    target_path = sample_mapping[sample_id]
    if not target_path.exists():
        # Regenerate samples
        sample_gen.generate_all()

    try:
        report = orchestrator.execute_pipeline(str(target_path), target_path.name)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing sample analysis: {str(e)}")


@app.get("/api/reports/{doc_id}")
async def get_report(doc_id: str):
    """Retrieves a previously computed report JSON."""
    report_file = ARTIFACTS_DIR / doc_id / "forensic_report.json"
    if not report_file.exists():
        raise HTTPException(status_code=404, detail="Report not found.")
    return FileResponse(str(report_file), media_type="application/json")


@app.get("/api/artifacts/{doc_id}/{filename}")
async def get_artifact(doc_id: str, filename: str):
    """Serves forensic artifacts (original, ELA heatmap, bounding box overlay)."""
    file_path = ARTIFACTS_DIR / doc_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Artifact file not found.")
    
    ext = file_path.suffix.lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".pdf": "application/pdf",
        ".json": "application/json",
        ".md": "text/markdown"
    }
    media_type = media_types.get(ext, "application/octet-stream")
    return FileResponse(str(file_path), media_type=media_type)


# Forensic Cases and Audit Trail Store
CASES_REGISTRY = [
    {
        "id": "ARG-2026-0042",
        "title": "Vertex Corp Tax Invoice Forgery Investigation",
        "category": "Financial Fraud",
        "status": "Active Investigation",
        "priority": "High",
        "created_at": "2026-09-24 16:45:00 UTC",
        "investigator": "Analyst Marcus Vance",
        "documents_count": 3,
        "findings_count": 4,
        "risk_level": "High",
        "risk_score": 74.9,
        "sample_id": "edited_amount_invoice",
        "description": "Questioned enterprise tax invoice with suspected localized raster patch modification on total payable amount."
    },
    {
        "id": "ARG-2026-0038",
        "title": "Pacific State University Academic Transcript Authentication",
        "category": "Academic Credentials",
        "status": "In Review",
        "priority": "Critical",
        "created_at": "2026-09-24 14:12:00 UTC",
        "investigator": "Analyst Sarah Jenkins",
        "documents_count": 2,
        "findings_count": 3,
        "risk_level": "High",
        "risk_score": 66.2,
        "sample_id": "edited_amount_invoice",
        "description": "Official transcript with suspected GPA line replacement and altered graduation honors font alignment."
    },
    {
        "id": "ARG-2026-0029",
        "title": "Apex Global Logistics Contract Signature Splicing Audit",
        "category": "Legal Agreements",
        "status": "Pending Verification",
        "priority": "Medium",
        "created_at": "2026-09-23 18:30:00 UTC",
        "investigator": "Analyst Marcus Vance",
        "documents_count": 1,
        "findings_count": 2,
        "risk_level": "Medium",
        "risk_score": 42.0,
        "sample_id": "conflicting_certificate",
        "description": "Commercial supply agreement presenting conflicting software producer metadata tags against visual pixel baseline."
    },
    {
        "id": "ARG-2026-0015",
        "title": "Nexus Technologies Executive Offer Letter Baseline Verification",
        "category": "Corporate HR",
        "status": "Closed / Verified",
        "priority": "Low",
        "created_at": "2026-09-22 09:15:00 UTC",
        "investigator": "Analyst David Ross",
        "documents_count": 1,
        "findings_count": 0,
        "risk_level": "Low",
        "risk_score": 6.1,
        "sample_id": "clean_invoice",
        "description": "Authentic digital employment offer. Early stop executed with zero anomalous regions detected."
    }
]

AUDIT_LOG_EVENTS = [
    {
        "id": "AUD-9941",
        "timestamp": "2026-09-24 18:55:04 UTC",
        "actor": "Analyst Marcus Vance",
        "action": "Generated Court-Ready Forensic Docket",
        "target": "DOC_20260924_124116_80dba2",
        "category": "Reporting",
        "status": "Completed",
        "checksum": "8f9a2d1c8e7a63b2"
    },
    {
        "id": "AUD-9940",
        "timestamp": "2026-09-24 18:54:12 UTC",
        "actor": "ARGUS AI Engine",
        "action": "Flagged Finding F-001 (High ELA Compression Residual)",
        "target": "edited_amount_invoice.pdf",
        "category": "Analysis",
        "status": "Flagged",
        "checksum": "3b71f92a105c48de"
    },
    {
        "id": "AUD-9939",
        "timestamp": "2026-09-24 18:53:30 UTC",
        "actor": "System Ingestion",
        "action": "Preserved Original Stream & Computed SHA-256",
        "target": "edited_amount_invoice.pdf",
        "category": "Chain of Custody",
        "status": "Verified",
        "checksum": "a82f019b7829cd55"
    },
    {
        "id": "AUD-9938",
        "timestamp": "2026-09-24 18:50:18 UTC",
        "actor": "Analyst Marcus Vance",
        "action": "Initiated Multi-Agent Forensic Inspection",
        "target": "CASE #ARG-2026-0042",
        "category": "Investigation",
        "status": "Active",
        "checksum": "f104d88e2c901aa7"
    }
]


@app.get("/api/cases")
async def list_cases():
    """Lists forensic investigation cases."""
    return CASES_REGISTRY


@app.get("/api/audit-log")
async def get_audit_log():
    """Returns chronological forensic audit trail."""
    return AUDIT_LOG_EVENTS


@app.post("/api/audit-log")
async def append_audit_log(entry: Dict[str, Any]):
    """Appends an event to the forensic audit log."""
    new_entry = {
        "id": f"AUD-{len(AUDIT_LOG_EVENTS) + 9942}",
        "timestamp": entry.get("timestamp") or "2026-09-24 19:00:00 UTC",
        "actor": entry.get("actor") or "Analyst Marcus Vance",
        "action": entry.get("action") or "Forensic Action",
        "target": entry.get("target") or "Document",
        "category": entry.get("category") or "Investigation",
        "status": entry.get("status") or "Recorded",
        "checksum": entry.get("checksum") or "e481b0a8f9c1"
    }
    AUDIT_LOG_EVENTS.insert(0, new_entry)
    return new_entry


# Mount static frontend directory
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(frontend_dir / "index.html"))
