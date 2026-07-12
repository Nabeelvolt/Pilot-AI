"""
Validation rules for planning application documents.
Derived from:
- GOV.UK National Validation Requirements (updated May 2025)
- Central Lincolnshire Local Validation Lists (adopted May 2024)
- Central Lincolnshire SPDs and Guidance Notes (2023)
"""

DOCUMENT_REQUIREMENTS = {

    "flood_risk_assessment": {
        "policy_basis": ["NPPF Paragraph 167", "Policy NE2"],
        "required_when": ["Flood Zone 2", "Flood Zone 3", "sites over 1 hectare in any zone"],
        "mandatory_sections": [
            "Sequential Test — demonstrating no reasonably available lower-risk sites",
            "Exception Test — where Sequential Test is passed but Flood Zone 2/3 unavoidable",
            "Climate change allowances — future flood risk over lifetime of development",
            "Flood risk vulnerability classification of proposed use",
            "Finished floor levels — minimum 300mm above 1% (1 in 100) flood level",
            "Safe access and escape route during flood event",
            "Sustainable Drainage System (SuDS) proposals",
            "Residual risk assessment after mitigation measures",
        ],
        "adequacy_indicators": [
            "References Environment Agency flood mapping data",
            "Includes hydraulic modelling or references existing modelling",
            "States the 1% annual probability flood level for the site",
            "Demonstrates consultation with Environment Agency",
            "Addresses surface water run-off rates — must not increase existing rates",
        ],
        "common_deficiencies": [
            "Sequential Test absent or inadequately justified",
            "Climate change allowances not applied or outdated (use 70% for residential to 2080s)",
            "Finished floor levels not specified or below required minimum",
            "SuDS strategy absent for sites over 0.1 hectare",
            "No safe access route demonstrated during design flood event",
        ]
    },

    "heritage_impact_statement": {
        "policy_basis": ["NPPF Paragraphs 195-202", "Policy D3"],
        "required_when": [
            "Conservation Area",
            "Grade I Listed Building",
            "Grade II* Listed Building",
            "Grade II Listed Building",
            "Within setting of any listed building",
            "Scheduled Ancient Monument within or adjacent"
        ],
        "mandatory_sections": [
            "Identification and description of heritage assets affected",
            "Assessment of significance of each heritage asset (using Historic England guidance)",
            "Assessment of the proposed development's impact on significance",
            "Direct impacts — physical changes to fabric of heritage asset",
            "Indirect impacts — changes to setting, views, character",
            "Magnitude of harm: Substantial harm / Less than substantial harm / No harm",
            "Public benefits justification (if any harm identified)",
            "Mitigation measures proposed",
            "Conclusion referencing NPPF heritage tests",
        ],
        "adequacy_indicators": [
            "References Historic England 'Conservation Principles' or 'Setting of Heritage Assets' guidance",
            "Uses the four-stage approach to assessing setting impacts",
            "Prepared by a suitably qualified heritage professional",
            "Includes historical research and photographic record",
            "Clearly distinguishes between designated and non-designated assets",
        ],
        "common_deficiencies": [
            "Significance not properly assessed — describes the building rather than assessing significance",
            "Setting assessment absent or superficial",
            "Does not apply the NPPF harm test (substantial vs less than substantial)",
            "Public benefits not weighed against harm",
            "Prepared by architect rather than heritage specialist — lacks independence",
        ]
    },

    "design_access_statement": {
        "policy_basis": ["NPPF Chapter 12", "Policy D1", "Lincoln Design SPD"],
        "required_when": [
            "Major development (10+ dwellings or 1000m² commercial)",
            "Development in Conservation Area of 1+ dwelling or 100m²+",
            "Listed Building Consent applications"
        ],
        "mandatory_sections": [
            "Context appraisal — site and surroundings analysis",
            "Design principles applied and how context informed them",
            "Layout — how buildings, routes and spaces are arranged",
            "Scale — relationship of building height/massing to surroundings",
            "Appearance — materials, architecture, facing materials",
            "Landscaping and public realm",
            "Access — pedestrian, cycle, and vehicle access arrangements",
            "Inclusive design — how development is accessible to all users",
            "Compliance with relevant Local Plan design policies",
        ],
        "adequacy_indicators": [
            "References Lincoln Design Guide SPD specifically",
            "Includes site photographs and analysis drawings",
            "Demonstrates how design evolved in response to context",
            "Addresses active frontages where required by policy",
            "Shows compliance with minimum space standards",
        ],
        "common_deficiencies": [
            "Describes the design rather than justifying it against policy",
            "Context appraisal absent or generic",
            "Does not reference Lincoln Design Guide SPD",
            "Access section missing or inadequate",
            "Prepared after design fixed — not used to shape design",
        ]
    },

    "biodiversity_net_gain": {
        "policy_basis": [
            "Environment Act 2021 Schedule 14",
            "NPPF Chapter 15",
            "Policy S61",
            "Central Lincolnshire BNG Guidance Note"
        ],
        "required_when": [
            "All major applications (10+ dwellings or 1 hectare+)",
            "All minor applications from April 2024 (mandatory statutory BNG)"
        ],
        "mandatory_sections": [
            "Biodiversity Metric calculation (Natural England Small Sites Metric or Biodiversity Metric 4.0)",
            "Baseline habitat survey — current condition of all habitats on site",
            "Proposed habitat creation and enhancement — post-development condition",
            "10% net gain calculation — demonstrating minimum 10% uplift",
            "Habitat Management and Monitoring Plan (HMMP) — 30-year commitment",
            "Off-site units register reference number (if off-site units used)",
            "Legal mechanism for securing BNG — conservation covenant or S106",
            "Registered biodiversity gain site details (if off-site)",
        ],
        "adequacy_indicators": [
            "Metric calculation completed by suitably qualified ecologist",
            "Habitat condition assessments completed on-site not desktop only",
            "All habitats including trees and hedgerows included in metric",
            "HMMP prepared to Natural England standard format",
            "Off-site units verified on Biodiversity Gain Sites Register",
        ],
        "common_deficiencies": [
            "10% uplift not achieved — metric shows less than 10% gain",
            "Habitats removed during demolition/site clearance not included in baseline",
            "Trees not included (often omitted — must use Biodiversity Metric 4.0 for trees)",
            "HMMP missing or not to required standard",
            "Off-site register reference number not provided",
            "Metric completed by architect rather than qualified ecologist",
            "Pre-clearance habitats not surveyed — baseline understated",
        ]
    },

    "energy_statement": {
        "policy_basis": ["Policies S6", "Policy S7", "Policy S8", "Central Lincolnshire Energy Efficiency Design Guide 2023"],
        "required_when": [
            "All residential development in Central Lincolnshire",
            "All commercial development in Central Lincolnshire"
        ],
        "mandatory_sections": [
            "Fabric efficiency — U-values for walls, roof, floor, windows",
            "Air permeability — target and specification",
            "Heating system type and efficiency rating",
            "Renewable energy provision (Policy S7 requirement)",
            "Carbon reduction calculation — percentage improvement over Building Regulations Part L",
            "SAP or SBEM calculation reference",
            "Compliance with Central Lincolnshire Energy Efficiency Checklist",
        ],
        "adequacy_indicators": [
            "References Central Lincolnshire Energy Efficiency Design Guide 2023",
            "Completes the Energy Efficiency Checklist (residential or non-residential version)",
            "Achieves minimum 10% carbon reduction beyond Part L (Policy S6)",
            "Includes renewable energy to achieve minimum 15% of energy from renewables (Policy S7)",
        ],
        "common_deficiencies": [
            "Does not reference Central Lincolnshire Energy Efficiency Design Guide",
            "Energy Efficiency Checklist not completed",
            "Carbon reduction target not met",
            "Renewable energy provision absent",
            "SAP calculation not referenced",
        ]
    },

    "planning_statement": {
        "policy_basis": ["Development Plan — Material Considerations", "NPPF Chapter 4"],
        "required_when": ["Major applications", "Applications raising significant policy issues"],
        "mandatory_sections": [
            "Description of site and surroundings",
            "Description of proposed development",
            "Relevant planning history of the site",
            "Assessment against relevant Local Plan policies",
            "Assessment against NPPF",
            "Assessment of material planning considerations",
            "Pre-application engagement summary",
            "Conclusion on planning balance",
        ],
        "adequacy_indicators": [
            "Addresses each relevant Local Plan policy individually",
            "References correct adopted Local Plan (Central Lincolnshire Local Plan 2023)",
            "Applies NPPF paragraph 11 presumption in favour test if development plan silent",
            "Acknowledges constraints and explains mitigation",
        ],
        "common_deficiencies": [
            "References outdated superseded policies",
            "Generic policy assessment not site-specific",
            "Pre-application engagement not referenced",
            "Conclusion does not address all material considerations",
        ]
    },

    "transport_assessment": {
        "policy_basis": ["NPPF Chapter 9", "Policy S47"],
        "required_when": [
            "Residential development of 100+ dwellings",
            "Commercial development generating significant traffic",
            "Development in locations with existing highway issues"
        ],
        "mandatory_sections": [
            "Existing site and highway conditions",
            "Trip generation — proposed development traffic",
            "Trip distribution and assignment to local network",
            "Impact assessment — junctions and links",
            "Mitigation measures — highway works, travel plan",
            "Sustainable transport provision — cycle, pedestrian links",
            "Travel Plan framework",
        ],
        "common_deficiencies": [
            "Trip generation uses inappropriate TRICS comparators",
            "Junction capacity assessment absent",
            "Sustainable transport routes not assessed",
            "Travel Plan absent",
        ]
    }
}

# National validation requirements by application type
# Source: GOV.UK Making an Application guidance (updated May 2025)
# + Central Lincolnshire Local Validation Lists (adopted May 2024)
VALIDATION_REQUIREMENTS = {

    "Full Planning Permission": {
        "national_mandatory": [
            "Completed application form (1APP standard form)",
            "Location plan at 1:1250 or 1:2500 scale with site edged red",
            "Block plan at 1:500 or 1:200 showing site and immediate surroundings",
            "Ownership Certificate (A, B, C or D as appropriate)",
            "Agricultural Land Declaration",
            "Correct application fee",
        ],
        "national_conditional": [
            {
                "document": "Design and Access Statement",
                "required_when": "Major development OR development in Conservation Area of 1+ dwelling or 100m²+"
            },
            {
                "document": "Fire Statement",
                "required_when": "High-rise residential buildings (18m+ or 7+ storeys) from 1 August 2021"
            },
            {
                "document": "Environmental Statement",
                "required_when": "EIA development — Schedule 1 or screened Schedule 2 development"
            }
        ],
        "central_lincolnshire_local_list": [
            {
                "document": "Flood Risk Assessment",
                "required_when": "Site in Flood Zone 2 or 3, or major development in Flood Zone 1"
            },
            {
                "document": "Heritage Impact Statement",
                "required_when": "Within or affecting setting of Listed Building, Conservation Area, or Scheduled Monument"
            },
            {
                "document": "Biodiversity Net Gain Assessment (Metric + HMMP)",
                "required_when": "All major applications; all applications from April 2024 (mandatory BNG)"
            },
            {
                "document": "Energy Statement + Energy Efficiency Checklist",
                "required_when": "All residential and commercial development in Central Lincolnshire"
            },
            {
                "document": "Transport Assessment or Transport Statement",
                "required_when": "Development generating significant traffic — discuss with highway authority"
            },
            {
                "document": "Planning Statement",
                "required_when": "Major applications or applications raising significant policy issues"
            },
            {
                "document": "Structural Survey",
                "required_when": "Applications involving conversion or change of use of existing buildings"
            },
            {
                "document": "Drainage Strategy",
                "required_when": "All sites over 0.1 hectare; mandatory SuDS for all major development"
            },
            {
                "document": "Health Impact Assessment",
                "required_when": "Major development — recommended using Central Lincolnshire HIA Guidance Note"
            },
        ]
    },

    "Householder Application": {
        "national_mandatory": [
            "Completed application form",
            "Location plan at 1:1250 or 1:2500",
            "Block plan at 1:500 or 1:200",
            "Existing and proposed elevation drawings at 1:50 or 1:100",
            "Existing and proposed floor plans",
            "Existing and proposed site plan showing extension footprint",
            "Ownership Certificate",
            "Correct application fee",
        ],
        "national_conditional": [
            {
                "document": "Design and Access Statement",
                "required_when": "Development in Conservation Area only"
            }
        ],
        "central_lincolnshire_local_list": [
            {
                "document": "Heritage Impact Statement",
                "required_when": "Property is Listed Building or in Conservation Area"
            },
            {
                "document": "Flood Risk Assessment",
                "required_when": "Site in Flood Zone 2 or 3"
            },
            {
                "document": "Tree Survey / Arboricultural Impact Assessment",
                "required_when": "Trees within or adjacent to site subject to TPO or in Conservation Area"
            }
        ]
    },

    "Listed Building Consent": {
        "national_mandatory": [
            "Completed application form",
            "Location plan at 1:1250 or 1:2500",
            "Plans and drawings showing existing and proposed works",
            "Design and Access Statement (mandatory for all LBC applications)",
            "Ownership Certificate",
            "Correct application fee",
        ],
        "central_lincolnshire_local_list": [
            {
                "document": "Heritage Impact Statement",
                "required_when": "All Listed Building Consent applications — mandatory"
            },
            {
                "document": "Structural Survey",
                "required_when": "Works affecting structural elements"
            },
            {
                "document": "Schedule of Works / Method Statement",
                "required_when": "All internal and external works — must specify materials and methods"
            },
            {
                "document": "Photographs of existing condition",
                "required_when": "All applications — existing interior and exterior"
            }
        ]
    },

    "Change of Use": {
        "national_mandatory": [
            "Completed application form",
            "Location plan",
            "Floor plans showing existing and proposed layout",
            "Ownership Certificate",
            "Correct application fee",
        ],
        "central_lincolnshire_local_list": [
            {
                "document": "Planning Statement",
                "required_when": "All Change of Use applications"
            },
            {
                "document": "Structural Survey",
                "required_when": "Change of use requiring physical alterations"
            },
            {
                "document": "Noise Assessment",
                "required_when": "Change to use class generating noise (A3, A4, A5, D2, B2)"
            }
        ]
    },

    "Outline Planning Permission": {
        "national_mandatory": [
            "Completed application form",
            "Location plan",
            "Site layout plan showing indicative access points",
            "Statement of proposed use and amount of development",
            "Ownership Certificate",
            "Correct application fee",
        ],
        "central_lincolnshire_local_list": [
            {
                "document": "Planning Statement",
                "required_when": "All outline applications"
            },
            {
                "document": "Parameter Plans",
                "required_when": "Large outline applications — showing development zones, heights, land uses"
            },
            {
                "document": "Flood Risk Assessment",
                "required_when": "Site in or near flood zone"
            },
            {
                "document": "Biodiversity Net Gain Assessment",
                "required_when": "All major outline applications"
            },
            {
                "document": "Transport Assessment",
                "required_when": "100+ dwellings or significant commercial"
            }
        ]
    }
}
