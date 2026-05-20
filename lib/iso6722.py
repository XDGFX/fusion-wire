"""
ISO 6722 single-core automotive cable: mm² cross-section → insulation OD.
Conductor OD is derived geometrically with a 1.1 stranding factor.
All values in mm.
"""

from math import sqrt, pi

# (cross_section_mm2, insulation_od_mm)
_TABLE = [
    (0.5,  2.7),
    (0.75, 2.9),
    (1.0,  3.0),
    (1.5,  3.3),
    (2.5,  3.9),
    (4.0,  4.7),
    (6.0,  5.5),
    (10.0, 7.0),
    (16.0, 8.5),
    (25.0, 10.5),
    (35.0, 12.2),
    (50.0, 14.5),
    (70.0, 17.0),
    (95.0, 19.5),
    (110.0, 21.0),
]

SIZES = [row[0] for row in _TABLE]

_OD_MAP = {row[0]: row[1] for row in _TABLE}


def insulation_od(cross_section: float) -> float:
    """Return insulation OD in mm for a given cross-section in mm²."""
    if cross_section not in _OD_MAP:
        raise ValueError(f'Unsupported cross-section: {cross_section} mm²')
    return _OD_MAP[cross_section]


def conductor_od(cross_section: float) -> float:
    """Return stranded conductor OD in mm for a given cross-section in mm²."""
    return sqrt(4 * cross_section / pi) * 1.1
