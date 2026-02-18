from __future__ import annotations


def zone_from_customer_type(kind: str) -> str:
    return "residential_zone" if kind == "residential" else "commercial_zone"
