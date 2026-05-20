# FusionWire — Domain Glossary

## Cable

A single pipe body swept along a **Sweep Path** using Fusion's Pipe feature. Carries three parameters: **Cross-Section**, **Insulation Colour**, and optionally a **Conductor Body**. One Cable is always produced per Sweep Path — there is no bundle or group entity.

## Sweep Path

A sketch curve (spline, line, arc, or any curve Fusion's Pipe feature accepts) that defines the route of a Cable. Must be a single continuous curve. Validated implicitly by Fusion — the addon does not pre-validate paths.

## Cross-Section

The conductor cross-sectional area in mm², used to derive **Insulation OD** via the ISO 6722 lookup table. Supported range: 0.5 mm² to 110 mm².

## Insulation OD

The outer diameter of the Cable body, in mm. Derived from **Cross-Section** via a hard-coded ISO 6722 lookup table. Never entered directly by the user.

## Insulation Colour

A named colour preset (red, black, blue, yellow) applied to the Cable body as a Fusion appearance (Plastic - Matte). Each preset maps to a fixed RGB value.

## Conductor Body

An optional second pipe body, concentric with the Cable, swept along the same **Sweep Path** at the conductor diameter derived from the **Cross-Section**. Rendered with a copper appearance. Toggled at the dialog level — applies to all Cables in a single operation.

## Cable Operation

A single execution of the addon dialog. Produces or replaces one Cable (and optionally one **Conductor Body**) per selected input. All inputs in one operation share the same **Cross-Section**, **Insulation Colour**, and **Conductor Body** toggle.

## Addon-Tagged Body

A Fusion body created by this addon that carries custom attributes recording its **Cross-Section**, **Insulation Colour**, and **Conductor Body** state. Only Addon-Tagged Bodies can be selected as edit targets — generic sweep or pipe bodies are excluded by the selection filter.
