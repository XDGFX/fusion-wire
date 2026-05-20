"""Read and write FusionWire custom attributes on BRepBody objects."""

import adsk.fusion

ATTR_GROUP = 'FusionWire'
ATTR_CROSS_SECTION = 'cross_section'
ATTR_COLOUR = 'colour'
ATTR_CONDUCTOR = 'conductor'


def tag(body: adsk.fusion.BRepBody, cross_section: float, colour: str, conductor: bool):
    """Write cable parameters onto a body."""
    body.attributes.add(ATTR_GROUP, ATTR_CROSS_SECTION, str(cross_section))
    body.attributes.add(ATTR_GROUP, ATTR_COLOUR, colour)
    body.attributes.add(ATTR_GROUP, ATTR_CONDUCTOR, str(conductor))


def read(body: adsk.fusion.BRepBody) -> dict | None:
    """Return stored parameters or None if body is not addon-tagged."""
    group = body.attributes.itemByName(ATTR_GROUP, ATTR_CROSS_SECTION)
    if not group:
        return None
    return {
        'cross_section': float(body.attributes.itemByName(ATTR_GROUP, ATTR_CROSS_SECTION).value),
        'colour': body.attributes.itemByName(ATTR_GROUP, ATTR_COLOUR).value,
        'conductor': body.attributes.itemByName(ATTR_GROUP, ATTR_CONDUCTOR).value == 'True',
    }


def is_tagged(body: adsk.fusion.BRepBody) -> bool:
    return body.attributes.itemByName(ATTR_GROUP, ATTR_CROSS_SECTION) is not None
