import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Define styles
styles = getSampleStyleSheet()
title_style = styles['Title']
title_style.fontName = 'Helvetica-Bold'
title_style.fontSize = 18

heading_style = ParagraphStyle(
    'Heading',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=14,
    spaceAfter=12
)

subheading_style = ParagraphStyle(
    'SubHeading',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=12,
    spaceAfter=8
)

body_style = styles['Normal']
body_style.fontName = 'Helvetica'
body_style.fontSize = 10
body_style.spaceAfter = 10

def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    text = "Page %s" % page_num
    canvas.drawRightString(A4[0] - inch, 0.75 * inch, text)

def build_pdf(filename, content):
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    doc.build(content, onFirstPage=add_page_number, onLaterPages=add_page_number)

def generate_nppf():
    elements = []
    elements.append(Paragraph("National Planning Policy Framework (2024 Edition)", title_style))
    elements.append(Spacer(1, 0.25 * inch))
    
    # Chapter 2
    elements.append(Paragraph("Chapter 2: Achieving sustainable development", heading_style))
    elements.append(Paragraph("Paragraph 11", subheading_style))
    elements.append(Paragraph("Plans and decisions should apply a presumption in favour of sustainable development. For decision-taking this means:", body_style))
    elements.append(Paragraph("c) approving development proposals that accord with an up-to-date development plan without delay; or", body_style))
    elements.append(Paragraph("d) where there are no relevant development plan policies, or the policies which are most important for determining the application are out-of-date, granting permission unless:", body_style))
    elements.append(Paragraph("i. the application of policies in this Framework that protect areas or assets of particular importance provides a clear reason for refusing the development proposed; or", body_style))
    elements.append(Paragraph("ii. any adverse impacts of doing so would significantly and demonstrably outweigh the benefits, when assessed against the policies in this Framework taken as a whole.", body_style))
    
    # Chapter 12
    elements.append(Paragraph("Chapter 12: Achieving well-designed places", heading_style))
    elements.append(Paragraph("Paragraph 130", subheading_style))
    elements.append(Paragraph("Planning policies and decisions should ensure that developments:", body_style))
    elements.append(Paragraph("a) will function well and add to the overall quality of the area, not just for the short term but over the lifetime of the development;", body_style))
    elements.append(Paragraph("b) are visually attractive as a result of good architecture, layout and appropriate and effective landscaping;", body_style))
    elements.append(Paragraph("c) are sympathetic to local character and history, including the surrounding built environment and landscape setting, while not preventing or discouraging appropriate innovation or change (such as increased densities);", body_style))
    elements.append(Paragraph("d) establish or maintain a strong sense of place, using the arrangement of streets, spaces, building types and materials to create attractive, welcoming and distinctive places to live, work and visit;", body_style))
    elements.append(Paragraph("e) optimise the potential of the site to accommodate and sustain an appropriate amount and mix of development (including green and other public space) and support local facilities and transport networks; and", body_style))
    elements.append(Paragraph("f) create places that are safe, inclusive and accessible and which promote health and well-being, with a high standard of amenity for existing and future users.", body_style))
    
    # Chapter 14
    elements.append(Paragraph("Chapter 14: Meeting the challenge of climate change, flooding and coastal change", heading_style))
    elements.append(Paragraph("Paragraph 167", subheading_style))
    elements.append(Paragraph("When determining any planning applications, local planning authorities should ensure that flood risk is not increased elsewhere. Where appropriate, applications should be supported by a site-specific flood-risk assessment. Development should only be allowed in areas at risk of flooding where, in the light of this assessment (and the sequential and exception tests, as applicable) it can be demonstrated that:", body_style))
    elements.append(Paragraph("a) within the site, the most vulnerable development is located in areas of lowest flood risk, unless there are overriding reasons to prefer a different location;", body_style))
    elements.append(Paragraph("b) the development is appropriately flood resistant and resilient such that, in the event of a flood, it could be quickly brought back into use without significant refurbishment;", body_style))
    elements.append(Paragraph("c) it incorporates sustainable drainage systems, unless there is clear evidence that this would be inappropriate;", body_style))
    elements.append(Paragraph("d) any residual risk can be safely managed; and", body_style))
    elements.append(Paragraph("e) safe access and escape routes are included where appropriate, as part of an agreed emergency plan.", body_style))

    # Chapter 16
    elements.append(Paragraph("Chapter 16: Conserving and enhancing the historic environment", heading_style))
    elements.append(Paragraph("Paragraph 135", subheading_style))
    elements.append(Paragraph("Local planning authorities should identify and assess the particular significance of any heritage asset that may be affected by a proposal (including by development affecting the setting of a heritage asset) taking account of the available evidence and any necessary expertise. They should take this into account when considering the impact of a proposal on a heritage asset, to avoid or minimise any conflict between the heritage asset's conservation and any aspect of the proposal.", body_style))
    elements.append(Paragraph("Paragraph 136", subheading_style))
    elements.append(Paragraph("Where there is evidence of deliberate neglect of, or damage to, a heritage asset, the deteriorated state of the heritage asset should not be taken into account in any decision.", body_style))
    elements.append(Paragraph("Paragraph 137", subheading_style))
    elements.append(Paragraph("In determining applications, local planning authorities should require an applicant to describe the significance of any heritage assets affected, including any contribution made by their setting. The level of detail should be proportionate to the assets' importance and no more than is sufficient to understand the potential impact of the proposal on their significance. As a minimum the relevant historic environment record should have been consulted and the heritage assets assessed using appropriate expertise where necessary. Where a site on which development is proposed includes, or has the potential to include, heritage assets with archaeological interest, local planning authorities should require developers to submit an appropriate desk-based assessment and, where necessary, a field evaluation.", body_style))
    
    build_pdf("nppf_excerpt.pdf", elements)

def generate_lincoln_local_plan():
    elements = []
    elements.append(Paragraph("Lincoln Local Plan 2023–2040", title_style))
    elements.append(Spacer(1, 0.25 * inch))
    
    # Housing Supply
    elements.append(Paragraph("Chapter 5: Housing", heading_style))
    elements.append(Paragraph("Policy H1: Housing Supply", subheading_style))
    elements.append(Paragraph("The Local Planning Authority will ensure the delivery of a minimum of 850 dwellings per annum over the plan period. Priority will be given to development on brownfield land within the existing built-up area of Lincoln. Windfall sites of 10 or more units will be acceptable in principle subject to compliance with other relevant policies in this plan, particularly regarding design, heritage, and flood risk.", body_style))
    
    # Affordable Housing
    elements.append(Paragraph("Policy H3: Affordable Housing", subheading_style))
    elements.append(Paragraph("On all residential development sites of 10 or more dwellings, or where the site has an area of 0.5 hectares or more, the Council will require a minimum of 30% of the total number of dwellings to be provided as affordable housing. The required tenure split for affordable housing is 70% social rent and 30% shared ownership. Where an applicant considers that the required level of affordable housing cannot be provided due to viability constraints, viability evidence must be submitted and will be subject to independent assessment at the applicant's expense.", body_style))
    
    # Design Quality
    elements.append(Paragraph("Chapter 7: Design and Built Environment", heading_style))
    elements.append(Paragraph("Policy D1: Design Quality", subheading_style))
    elements.append(Paragraph("All new development must achieve high-quality design and contribute positively to local character. Development proposals must demonstrate compliance with the Lincoln Design Guide. Commercial developments must achieve a minimum BREEAM rating of 'Very Good'. In city centre locations and along major movement corridors, ground floor commercial uses must provide active frontages to the street. Residential developments must provide minimum floor-to-ceiling heights of 2.5 metres for habitable rooms.", body_style))
    
    # Heritage
    elements.append(Paragraph("Policy D3: Heritage Assets", subheading_style))
    elements.append(Paragraph("The City of Lincoln has a rich and unique historic environment. A Heritage Impact Assessment is mandatory for any development proposal that affects the setting of a listed building, or is located within or adjacent to a Conservation Area. Development proposals must demonstrate how they preserve or enhance the character, appearance, and setting of heritage assets. The NPPF tests for assessing substantial and less than substantial harm will be rigorously applied. Proposals causing substantial harm will be refused unless it can be demonstrated that the harm is necessary to achieve substantial public benefits.", body_style))
    
    # Flood Risk
    elements.append(Paragraph("Chapter 9: Natural Environment", heading_style))
    elements.append(Paragraph("Policy NE2: Flood Risk", subheading_style))
    elements.append(Paragraph("Development proposals must comply with the Sequential Approach to flood risk. For any development proposed in Flood Zone 2 or Flood Zone 3, the Sequential Test must be applied and passed. For highly vulnerable or more vulnerable development in Flood Zone 2, the Exception Test is also required. Sustainable Drainage Systems (SuDS) are mandatory for all development sites above 0.1 hectares. Under no circumstances will highly vulnerable development be permitted in Flood Zone 3b (Functional Floodplain).", body_style))
    
    build_pdf("lincoln_local_plan.pdf", elements)

def generate_lincoln_spd():
    elements = []
    elements.append(Paragraph("Lincoln Design Supplementary Planning Document (SPD)", title_style))
    elements.append(Spacer(1, 0.25 * inch))
    
    elements.append(Paragraph("1.0 Introduction", heading_style))
    elements.append(Paragraph("This Supplementary Planning Document (SPD) provides detailed guidance to support Policy D1 of the Lincoln Local Plan 2023-2040. It is a material consideration in the determination of planning applications.", body_style))
    
    elements.append(Paragraph("2.0 Character Area Analysis", heading_style))
    elements.append(Paragraph("All major planning applications and applications within Conservation Areas must be supported by a detailed Character Area Analysis. This analysis must identify the key defining features of the immediate context, including plot widths, building lines, roofscapes, and predominant materials. The proposed design must respond directly and positively to these identified features.", body_style))
    
    elements.append(Paragraph("3.0 Building Heights and Massing", heading_style))
    elements.append(Paragraph("Building heights must be proportionate to the width of the adjacent street. As a general rule, the building height should not exceed the width of the street to ensure adequate daylight, sunlight, and a sense of enclosure without being overbearing. Within the historic core, new development should generally not exceed 3 to 4 storeys unless robust justification can be provided demonstrating no adverse impact on key strategic views, particularly those of Lincoln Cathedral.", body_style))
    
    elements.append(Paragraph("4.0 Materials Palette", heading_style))
    elements.append(Paragraph("For developments within the Lincoln city centre and adjacent Conservation Areas, the materials palette must reflect the traditional vernacular. Acceptable materials include red multi-stock brick, natural stone (limestone), natural slate for roofs, and clay pantiles. The use of large expanses of render or inappropriate modern cladding materials will be strongly resisted.", body_style))
    
    elements.append(Paragraph("5.0 Frontage Activation", heading_style))
    elements.append(Paragraph("To ensure vibrant and safe streets, development along principal routes must incorporate active frontages. Ground floor uses should include entrances, large windows, and activity-generating uses. Blank, inactive facades exceeding 5 metres in length along street frontages will not be acceptable.", body_style))

    elements.append(Paragraph("6.0 Parking Design Standards", heading_style))
    elements.append(Paragraph("Parking must be seamlessly integrated into the development and not dominate the street scene. For residential developments, communal parking areas must be well-landscaped and overlooked by habitable rooms to provide passive surveillance. A minimum of 1 secure, covered cycle parking space per bedroom must be provided.", body_style))

    build_pdf("lincoln_design_spd.pdf", elements)

def generate_sample_application():
    elements = []
    elements.append(Paragraph("Planning Application Statement", title_style))
    elements.append(Spacer(1, 0.25 * inch))
    
    elements.append(Paragraph("1.0 Application Details", heading_style))
    elements.append(Paragraph("Reference: APP/2025/0187", body_style))
    elements.append(Paragraph("Site Address: Former garage site, 14–18 Brayford Street, Lincoln, LN1 3XX", body_style))
    elements.append(Paragraph("Applicant: Midlands Developments Ltd", body_style))
    elements.append(Paragraph("Application Type: Full Planning Permission", body_style))
    
    elements.append(Paragraph("2.0 Proposed Development", heading_style))
    elements.append(Paragraph("The proposal involves the demolition of the existing disused garages on the site and the erection of a 3-storey residential block comprising 12 apartments (8 x 2-bed and 4 x 1-bed units). The development includes associated parking for 6 vehicles and communal landscaping to the rear.", body_style))
    
    elements.append(Paragraph("3.0 Site Context and Constraints", heading_style))
    elements.append(Paragraph("The application site is located within the Lincoln Conservation Area. It is situated immediately adjacent to a Grade II listed Victorian terrace at 20-24 Brayford Street. Furthermore, the site is located within 50 metres of the River Witham, and the Environment Agency's Flood Zone 2 boundary runs along the southern edge of the site.", body_style))

    elements.append(Paragraph("4.0 Design and Policy Justification", heading_style))
    elements.append(Paragraph("The proposed 3-storey scale is considered appropriate and respects the height of the adjacent 3-storey listed terrace. The material palette comprises contemporary grey brick with zinc cladding to the upper floor, which the applicant considers provides a high-quality modern contrast to the historic surroundings. Two of the twelve units (16%) are proposed as affordable housing, which the applicant's viability assessment demonstrates is the maximum viable amount for this brownfield site. The submitted Flood Risk Assessment confirms that the residential use is safe and that floor levels will be raised by 300mm above the 1 in 100 year flood level.", body_style))

    build_pdf("sample_application.pdf", elements)

if __name__ == "__main__":
    generate_nppf()
    generate_lincoln_local_plan()
    generate_lincoln_spd()
    generate_sample_application()
