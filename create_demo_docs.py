"""
Script to generate high-fidelity, presentation-ready demonstration documents for the professor.
Creates documents in 'demo_documents_for_presentation/':
1. 1_Authentic_Employment_Offer.pdf -> Low Risk, Early Stop demo
2. 2_Doctored_University_Transcript.pdf -> High Risk, Text-replacement (Altered GPA & Honors)
3. 3_Forged_Bank_Statement.pdf -> High Risk, Financial balance tampering ($2,150 -> $92,150)
4. 4_Tampered_Medical_Report.png -> High Risk, Spliced diagnostic stamp & signature
5. 5_Conflicting_Tax_Certificate.pdf -> Medium Risk, Photoshop metadata vs clean pixels (Adaptive Re-examination)
"""

import os
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

OUT_DIR = Path("demo_documents_for_presentation")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def create_authentic_employment_offer():
    """Authentic employment agreement: pristine digital PDF."""
    pdf_path = OUT_DIR / "1_Authentic_Employment_Offer.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    w, h = letter

    # Header / Corporate Logo
    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0.1, 0.2, 0.4)
    c.drawString(54, h - 60, "NEXUS TECHNOLOGIES CORP.")
    
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(54, h - 75, "Department of People Operations | San Francisco, CA")
    c.drawString(54, h - 88, "Date of Issuance: September 15, 2026 | Ref: EMP-OFFER-7729")

    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.setLineWidth(1)
    c.line(54, h - 98, w - 54, h - 98)

    # Title
    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.drawString(54, h - 130, "CONFIDENTIAL OFFER OF EMPLOYMENT")

    # Body Text
    c.setFont("Helvetica", 10)
    c.drawString(54, h - 160, "Dear Candidate,")
    c.drawString(54, h - 180, "On behalf of Nexus Technologies Corp., we are pleased to offer you the position of:")
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(54, h - 200, "Senior AI Systems Research Engineer")

    c.setFont("Helvetica", 10)
    c.drawString(54, h - 225, "1. Annual Base Compensation: $165,000.00 USD, payable semi-monthly.")
    c.drawString(54, h - 245, "2. Performance Equity Bonus: 15,000 Incentive Stock Options vesting over 4 years.")
    c.drawString(54, h - 265, "3. Health & Welfare Benefits: Comprehensive medical, dental, and life coverage.")
    c.drawString(54, h - 285, "4. Start Date: November 2, 2026.")

    c.drawString(54, h - 330, "This offer is contingent upon standard background verification and reference validation.")
    
    # Signatures
    c.drawString(54, h - 420, "Authorized Executive Signature:")
    c.setFont("Helvetica-Oblique", 14)
    c.drawString(54, h - 445, "Marcus Vance (VP People & Talent)")

    c.setAuthor("Nexus HR Automated Portal v4.2")
    c.setCreator("Quartz PDF Generator")
    c.save()
    print("Created:", pdf_path)


def create_doctored_transcript():
    """University transcript with doctored Cumulative GPA from 2.85 to 3.98."""
    pdf_path = OUT_DIR / "2_Doctored_University_Transcript.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    w, h = letter

    # Seal & Header
    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(0.5, 0.1, 0.1)
    c.drawString(54, h - 60, "PACIFIC STATE UNIVERSITY")

    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.drawString(54, h - 75, "Office of the University Registrar | Official Academic Record")
    c.drawString(54, h - 88, "Student: Alexander Hayes | Student ID: PSU-992014 | Degree: B.S. Computer Science")

    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.line(54, h - 98, w - 54, h - 98)

    # Course Table
    c.setFont("Helvetica-Bold", 10)
    c.drawString(54, h - 130, "Course Code")
    c.drawString(160, h - 130, "Course Description")
    c.drawString(380, h - 130, "Credits")
    c.drawString(450, h - 130, "Grade")

    c.setStrokeColorRGB(0.85, 0.85, 0.85)
    c.line(54, h - 136, w - 54, h - 136)

    courses = [
        ("CS-301", "Data Structures & Algorithms", "4.0", "A"),
        ("CS-340", "Operating Systems Internals", "4.0", "B+"),
        ("MATH-220", "Linear Algebra & Vector Spaces", "3.0", "A-"),
        ("CS-480", "Machine Learning & Neural Nets", "4.0", "A"),
        ("CS-495", "Senior Engineering Capstone", "4.0", "A"),
    ]

    y = h - 160
    c.setFont("Helvetica", 9)
    for code, name, cr, gr in courses:
        c.drawString(54, y, code)
        c.drawString(160, y, name)
        c.drawString(390, y, cr)
        c.drawString(460, y, gr)
        y -= 24

    c.line(54, y + 10, w - 54, y + 10)

    # Cumulative GPA - Modified area
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.drawString(54, y - 15, "Cumulative Grade Point Average (GPA):")
    c.save()

    # Now open with PyMuPDF and doctor the GPA with a raster compression artifact
    doc = fitz.open(str(pdf_path))
    page = doc[0]
    pix = page.get_pixmap(dpi=300)
    img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR) if pix.n >= 3 else img_np

    # Insert altered text "3.98 / 4.00 (Summa Cum Laude)" with altered compression
    patch_w, patch_h = 750, 85
    x0, y0 = 1250, int(pix.height * 0.44)
    patch = np.ones((patch_h, patch_w, 3), dtype=np.uint8) * 255
    cv2.putText(patch, "3.98 / 4.00 - Summa Cum Laude", (10, 55), cv2.FONT_HERSHEY_DUPLEX, 1.4, (20, 20, 20), 3)

    # Compress patch with low JPEG quality to create strong ELA anomaly
    _, enc = cv2.imencode(".jpg", patch, [int(cv2.IMWRITE_JPEG_QUALITY), 32])
    patch_doctored = cv2.imdecode(enc, cv2.IMREAD_COLOR)

    img_bgr[y0:y0+patch_h, x0:x0+patch_w] = patch_doctored

    # Save as altered PDF
    doc.close()
    cv2.imwrite("temp_transcript.png", img_bgr)
    doc_out = fitz.open()
    rect = fitz.Rect(0, 0, w, h)
    p_out = doc_out.new_page(width=w, height=h)
    p_out.insert_image(rect, filename="temp_transcript.png")
    doc_out.save(str(pdf_path))
    doc_out.close()
    if os.path.exists("temp_transcript.png"):
        os.remove("temp_transcript.png")
    print("Created:", pdf_path)


def create_forged_bank_statement():
    """Bank statement with spliced closing balance ($2,150 -> $92,150)."""
    pdf_path = OUT_DIR / "3_Forged_Bank_Statement.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    w, h = letter

    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0.05, 0.35, 0.25)
    c.drawString(54, h - 60, "FIRST HORIZON NATIONAL BANK")

    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.drawString(54, h - 75, "Account Statement: Checking & Money Market | Period: Aug 1 - Aug 31, 2026")
    c.drawString(54, h - 88, "Account Holder: Sarah Jenkins | Account #: ****-****-8819")

    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.line(54, h - 98, w - 54, h - 98)

    # Summary table
    c.setFont("Helvetica-Bold", 11)
    c.drawString(54, h - 130, "Starting Balance:  $3,410.20")
    c.drawString(54, h - 150, "Total Deposits:    $4,800.00")
    c.drawString(54, h - 170, "Total Withdrawals: $6,060.20")
    c.drawString(54, h - 195, "Ending Ledger Balance:")

    c.save()

    # Render and tamper ending balance
    doc = fitz.open(str(pdf_path))
    page = doc[0]
    pix = page.get_pixmap(dpi=300)
    img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # Insert tampered balance "$92,150.00"
    x0, y0 = 950, int(pix.height * 0.235)
    patch = np.ones((70, 480, 3), dtype=np.uint8) * 255
    cv2.putText(patch, "$92,150.00", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (10, 10, 10), 3)

    _, enc = cv2.imencode(".jpg", patch, [int(cv2.IMWRITE_JPEG_QUALITY), 35])
    patch_doctored = cv2.imdecode(enc, cv2.IMREAD_COLOR)

    img_bgr[y0:y0+70, x0:x0+480] = patch_doctored

    doc.close()
    cv2.imwrite("temp_bank.png", img_bgr)
    doc_out = fitz.open()
    rect = fitz.Rect(0, 0, w, h)
    p_out = doc_out.new_page(width=w, height=h)
    p_out.insert_image(rect, filename="temp_bank.png")
    doc_out.save(str(pdf_path))
    doc_out.close()
    if os.path.exists("temp_bank.png"):
        os.remove("temp_bank.png")
    print("Created:", pdf_path)


def create_tampered_medical_report():
    """Diagnostic medical test report with spliced NEGATIVE stamp and doctor signature."""
    png_path = OUT_DIR / "4_Tampered_Medical_Report.png"
    w, h = 2479, 3508  # 300 DPI A4
    img = np.ones((h, w, 3), dtype=np.uint8) * 255

    # Add scanner noise to base
    noise = np.random.normal(0, 3.0, (h, w, 3)).astype(np.float32)
    img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    # Header
    cv2.putText(img, "METRO HEALTH DIAGNOSTICS & PATHOLOGY LAB", (150, 240), cv2.FONT_HERSHEY_DUPLEX, 1.8, (20, 40, 100), 4)
    cv2.putText(img, "CLINICAL PATHOLOGY REPORT - CONFIDENTIAL", (150, 320), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (80, 80, 80), 2)
    cv2.line(img, (150, 360), (w - 150, 360), (180, 180, 180), 3)

    cv2.putText(img, "Patient Name: Robert Chen", (150, 480), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (30, 30, 30), 3)
    cv2.putText(img, "DOB: 1988-04-12 | Sex: Male | Specimen ID: LAB-2026-X889", (150, 540), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (90, 90, 90), 2)
    cv2.putText(img, "Collection Date: 2026-09-20 08:30 AM", (150, 600), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (90, 90, 90), 2)

    cv2.line(img, (150, 660), (w - 150, 660), (200, 200, 200), 2)

    # Test Results
    cv2.putText(img, "TEST ASSAY", (150, 760), cv2.FONT_HERSHEY_DUPLEX, 1.1, (20, 40, 100), 3)
    cv2.putText(img, "METHODOLOGY", (800, 760), cv2.FONT_HERSHEY_DUPLEX, 1.1, (20, 40, 100), 3)
    cv2.putText(img, "CLINICAL RESULT", (1600, 760), cv2.FONT_HERSHEY_DUPLEX, 1.1, (20, 40, 100), 3)

    cv2.putText(img, "SARS-CoV-2 RT-PCR", (150, 850), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (30, 30, 30), 2)
    cv2.putText(img, "Multiplex Nucleic Acid Amp", (800, 850), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (30, 30, 30), 2)

    # Spliced Result Badge "NEGATIVE" from different sensor/JPEG source
    stamp_w, stamp_h = 550, 140
    stamp = np.ones((stamp_h, stamp_w, 3), dtype=np.uint8) * 255
    cv2.rectangle(stamp, (10, 10), (stamp_w - 10, stamp_h - 10), (20, 140, 40), 5)
    cv2.putText(stamp, "NEGATIVE", (60, 95), cv2.FONT_HERSHEY_DUPLEX, 2.2, (20, 140, 40), 5)

    # Heavy foreign sensor noise on stamp to trigger splicing & noise inconsistency
    stamp_noise = np.random.normal(0, 18.0, (stamp_h, stamp_w, 3)).astype(np.float32)
    stamp_noisy = np.clip(stamp.astype(np.float32) + stamp_noise, 0, 255).astype(np.uint8)

    img[800:800+stamp_h, 1550:1550+stamp_w] = stamp_noisy

    # Spliced Doctor Signature & Seal
    sig_w, sig_h = 600, 200
    sig_patch = np.ones((sig_h, sig_w, 3), dtype=np.uint8) * 250
    cv2.putText(sig_patch, "Dr. Eleanor Vance, M.D.", (30, 110), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2.4, (120, 20, 20), 4)
    cv2.putText(sig_patch, "Licensed Pathologist #99142", (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (80, 80, 80), 2)
    sig_noise = np.random.normal(0, 14.0, (sig_h, sig_w, 3)).astype(np.float32)
    sig_patch = np.clip(sig_patch.astype(np.float32) + sig_noise, 0, 255).astype(np.uint8)

    img[2600:2600+sig_h, 1400:1400+sig_w] = sig_patch

    cv2.imwrite(str(png_path), img)
    print("Created:", png_path)


def create_conflicting_tax_certificate():
    """Tax certificate: pristine visual text but Photoshop producer tag to trigger Adaptive Re-examination."""
    pdf_path = OUT_DIR / "5_Conflicting_Tax_Certificate.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    w, h = letter

    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0.15, 0.25, 0.45)
    c.drawString(54, h - 60, "STATE DEPARTMENT OF REVENUE")

    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.drawString(54, h - 75, "Certificate of Good Standing & Tax Clearance | Issue Year: 2026")
    c.drawString(54, h - 88, "Entity: Apex Global Logistics LLC | Registration ID: TAX-REV-448201")

    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.line(54, h - 98, w - 54, h - 98)

    c.setFont("Helvetica", 10)
    c.drawString(54, h - 140, "This certifies that the entity named above is in full compliance with state revenue")
    c.drawString(54, h - 160, "and franchise tax filing requirements through the current fiscal quarter.")
    c.drawString(54, h - 180, "Status: ACTIVE AND IN GOOD STANDING.")

    c.drawString(54, h - 240, "Certified by the State Tax Commissioner on September 18, 2026.")

    # Photoshop signature injected in PDF metadata
    c.setCreator("Adobe Photoshop 2024 (Windows)")
    c.setAuthor("External Editor (Exported via Photoshop CC)")
    c.save()
    print("Created:", pdf_path)


if __name__ == "__main__":
    create_authentic_employment_offer()
    create_doctored_transcript()
    create_forged_bank_statement()
    create_tampered_medical_report()
    create_conflicting_tax_certificate()
    print("\nAll presentation demo files successfully created in 'demo_documents_for_presentation/'!")
