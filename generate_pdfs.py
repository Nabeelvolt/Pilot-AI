import os
from fpdf import FPDF

# Define the folder path on the user's Desktop
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
output_folder = os.path.join(desktop, "Pilot-AI Demo Documents")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def create_pdf(filename, title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=1, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=content)
    pdf.output(os.path.join(output_folder, filename))

# 1. Flood Risk Assessment (Make it ADEQUATE)
fra_content = """
FLOOD RISK ASSESSMENT
Site: 14-18 Brayford Street, Lincoln LN1 3XX
Prepared by: AquaHydraulics Consulting Ltd

1. Introduction
This Flood Risk Assessment has been prepared to support the application for the erection of a 3-storey residential block.

2. Sequential and Exception Test
The Sequential Test has been applied. Due to the requirement for city-centre housing and the lack of available lower-risk sites within the boundary, the development is located in Flood Zone 3. The Exception Test is passed as the development provides wider sustainability benefits to the community.

3. Climate Change Allowances
In accordance with Environment Agency guidance, a 70% climate change allowance has been factored into the hydraulic modelling to account for the residential lifetime (up to the 2080s).

4. Finished Floor Levels and Safe Access
Finished floor levels will be set at a minimum of 300mm above the 1% (1 in 100 year) flood level. A safe access and escape route is available via Brayford Street to the north, which remains flood-free during the design flood event.

5. Sustainable Drainage (SuDS)
Surface water run-off will be managed via a green roof and a cellular attenuation tank, ensuring no increase in existing run-off rates.
"""
create_pdf("Flood Risk Assessment.pdf", "Flood Risk Assessment", fra_content)

# 2. Design and Access Statement (Make it PARTIALLY ADEQUATE - missing SPD reference)
das_content = """
DESIGN AND ACCESS STATEMENT
Site: 14-18 Brayford Street, Lincoln LN1 3XX

1. Context Appraisal
The site is currently occupied by dilapidated garages. The surrounding area is characterized by 3-4 storey residential and commercial buildings using red brick and slate roofs.

2. Design Principles
The design has evolved to respect the scale and massing of the adjacent buildings. The proposed 3-storey block matches the height of the neighbouring properties.

3. Appearance and Materials
The building will be constructed using red facing brickwork and dark grey roof tiles to blend in with the local vernacular.

4. Access
Pedestrian access is provided directly from Brayford Street. Level access will be provided to all ground floor apartments in compliance with Part M of the Building Regulations, ensuring inclusive design.

5. Landscaping
Communal landscaping is provided to the rear, including native shrub planting.

[Note: Does not explicitly reference the Lincoln Design Guide SPD, which is a common deficiency]
"""
create_pdf("Design and Access Statement.pdf", "Design and Access Statement", das_content)

# 3. Energy Statement (Make it ADEQUATE)
energy_content = """
ENERGY STATEMENT
Site: 14-18 Brayford Street, Lincoln LN1 3XX

1. Policy Context
This statement demonstrates compliance with Policies S6, S7, and S8 of the Central Lincolnshire Local Plan. 

2. Central Lincolnshire Energy Efficiency Design Guide
We have completed and attached the Central Lincolnshire Energy Efficiency Checklist (Residential) in Appendix A. 

3. Fabric Efficiency
The building has been designed with a fabric-first approach. U-values will exceed Building Regulations Part L requirements: Walls 0.15, Roof 0.11, Windows 1.2.

4. Carbon Reduction and Renewable Energy (Policy S6 & S7)
SAP calculations confirm a 15% carbon reduction beyond Part L requirements.
To meet Policy S7, 18 solar PV panels will be installed on the south-facing roof slope, generating approximately 20% of the building's energy requirements from renewable sources.
"""
create_pdf("Energy Statement.pdf", "Energy Statement", energy_content)

print(f"PDFs generated successfully in {output_folder}")
