"""
ADFF - Agentic AI Document Tampering Detection & Forensic Analysis
Data models and schemas conforming to forensic reporting and pipeline requirements.
"""

from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class ManipulationCategory(str, Enum):
    TEXT_REPLACEMENT = "text-replacement"
    COPY_MOVE = "copy-move"
    SPLICING = "splicing"
    LOCAL_EDIT = "local-edit"
    INSERTION_DELETION = "insertion-deletion"
    AI_ASSISTED = "ai-assisted"
    UNDETERMINED = "undetermined"


class SuspiciousRegion(BaseModel):
    page: int = Field(default=0, description="Page index (0-based)")
    bbox: List[int] = Field(description="Bounding box [x0, y0, x1, y1] in pixel space")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    reason: str = Field(default="", description="Reason for anomaly flag")
    associated_text: Optional[str] = Field(default=None, description="Nearby or enclosed OCR text tokens")
    source_method: str = Field(default="image_forensics", description="Originating detection method")


class EvidenceItem(BaseModel):
    id: Optional[str] = Field(default=None, description="Identifier (e.g., OBS-01 or INT-01)")
    type: str = Field(description="'observation' or 'interpretation'")
    text: str = Field(description="Forensic observation or reasoned interpretation text")
    supported_by: Optional[List[str]] = Field(default=None, description="Observation IDs supporting this interpretation")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    source_agent: Optional[str] = Field(default=None)


class DocumentMetadata(BaseModel):
    file_name: str
    file_type: str
    file_size_bytes: int
    sha256_hash: str
    page_count: int
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[str] = None
    mod_date: Optional[str] = None
    is_modified_post_creation: bool = False
    has_incremental_updates: bool = False
    suspicious_software_flag: bool = False
    software_flags: List[str] = Field(default_factory=list)
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentUnderstandingResult(BaseModel):
    document_type: str = Field(description="Invoice, Contract, Certificate, Bank Statement, Form, etc.")
    page_count: int
    dimensions: List[Dict[str, float]]
    text_density: str = Field(description="Low, Medium, High")
    high_value_zones: List[Dict[str, Any]] = Field(default_factory=list, description="Target regions like amounts, signatures")
    has_raster_images: bool = False
    has_vector_text: bool = False


class OCRToken(BaseModel):
    text: str
    bbox: List[int]  # [x0, y0, x1, y1]
    confidence: float = 1.0
    is_numeric: bool = False
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    line_num: int = 0


class OCRResult(BaseModel):
    page_index: int
    text_content: str
    tokens: List[OCRToken]
    numeric_fields: List[Dict[str, Any]] = Field(default_factory=list)
    typography_anomalies: List[Dict[str, Any]] = Field(default_factory=list)


class ImageForensicsResult(BaseModel):
    page_index: int
    ela_mean_residual: float
    ela_max_residual: float
    ela_anomaly_score: float
    noise_variance_mean: float
    noise_variance_std: float
    noise_inconsistency_score: float
    edge_gradient_discontinuity_score: float
    copy_move_detected: bool = False
    copy_move_matches: int = 0
    anomalous_clusters: List[Dict[str, Any]] = Field(default_factory=list)
    ela_image_path: Optional[str] = None
    heatmap_image_path: Optional[str] = None


class ExecutionLogEntry(BaseModel):
    step: int
    agent: str
    action: str
    decision: str
    rationale: str
    timestamp: str


class ForensicReport(BaseModel):
    document_id: str
    analysis_date: str
    suspicious_regions: List[SuspiciousRegion] = Field(default_factory=list)
    risk_level: RiskLevel
    risk_score: float = Field(ge=0.0, le=100.0)
    evidence: List[EvidenceItem]
    likely_manipulation_category: ManipulationCategory
    methods_executed: List[str]
    unresolved_conflicts: List[str] = Field(default_factory=list)
    recommended_verification_steps: List[str] = Field(default_factory=list)
    disclaimer: str = (
        "These findings are indicators for further examination and do not independently "
        "establish legal proof of forgery. Final determination rests with a qualified human investigator."
    )
    # Additional transparency metadata for the dashboard
    execution_trace: List[ExecutionLogEntry] = Field(default_factory=list)
    page_artifacts: List[Dict[str, str]] = Field(default_factory=list)
    document_type: Optional[str] = None
    document_metadata: Optional[Dict[str, Any]] = None
    forensic_signals: Optional[Dict[str, Any]] = None
    chain_of_custody: Optional[List[Dict[str, Any]]] = None
