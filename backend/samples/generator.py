"""
ADFF - Synthetic Test Case Generator
Generates 4 realistic, distinct test cases demonstrating the system's adaptive pipeline:
1. clean_invoice.pdf -> Authentic digital invoice (demonstrates adaptive Early Stop)
2. edited_amount_invoice.pdf -> Invoice with altered financial total (demonstrates text-replacement localization)
3. spliced_contract.png -> Contract with imported signature/stamp (demonstrates splicing & noise inconsistency)
4. conflicting_certificate.pdf -> Certificate with Photoshop metadata vs clean pixels (demonstrates adaptive re-examination)
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
import pymupdf
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class SampleGenerator:
    def __init__(self, output_dir: str = "data/samples"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self) -> dict:
        """Generates all 4 synthetic test cases and returns their file paths."""
        return {
            "clean_invoice": str(self.generate_clean_invoice()),
            "edited_amount_invoice": str(self.generate_edited_amount_invoice()),
            "spliced_contract": str(self.generate_spliced_contract()),
            "conflicting_certificate": str(self.generate_conflicting_certificate()),
        }

    def generate_clean_invoice(self) -> Path:
        """
        Authentic digital corporate invoice.
        Pristine metadata, uniform font, consistent spacing.
        """
        pdf_path = self.output_dir / "clean_invoice.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        w, h = letter

        # Header
        c.setFont("Helvetica-Bold", 20)
        c.setFillColorRGB(0.12, 0.23, 0.38)
        c.drawString(54, h - 60, "VERTEX ENTERPRISE SOLUTIONS")

        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0.35, 0.35, 0.35)
        c.drawString(54, h - 75, "450 Silicon Boulevard, Suite 800, Tech Park, CA 94025")
        c.drawString(54, h - 88, "contact@vertex-solutions.com | +1 (800) 555-0199")

        # Invoice Banner
        c.setFont("Helvetica-Bold", 15)
        c.setFillColorRGB(0.12, 0.23, 0.38)
        c.drawString(420, h - 60, "TAX INVOICE")
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0.25, 0.25, 0.25)
        c.drawString(420, h - 75, "Invoice No: INV-2026-8942")
        c.drawString(420, h - 88, "Date: March 10, 2026")
        c.drawString(420, h - 101, "Due Date: April 10, 2026")

        # Rule
        c.setStrokeColorRGB(0.8, 0.82, 0.85)
        c.setLineWidth(1)
        c.line(54, h - 115, w - 54, h - 115)

        # Bill To
        c.setFont("Helvetica-Bold", 10)
        c.drawString(54, h - 138, "BILL TO:")
        c.setFont("Helvetica", 9)
        c.drawString(54, h - 152, "Apex Global Logistics Inc.")
        c.drawString(54, h - 165, "Attn: Accounts Payable")
        c.drawString(54, h - 178, "1200 Harbor View Way, Seattle, WA 98104")

        # Table Header
        c.setFillColorRGB(0.92, 0.94, 0.97)
        c.rect(54, h - 215, w - 108, 20, fill=True, stroke=False)
        c.setFillColorRGB(0.12, 0.23, 0.38)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(64, h - 202, "ITEM DESCRIPTION")
        c.drawString(320, h - 202, "HOURS")
        c.drawString(390, h - 202, "RATE")
        c.drawRightString(w - 64, h - 202, "AMOUNT (USD)")

        # Table Rows
        rows = [
            ("Cloud Architecture Modernization & Migration", "14.0", "$150.00", "$2,100.00"),
            ("Automated CI/CD Pipeline Configuration", "8.0", "$150.00", "$1,200.00"),
            ("Kubernetes Cluster Hardening & Monitoring", "6.0", "$160.00", "$960.00"),
            ("Infrastructure Security Audit & Compliance", "4.0", "$180.00", "$720.00"),
        ]

        y = h - 232
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0.15, 0.15, 0.15)
        for desc, qty, rate, amt in rows:
            c.drawString(64, y, desc)
            c.drawString(330, y, qty)
            c.drawString(395, y, rate)
            c.drawRightString(w - 64, y, amt)
            y -= 18

        # Totals
        c.line(340, y - 4, w - 54, y - 4)
        y -= 20
        c.drawString(350, y, "Subtotal:")
        c.drawRightString(w - 64, y, "$4,980.00")
        y -= 15
        c.drawString(350, y, "Tax (8.5%):")
        c.drawRightString(w - 64, y, "$423.30")
        y -= 18

        # Grand Total Bar
        c.setFillColorRGB(0.92, 0.94, 0.97)
        c.rect(340, y - 5, w - 394, 20, fill=True, stroke=False)
        c.setFillColorRGB(0.12, 0.23, 0.38)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(350, y, "TOTAL DUE:")
        c.drawRightString(w - 64, y, "$5,403.30")

        # Footer
        c.setFont("Helvetica", 8)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawString(54, 45, "Thank you for your business. Payment terms: Net 30 days via wire transfer.")

        # Standard clean metadata
        c.setCreator("Vertex Enterprise Invoicing Engine v4.2")
        c.setProducer("ReportLab PDF Library")
        c.save()

        return pdf_path

    def generate_edited_amount_invoice(self) -> Path:
        """
        Invoice where the total amount "$5,403.30" has been tampered to "$95,403.30"
        by overlaying an altered raster patch with an incongruent font and compression difference.
        """
        clean_pdf = self.generate_clean_invoice()
        pdf_path = self.output_dir / "edited_amount_invoice.pdf"

        doc = pymupdf.open(clean_pdf)
        page = doc[0]

        # Search for original total amount position
        text_instances = page.search_for("$5,403.30")
        if text_instances:
            rect = text_instances[0]
        else:
            rect = pymupdf.Rect(510, 375, 550, 395)

        # Expand rect slightly to cover the whole amount box
        patch_rect = pymupdf.Rect(rect.x0 - 45, rect.y0 - 2, rect.x1 + 6, rect.y1 + 2)

        # Create a doctored raster image of "$95,403.30"
        pw = int(patch_rect.width * 4)
        ph = int(patch_rect.height * 4)
        patch_img = np.full((ph, pw, 3), (235, 240, 247), dtype=np.uint8)  # BGR matching light blue bar

        # Draw doctored amount with mismatched font and color tone
        cv2.putText(
            patch_img,
            "$95,403.30",
            (8, int(ph * 0.72)),
            cv2.FONT_HERSHEY_TRIPLEX,
            0.85,
            (40, 10, 10),  # Dark navy/black
            2,
            cv2.LINE_AA
        )

        # Compress heavily at low JPEG quality to introduce stark JPEG blocking and high ELA residual
        temp_patch_path = self.output_dir / "_temp_edited_patch.jpg"
        patch_pil = Image.fromarray(cv2.cvtColor(patch_img, cv2.COLOR_BGR2RGB))
        patch_pil.save(temp_patch_path, "JPEG", quality=40)

        # Insert raster image patch into PDF page over original total
        page.insert_image(patch_rect, filename=str(temp_patch_path))

        # Update metadata to reflect external editor and modified timestamp
        doc.set_metadata({
            "creator": "Adobe Acrobat Pro 24.0",
            "producer": "Adobe PDF Library 24.1",
            "creationDate": "D:20260310090000Z",
            "modDate": "D:20260310144500Z"  # 5 hours later
        })

        doc.save(str(pdf_path))
        doc.close()

        if temp_patch_path.exists():
            temp_patch_path.unlink()

        return pdf_path

    def generate_spliced_contract(self) -> Path:
        """
        Scanned contract agreement with a signature and seal spliced from an external scan.
        Generates distinct noise variance and compression boundary on the signature block.
        """
        png_path = self.output_dir / "spliced_contract.png"
        w, h = 1200, 1600

        # Create base contract image with gentle parchment texture and baseline noise
        np.random.seed(42)
        base = np.full((h, w, 3), 250, dtype=np.uint8)
        # Subtle scanner background noise
        paper_noise = np.random.normal(0, 2.5, (h, w, 3)).astype(np.int16)
        base = np.clip(base.astype(np.int16) + paper_noise, 0, 255).astype(np.uint8)

        # Header
        cv2.putText(base, "MUTUAL RELEASE AND SETTLEMENT AGREEMENT", (140, 130), cv2.FONT_HERSHEY_TRIPLEX, 0.90, (30, 30, 30), 2, cv2.LINE_AA)
        cv2.line(base, (140, 155), (1060, 155), (100, 100, 100), 2)

        # Paragraphs of text
        paragraphs = [
            "This Mutual Release and Settlement Agreement (the 'Agreement') is entered into by and",
            "between Apex Industrial Holdings LLC ('Party A') and Horizon Marine Services Ltd ('Party B').",
            "",
            "1. SETTLEMENT CONSIDERATION: Party A agrees to wire transfer the non-refundable sum",
            "of $1,850,000.00 USD to the designated depository account of Party B within 5 business days.",
            "",
            "2. RELEASE OF CLAIMS: Upon receipt of cleared funds, Party B fully waives and discharges all",
            "past, present, and contingent claims arising out of maritime transport contract #MT-2025-09.",
            "",
            "3. CONFIDENTIALITY: Neither party shall disclose the underlying terms, quantum, or existence",
            "of this settlement to any third party without express prior written authorization.",
            "",
            "IN WITNESS WHEREOF, the authorized legal representative has executed this instrument below:"
        ]

        y = 220
        for p in paragraphs:
            if p:
                cv2.putText(base, p, (140, y), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (40, 40, 40), 1, cv2.LINE_AA)
            y += 38

        # Signature line
        sig_y = 1050
        cv2.line(base, (160, sig_y), (600, sig_y), (50, 50, 50), 2)
        cv2.putText(base, "AUTHORIZED SIGNATURE — J. R. STERLING, MANAGING DIRECTOR", (160, sig_y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (60, 60, 60), 1, cv2.LINE_AA)
        cv2.putText(base, "DATE: FEBRUARY 14, 2026", (160, sig_y + 65), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (60, 60, 60), 1, cv2.LINE_AA)

        # SPLICED SIGNATURE PATCH
        # Has distinct sensor noise variance + heavy low-Q compression artifact
        patch_w, patch_h = 420, 200
        sig_patch = np.full((patch_h, patch_w, 3), 244, dtype=np.uint8)

        # Stark sensor noise disparity
        sensor_noise = np.random.normal(0, 18.0, (patch_h, patch_w, 3)).astype(np.int16)
        sig_patch = np.clip(sig_patch.astype(np.int16) + sensor_noise, 0, 255).astype(np.uint8)

        # Blue ink signature
        pts = np.array([
            [30, 130], [70, 65], [95, 145], [130, 55], [150, 95],
            [190, 45], [230, 135], [260, 75], [320, 115], [360, 55]
        ], np.int32)
        cv2.polylines(sig_patch, [pts], False, (140, 30, 20), 3, cv2.LINE_AA)
        cv2.ellipse(sig_patch, (180, 95), (130, 45), 25, 0, 360, (130, 25, 15), 2, cv2.LINE_AA)

        # Red corporate seal
        cv2.circle(sig_patch, (330, 105), 50, (30, 30, 210), 3, cv2.LINE_AA)
        cv2.putText(sig_patch, "OFFICIAL", (295, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (30, 30, 210), 1, cv2.LINE_AA)
        cv2.putText(sig_patch, "SEAL", (310, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (30, 30, 210), 1, cv2.LINE_AA)

        # Compress patch heavily at Q=30 to induce severe block boundary artifacts
        sig_pil = Image.fromarray(cv2.cvtColor(sig_patch, cv2.COLOR_BGR2RGB))
        temp_sig_jpg = self.output_dir / "_temp_sig.jpg"
        sig_pil.save(temp_sig_jpg, "JPEG", quality=30)
        spliced_sig_bgr = cv2.imread(str(temp_sig_jpg))
        if temp_sig_jpg.exists():
            temp_sig_jpg.unlink()

        # Splice into document over signature line
        splice_x = 170
        splice_y = sig_y - 170
        base[splice_y:splice_y + patch_h, splice_x:splice_x + patch_w] = spliced_sig_bgr

        cv2.imwrite(str(png_path), base)
        return png_path

    def generate_conflicting_certificate(self) -> Path:
        """
        Academic achievement certificate.
        Metadata exhibits 'Adobe Photoshop 24.1' / incremental revisions, but pixels and typography are clean.
        Triggers the Orchestrator's adaptive re-examination pass to reconcile the conflict.
        """
        pdf_path = self.output_dir / "conflicting_certificate.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        w, h = letter

        # Gold border
        c.setStrokeColorRGB(0.68, 0.54, 0.22)
        c.setLineWidth(4)
        c.rect(36, 36, w - 72, h - 72)
        c.setLineWidth(1)
        c.rect(42, 42, w - 84, h - 84)

        # Title
        c.setFont("Times-Bold", 24)
        c.setFillColorRGB(0.12, 0.18, 0.32)
        c.drawCentredString(w / 2.0, h - 130, "CERTIFICATE OF RECOGNITION")

        c.setFont("Times-Italic", 12)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawCentredString(w / 2.0, h - 165, "This is proudly presented to")

        # Recipient
        c.setFont("Times-BoldItalic", 22)
        c.setFillColorRGB(0.68, 0.54, 0.22)
        c.drawCentredString(w / 2.0, h - 215, "DR. ELEANOR V. VANCE")

        # Description
        c.setFont("Times-Roman", 11)
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.drawCentredString(w / 2.0, h - 265, "For outstanding technical contributions and demonstrated leadership in")
        c.drawCentredString(w / 2.0, h - 285, "Applied Machine Intelligence and Autonomous Document Forensics.")

        c.drawCentredString(w / 2.0, h - 340, "Conferred on the 15th day of January, 2026.")

        # Signatures
        c.setFont("Times-Roman", 10)
        c.line(100, h - 440, 260, h - 440)
        c.drawCentredString(180, h - 455, "Dean of Engineering")

        c.line(w - 260, h - 440, w - 100, h - 440)
        c.drawCentredString(w - 180, h - 455, "President of the Academy")

        # Conflicting metadata: Photoshop software flag
        c.setCreator("Adobe Photoshop 24.1 (Windows)")
        c.setProducer("Adobe PDF Library 17.0")
        c.save()

        # Add an incremental trailer marker to simulate post-generation edit
        with open(pdf_path, "ab") as f:
            f.write(b"\n%%EOF\n% Incremental update revision 2\n")

        return pdf_path
