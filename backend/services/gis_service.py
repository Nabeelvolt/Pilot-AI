"""
GIS constraint auto-detection using free UK government open data APIs.
No API key required for any of these services.

APIs used:
- Environment Agency Flood Map for Planning (WFS - free, open)
- Historic England Listed Buildings API (free, open)
- Historic England Register of Parks and Gardens (free, open)
- OS Places API for address/UPRN lookup (free tier via data.gov.uk)
- Natural England SSSI data (WFS - free, open)
"""

import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def get_coordinates_from_address(address: str) -> Optional[dict]:
    """
    Geocode a UK address using the OS Names API (free, open data).
    Returns {lat, lon, uprn, match_description} or None.
    """
    try:
        # Use postcodes.io for postcode-based geocoding (completely free, no key)
        # Extract postcode from address if present
        import re
        postcode_match = re.search(
            r'[A-Z]{1,2}[0-9][0-9A-Z]?\s*[0-9][A-Z]{2}',
            address.upper()
        )
        if postcode_match:
            postcode = postcode_match.group().replace(" ", "")
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(f"https://api.postcodes.io/postcodes/{postcode}")
                if r.status_code == 200:
                    data = r.json()["result"]
                    return {
                        "lat": data["latitude"],
                        "lon": data["longitude"],
                        "postcode": postcode,
                        "admin_district": data.get("admin_district"),
                        "admin_ward": data.get("admin_ward"),
                    }
    except Exception as e:
        logger.warning(f"Geocoding failed: {e}")
    return None


async def check_flood_zone(lat: float, lon: float) -> dict:
    """
    Query Environment Agency Flood Map for Planning WFS.
    Free open government data. No API key required.
    Returns {in_flood_zone_2, in_flood_zone_3, flood_zone_label}
    """
    try:
        # EA Flood Map WFS endpoint
        ea_wfs_url = (
            "https://environment.data.gov.uk/spatialdata/flood-map-for-planning-rivers-and-sea-flood-zone-3/wfs"
        )
        params = {
            "SERVICE": "WFS",
            "VERSION": "2.0.0",
            "REQUEST": "GetFeature",
            "TYPENAMES": "ms:Flood_Map_for_Planning_Rivers_and_Sea_Flood_Zone_3",
            "SRSNAME": "EPSG:4326",
            "CQL_FILTER": f"INTERSECTS(SHAPE,POINT({lon} {lat}))",
            "outputFormat": "application/json",
            "count": "1",
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(ea_wfs_url, params=params)
            fz3 = r.status_code == 200 and len(r.json().get("features", [])) > 0

        # Check Flood Zone 2 (includes FZ3 area)
        ea_fz2_url = (
            "https://environment.data.gov.uk/spatialdata/flood-map-for-planning-rivers-and-sea-flood-zone-2/wfs"
        )
        params["TYPENAMES"] = "ms:Flood_Map_for_Planning_Rivers_and_Sea_Flood_Zone_2"
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(ea_fz2_url, params=params)
            fz2 = r.status_code == 200 and len(r.json().get("features", [])) > 0

        return {
            "in_flood_zone_3": fz3,
            "in_flood_zone_2": fz2 or fz3,
            "flood_zone_label": "Flood Zone 3" if fz3 else ("Flood Zone 2" if fz2 else "Flood Zone 1"),
            "requires_flood_risk_assessment": fz2 or fz3,
            "requires_exception_test": fz3,
        }
    except Exception as e:
        logger.warning(f"EA flood API error: {e}")
        return {"error": str(e), "in_flood_zone_2": None, "in_flood_zone_3": None}


async def check_listed_buildings(lat: float, lon: float, radius_metres: int = 100) -> dict:
    """
    Query Historic England Listed Buildings data via their API.
    Free and open — no API key required.
    Returns listed buildings within radius of the site.
    """
    try:
        url = "https://api.historicengland.org.uk/historicengland.api.images/v3/assets"
        params = {
            "lat": lat,
            "lng": lon,
            "radius": radius_metres,
            "type": "ListedBuilding",
            "apikey": "public",
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url, params=params)

        # Fallback: use the Historic England Heritage Gateway if above fails
        if r.status_code != 200:
            gateway_url = "https://www.heritagegateway.org.uk/Gateway/Results.aspx"
            params2 = {
                "dn": "Listed Buildings",
                "lat": lat,
                "lng": lon,
                "radius": radius_metres,
                "fmt": "json",
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.get(gateway_url, params=params2)

        listings = []
        grades = []

        if r.status_code == 200:
            try:
                data = r.json()
                listings = data.get("results", data.get("features", []))[:10]
                grades = [
                    str(b.get("grade", b.get("properties", {}).get("grade", ""))).upper()
                    for b in listings
                ]
            except Exception:
                pass

        return {
            "listed_buildings_within_100m": listings[:5],
            "count": len(listings),
            "grades_present": list(set(g for g in grades if g)),
            "has_grade_1": "I" in grades or "GRADE I" in grades,
            "has_grade_2_star": "II*" in grades or "GRADE II*" in grades,
            "has_grade_2": "II" in grades or "GRADE II" in grades,
            "requires_heritage_statement": len(listings) > 0,
        }

    except Exception as e:
        logger.warning(f"Listed buildings API error: {e}")
        return {
            "listed_buildings_within_100m": [],
            "count": 0,
            "grades_present": [],
            "has_grade_1": False,
            "has_grade_2_star": False,
            "has_grade_2": False,
            "requires_heritage_statement": False,
            "error": str(e),
        }


async def check_conservation_area(lat: float, lon: float) -> dict:
    """
    Check if the site falls within a Conservation Area.
    Uses the MHCLG Planning Data Platform (free, open, no key needed).
    This is the same platform Extract publishes to — reliable and authoritative.
    """
    try:
        # MHCLG Planning Data Platform — Conservation Areas dataset
        url = "https://www.planning.data.gov.uk/entity.json"
        params = {
            "dataset": "conservation-area",
            "latitude": lat,
            "longitude": lon,
            "geometry_relation": "intersects",
            "limit": 5,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url, params=params)

        if r.status_code == 200:
            data = r.json()
            entities = data.get("entities", [])
            if entities:
                ca = entities[0]
                return {
                    "in_conservation_area": True,
                    "conservation_area_name": ca.get("name", "Conservation Area"),
                    "reference": ca.get("reference", ""),
                    "local_authority": ca.get("organisation-entity", ""),
                    "requires_heritage_statement": True,
                    "requires_design_access_statement": True,
                    "data_source": "MHCLG Planning Data Platform",
                }

        return {
            "in_conservation_area": False,
            "conservation_area_name": None,
            "requires_heritage_statement": False,
            "requires_design_access_statement": False,
            "data_source": "MHCLG Planning Data Platform",
        }

    except Exception as e:
        logger.warning(f"Conservation area API error: {e}")
        return {
            "in_conservation_area": False,
            "conservation_area_name": None,
            "error": str(e),
        }


async def check_article4_direction(lat: float, lon: float) -> dict:
    """
    Check if the site is subject to an Article 4 Direction.
    Uses the MHCLG Planning Data Platform.
    Article 4 Directions remove permitted development rights —
    critical for change of use and householder applications.
    """
    try:
        url = "https://www.planning.data.gov.uk/entity.json"
        params = {
            "dataset": "article-4-direction-area",
            "latitude": lat,
            "longitude": lon,
            "geometry_relation": "intersects",
            "limit": 5,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url, params=params)

        if r.status_code == 200:
            data = r.json()
            entities = data.get("entities", [])
            if entities:
                a4 = entities[0]
                return {
                    "in_article4_direction": True,
                    "direction_name": a4.get("name", "Article 4 Direction"),
                    "reference": a4.get("reference", ""),
                    "note": "Permitted development rights may be restricted. Check with LPA before assuming PD applies.",
                    "data_source": "MHCLG Planning Data Platform",
                }

        return {
            "in_article4_direction": False,
            "data_source": "MHCLG Planning Data Platform",
        }

    except Exception as e:
        logger.warning(f"Article 4 API error: {e}")
        return {"in_article4_direction": False, "error": str(e)}


async def check_tree_preservation_orders(lat: float, lon: float) -> dict:
    """
    Check for Tree Preservation Orders on or near the site.
    Uses the MHCLG Planning Data Platform TPO dataset.
    """
    try:
        url = "https://www.planning.data.gov.uk/entity.json"
        params = {
            "dataset": "tree-preservation-order",
            "latitude": lat,
            "longitude": lon,
            "geometry_relation": "intersects",
            "limit": 10,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url, params=params)

        if r.status_code == 200:
            data = r.json()
            entities = data.get("entities", [])
            return {
                "tpos_on_site": len(entities) > 0,
                "tpo_count": len(entities),
                "tpos": [{"reference": t.get("reference", ""), "name": t.get("name", "TPO")} for t in entities[:5]],
                "requires_arboricultural_assessment": len(entities) > 0,
                "data_source": "MHCLG Planning Data Platform",
            }

        return {
            "tpos_on_site": False,
            "tpo_count": 0,
            "requires_arboricultural_assessment": False,
        }

    except Exception as e:
        logger.warning(f"TPO API error: {e}")
        return {"tpos_on_site": False, "error": str(e)}


async def auto_detect_constraints(address: str) -> dict:
    """
    Master function: given a site address string, auto-detects all
    planning constraints using free UK government open data APIs.

    Data sources:
    - postcodes.io — geocoding (free, no key)
    - Environment Agency WFS — flood zones (free, no key)
    - MHCLG Planning Data Platform — conservation areas, Article 4,
      TPOs (free, no key — same platform Extract publishes to)
    - Historic England — listed buildings (free, no key)

    Returns detected constraints and suggested checkbox pre-selections
    for the analysis form.
    """
    # Step 1: Geocode the address
    coords = await get_coordinates_from_address(address)
    if not coords:
        return {
            "geocoding_success": False,
            "message": (
                "Could not geocode this address. Please include the full postcode "
                "(e.g. LN1 3XX) for accurate constraint detection."
            ),
            "detected_constraints": [],
            "suggested_checkboxes": [],
        }

    lat, lon = coords["lat"], coords["lon"]

    # Step 2: Run all constraint checks concurrently
    import asyncio
    (
        flood_result,
        listed_result,
        conservation_result,
        article4_result,
        tpo_result,
    ) = await asyncio.gather(
        check_flood_zone(lat, lon),
        check_listed_buildings(lat, lon, radius_metres=100),
        check_conservation_area(lat, lon),
        check_article4_direction(lat, lon),
        check_tree_preservation_orders(lat, lon),
    )

    # Step 3: Build detected constraints list and suggested checkboxes
    detected = []
    suggested = []

    # Flood zone
    if flood_result.get("in_flood_zone_3"):
        detected.append({
            "constraint": "Flood Zone 3",
            "source": "Environment Agency Flood Map for Planning",
            "confidence": "HIGH",
            "implication": "Sequential Test + Exception Test required. No more vulnerable development.",
        })
        suggested.append("Flood Zone 3")
    elif flood_result.get("in_flood_zone_2"):
        detected.append({
            "constraint": "Flood Zone 2",
            "source": "Environment Agency Flood Map for Planning",
            "confidence": "HIGH",
            "implication": "Flood Risk Assessment required. Sequential Test required.",
        })
        suggested.append("Flood Zone 2")

    # Conservation area
    if conservation_result.get("in_conservation_area"):
        ca_name = conservation_result.get("conservation_area_name", "Conservation Area")
        detected.append({
            "constraint": f"Conservation Area — {ca_name}",
            "source": "MHCLG Planning Data Platform",
            "confidence": "HIGH",
            "implication": "Heritage Impact Statement required. Design & Access Statement required. Demolition requires consent.",
        })
        suggested.append("Conservation Area")

    # Listed buildings
    if listed_result.get("has_grade_1"):
        detected.append({
            "constraint": "Grade I Listed Building within 100m",
            "source": "Historic England National Heritage List",
            "confidence": "HIGH",
            "implication": "Heritage Impact Statement required. Setting of listed building must be assessed.",
        })
        suggested.append("Grade I Listed Building")

    if listed_result.get("has_grade_2_star"):
        detected.append({
            "constraint": "Grade II* Listed Building within 100m",
            "source": "Historic England National Heritage List",
            "confidence": "HIGH",
            "implication": "Heritage Impact Statement required.",
        })
        suggested.append("Grade II* Listed Building")

    if listed_result.get("has_grade_2") and not listed_result.get("has_grade_1") and not listed_result.get("has_grade_2_star"):
        detected.append({
            "constraint": "Grade II Listed Building within 100m",
            "source": "Historic England National Heritage List",
            "confidence": "HIGH",
            "implication": "Heritage Impact Statement required where setting is affected.",
        })
        suggested.append("Grade II Listed Building")

    # Article 4
    if article4_result.get("in_article4_direction"):
        detected.append({
            "constraint": f"Article 4 Direction — {article4_result.get('direction_name', '')}",
            "source": "MHCLG Planning Data Platform",
            "confidence": "HIGH",
            "implication": "Permitted development rights restricted. Full planning permission may be required for works that would otherwise be PD.",
        })
        suggested.append("Article 4 Direction")

    # TPOs
    if tpo_result.get("tpos_on_site"):
        detected.append({
            "constraint": f"Tree Preservation Order(s) — {tpo_result.get('tpo_count', 0)} TPO(s) on or near site",
            "source": "MHCLG Planning Data Platform",
            "confidence": "HIGH",
            "implication": "Arboricultural Impact Assessment required. TPO works require separate consent.",
        })
        suggested.append("Tree Preservation Order")

    return {
        "geocoding_success": True,
        "address_searched": address,
        "coordinates": {"lat": lat, "lon": lon},
        "location_info": coords,
        "detected_constraints": detected,
        "suggested_checkboxes": suggested,
        "constraint_count": len(detected),
        "detail": {
            "flood": flood_result,
            "listed_buildings": listed_result,
            "conservation_area": conservation_result,
            "article4": article4_result,
            "tree_preservation_orders": tpo_result,
        },
        "data_sources": [
            "Environment Agency Flood Map for Planning (open government data)",
            "MHCLG Planning Data Platform — Conservation Areas, Article 4, TPOs (open government data)",
            "Historic England National Heritage List (open government data)",
            "postcodes.io — geocoding (open data)",
        ],
        "disclaimer": (
            "Constraint detection uses national open datasets. Always verify against "
            "your authority's definitive GIS layers before relying on for formal decision-making. "
            "Data accuracy depends on local authority publication to national platforms."
        ),
    }
