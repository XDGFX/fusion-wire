# FusionWire

A Fusion 360 Add-In for creating and editing cable bodies from sketch curves.

## What it does

Select one or more sketch curves (splines, lines, arcs) or existing cable bodies, choose a cross-section size and insulation colour, and the add-in creates correctly-sized, coloured pipe bodies in one shot.

## Installation

1. Clone this repo into your Fusion 360 add-ins directory:
   - **Mac:** `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`
   - **Windows:** `%appdata%\Autodesk\Autodesk Fusion 360\API\AddIns\`
2. In Fusion 360: **Tools → ADD-INS → Add-Ins tab → click the green + → select the FusionWire folder**
3. Select FusionWire and click **Run**. The button appears in the **Solid → Create** panel.

## Usage

### Creating cables

1. Draw your cable routes as sketch curves in a 3D sketch.
2. Click the **FusionWire** toolbar button.
3. Select one or more sketch curves.
4. Choose cross-section (mm²) and insulation colour.
5. Optionally enable **Show conductor**.
6. Click **OK**.

### Editing cables

1. Click the **FusionWire** toolbar button.
2. Select one or more existing cable bodies (created by FusionWire).
3. Adjust parameters — all selected cables will be updated to the new values.
4. Click **OK**.

## Cable sizes

Insulation ODs follow ISO 6722 (single-core automotive cable), 0.5 mm² through 110 mm².

## Development

```text
FusionWire/
├── FusionWire.py          # Add-In entry point (run / stop)
├── FusionWire.manifest    # Fusion metadata
├── commands/
│   └── CableCommand/
│       ├── entry.py       # Toolbar button registration
│       ├── dialog.py      # Command dialog and event handlers
│       └── resources/     # Toolbar icon PNGs (16x16, 32x32, 64x64)
└── lib/
    ├── iso6722.py         # mm² → OD lookup table
    ├── attributes.py      # Custom attribute helpers
    └── pipe_builder.py    # Pipe creation and appearance logic
```
