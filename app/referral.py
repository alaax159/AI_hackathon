"""Legal aid clinic referral lookup.

Static directory of free / low-cost legal aid providers in the West Bank
and Gaza. Intended to be replaced with a live database later.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Clinic:
    name: str
    city: str
    region: str
    phone: str
    email: str
    latitude: float
    longitude: float
    specialties: list[str]


CLINICS: list[Clinic] = [
    Clinic(
        name="Al-Haq Legal Research and Human Rights Organization",
        city="Ramallah",
        region="West Bank",
        phone="+970-2-295-4646",
        email="info@alhaq.org",
        latitude=31.9038,
        longitude=35.2034,
        specialties=["human rights", "detention", "criminal", "discrimination"],
    ),
    Clinic(
        name="Women's Centre for Legal Aid and Counselling (WCLAC)",
        city="Ramallah",
        region="West Bank",
        phone="+970-2-295-6146",
        email="wclac@wclac.org",
        latitude=31.9073,
        longitude=35.2070,
        specialties=["family", "gender", "custody", "divorce", "domestic violence"],
    ),
    Clinic(
        name="Al-Mezan Center for Human Rights",
        city="Gaza City",
        region="Gaza",
        phone="+970-8-282-0447",
        email="info@mezan.org",
        latitude=31.5017,
        longitude=34.4668,
        specialties=["human rights", "detention", "emergency", "criminal"],
    ),
    Clinic(
        name="Palestinian Centre for Human Rights (PCHR)",
        city="Gaza City",
        region="Gaza",
        phone="+970-8-282-4776",
        email="pchr@pchrgaza.org",
        latitude=31.5200,
        longitude=34.4480,
        specialties=["human rights", "criminal", "emergency"],
    ),
    Clinic(
        name="Birzeit University Legal Aid Clinic",
        city="Birzeit",
        region="West Bank",
        phone="+970-2-298-2000",
        email="legalclinic@birzeit.edu",
        latitude=31.9716,
        longitude=35.1969,
        specialties=["labor", "housing", "education", "general"],
    ),
    Clinic(
        name="Defense for Children International — Palestine (DCIP)",
        city="Ramallah",
        region="West Bank",
        phone="+970-2-242-7530",
        email="info@dci-palestine.org",
        latitude=31.9038,
        longitude=35.2034,
        specialties=["children", "detention", "family"],
    ),
    Clinic(
        name="Musawa — the Palestinian Center for Independence of the Judiciary",
        city="Nablus",
        region="West Bank",
        phone="+970-9-233-1776",
        email="info@musawa.ps",
        latitude=32.2211,
        longitude=35.2544,
        specialties=["judicial", "discrimination", "general"],
    ),
]


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def find_clinics(
    *,
    intent: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    limit: int = 3,
) -> list[dict]:
    candidates: list[Clinic] = list(CLINICS)

    if intent and intent != "general":
        tagged = [c for c in candidates if intent in c.specialties or "general" in c.specialties]
        if tagged:
            candidates = tagged

    scored: list[tuple[float, Clinic]] = []
    for c in candidates:
        if lat is not None and lon is not None:
            distance = _haversine_km(lat, lon, c.latitude, c.longitude)
        else:
            distance = float("inf")
        scored.append((distance, c))

    scored.sort(key=lambda kv: kv[0])
    out: list[dict] = []
    for distance, c in scored[:limit]:
        out.append(
            {
                "name": c.name,
                "city": c.city,
                "region": c.region,
                "phone": c.phone,
                "email": c.email,
                "latitude": c.latitude,
                "longitude": c.longitude,
                "specialties": c.specialties,
                "distance_km": None if math.isinf(distance) else round(distance, 1),
            }
        )
    return out
