"""
ADFF - End-to-End Pipeline & Orchestration Integration Tests
"""

import unittest
import json
from pathlib import Path
from backend.samples.generator import SampleGenerator
from backend.agents.orchestrator import ForensicOrchestrator
from backend.models.schemas import RiskLevel, ManipulationCategory


class TestForensicPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = SampleGenerator(output_dir="data/test_samples")
        cls.samples = cls.generator.generate_all()
        cls.orchestrator = ForensicOrchestrator(storage_dir="data/test_artifacts")

    def test_clean_invoice_early_stop(self):
        """Clean document must trigger early stop with Low risk."""
        report = self.orchestrator.execute_pipeline(self.samples["clean_invoice"], "clean_invoice.pdf")
        
        self.assertEqual(report.risk_level, RiskLevel.LOW)
        self.assertLess(report.risk_score, 35.0)
        self.assertEqual(len(report.suspicious_regions), 0)
        
        # Verify early stop decision in trace
        early_stop_found = any(entry.decision == "EARLY_STOP" for entry in report.execution_trace)
        self.assertTrue(early_stop_found, "Orchestrator should trigger EARLY_STOP on clean invoice.")

    def test_edited_amount_localization(self):
        """Edited amount invoice must trigger High risk, text-replacement, and localized bbox."""
        report = self.orchestrator.execute_pipeline(self.samples["edited_amount_invoice"], "edited_amount_invoice.pdf")
        
        self.assertEqual(report.risk_level, RiskLevel.HIGH)
        self.assertGreaterEqual(report.risk_score, 65.0)
        self.assertEqual(report.likely_manipulation_category, ManipulationCategory.TEXT_REPLACEMENT)
        self.assertGreater(len(report.suspicious_regions), 0)
        
        # Verify bounding box exists and contains valid coordinates [x0, y0, x1, y1]
        for reg in report.suspicious_regions:
            x0, y0, x1, y1 = reg.bbox
            self.assertLess(x0, x1)
            self.assertLess(y0, y1)

    def test_spliced_contract_detection(self):
        """Spliced contract must detect splicing and localized signature patch."""
        report = self.orchestrator.execute_pipeline(self.samples["spliced_contract"], "spliced_contract.png")
        
        self.assertIn(report.risk_level, [RiskLevel.HIGH, RiskLevel.MEDIUM])
        self.assertEqual(report.likely_manipulation_category, ManipulationCategory.SPLICING)
        self.assertGreater(len(report.suspicious_regions), 0)

    def test_conflicting_certificate_deep_pass(self):
        """Conflicting certificate must trigger adaptive re-examination pass and surface conflict."""
        report = self.orchestrator.execute_pipeline(self.samples["conflicting_certificate"], "conflicting_certificate.pdf")
        
        self.assertEqual(report.risk_level, RiskLevel.MEDIUM)
        self.assertIn("adaptive_deep_reexamination", report.methods_executed)
        self.assertTrue(len(report.unresolved_conflicts) > 0)
        
        deep_pass_found = any(entry.decision == "ADAPTIVE_REEXAMINATION_PASS" for entry in report.execution_trace)
        self.assertTrue(deep_pass_found, "Orchestrator should trigger ADAPTIVE_REEXAMINATION_PASS.")

    def test_report_schema_compliance(self):
        """Report JSON must adhere strictly to the schema in Section 8."""
        report = self.orchestrator.execute_pipeline(self.samples["edited_amount_invoice"], "edited_amount_invoice.pdf")
        dumped = json.loads(report.model_dump_json())

        # Check required keys from Section 8 schema
        required_keys = [
            "document_id",
            "analysis_date",
            "suspicious_regions",
            "risk_level",
            "risk_score",
            "evidence",
            "likely_manipulation_category",
            "methods_executed",
            "unresolved_conflicts",
            "recommended_verification_steps",
            "disclaimer"
        ]
        for k in required_keys:
            self.assertIn(k, dumped, f"Key '{k}' missing from report JSON.")

        # Check evidence structure (observations vs interpretations)
        for ev in dumped["evidence"]:
            self.assertIn("type", ev)
            self.assertIn("text", ev)
            if ev["type"] == "interpretation":
                self.assertIn("supported_by", ev)


if __name__ == "__main__":
    unittest.main()
