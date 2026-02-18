from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY
import os
import random

def create_complex_pdf(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

    # Title Page
    story.append(Spacer(1, 100))
    story.append(Paragraph("CLINICAL STUDY PROTOCOL", styles['Title']))
    story.append(Spacer(1, 24))
    story.append(Paragraph("Protocol Number: NX-2024-003", styles['Heading2']))
    story.append(Paragraph("Investigational Product: NeuroX-2024", styles['Heading2']))
    story.append(Paragraph("Phase: 3", styles['Heading2']))
    story.append(Spacer(1, 48))
    story.append(Paragraph("Confidentality Statement:", styles['Heading3']))
    story.append(Paragraph("This document contains confidential information belonging to PharmaCorp Inc.", styles['Normal']))
    story.append(PageBreak())

    # Section 1: Introduction (Page 2)
    story.append(Paragraph("1. Introduction", styles['Heading1']))
    text = """
    Alzheimer's disease (AD) is a progressive neurodegenerative disorder characterized by cognitive decline and the accumulation of amyloid-beta plaques. 
    NeuroX-2024 is a humanized monoclonal antibody targeting protofibrillar amyloid-beta. 
    Previous Phase 2 data (Study NX-2022-001) demonstrated a dose-dependent reduction in amyloid burden.
    """
    story.append(Paragraph(text, styles['Justify']))
    story.append(Spacer(1, 12))
    
    text = """
    The rationale for this Phase 3 study is to confirm the clinical efficacy observed in the Phase 2 trial. 
    Specifically, we aim to replicate the 30% reduction in cognitive decline designated as the primary outcome in the earlier study.
    (See Section 4 for detailed Efficacy Endpoints).
    """
    story.append(Paragraph(text, styles['Justify']))
    story.append(PageBreak())

    # Section 2: Study Objectives (Page 3)
    story.append(Paragraph("2. Study Objectives", styles['Heading1']))
    story.append(Paragraph("2.1 Primary Objective", styles['Heading2']))
    story.append(Paragraph("To evaluate the efficacy of NeuroX-2024 compared to placebo in slowing clinical decline.", styles['Normal']))
    
    story.append(Paragraph("2.2 Secondary Objectives", styles['Heading2']))
    story.append(Paragraph("- To assess the safety and tolerability of NeuroX-2024.", styles['Normal']))
    story.append(Paragraph("- To measure reduction in amyloid PET signal.", styles['Normal']))
    story.append(Paragraph("- To evaluate changes in tau biomarkers in cerebrospinal fluid (CSF).", styles['Normal']))
    story.append(PageBreak())

    # Section 3: Study Design (Page 4)
    story.append(Paragraph("3. Study Design", styles['Heading1']))
    text = """
    This is a multicenter, randomized, double-blind, placebo-controlled, parallel-group study.
    Approximately 2,500 subjects will be randomized in a 1:1 ratio to receive:
    1. NeuroX-2024 10 mg/kg IV every 4 weeks (Q4W)
    2. Placebo IV every 4 weeks (Q4W)
    """
    story.append(Paragraph(text, styles['Justify']))
    
    text = """
    The treatment period will last for 72 weeks (18 months), followed by a 4-week safety follow-up period.
    An optional Open-Label Extension (OLE) will be offered to eligible participants completing the double-blind period.
    """
    story.append(Paragraph(text, styles['Justify']))
    story.append(PageBreak())

    # Section 4: Efficacy Endpoints (Page 5)
    story.append(Paragraph("4. Efficacy Endpoints", styles['Heading1']))
    story.append(Paragraph("4.1 Primary Endpoint", styles['Heading2']))
    story.append(Paragraph("Change from baseline in CDR-SB score at Week 72.", styles['Normal']))
    
    story.append(Paragraph("4.2 Key Secondary Endpoints", styles['Heading2']))
    story.append(Paragraph("1. Change from baseline in ADAS-Cog13 score at Week 72.", styles['Normal']))
    story.append(Paragraph("2. Change from baseline in ADCS-ADL-MCI score at Week 72.", styles['Normal']))
    
    text = """
    Statistical analysis will be performed using a Mixed Model for Repeated Measures (MMRM).
    The study is powered at 90% to detect a treatment difference of 0.4 points on the CDR-SB.
    """
    story.append(Paragraph(text, styles['Justify']))
    story.append(PageBreak())

    # Section 5: Safety Assessment (Page 6)
    story.append(Paragraph("5. Safety Assessment", styles['Heading1']))
    text = """
    Safety will be assessed via adverse event (AE) monitoring, physical examinations, vital signs, ECGs, and laboratory labels.
    Particular attention will be paid to Amyloid Related Imaging Abnormalities (ARIA).
    """
    story.append(Paragraph(text, styles['Justify']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("5.1 ARIA Management", styles['Heading2']))
    text = """
    MRI scans will be performed at Screening, Week 12, Week 24, Week 48, and Week 72.
    If ARIA-E (Edema) is observed:
    - Asymptomatic mild severity: Continue dosing.
    - Asymptomatic moderate/severe: Suspend dosing until resolution.
    - Symptomatic: Suspend dosing.
    (See Appendix A for ARIA Grading Scale).
    """
    story.append(Paragraph(text, styles['Justify']))
    story.append(PageBreak())

    # Filler Pages for content volume (Pages 7-9)
    for i in range(7, 10):
        story.append(Paragraph(f"{i}. Operational Details (Page {i})", styles['Heading1']))
        text = f"""
        This section contains operational details for site management, drug storage, and data handling. 
        Drug storage temperature must be maintained between 2 and 8 degrees Celsius.
        Site monitoring visits will occur every {random.randint(4,8)} weeks.
        Data entry must be completed within 48 hours of the subject visit.
        """
        story.append(Paragraph(text, styles['Justify']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 10, styles['Normal']))
        story.append(PageBreak())

    # Section 10: References (Page 10)
    story.append(Paragraph("10. References", styles['Heading1']))
    references = [
        "1. Smith J et al. Amyloid hypothesis in 2024. J Neuro. 2024;45:112-118.",
        "2. Doe A et al. Phase 2 results of NeuroX-2024. Lancet Neuro. 2023;22:88-95.",
        "3. PharmaCorp Investigator Brochure Ed 5.0, 2023."
    ]
    for ref in references:
        story.append(Paragraph(ref, styles['Normal']))
        story.append(Spacer(1, 6))

    doc.build(story)
    print(f"Complex PDF created at: {filename}")

if __name__ == "__main__":
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, "complex_clinical_protocol.pdf")
    create_complex_pdf(pdf_path)
