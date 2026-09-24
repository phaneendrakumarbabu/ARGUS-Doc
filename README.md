# ARGUS-Doc — Agentic AI Document Tampering Detection & Forensic Analysis

ARGUS-Doc coordinates 10 specialized forensic agents through an **adaptive orchestrator control loop** to detect, localize, explain, and prioritize document modifications across PDF, JPG, and PNG inputs, leaving final determinations to human investigators.

---

## Key Features

1. **Multi-Agent Forensic Architecture**:
   - **Ingestion Agent**: Validates file integrity, assigns analysis ID (`DOC_...`), computes SHA-256 hash, and renders pages at 300 DPI.
   - **Document Understanding Agent**: Identifies document genres (Invoice, Contract, Certificate, Bank Statement) and high-value target zones (amounts, signatures, dates).
   - **OCR & Typography Agent**: Extracts words, bounding boxes, numeric fields, and detects typography anomalies (font family mismatch, baseline jitter).
   - **Image Forensics Agent**: Performs Error Level Analysis (ELA), Laplacian local noise inconsistency profiling, edge continuity analysis, and copy-move block matching.
   - **Metadata Agent**: Inspects PDF object structures, software signatures (`Photoshop`, `Canva`, `iLovePDF`, `Sejda`), incremental updates (`%%EOF` chains), and creation/modification timestamp discrepancies.
   - **Tampering Detection Agent**: Aggregates multi-modal signals and classifies the likely manipulation category (`text-replacement`, `copy-move`, `splicing`, `local-edit`, `insertion-deletion`, `undetermined`).
   - **Localization Agent**: Maps high-residual clusters directly to document space, cross-referencing OCR coordinates to generate visual bounding box overlays.
   - **Evidence Reasoning Agent**: Strictly separates **Observations** (raw measurements e.g. `OBS-01`) from **Interpretations** (reasoned deductions e.g. `INT-01`) citing supporting observation IDs, and surfaces cross-agent conflicts.
   - **Risk Assessment Agent**: Computes fused 0-100 score and assigns triage level (**Low**, **Medium**, **High**).
   - **Report Generator Agent**: Compiles investigator-ready JSON matching the required schema and Markdown dockets.
   - **Adaptive Orchestrator Loop**: Dynamically decides which agents to execute:
     - **Early Stop**: Clean documents with pristine metadata and uniform compression terminate early to save compute.
     - **Adaptive Re-examination Pass**: Documents with conflicting signals (e.g., Photoshop metadata vs. clean pixels) trigger an extra high-sensitivity forensic pass.

2. **Standardized Forensic Report (§8 Schema)**:
   Outputs JSON strictly adhering to the schema:
   - `document_id`, `analysis_date`, `suspicious_regions`, `risk_level`, `risk_score`
   - `evidence` (observations and interpretations with citation linkages)
   - `likely_manipulation_category`
   - `methods_executed`
   - `unresolved_conflicts`
   - `recommended_verification_steps`
   - `disclaimer`

3. **Interactive Modern Dashboard**:
   - Multi-view visualizer: Bounding Box Overlay, Thermal ELA Heatmap, and Base Document.
   - Live Orchestrator Decision Trace showing every execution step and rationale.
   - Evidence Matrix linking Interpretations to raw Observations.
   - Human Investigator Action Checklist.
   - Quick one-click runner for 4 pre-configured synthetic benchmark cases.

---

## Quick Start

### 1. Requirements & Installation
Ensure Python 3.10+ is installed with the required libraries:
```bash
pip install fastapi uvicorn pillow pypdf reportlab pymupdf numpy opencv-python-headless scipy httpx python-multipart
```

### 2. Start the Server
Run the FastAPI application from the project root:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

### 3. Run Automated Tests
Run the comprehensive unit and integration test suite:
```bash
python -m unittest discover -s tests -v
```

---

## Synthetic Test Cases

ADFF includes 4 self-contained synthetic benchmark cases:

| Case | File | Key Signals | Expected Orchestrator Behavior |
|---|---|---|---|
| **1. Clean Invoice** | `clean_invoice.pdf` | Authentic metadata, uniform compression | **Early Stop** triggered; **Low Risk** (~6/100); 0 suspicious regions |
| **2. Doctored Invoice** | `edited_amount_invoice.pdf` | Total modified from $5,403 to $95,403 | **High Risk** (~75/100); `text-replacement`; localized bbox over total due |
| **3. Spliced Contract** | `spliced_contract.png` | Spliced signature block & seal | **High Risk** (~62/100); `splicing`; localized bbox over signature patch |
| **4. Conflicting Evidence** | `conflicting_certificate.pdf` | Photoshop producer tag + clean visual pixels | **Adaptive Re-examination Pass** triggered; **Medium Risk** (~42/100); unresolved conflict surfaced |
