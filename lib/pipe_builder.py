"""Create cable pipe bodies and apply appearances."""

import adsk.core
import adsk.fusion

from lib import iso6722, attributes

# Preset insulation colours (name → RGB 0–255)
COLOUR_PRESETS = {
    "Red": (220, 50, 50),
    "Black": (30, 30, 30),
    "Blue": (50, 100, 220),
    "Yellow": (240, 210, 40),
}

INSULATION_APPEARANCE = "Plastic - Matte"
CONDUCTOR_APPEARANCE = "Copper - Polished"


def create_cable(
    component: adsk.fusion.Component,
    path_curve,
    cross_section: float,
    colour: str,
    include_conductor: bool,
) -> list[adsk.fusion.BRepBody]:
    """
    Sweep a cable pipe along path_curve.
    Returns a list of created bodies (1 or 2 if conductor is included).
    """
    od_mm = iso6722.insulation_od(cross_section)
    od_cm = od_mm / 10.0

    path = adsk.fusion.Path.create(
        path_curve, adsk.fusion.ChainedCurveOptions.noChainedCurves
    )

    pipe_features = component.features.pipeFeatures
    pipe_input = pipe_features.createInput(
        path,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    )
    pipe_input.sectionSize = adsk.core.ValueInput.createByReal(od_cm)
    pipe_input.isHollow = False

    pipe_feature = pipe_features.add(pipe_input)
    body = pipe_feature.bodies.item(0)

    _apply_appearance(body, INSULATION_APPEARANCE, COLOUR_PRESETS[colour])
    _auto_name(body, cross_section, colour, component)
    attributes.tag(body, cross_section, colour, False)

    return [body]


def delete_cable(body: adsk.fusion.BRepBody):
    """Delete a cable body (and its paired conductor body if present)."""
    # TODO: Slice 3 — implement body deletion
    raise NotImplementedError


def _find_appearance(app, design, appearance_name: str):
    """
    Return a base appearance by name.
    Tries: design-local → exact library name → known variant names → fuzzy word match.
    Shows a diagnostic message if nothing is found so the correct name can be identified.
    """
    # Variant names for appearances whose exact label differs between Fusion versions
    _VARIANTS = {
        "Plastic - Matte": [
            "Plastic - Matte",
            "Plastic - Matte (White)",
            "Plastic - Matte White",
        ],
    }
    candidates = _VARIANTS.get(appearance_name, [appearance_name])

    # 1. Design-local appearances (fastest; covers re-use across calls)
    for name in candidates:
        a = design.appearances.itemByName(name)
        if a:
            return a

    # 2. Walk every material/appearance library
    all_names: list[str] = []
    try:
        for lib in app.materialLibraries:
            try:
                for name in candidates:
                    a = lib.appearances.itemByName(name)
                    if a:
                        return a
                # Collect names for fuzzy fallback and diagnostics
                for i in range(lib.appearances.count):
                    all_names.append(lib.appearances.item(i).name)
            except Exception:
                continue
    except Exception:
        pass

    # 3. Fuzzy: any appearance whose name contains every word in the requested name
    words = appearance_name.lower().split()
    for name in all_names:
        if all(w in name.lower() for w in words):
            a = design.appearances.itemByName(name) or None
            if not a:
                # Try to find it in the libraries by the matched name
                try:
                    for lib in app.materialLibraries:
                        try:
                            a = lib.appearances.itemByName(name)
                            if a:
                                return a
                        except Exception:
                            continue
                except Exception:
                    pass

    # 4. Nothing found — show a diagnostic so the correct name can be identified
    sample = ", ".join(sorted(all_names)[:20]) or "(no libraries accessible)"
    app.userInterface.messageBox(
        f'FusionWire: could not find appearance "{appearance_name}".\n\n'
        f"First 20 appearances found in loaded libraries:\n{sample}"
    )
    return None


def _apply_appearance(
    body: adsk.fusion.BRepBody, appearance_name: str, rgb: tuple | None
):
    """Apply a named Fusion appearance to a body, optionally overriding its colour."""
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)

    mat_lib = app.materialLibraries.itemByName("Fusion Appearance Library")
    base_appearance = mat_lib.appearances.itemByName("Plastic - Matte (Black)")

    if rgb is None:
        body.appearance = base_appearance
        return

    r, g, b = rgb
    custom_name = f"FusionWire {appearance_name} {r},{g},{b}"

    custom_appearance = design.appearances.itemByName(custom_name)
    if not custom_appearance:
        custom_appearance = design.appearances.addByCopy(base_appearance, custom_name)
        props = custom_appearance.appearanceProperties
        for i in range(props.count):
            color_prop = adsk.core.ColorProperty.cast(props.item(i))
            if color_prop:
                color_prop.value = adsk.core.Color.create(r, g, b, 255)
                break

    body.appearance = custom_appearance


def _auto_name(
    body: adsk.fusion.BRepBody,
    cross_section: float,
    colour: str,
    component: adsk.fusion.Component,
):
    """Set body name to e.g. 'Cable 2.5mm² Red', with a suffix if the name already exists."""
    base = f"Cable {cross_section:g}mm² {colour}"
    existing = {b.name for b in component.bRepBodies if b != body}

    candidate = base
    i = 2
    while candidate in existing:
        candidate = f"{base} ({i})"
        i += 1

    body.name = candidate
