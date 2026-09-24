"""
ADFF - Automated Unit Tests for Specialized Agents
"""

import unittest
from pathlib import Path
from backend.samples.generator import SampleGenerator
from backend.agents.ingestion import IngestionAgent
from backend.agents.document_understanding import DocumentUnderstandingAgent
from backend.agents.metadata import MetadataAgent
from backend.agents.image_forensics import ImageForensicsAgent
from backend.agents.ocr_agent import OCRAgent
from backend.agents.tampering_detection import TamperingDetectionAgent
from backend.agents.localization import LocalizationAgent
from backend.agents.evidence_reasoning import EvidenceReasoningAgent
from backend.agents.risk_assessment import RiskAssessmentAgent
from backend.agents.report_generator import ReportGeneratorAgent
from backend.models.schemas import RiskLevel, ManipulationCategory


class TestForensicAgents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = SampleGenerator(output_dir="data/test_samples")
        cls.samples = cls.generator.generate_all()
        cls.storage_dir = "data/test_artifacts"

    def test_ingestion_pdf(self):
        agent = IngestionAgent(self.storage_dir)
        res = agent.validate_and_ingest(self.samples["clean_invoice"], "clean_invoice.pdf")
        self.assertTrue(res["document_id"].startswith("DOC_"))
        self.assertEqual(res["file_type"], "PDF")
        self.assertEqual(res["page_count"], 1)
        self.assertTrue(len(res["sha256"]) == 64)
        self.assertTrue(Path(res["page_image_paths"][0]).exists())

    def test_ingestion_png(self):
        agent = IngestionAgent(self.storage_dir)
        res = agent.validate_and_ingest(self.samples["spliced_contract"], "spliced_contract.png")
        self.assertEqual(res["file_type"], "PNG")
        self.assertEqual(res["page_count"], 1)
        self.assertTrue(Path(res["page_image_paths"][0]).exists())

    def test_document_understanding(self):
        ingest_agent = IngestionAgent(self.storage_dir)
        ingest_res = ingest_agent.validate_and_ingest(self.samples["clean_invoice"], "clean_invoice.pdf")
        
        agent = DocumentUnderstandingAgent()
        res = agent.analyze(ingest_res["original_path"], ingest_res["file_type"], ingest_res["page_image_paths"])
        self.assertIn("Invoice", res["document_type"])
        self.assertTrue(res["has_vector_text"])
        self.assertFalse(res["has_raster_images"])
        self.assertTrue(len(res["high_value_zones"]) > 0)

    def test_metadata_clean_vs_suspicious(self):
        agent = MetadataAgent()
        # Clean
        clean_res = agent.analyze(self.samples["clean_invoice"], "PDF")
        self.assertFalse(clean_res["suspicious_software_flag"])
        self.assertFalse(clean_res["is_modified_post_creation"])
        
        # Conflicting with Photoshop
        conf_res = agent.analyze(self.samples["conflicting_certificate"], "PDF")
        self.assertTrue(conf_res["suspicious_software_flag"])
        self.assertIn("Photoshop", conf_res["software_flags"])

    def test_image_forensics_ela(self):
        ingest_agent = IngestionAgent(self.storage_dir)
        ingest_res = ingest_agent.validate_and_ingest(self.samples["spliced_contract"], "spliced_contract.png")
        
        agent = ImageForensicsAgent(quality=90, ela_scale=18.0)
        res = agent.analyze_page(ingest_res["page_image_paths"][0], ingest_res["doc_dir"], page_idx=0)
        self.assertIn("ela_mean_residual", res)
        self.assertIn("noise_variance_mean", res)
        self.assertTrue(Path(res["heatmap_image_path"]).exists())
        self.assertTrue(Path(res["ela_image_path"]).exists())

    def test_ocr_extraction(self):
        ingest_agent = IngestionAgent(self.storage_dir)
        ingest_res = ingest_agent.validate_and_ingest(self.samples["clean_invoice"], "clean_invoice.pdf")

        agent = OCRAgent()
        ocr_res = agent.extract(ingest_res["original_path"], ingest_res["file_type"], ingest_res["page_image_paths"])
        self.assertEqual(len(ocr_res), 1)
        self.assertTrue(len(ocr_res[0]["tokens"]) > 10)
        self.assertTrue(len(ocr_res[0]["numeric_fields"]) > 0)

    def test_evidence_reasoning_citations(self):
        reasoning_agent = EvidenceReasoningAgent()
        meta = {"suspicious_software_flag": True, "software_flags": ["Photoshop"], "creator": "Photoshop", "producer": "Adobe"}
        forensics = [{"ela_mean_residual": 5.0, "ela_anomaly_score": 0.1, "anomalous_clusters": []}]
        ocr = [{"typography_anomalies": []}]
        understanding = {"document_type": "Invoice", "high_value_zones": []}
        tampering = {"likely_manipulation_category": "local-edit"}
        
        evidence, conflicts = reasoning_agent.reason(meta, forensics, ocr, understanding, tampering, [])
        # Verify that all interpretations have supporting observations
        for ev in evidence:
            if ev.type == "interpretation":
                self.assertIsNotNone(ev.supported_by)
                self.assertTrue(len(ev.supported_by) > 0)
        # Verify conflict detected (Photoshop meta but clean pixels)
        self.assertTrue(len(conflicts) > 0)


if __name__ == "__main__":
    unittest.main()
