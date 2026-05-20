from html import entities
import os
import struct
import zlib

import adsk.core
import adsk.fusion

from lib import iso6722, attributes, pipe_builder

_COLOURS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "resources", "colours"
)


def _make_solid_png(r: int, g: int, b: int, size: int = 16) -> bytes:
    def chunk(tag, data):
        payload = tag + data
        return (
            struct.pack(">I", len(data))
            + payload
            + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)
        )

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    row = b"\x00" + bytes([r, g, b] * size)
    idat = chunk(b"IDAT", zlib.compress(row * size))
    iend = chunk(b"IEND", b"")
    return sig + ihdr + idat + iend


def _ensure_swatches():
    for name, (r, g, b) in pipe_builder.COLOUR_PRESETS.items():
        folder = os.path.join(_COLOURS_DIR, name)
        os.makedirs(folder, exist_ok=True)
        path_16 = os.path.join(folder, "16x16.png")
        if not os.path.exists(path_16):
            with open(path_16, "wb") as f:
                f.write(_make_solid_png(r, g, b, 16))


_ensure_swatches()

# Persisted across dialog opens within a session
_last_cross_section = 2.5
_last_colour = "Red"
_last_conductor = False
_last_hide_sketch = False

# Keeps handler references alive for the duration of each command invocation
_handlers = []


def _classify_selection(sel_input: adsk.core.SelectionCommandInput) -> str:
    """
    Classify the current selection content.

    Returns one of:
      'empty'   — nothing selected
      'curves'  — all sketch curves
      'bodies'  — all addon-tagged cable bodies
      'mixed'   — sketch curves and cable bodies together (rejected)
      'invalid' — contains a solid body not tagged by this add-in (rejected)
    """
    if sel_input.selectionCount == 0:
        return "empty"

    has_curves = False
    has_bodies = False

    for i in range(sel_input.selectionCount):
        entity = sel_input.selection(i).entity
        body = adsk.fusion.BRepBody.cast(entity)
        if body is None:
            has_curves = True
        elif attributes.is_tagged(body):
            has_bodies = True
        else:
            return "invalid"

    if has_curves and has_bodies:
        return "mixed"
    return "bodies" if has_bodies else "curves"


class CableCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            cmd = adsk.core.Command.cast(args.command)
            inputs = cmd.commandInputs

            sel_input = inputs.addSelectionInput(
                "path_curves", "Path", "Select sketch curves or existing cable bodies"
            )
            sel_input.addSelectionFilter(adsk.core.SelectionFilters.SketchCurves)
            sel_input.addSelectionFilter(adsk.core.SelectionFilters.SolidBodies)
            sel_input.setSelectionLimits(1, 0)

            cs_input = inputs.addDropDownCommandInput(
                "cross_section",
                "Cross-Section",
                adsk.core.DropDownStyles.TextListDropDownStyle,
            )
            for size in iso6722.SIZES:
                od = iso6722.insulation_od(size)
                label = f"{size:g} mm²"
                cs_input.listItems.add(label, size == _last_cross_section)

            col_input = inputs.addButtonRowCommandInput("colour", "Colour", False)
            for colour_name in pipe_builder.COLOUR_PRESETS:
                folder = os.path.join(_COLOURS_DIR, colour_name)
                col_input.listItems.add(colour_name, colour_name == _last_colour, folder)

            inputs.addBoolValueInput(
                "hide_sketch", "Hide Sketch", True, "", _last_hide_sketch
            )

            on_input_changed = CableCommandInputChangedHandler()
            cmd.inputChanged.add(on_input_changed)
            _handlers.append(on_input_changed)

            on_validate = CableCommandValidateHandler()
            cmd.validateInputs.add(on_validate)
            _handlers.append(on_validate)

            on_execute = CableCommandExecuteHandler()
            cmd.execute.add(on_execute)
            _handlers.append(on_execute)

            on_destroy = CableCommandDestroyHandler()
            cmd.destroy.add(on_destroy)
            _handlers.append(on_destroy)

        except Exception as e:
            adsk.core.Application.get().userInterface.messageBox(
                f"CableCommand setup failed:\n{e}"
            )


class CableCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def notify(self, args):
        try:
            event_args = adsk.core.InputChangedEventArgs.cast(args)
            if event_args.input.id != "path_curves":
                return

            cmd = adsk.core.Command.cast(event_args.firingEvent.sender)
            inputs = cmd.commandInputs
            sel_input = adsk.core.SelectionCommandInput.cast(
                inputs.itemById("path_curves")
            )
            cs_input = adsk.core.DropDownCommandInput.cast(
                inputs.itemById("cross_section")
            )
            col_input = adsk.core.ButtonRowCommandInput.cast(inputs.itemById("colour"))

            if _classify_selection(sel_input) != "bodies":
                return

            body = adsk.fusion.BRepBody.cast(sel_input.selection(0).entity)
            params = attributes.read(body)
            if not params:
                return

            for i, size in enumerate(iso6722.SIZES):
                if size == params["cross_section"]:
                    cs_input.listItems.item(i).isSelected = True
                    break

            for i in range(col_input.listItems.count):
                if col_input.listItems.item(i).name == params["colour"]:
                    col_input.listItems.item(i).isSelected = True
                    break

        except Exception:
            pass


class CableCommandExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            cmd = adsk.core.Command.cast(args.firingEvent.sender)
            inputs = cmd.commandInputs

            sel_input = adsk.core.SelectionCommandInput.cast(
                inputs.itemById("path_curves")
            )
            cs_input = adsk.core.DropDownCommandInput.cast(
                inputs.itemById("cross_section")
            )
            col_input = adsk.core.ButtonRowCommandInput.cast(inputs.itemById("colour"))
            hide_input = adsk.core.BoolValueCommandInput.cast(
                inputs.itemById("hide_sketch")
            )

            cross_section = iso6722.SIZES[cs_input.selectedItem.index]
            colour = col_input.selectedItem.name
            hide_sketch = hide_input.value if hide_input else False

            app = adsk.core.Application.get()
            design = adsk.fusion.Design.cast(app.activeProduct)
            component = design.activeComponent

            mode = _classify_selection(sel_input)
            selected = [
                sel_input.selection(i).entity for i in range(sel_input.selectionCount)
            ]

            if mode == "bodies":
                # Resolve all path curves BEFORE any timeline mutation.
                # deleteMe() causes Fusion to re-sequence entity tokens; any
                # resolve attempted after the first deletion returns a stale
                # reference (wrong type) for bodies nearby in the timeline.
                bodies_to_delete = []
                path_curves = []
                for entity in selected:
                    body = adsk.fusion.BRepBody.cast(entity)
                    params = attributes.read(body)
                    if params and params.get("path_token"):
                        curve = pipe_builder.recover_path(params["path_token"])
                        if curve:
                            path_curves.append(curve)
                    bodies_to_delete.append(body)

                for body in bodies_to_delete:
                    pipe_builder.delete_cable(body)

                for path_curve in path_curves:
                    pipe_builder.create_cable(
                        component, path_curve, cross_section, colour, False
                    )
            else:
                sketches = []
                for e in selected:
                    sc = adsk.fusion.SketchCurve.cast(e)
                    if sc and sc.parentSketch not in sketches:
                        sketches.append(sc.parentSketch)

                for entity in selected:
                    pipe_builder.create_cable(
                        component, entity, cross_section, colour, False
                    )

                # Fusion auto-hides path sketches when a pipe feature is created,
                # so always set visibility explicitly to honour the checkbox.
                for sketch in sketches:
                    if sketch:
                        sketch.isVisible = not hide_sketch

        except Exception as e:
            adsk.core.Application.get().userInterface.messageBox(
                f"CableCommand execute failed:\n{e}"
            )


class CableCommandValidateHandler(adsk.core.ValidateInputsEventHandler):
    def notify(self, args):
        try:
            cmd = adsk.core.Command.cast(args.firingEvent.sender)
            sel_input = adsk.core.SelectionCommandInput.cast(
                cmd.commandInputs.itemById("path_curves")
            )
            try:
                mode = _classify_selection(sel_input)
                args.areInputsValid = mode in ("curves", "bodies")
            except Exception:
                # Entity access can be unreliable during validateInputs; fall
                # back to the simple "something is selected" check so a transient
                # API quirk never silently disables the OK button.
                args.areInputsValid = (
                    sel_input is not None and sel_input.selectionCount >= 1
                )
        except Exception:
            args.areInputsValid = False


class CableCommandDestroyHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        global _last_cross_section, _last_colour, _last_hide_sketch
        try:
            cmd = adsk.core.Command.cast(args.firingEvent.sender)
            inputs = cmd.commandInputs

            cs_input = adsk.core.DropDownCommandInput.cast(
                inputs.itemById("cross_section")
            )
            col_input = adsk.core.ButtonRowCommandInput.cast(inputs.itemById("colour"))
            hide_input = adsk.core.BoolValueCommandInput.cast(
                inputs.itemById("hide_sketch")
            )

            if cs_input and cs_input.selectedItem:
                _last_cross_section = iso6722.SIZES[cs_input.selectedItem.index]
            if col_input and col_input.selectedItem:
                _last_colour = col_input.selectedItem.name
            if hide_input:
                _last_hide_sketch = hide_input.value
        except Exception:
            pass
