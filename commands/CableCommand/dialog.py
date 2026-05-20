from html import entities

import adsk.core
import adsk.fusion

from lib import iso6722, attributes, pipe_builder

# Persisted across dialog opens within a session
_last_cross_section = 2.5
_last_colour = "Red"
_last_conductor = False

# Keeps handler references alive for the duration of each command invocation
_handlers = []


class CableCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            cmd = adsk.core.Command.cast(args.command)
            inputs = cmd.commandInputs

            sel_input = inputs.addSelectionInput(
                "path_curves", "Path", "Select sketch curves"
            )
            sel_input.addSelectionFilter(adsk.core.SelectionFilters.SketchCurves)
            sel_input.setSelectionLimits(1, 0)

            cs_input = inputs.addDropDownCommandInput(
                "cross_section",
                "Cross-Section",
                adsk.core.DropDownStyles.TextListDropDownStyle,
            )
            for size in iso6722.SIZES:
                od = iso6722.insulation_od(size)
                label = f"{size:g} mm² ({od:g}mm OD)"
                cs_input.listItems.add(label, size == _last_cross_section)

            col_input = inputs.addDropDownCommandInput(
                "colour",
                "Colour",
                adsk.core.DropDownStyles.TextListDropDownStyle,
            )
            for colour_name in pipe_builder.COLOUR_PRESETS:
                col_input.listItems.add(colour_name, colour_name == _last_colour)

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
        # TODO: Slice 1 — react to selection changes (switch create/edit mode)
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
            col_input = adsk.core.DropDownCommandInput.cast(inputs.itemById("colour"))

            cross_section = iso6722.SIZES[cs_input.selectedItem.index]
            colour = col_input.selectedItem.name

            app = adsk.core.Application.get()
            design = adsk.fusion.Design.cast(app.activeProduct)
            component = design.activeComponent

            entities = [
                sel_input.selection(i).entity for i in range(sel_input.selectionCount)
            ]

            for entity in entities:
                pipe_builder.create_cable(
                    component, entity, cross_section, colour, False
                )

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
            args.areInputsValid = (
                sel_input is not None and sel_input.selectionCount >= 1
            )
        except Exception:
            args.areInputsValid = False


class CableCommandDestroyHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        global _last_cross_section, _last_colour
        try:
            cmd = adsk.core.Command.cast(args.firingEvent.sender)
            inputs = cmd.commandInputs

            cs_input = adsk.core.DropDownCommandInput.cast(
                inputs.itemById("cross_section")
            )
            col_input = adsk.core.DropDownCommandInput.cast(inputs.itemById("colour"))

            if cs_input and cs_input.selectedItem:
                _last_cross_section = iso6722.SIZES[cs_input.selectedItem.index]
            if col_input and col_input.selectedItem:
                _last_colour = col_input.selectedItem.name
        except Exception:
            pass
