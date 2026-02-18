"""
Generate complex, interrelated test PDFs for multi-document RAG testing
"""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

def create_protocol_pdf():
    """Create Alzheimer's Clinical Trial Protocol"""
    filename = "test_documents/alzheimer_clinical_trial_protocol.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='darkblue',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Phase 3 Clinical Trial Protocol", title_style))
    story.append(Paragraph("NeuroX-2024: Anti-Amyloid Antibody for Alzheimer's Disease", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Protocol Number
    story.append(Paragraph("<b>Protocol ID:</b> NCT04567891", styles['Normal']))
    story.append(Paragraph("<b>Sponsor:</b> NeuroPharm Therapeutics", styles['Normal']))
    story.append(Paragraph("<b>Version:</b> 3.0 | Date: January 15, 2024", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Section 1: Introduction
    story.append(Paragraph("1. INTRODUCTION", styles['Heading2']))
    intro_text = """
    Alzheimer's disease (AD) is a progressive neurodegenerative disorder affecting over 6 million 
    Americans. The accumulation of amyloid-beta plaques is a hallmark pathological feature. 
    NeuroX-2024 is a humanized monoclonal antibody designed to target and clear these plaques.
    
    This Phase 3 study aims to replicate the promising cognitive benefits observed in Phase 2 
    trials, where a 30% reduction in cognitive decline was demonstrated over 18 months.
    """
    story.append(Paragraph(intro_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Section 2: Study Design
    story.append(Paragraph("2. STUDY DESIGN", styles['Heading2']))
    design_text = """
    <b>Study Type:</b> Randomized, double-blind, placebo-controlled<br/>
    <b>Population:</b> 2,500 participants with early Alzheimer's disease<br/>
    <b>Age Range:</b> 50-85 years<br/>
    <b>Duration:</b> 72 weeks (18 months)<br/>
    <b>Dosing:</b> NeuroX-2024 10 mg/kg IV infusion every 4 weeks vs. placebo
    """
    story.append(Paragraph(design_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Section 3: Inclusion Criteria
    story.append(Paragraph("3. INCLUSION CRITERIA", styles['Heading2']))
    criteria_text = """
    • Diagnosis of mild cognitive impairment (MCI) due to Alzheimer's disease or mild AD dementia<br/>
    • CDR-Global Score of 0.5 or 1.0<br/>
    • MMSE score between 20-28<br/>
    • Positive amyloid PET scan or CSF biomarkers<br/>
    • Stable concomitant medications for at least 4 weeks
    """
    story.append(Paragraph(criteria_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Section 4: Endpoints
    story.append(Paragraph("4. ENDPOINTS", styles['Heading2']))
    story.append(Paragraph("4.1 Primary Endpoint", styles['Heading3']))
    primary_text = """
    The primary endpoint is the change from baseline in Clinical Dementia Rating Scale Sum of Boxes 
    (CDR-SB) score at Week 72. CDR-SB ranges from 0 (no impairment) to 18 (maximum impairment).
    A positive change indicates worsening cognition.
    
    <b>Target:</b> Demonstrate at least 25% slowing of cognitive decline compared to placebo.
    """
    story.append(Paragraph(primary_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("4.2 Secondary Endpoints", styles['Heading3']))
    secondary_text = """
    • Change in ADAS-Cog13 (Alzheimer's Disease Assessment Scale-Cognitive Subscale) at Week 72<br/>
    • Change in ADCS-ADL-MCI (Activities of Daily Living) at Week 72<br/>
    • Amyloid plaque reduction measured by PET imaging at Week 72<br/>
    • Change in plasma p-tau217 biomarker levels
    """
    story.append(Paragraph(secondary_text, styles['BodyText']))
    story.append(PageBreak())
    
    # Section 5: Safety Monitoring
    story.append(Paragraph("5. SAFETY MONITORING", styles['Heading2']))
    story.append(Paragraph("5.1 ARIA-E (Amyloid-Related Imaging Abnormalities - Edema)", styles['Heading3']))
    aria_text = """
    ARIA-E is a known adverse event associated with anti-amyloid antibodies, characterized by 
    vasogenic edema visible on MRI. All participants will undergo MRI scans at baseline, Week 12, 
    Week 24, and every 12 weeks thereafter.
    
    <b>Management Protocol:</b><br/>
    • Asymptomatic mild ARIA-E: Continue dosing with increased monitoring<br/>
    • Asymptomatic moderate ARIA-E: Suspend dosing until resolution<br/>
    • Symptomatic ARIA-E (any severity): Permanently discontinue treatment
    
    Expected incidence based on Phase 2 data: 12-15% of treated patients.
    """
    story.append(Paragraph(aria_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("5.2 Other Safety Assessments", styles['Heading3']))
    safety_text = """
    • Infusion-related reactions: Monitor for 2 hours post-infusion<br/>
    • Vital signs and laboratory assessments at each visit<br/>
    • Columbia Suicide Severity Rating Scale (C-SSRS) at baseline and Week 72<br/>
    • Adverse event reporting per ICH-GCP guidelines
    """
    story.append(Paragraph(safety_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Section 6: Statistical Analysis
    story.append(Paragraph("6. STATISTICAL ANALYSIS", styles['Heading2']))
    stats_text = """
    <b>Sample Size Justification:</b> 2,500 participants (1,250 per arm) provides 90% power to 
    detect a 25% treatment effect on CDR-SB at alpha=0.05, assuming a standard deviation of 2.5 
    and 15% dropout rate.
    
    <b>Analysis Population:</b> Intent-to-treat (ITT) for primary efficacy; safety population 
    for all safety endpoints.
    
    <b>Statistical Test:</b> ANCOVA with baseline CDR-SB, age, sex, and APOE ε4 status as covariates.
    """
    story.append(Paragraph(stats_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Operational Details
    story.append(Paragraph("7. OPERATIONAL DETAILS", styles['Heading2']))
    operational_text = """
    <b>Study Sites:</b> 150 sites across United States, Europe, and Asia<br/>
    <b>Drug Storage:</b> NeuroX-2024 must be stored between 2-8°C. Do not freeze.<br/>
    <b>Enrollment Period:</b> Q1 2024 - Q3 2024<br/>
    <b>Primary Completion:</b> Anticipated Q1 2026<br/>
    <b>Regulatory Submission:</b> FDA BLA planned Q2 2026
    """
    story.append(Paragraph(operational_text, styles['BodyText']))
    
    doc.build(story)
    print(f"Created: {filename}")

def create_results_pdf():
    """Create Alzheimer's Clinical Trial Results"""
    filename = "test_documents/alzheimer_clinical_trial_results.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='darkgreen',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Phase 3 Clinical Trial Results", title_style))
    story.append(Paragraph("NeuroX-2024 in Early Alzheimer's Disease", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Trial Info
    story.append(Paragraph("<b>Trial ID:</b> NCT04567891", styles['Normal']))
    story.append(Paragraph("<b>Publication Date:</b> January 20, 2026", styles['Normal']))
    story.append(Paragraph("<b>Lead Investigator:</b> Dr. Emily Chen, MD, PhD", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Abstract
    story.append(Paragraph("ABSTRACT", styles['Heading2']))
    abstract_text = """
    <b>Background:</b> NeuroX-2024 is an anti-amyloid-beta monoclonal antibody evaluated for 
    treatment of early Alzheimer's disease (AD).
    
    <b>Methods:</b> This Phase 3, randomized, double-blind, placebo-controlled trial enrolled 
    2,500 participants with early AD. Participants received NeuroX-2024 10 mg/kg or placebo 
    IV every 4 weeks for 72 weeks.
    
    <b>Results:</b> NeuroX-2024 met its primary endpoint, demonstrating a 27% slowing of cognitive 
    decline on the CDR-SB scale compared to placebo (p=0.001). Significant reductions in brain 
    amyloid were observed. ARIA-E occurred in 15% of treated participants.
    
    <b>Conclusion:</b> NeuroX-2024 produced clinically meaningful benefits in early AD with a 
    manageable safety profile.
    """
    story.append(Paragraph(abstract_text, styles['BodyText']))
    story.append(PageBreak())
    
    # Results
    story.append(Paragraph("RESULTS", styles['Heading2']))
    
    story.append(Paragraph("1. Participant Disposition", styles['Heading3']))
    disposition_text = """
    • Total randomized: 2,500 (NeuroX-2024: 1,251; Placebo: 1,249)<br/>
    • Completed 72 weeks: 2,175 (87%)<br/>
    • Discontinuations: 325 (13%) - withdrawn consent (5%), adverse events (4%), lost to follow-up (4%)<br/>
    • Mean age: 71 years; 58% female; 42% APOE ε4 carriers
    """
    story.append(Paragraph(disposition_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("2. Primary Endpoint: CDR-SB", styles['Heading3']))
    primary_results = """
    At Week 72, the change from baseline in CDR-SB was:<br/>
    • NeuroX-2024 group: +1.21 (SE 0.08)<br/>
    • Placebo group: +1.66 (SE 0.09)<br/>
    • Difference: -0.45 points (95% CI: -0.67 to -0.23)<br/>
    • Percent slowing: 27% (p=0.001)
    
    This represents a statistically significant and clinically meaningful reduction in cognitive 
    decline. The treatment effect was consistent across subgroups including age, sex, baseline 
    severity, and APOE ε4 status.
    """
    story.append(Paragraph(primary_results, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("3. Secondary Endpoints", styles['Heading3']))
    secondary_results = """
    <b>ADAS-Cog13:</b> NeuroX-2024 showed 22% slowing of decline (p=0.008)<br/>
    <b>ADCS-ADL-MCI:</b> 18% slowing of functional decline (p=0.04)<br/>
    <b>Amyloid PET:</b> 82% reduction in brain amyloid at Week 72 vs. 2% in placebo (p<0.001)<br/>
    <b>Plasma p-tau217:</b> 35% reduction in NeuroX-2024 group vs. 5% increase in placebo (p<0.001)
    """
    story.append(Paragraph(secondary_results, styles['BodyText']))
    story.append(PageBreak())
    
    story.append(Paragraph("4. Safety Results", styles['Heading2']))
    safety_results = """
    <b>ARIA-E:</b> Occurred in 15.3% of NeuroX-2024 participants vs. 1.2% placebo<br/>
    • Asymptomatic: 12.1%<br/>
    • Symptomatic (headache, confusion): 3.2%<br/>
    • Severe: 0.8% (all resolved with treatment discontinuation)<br/>
    • No deaths attributed to ARIA-E
    
    <b>Infusion-Related Reactions:</b> 12% in NeuroX-2024 group vs. 6% placebo, mostly mild (flushing, chills)
    
    <b>Serious Adverse Events:</b> 18% NeuroX-2024 vs. 16% placebo (not significantly different)
    
    <b>Deaths:</b> 2.1% NeuroX-2024 vs. 2.3% placebo (none related to study drug)
    """
    story.append(Paragraph(safety_results, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Discussion
    story.append(Paragraph("DISCUSSION", styles['Heading2']))
    discussion_text = """
    This Phase 3 trial demonstrates that NeuroX-2024 significantly slows cognitive and functional 
    decline in early Alzheimer's disease. The 27% slowing on the CDR-SB primary endpoint exceeds 
    the protocol-defined 25% target and represents a clinically meaningful benefit for patients 
    and caregivers.
    
    The robust amyloid clearance (82% reduction) supports the amyloid hypothesis and correlates with 
    the observed clinical benefits. The biomarker changes in plasma p-tau217 suggest downstream 
    effects on tau pathology.
    
    The safety profile was generally consistent with the Phase 2 experience. ARIA-E, while occurring 
    in 15% of participants, was predominantly asymptomatic and manageable with protocol-specified 
    monitoring and dose modifications. No new safety signals emerged.
    
    <b>Regulatory Path:</b> Based on these results, NeuroPharm Therapeutics plans to submit a 
    Biologics License Application (BLA) to the FDA in Q2 2026, with potential approval anticipated 
    in Q4 2026.
    
    <b>Clinical Impact:</b> If approved, NeuroX-2024 would provide a disease-modifying treatment 
    option for the millions of patients with early Alzheimer's disease, addressing a significant 
    unmet medical need.
    """
    story.append(Paragraph(discussion_text, styles['BodyText']))
    
    doc.build(story)
    print(f"Created: {filename}")

def create_mechanism_pdf():
    """Create Drug Mechanism of Action Document"""
    filename = "test_documents/alzheimer_drug_mechanism.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='darkred',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Mechanism of Action Review", title_style))
    story.append(Paragraph("Anti-Amyloid Antibodies in Alzheimer's Disease", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Introduction
    story.append(Paragraph("1. THE AMYLOID HYPOTHESIS", styles['Heading2']))
    amyloid_text = """
    Alzheimer's disease (AD) is characterized by the accumulation of amyloid-beta (Aβ) peptides in 
    the brain, forming extracellular plaques. The amyloid cascade hypothesis posits that Aβ 
    accumulation triggers a pathological cascade including tau hyperphosphorylation, neuroinflammation, 
    synaptic dysfunction, and ultimately neuronal death.
    
    <b>Key Aβ Species:</b><br/>
    • Aβ40: More abundant, less aggregation-prone<br/>
    • Aβ42: More fibrillogenic, forms plaques more readily<br/>
    • Oligomeric Aβ: Soluble aggregates thought to be most neurotoxic
    """
    story.append(Paragraph(amyloid_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Mechanism of Action
    story.append(Paragraph("2. ANTI-AMYLOID ANTIBODY MECHANISM", styles['Heading2']))
    moa_text = """
    Anti-amyloid monoclonal antibodies like NeuroX-2024 target Aβ through multiple mechanisms:
    
    <b>Direct Binding:</b> The antibody binds to specific Aβ epitopes (NeuroX-2024 targets the 
    N-terminal region of Aβ, recognizing amino acids 1-16). This binding prevents Aβ aggregation 
    and stabilizes monomeric forms.
    
    <b>Plaque Clearance:</b> Antibody-Aβ complexes recruit microglia (brain immune cells) through 
    Fc receptor engagement. Microglia then phagocytose (engulf and degrade) the Aβ plaques.
    
    <b>Peripheral Sink Hypothesis:</b> By binding circulating Aβ in plasma, antibodies shift the 
    equilibrium, promoting efflux of Aβ from brain to blood across the blood-brain barrier.
    
    <b>Neuroinflammation Modulation:</b> By reducing plaque burden, chronic microglial activation 
    and astrocyte reactivity are decreased, reducing neuroinflammation.
    """
    story.append(Paragraph(moa_text, styles['BodyText']))
    story.append(PageBreak())
    
    # ARIA-E Mechanism
    story.append(Paragraph("3. ARIA-E: UNDERSTANDING THE SIDE EFFECT", styles['Heading2']))
    aria_mech = """
    <b>What is ARIA-E?</b><br/>
    ARIA-E (Amyloid-Related Imaging Abnormalities - Edema/Effusion) is a radiographic finding on MRI 
    characterized by vasogenic edema and/or sulcal effusions. It appears as hyperintensity on 
    fluid-attenuated inversion recovery (FLAIR) sequences.
    
    <b>Pathophysiology:</b><br/>
    The exact mechanism is not fully understood, but current theories include:
    
    • <b>Rapid Plaque Clearance:</b> Antibody-mediated removal of Aβ from vessel walls 
    (cerebral amyloid angiopathy) may transiently compromise blood-brain barrier integrity.
    
    • <b>Local Inflammation:</b> Microglial activation during phagocytosis releases inflammatory 
    mediators, increasing vascular permeability.
    
    • <b>Hemodynamic Changes:</b> Removal of perivascular amyloid may alter local blood flow dynamics.
    
    <b>Clinical Presentation:</b><br/>
    • Asymptomatic (detected only on MRI): 80% of ARIA-E cases<br/>
    • Symptomatic: Headache (most common), confusion, visual disturbances, gait instability<br/>
    • Resolution: Usually resolves within 4-16 weeks, especially with dose modification or discontinuation
    
    <b>Risk Factors:</b> APOE ε4 carriers, higher antibody doses, presence of pre-existing cerebral 
    microhemorrhages.
    """
    story.append(Paragraph(aria_mech, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Clinical Scales
    story.append(Paragraph("4. UNDERSTANDING CLINICAL OUTCOME SCALES", styles['Heading2']))
    
    story.append(Paragraph("4.1 CDR-SB (Clinical Dementia Rating - Sum of Boxes)", styles['Heading3']))
    cdr_text = """
    The CDR-SB is a widely used scale to assess dementia severity across six domains:
    
    • Memory<br/>
    • Orientation<br/>
    • Judgment and problem solving<br/>
    • Community affairs<br/>
    • Home and hobbies<br/>
    • Personal care
    
    Each domain is rated 0 (no impairment) to 3 (severe impairment). The CDR-SB sums all boxes, 
    yielding a score from 0 to 18.
    
    <b>Interpretation:</b><br/>
    • 0-1: Normal or very mild impairment<br/>
    • 1.5-4: Mild dementia<br/>
    • 5-9: Moderate dementia<br/>
    • >9: Severe dementia
    
    <b>Clinically Meaningful Change:</b> A difference of 0.5-1.0 points is generally considered 
    clinically perceptible. The 0.45-point difference observed with NeuroX-2024 represents a 
    meaningful slowing of progression.
    """
    story.append(Paragraph(cdr_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("4.2 ADAS-Cog13 (Alzheimer's Disease Assessment Scale - Cognitive)", styles['Heading3']))
    adas_text = """
    The ADAS-Cog13 is a 13-item cognitive test assessing:
    • Word recall (immediate and delayed)<br/>
    • Naming objects and fingers<br/>
    • Following commands<br/>
    • Constructional praxis<br/>
    • Ideational praxis<br/>
    • Orientation<br/>
    • Word recognition<br/>
    • Language (spoken and comprehension)<br/>
    • Number cancellation<br/>
    • Maze completion
    
    Scores range from 0 (best) to 85 (worst). Higher scores indicate greater cognitive impairment.
    A 4-point change over 18 months in AD patients is typical. The 22% slowing observed with 
    NeuroX-2024 translates to approximately a 3-month delay in cognitive decline.
    """
    story.append(Paragraph(adas_text, styles['BodyText']))
    story.append(PageBreak())
    
    # Biomarkers
    story.append(Paragraph("5. BIOMARKERS IN ALZHEIMER'S DISEASE", styles['Heading2']))
    biomarker_text = """
    <b>Amyloid PET Imaging:</b> Uses radiotracers (e.g., florbetapir, florbetaben) that bind to 
    Aβ plaques. Standardized uptake value ratios (SUVr) quantify plaque burden. Reduction in SUVr 
    indicates successful amyloid clearance.
    
    <b>Plasma p-tau217:</b> Phosphorylated tau at threonine 217 is a blood biomarker that correlates 
    with brain tau pathology. Elevated p-tau217 predicts cognitive decline. The 35% reduction seen 
    with NeuroX-2024 suggests downstream effects on tau pathology, supporting a disease-modifying 
    mechanism beyond simple symptom management.
    
    <b>CSF Biomarkers:</b> Cerebrospinal fluid (CSF) shows decreased Aβ42 and elevated tau/p-tau in AD. 
    Anti-amyloid therapies typically increase CSF Aβ42 (due to plaque solubilization) and may 
    reduce tau levels.
    """
    story.append(Paragraph(biomarker_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Conclusion
    story.append(Paragraph("6. THERAPEUTIC IMPLICATIONS", styles['Heading2']))
    conclusion_text = """
    Anti-amyloid antibodies represent a paradigm shift in Alzheimer's treatment from purely symptomatic 
    therapies (e.g., cholinesterase inhibitors) to disease-modifying interventions. By targeting the 
    underlying pathology, these agents offer the potential to slow disease progression.
    
    <b>Target Population:</b> Early AD (MCI due to AD or mild dementia) appears to be the optimal 
    treatment window, before extensive irreversible neuronal loss.
    
    <b>Combination Strategies:</b> Future research may explore combinations with anti-tau therapies, 
    BACE inhibitors, or neuroprotective agents to maximize clinical benefit.
    
    <b>Monitoring Requirements:</b> Regular MRI surveillance for ARIA is essential, particularly in 
    APOE ε4 carriers and during the first 6 months of treatment when ARIA-E risk is highest.
    """
    story.append(Paragraph(conclusion_text, styles['BodyText']))
    
    doc.build(story)
    print(f"Created: {filename}")

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs("test_documents", exist_ok=True)
    
    # Generate all test PDFs
    create_protocol_pdf()
    create_results_pdf()
    create_mechanism_pdf()
    
    print("\nAll test documents created successfully!")
    print("\nTest these documents by uploading all three and asking:")
    print("1. 'What was the primary endpoint for NeuroX-2024 and did it meet that endpoint?'")
    print("2. 'Explain the mechanism behind the cognitive improvements seen in the trial'")
    print("3. 'What is ARIA-E and how frequently was it observed in the trial?'")
