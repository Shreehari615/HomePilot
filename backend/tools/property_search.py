"""
HomePilot AI — Property Search Tool

Provides property search with 30+ realistic mock listings across
major Indian cities. Supports filtering by budget, city, bedrooms,
and bathrooms.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from langchain_core.tools import tool

from utils.logger import log_tool_call
from utils.helpers import format_inr


# ── Mock Property Database (30+ realistic Indian properties) ────────────────

MOCK_PROPERTIES: list[dict[str, Any]] = [
    # ── Mumbai ────────────────────────────────────────────────────────────
    {
        "id": "prop-mum-001",
        "title": "Luxe 3BHK in Andheri West",
        "price": 15000000,
        "city": "Mumbai",
        "locality": "Andheri West",
        "address": "Lotus Tower, Lokhandwala Complex, Andheri West, Mumbai 400053",
        "latitude": 19.1364,
        "longitude": 72.8296,
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqft": 1250,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "12th of 20",
        "images": [{"url": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800", "alt": "Living room"}],
        "amenities": ["Swimming Pool", "Gym", "Parking", "Security", "Power Backup", "Garden"],
    },
    {
        "id": "prop-mum-002",
        "title": "Modern 2BHK in Bandra East",
        "price": 12000000,
        "city": "Mumbai",
        "locality": "Bandra East",
        "address": "Rizvi Complex, Bandra East, Mumbai 400051",
        "latitude": 19.0596,
        "longitude": 72.8411,
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 950,
        "property_type": "Apartment",
        "furnishing": "Furnished",
        "floor": "8th of 15",
        "images": [{"url": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800", "alt": "Apartment interior"}],
        "amenities": ["Gym", "Parking", "Security", "Lift", "Power Backup"],
    },
    {
        "id": "prop-mum-003",
        "title": "Spacious 3BHK in Powai",
        "price": 18000000,
        "city": "Mumbai",
        "locality": "Powai",
        "address": "Hiranandani Gardens, Powai, Mumbai 400076",
        "latitude": 19.1196,
        "longitude": 72.9052,
        "bedrooms": 3,
        "bathrooms": 3,
        "area_sqft": 1500,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "15th of 25",
        "images": [{"url": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800", "alt": "Modern apartment"}],
        "amenities": ["Swimming Pool", "Gym", "Parking", "Security", "Club House", "Garden", "Jogging Track"],
    },
    {
        "id": "prop-mum-004",
        "title": "Premium 4BHK in Worli",
        "price": 45000000,
        "city": "Mumbai",
        "locality": "Worli",
        "address": "Birla Centurion, Century Mills, Worli, Mumbai 400030",
        "latitude": 19.0130,
        "longitude": 72.8208,
        "bedrooms": 4,
        "bathrooms": 4,
        "area_sqft": 2400,
        "property_type": "Apartment",
        "furnishing": "Furnished",
        "floor": "32nd of 45",
        "images": [{"url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800", "alt": "Luxury apartment"}],
        "amenities": ["Swimming Pool", "Gym", "Spa", "Parking", "Concierge", "Home Theatre", "Rooftop Garden"],
    },
    {
        "id": "prop-mum-005",
        "title": "Cozy 1BHK in Kandivali East",
        "price": 5500000,
        "city": "Mumbai",
        "locality": "Kandivali East",
        "address": "Thakur Village, Kandivali East, Mumbai 400101",
        "latitude": 19.2094,
        "longitude": 72.8656,
        "bedrooms": 1,
        "bathrooms": 1,
        "area_sqft": 550,
        "property_type": "Apartment",
        "furnishing": "Unfurnished",
        "floor": "5th of 12",
        "images": [{"url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800", "alt": "Compact apartment"}],
        "amenities": ["Parking", "Security", "Lift", "Power Backup"],
    },
    {
        "id": "prop-mum-006",
        "title": "Elegant 2BHK in Thane West",
        "price": 8500000,
        "city": "Mumbai",
        "locality": "Thane West",
        "address": "Hiranandani Estate, Thane West, Mumbai 400607",
        "latitude": 19.2403,
        "longitude": 72.9638,
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 1050,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "10th of 18",
        "images": [{"url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800", "alt": "Elegant interior"}],
        "amenities": ["Swimming Pool", "Gym", "Parking", "Garden", "Club House", "Children's Play Area"],
    },
    # ── Bangalore ─────────────────────────────────────────────────────────
    {
        "id": "prop-blr-001",
        "title": "Modern 3BHK in Whitefield",
        "price": 12500000,
        "city": "Bangalore",
        "locality": "Whitefield",
        "address": "Prestige Shantiniketan, Whitefield, Bangalore 560048",
        "latitude": 12.9698,
        "longitude": 77.7500,
        "bedrooms": 3,
        "bathrooms": 3,
        "area_sqft": 1650,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "7th of 14",
        "images": [{"url": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800", "alt": "Modern apartment"}],
        "amenities": ["Swimming Pool", "Gym", "Parking", "Tennis Court", "Club House", "Jogging Track"],
    },
    {
        "id": "prop-blr-002",
        "title": "Tech Hub 2BHK in Koramangala",
        "price": 9500000,
        "city": "Bangalore",
        "locality": "Koramangala",
        "address": "8th Block, Koramangala, Bangalore 560095",
        "latitude": 12.9352,
        "longitude": 77.6245,
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 1100,
        "property_type": "Apartment",
        "furnishing": "Furnished",
        "floor": "4th of 8",
        "images": [{"url": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800", "alt": "Tech hub apartment"}],
        "amenities": ["Parking", "Security", "Gym", "Power Backup", "Lift"],
    },
    {
        "id": "prop-blr-003",
        "title": "Garden Villa in Sarjapur Road",
        "price": 22000000,
        "city": "Bangalore",
        "locality": "Sarjapur Road",
        "address": "Sobha Dream Acres, Sarjapur Road, Bangalore 562125",
        "latitude": 12.8590,
        "longitude": 77.7840,
        "bedrooms": 4,
        "bathrooms": 4,
        "area_sqft": 2800,
        "property_type": "Villa",
        "furnishing": "Semi-Furnished",
        "floor": "Ground + 1",
        "images": [{"url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800", "alt": "Beautiful villa"}],
        "amenities": ["Private Garden", "Swimming Pool", "Parking", "Club House", "Gym", "Children's Play Area"],
    },
    {
        "id": "prop-blr-004",
        "title": "Smart 2BHK in Electronic City",
        "price": 6500000,
        "city": "Bangalore",
        "locality": "Electronic City",
        "address": "Brigade Xanadu, Electronic City Phase 1, Bangalore 560100",
        "latitude": 12.8446,
        "longitude": 77.6603,
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 1000,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "9th of 16",
        "images": [{"url": "https://images.unsplash.com/photo-1600573472550-8090b5e0745e?w=800", "alt": "Smart apartment"}],
        "amenities": ["Swimming Pool", "Gym", "Parking", "Security", "Power Backup", "Indoor Games"],
    },
    {
        "id": "prop-blr-005",
        "title": "Premium 3BHK in Indiranagar",
        "price": 16000000,
        "city": "Bangalore",
        "locality": "Indiranagar",
        "address": "100 Feet Road, Indiranagar, Bangalore 560038",
        "latitude": 12.9784,
        "longitude": 77.6408,
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqft": 1400,
        "property_type": "Apartment",
        "furnishing": "Furnished",
        "floor": "6th of 10",
        "images": [{"url": "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=800", "alt": "Premium apartment"}],
        "amenities": ["Parking", "Security", "Gym", "Rooftop Terrace", "Power Backup"],
    },
    # ── Delhi NCR ─────────────────────────────────────────────────────────
    {
        "id": "prop-del-001",
        "title": "Elegant 3BHK in Dwarka",
        "price": 11000000,
        "city": "Delhi",
        "locality": "Dwarka",
        "address": "Sector 22, Dwarka, New Delhi 110077",
        "latitude": 28.5693,
        "longitude": 77.0521,
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqft": 1350,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "6th of 14",
        "images": [{"url": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800", "alt": "Dwarka apartment"}],
        "amenities": ["Parking", "Gym", "Garden", "Security", "Power Backup", "Lift"],
    },
    {
        "id": "prop-del-002",
        "title": "Luxury 4BHK in Vasant Kunj",
        "price": 35000000,
        "city": "Delhi",
        "locality": "Vasant Kunj",
        "address": "DLF Emporio Residences, Vasant Kunj, New Delhi 110070",
        "latitude": 28.5218,
        "longitude": 77.1548,
        "bedrooms": 4,
        "bathrooms": 3,
        "area_sqft": 2200,
        "property_type": "Apartment",
        "furnishing": "Furnished",
        "floor": "18th of 22",
        "images": [{"url": "https://images.unsplash.com/photo-1600607687644-c7171b42498f?w=800", "alt": "Luxury residence"}],
        "amenities": ["Swimming Pool", "Gym", "Spa", "Parking", "Concierge", "Club House", "Tennis Court"],
    },
    {
        "id": "prop-del-003",
        "title": "Family 3BHK in Noida Sector 150",
        "price": 8000000,
        "city": "Delhi",
        "locality": "Noida",
        "address": "ATS Destinaire, Sector 150, Noida 201310",
        "latitude": 28.4670,
        "longitude": 77.5300,
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqft": 1450,
        "property_type": "Apartment",
        "furnishing": "Unfurnished",
        "floor": "11th of 30",
        "images": [{"url": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=800", "alt": "Noida apartment"}],
        "amenities": ["Swimming Pool", "Gym", "Parking", "Children's Play Area", "Jogging Track", "Club House"],
    },
    {
        "id": "prop-del-004",
        "title": "Budget 2BHK in Gurgaon",
        "price": 6000000,
        "city": "Delhi",
        "locality": "Gurgaon",
        "address": "Sector 83, Gurgaon, Haryana 122004",
        "latitude": 28.3929,
        "longitude": 76.9478,
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 1050,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "7th of 20",
        "images": [{"url": "https://images.unsplash.com/photo-1600566753086-00f18f6b5a8c?w=800", "alt": "Gurgaon apartment"}],
        "amenities": ["Swimming Pool", "Gym", "Parking", "Security", "Power Backup"],
    },
    {
        "id": "prop-del-005",
        "title": "Green 3BHK in Greater Noida",
        "price": 5500000,
        "city": "Delhi",
        "locality": "Greater Noida",
        "address": "Gaur City, Greater Noida West 201318",
        "latitude": 28.5650,
        "longitude": 77.4530,
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqft": 1350,
        "property_type": "Apartment",
        "furnishing": "Unfurnished",
        "floor": "14th of 25",
        "images": [{"url": "https://images.unsplash.com/photo-1600573472591-ee6981cf81f0?w=800", "alt": "Green apartment"}],
        "amenities": ["Swimming Pool", "Gym", "Parking", "Garden", "Cricket Ground", "Club House"],
    },
    # ── Pune ──────────────────────────────────────────────────────────────
    {
        "id": "prop-pun-001",
        "title": "IT Hub 2BHK in Hinjawadi",
        "price": 7000000,
        "city": "Pune",
        "locality": "Hinjawadi",
        "address": "Godrej 24, Hinjawadi Phase 1, Pune 411057",
        "latitude": 18.5912,
        "longitude": 73.7390,
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 1000,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "8th of 15",
        "images": [{"url": "https://images.unsplash.com/photo-1600047509358-9dc75507daeb?w=800", "alt": "IT hub apartment"}],
        "amenities": ["Swimming Pool", "Gym", "Parking", "Club House", "Power Backup"],
    },
    {
        "id": "prop-pun-002",
        "title": "Heritage 3BHK in Koregaon Park",
        "price": 14000000,
        "city": "Pune",
        "locality": "Koregaon Park",
        "address": "Lane 7, Koregaon Park, Pune 411001",
        "latitude": 18.5362,
        "longitude": 73.8940,
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqft": 1450,
        "property_type": "Apartment",
        "furnishing": "Furnished",
        "floor": "3rd of 7",
        "images": [{"url": "https://images.unsplash.com/photo-1600210491892-03d54c0aaf87?w=800", "alt": "Heritage apartment"}],
        "amenities": ["Parking", "Garden", "Security", "Gym", "Power Backup"],
    },
    {
        "id": "prop-pun-003",
        "title": "Family 3BHK in Baner",
        "price": 9500000,
        "city": "Pune",
        "locality": "Baner",
        "address": "Blue Ridge Township, Baner, Pune 411045",
        "latitude": 18.5596,
        "longitude": 73.7769,
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqft": 1300,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "5th of 12",
        "images": [{"url": "https://images.unsplash.com/photo-1600585153490-76fb20a32601?w=800", "alt": "Family apartment"}],
        "amenities": ["Swimming Pool", "Gym", "Parking", "Children's Play Area", "Garden", "Club House"],
    },
    {
        "id": "prop-pun-004",
        "title": "Budget 1BHK in Wakad",
        "price": 4200000,
        "city": "Pune",
        "locality": "Wakad",
        "address": "Shankar Kalat Nagar, Wakad, Pune 411057",
        "latitude": 18.5980,
        "longitude": 73.7604,
        "bedrooms": 1,
        "bathrooms": 1,
        "area_sqft": 600,
        "property_type": "Apartment",
        "furnishing": "Unfurnished",
        "floor": "3rd of 10",
        "images": [{"url": "https://images.unsplash.com/photo-1600566752355-35792bedcfea?w=800", "alt": "Budget apartment"}],
        "amenities": ["Parking", "Security", "Lift", "Power Backup"],
    },
    {
        "id": "prop-pun-005",
        "title": "Premium 3BHK in Kharadi",
        "price": 10500000,
        "city": "Pune",
        "locality": "Kharadi",
        "address": "World Trade Center, Kharadi, Pune 411014",
        "latitude": 18.5538,
        "longitude": 73.9406,
        "bedrooms": 3,
        "bathrooms": 3,
        "area_sqft": 1550,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "16th of 22",
        "images": [{"url": "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=800", "alt": "Premium apartment"}],
        "amenities": ["Swimming Pool", "Gym", "Parking", "Indoor Games", "Jogging Track", "Club House"],
    },
    # ── Hyderabad ─────────────────────────────────────────────────────────
    {
        "id": "prop-hyd-001",
        "title": "Tech Corridor 3BHK in Gachibowli",
        "price": 11000000,
        "city": "Hyderabad",
        "locality": "Gachibowli",
        "address": "My Home Bhooja, Gachibowli, Hyderabad 500032",
        "latitude": 17.4401,
        "longitude": 78.3489,
        "bedrooms": 3,
        "bathrooms": 3,
        "area_sqft": 1600,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "12th of 20",
        "images": [{"url": "https://images.unsplash.com/photo-1600566753104-685f4f24cb4d?w=800", "alt": "Tech corridor apartment"}],
        "amenities": ["Swimming Pool", "Gym", "Parking", "Club House", "Indoor Games", "Jogging Track"],
    },
    {
        "id": "prop-hyd-002",
        "title": "Budget 2BHK in Kompally",
        "price": 4500000,
        "city": "Hyderabad",
        "locality": "Kompally",
        "address": "Pocharam, Kompally, Hyderabad 500014",
        "latitude": 17.5431,
        "longitude": 78.4889,
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 1000,
        "property_type": "Apartment",
        "furnishing": "Unfurnished",
        "floor": "4th of 10",
        "images": [{"url": "https://images.unsplash.com/photo-1600585152220-90363fe7e115?w=800", "alt": "Budget apartment"}],
        "amenities": ["Parking", "Security", "Gym", "Power Backup", "Garden"],
    },
    {
        "id": "prop-hyd-003",
        "title": "Luxury 4BHK in Jubilee Hills",
        "price": 28000000,
        "city": "Hyderabad",
        "locality": "Jubilee Hills",
        "address": "Road No 36, Jubilee Hills, Hyderabad 500033",
        "latitude": 17.4325,
        "longitude": 78.4073,
        "bedrooms": 4,
        "bathrooms": 4,
        "area_sqft": 2600,
        "property_type": "Apartment",
        "furnishing": "Furnished",
        "floor": "8th of 12",
        "images": [{"url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800", "alt": "Luxury apartment"}],
        "amenities": ["Swimming Pool", "Gym", "Spa", "Parking", "Concierge", "Rooftop Garden", "Home Theatre"],
    },
    {
        "id": "prop-hyd-004",
        "title": "Family 3BHK in Kukatpally",
        "price": 7500000,
        "city": "Hyderabad",
        "locality": "Kukatpally",
        "address": "KPHB Colony, Kukatpally, Hyderabad 500072",
        "latitude": 17.4849,
        "longitude": 78.3942,
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqft": 1350,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "6th of 14",
        "images": [{"url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800", "alt": "Family apartment"}],
        "amenities": ["Swimming Pool", "Gym", "Parking", "Children's Play Area", "Club House"],
    },
    {
        "id": "prop-hyd-005",
        "title": "Modern 2BHK in Madhapur",
        "price": 8500000,
        "city": "Hyderabad",
        "locality": "Madhapur",
        "address": "Cyber Towers Road, Madhapur, Hyderabad 500081",
        "latitude": 17.4483,
        "longitude": 78.3915,
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 1100,
        "property_type": "Apartment",
        "furnishing": "Furnished",
        "floor": "10th of 18",
        "images": [{"url": "https://images.unsplash.com/photo-1600210491369-e753d80a41f3?w=800", "alt": "Modern apartment"}],
        "amenities": ["Gym", "Parking", "Security", "Power Backup", "Rooftop Garden"],
    },
    # ── Chennai ───────────────────────────────────────────────────────────
    {
        "id": "prop-che-001",
        "title": "Sea-View 3BHK in Besant Nagar",
        "price": 13500000,
        "city": "Chennai",
        "locality": "Besant Nagar",
        "address": "2nd Avenue, Besant Nagar, Chennai 600090",
        "latitude": 13.0002,
        "longitude": 80.2671,
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqft": 1400,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "9th of 12",
        "images": [{"url": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800", "alt": "Sea view apartment"}],
        "amenities": ["Parking", "Gym", "Security", "Garden", "Power Backup"],
    },
    {
        "id": "prop-che-002",
        "title": "IT Corridor 2BHK in OMR",
        "price": 6500000,
        "city": "Chennai",
        "locality": "OMR",
        "address": "Thoraipakkam, OMR, Chennai 600097",
        "latitude": 12.9352,
        "longitude": 80.2268,
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 1050,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "7th of 15",
        "images": [{"url": "https://images.unsplash.com/photo-1600573472591-ee6981cf81f0?w=800", "alt": "IT corridor apartment"}],
        "amenities": ["Swimming Pool", "Gym", "Parking", "Club House", "Power Backup", "Jogging Track"],
    },
    {
        "id": "prop-che-003",
        "title": "Spacious 3BHK in Anna Nagar",
        "price": 11500000,
        "city": "Chennai",
        "locality": "Anna Nagar",
        "address": "2nd Avenue, Anna Nagar, Chennai 600040",
        "latitude": 13.0860,
        "longitude": 80.2101,
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqft": 1500,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "5th of 8",
        "images": [{"url": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800", "alt": "Spacious apartment"}],
        "amenities": ["Parking", "Gym", "Garden", "Security", "Lift", "Power Backup"],
    },
    # ── Kolkata ───────────────────────────────────────────────────────────
    {
        "id": "prop-kol-001",
        "title": "Modern 3BHK in New Town",
        "price": 7500000,
        "city": "Kolkata",
        "locality": "New Town",
        "address": "Action Area II, New Town, Kolkata 700161",
        "latitude": 22.5958,
        "longitude": 88.4795,
        "bedrooms": 3,
        "bathrooms": 2,
        "area_sqft": 1300,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "8th of 15",
        "images": [{"url": "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=800", "alt": "Modern apartment"}],
        "amenities": ["Swimming Pool", "Gym", "Parking", "Club House", "Garden", "Children's Play Area"],
    },
    {
        "id": "prop-kol-002",
        "title": "Heritage 2BHK in Salt Lake",
        "price": 5500000,
        "city": "Kolkata",
        "locality": "Salt Lake",
        "address": "Sector V, Salt Lake City, Kolkata 700091",
        "latitude": 22.5726,
        "longitude": 88.4338,
        "bedrooms": 2,
        "bathrooms": 1,
        "area_sqft": 900,
        "property_type": "Apartment",
        "furnishing": "Semi-Furnished",
        "floor": "4th of 7",
        "images": [{"url": "https://images.unsplash.com/photo-1600585152220-90363fe7e115?w=800", "alt": "Heritage apartment"}],
        "amenities": ["Parking", "Security", "Garden", "Power Backup"],
    },
]


def _match_properties(
    budget_min: float | None = None,
    budget_max: float | None = None,
    city: str | None = None,
    bedrooms: int | None = None,
    bathrooms: int | None = None,
    property_type: str | None = None,
) -> list[dict]:
    """Filter mock properties based on criteria."""
    results = []
    for prop in MOCK_PROPERTIES:
        # Budget filter
        if budget_min and prop["price"] < budget_min:
            continue
        if budget_max and prop["price"] > budget_max:
            continue
        # City filter (case-insensitive, partial match)
        if city:
            city_lower = city.lower()
            prop_city_lower = prop["city"].lower()
            prop_locality_lower = prop["locality"].lower()
            if city_lower not in prop_city_lower and city_lower not in prop_locality_lower:
                # Also check for NCR variations
                if city_lower in ("ncr", "delhi ncr", "delhi-ncr"):
                    if prop["city"] not in ("Delhi",):
                        continue
                else:
                    continue
        # Bedroom filter
        if bedrooms and prop["bedrooms"] != bedrooms:
            continue
        # Bathroom filter
        if bathrooms and prop["bathrooms"] != bathrooms:
            continue
        # Property type filter
        if property_type:
            if property_type.lower() not in prop["property_type"].lower():
                continue

        # Add formatted price
        prop_copy = prop.copy()
        prop_copy["formatted_price"] = format_inr(prop["price"])
        results.append(prop_copy)

    return results


@tool
def property_search(
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    city: Optional[str] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[int] = None,
    property_type: Optional[str] = None,
) -> dict[str, Any]:
    """
    Search for properties matching the given criteria.

    Args:
        budget_min: Minimum budget in INR (e.g., 5000000 for 50 lakh)
        budget_max: Maximum budget in INR (e.g., 15000000 for 1.5 crore)
        city: City name (Mumbai, Bangalore, Delhi, Pune, Hyderabad, Chennai, Kolkata)
        bedrooms: Number of bedrooms
        bathrooms: Number of bathrooms
        property_type: Type of property (Apartment, Villa, Independent House)

    Returns:
        Dictionary with 'properties' list and 'total_count'.
    """
    start = time.time()

    results = _match_properties(
        budget_min=budget_min,
        budget_max=budget_max,
        city=city,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        property_type=property_type,
    )

    elapsed = (time.time() - start) * 1000
    log_tool_call(
        tool_name="property_search",
        input_data={
            "budget_min": budget_min,
            "budget_max": budget_max,
            "city": city,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
        },
        output_summary=f"Found {len(results)} properties",
        duration_ms=elapsed,
    )

    return {
        "properties": results,
        "total_count": len(results),
        "filters": {
            "budget_min": budget_min,
            "budget_max": budget_max,
            "city": city,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "property_type": property_type,
        },
    }


def get_property_by_id(property_id: str) -> dict | None:
    """Get a single property by its ID (non-tool utility function)."""
    for prop in MOCK_PROPERTIES:
        if prop["id"] == property_id:
            prop_copy = prop.copy()
            prop_copy["formatted_price"] = format_inr(prop["price"])
            return prop_copy
    return None


def get_all_properties() -> list[dict]:
    """Get all properties (for browsing)."""
    return [
        {**prop, "formatted_price": format_inr(prop["price"])}
        for prop in MOCK_PROPERTIES
    ]
