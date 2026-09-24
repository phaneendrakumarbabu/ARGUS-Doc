"""Agents package for ADFF."""
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
from backend.agents.orchestrator import ForensicOrchestrator

__all__ = [
    "IngestionAgent",
    "DocumentUnderstandingAgent",
    "OCRAgent",
    "ImageForensicsAgent",
    "MetadataAgent",
    "TamperingDetectionAgent",
    "LocalizationAgent",
    "EvidenceReasoningAgent",
    "RiskAssessmentAgent",
    "ReportGeneratorAgent",
    "ForensicOrchestrator",
]
