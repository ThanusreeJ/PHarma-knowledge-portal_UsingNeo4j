from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import os

def create_sample_pdf(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    story.append(Paragraph("Clinical Trial Summary: NeuroX-2024 for Alzheimer's Disease", styles['Title']))
    story.append(Spacer(1, 12))

    # Abstract
    story.append(Paragraph("<b>Abstract</b>", styles['Heading2']))
    text = """
    This document summarizes the Phase 3 clinical trial results of NeuroX-2024, a novel monoclonal antibody designed to target amyloid-beta plaques in early-stage Alzheimer's disease patients. 
    The study, conducted over 18 months with 2,500 participants, demonstrated a significant reduction in cognitive decline compared to the placebo group.
    """
    story.append(Paragraph(text, styles['Normal']))
    story.append(Spacer(1, 12))

    # Methodology
    story.append(Paragraph("<b>Methodology</b>", styles['Heading2']))
    text = """
    Participants were randomized 1:1 to receive either NeuroX-2024 (10mg/kg intravenously every 4 weeks) or a matching placebo. 
    Primary endpoints included change from baseline in the Clinical Dementia Rating-Sum of Boxes (CDR-SB).
    Secondary endpoints included amyloid PET burden and safety assessments.
    """
    story.append(Paragraph(text, styles['Normal']))
    story.append(Spacer(1, 12))

    # Results
    story.append(Paragraph("<b>Results</b>", styles['Heading2']))
    text = """
    <b>Efficacy:</b> NeuroX-2024 slowed clinical decline by 27% on the CDR-SB scale compared to placebo (p=0.001) at 18 months. 
    Amyloid PET imaging showed a robust reduction in amyloid levels to below the threshold for positivity in 80% of treated participants.
    <br/><br/>
    <b>Safety:</b> The most common adverse event was infusion-related reactions (12% vs 3% placebo). 
    ARIA-E (Amyloid Related Imaging Abnormalities - Edema) occurred in 15% of the NeuroX-2024 group, mostly asymptomatic and resolving with dose suspension.
    """
    story.append(Paragraph(text, styles['Normal']))
    story.append(Spacer(1, 12))

    # Conclusion
    story.append(Paragraph("<b>Conclusion</b>", styles['Heading2']))
    text = """
    NeuroX-2024 represents a significant advancement in disease-modifying therapies for Alzheimer's. 
    The safety profile is manageable with appropriate monitoring. 
    FDA submission is planned for Q4 2024.
    """
    story.append(Paragraph(text, styles['Normal']))

    doc.build(story)
    print(f"PDF created at: {filename}")

if __name__ == "__main__":
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, "sample_clinical_trial.pdf")
    create_sample_pdf(pdf_path)
