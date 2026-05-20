"""Read and write FusionWire custom attributes on BRepBody objects."""

import adsk.fusion

ATTR_GROUP = 'FusionWire'
ATTR_CROSS_SECTION = 'cross_section'
ATTR_COLOUR = 'colour'
ATTR_CONDUCTOR = 'conductor'
ATTR_PATH_TOKEN = 'path_token'


def _native(body: adsk.fusion.BRepBody) -> adsk.fusion.BRepBody:
    # When a body is selected through an assembly occurrence its attribute
    # collection belongs to the occurrence context, not the body itself.
    # nativeObject strips the occurrence wrapper; it returns None when the
    # body is already in its own component context.
    native = body.nativeObject
    return native if native is not None else body


def tag(body: adsk.fusion.BRepBody, cross_section: float, colour: str, conductor: bool, path_token: str = ''):
    """Write cable parameters onto a body."""
    b = _native(body)
    b.attributes.add(ATTR_GROUP, ATTR_CROSS_SECTION, str(cross_section))
    b.attributes.add(ATTR_GROUP, ATTR_COLOUR, colour)
    b.attributes.add(ATTR_GROUP, ATTR_CONDUCTOR, str(conductor))
    b.attributes.add(ATTR_GROUP, ATTR_PATH_TOKEN, path_token)


def read(body: adsk.fusion.BRepBody) -> dict | None:
    """Return stored parameters or None if body is not addon-tagged."""
    b = _native(body)
    group = b.attributes.itemByName(ATTR_GROUP, ATTR_CROSS_SECTION)
    if not group:
        return None
    path_attr = b.attributes.itemByName(ATTR_GROUP, ATTR_PATH_TOKEN)
    return {
        'cross_section': float(b.attributes.itemByName(ATTR_GROUP, ATTR_CROSS_SECTION).value),
        'colour': b.attributes.itemByName(ATTR_GROUP, ATTR_COLOUR).value,
        'conductor': b.attributes.itemByName(ATTR_GROUP, ATTR_CONDUCTOR).value == 'True',
        'path_token': path_attr.value if path_attr else '',
    }


def is_tagged(body: adsk.fusion.BRepBody) -> bool:
    return _native(body).attributes.itemByName(ATTR_GROUP, ATTR_CROSS_SECTION) is not None
