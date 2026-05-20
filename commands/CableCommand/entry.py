import os
import adsk.core
import adsk.fusion

from commands.CableCommand.dialog import CableCommandCreatedHandler

COMMAND_ID = 'FusionWireCableCommand'
COMMAND_NAME = 'FusionWire: Create/Edit Cables'
COMMAND_DESCRIPTION = 'Create or edit cable bodies from sketch curves'
PANEL_ID = 'SolidCreatePanel'
WORKSPACE_ID = 'FusionSolidEnvironment'

_handlers = []
_button = None


def start():
    app = adsk.core.Application.get()
    ui = app.userInterface

    cmd_defs = ui.commandDefinitions
    resources = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')

    cmd_def = cmd_defs.itemById(COMMAND_ID)
    if cmd_def:
        cmd_def.deleteMe()

    cmd_def = cmd_defs.addButtonDefinition(
        COMMAND_ID,
        COMMAND_NAME,
        COMMAND_DESCRIPTION,
        resources,
    )

    handler = CableCommandCreatedHandler()
    cmd_def.commandCreated.add(handler)
    _handlers.append(handler)

    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    global _button
    _button = panel.controls.addCommand(cmd_def)
    _button.isPromotedByDefault = True
    _button.isPromoted = True


def stop():
    app = adsk.core.Application.get()
    ui = app.userInterface

    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    ctrl = panel.controls.itemById(COMMAND_ID)
    if ctrl:
        ctrl.deleteMe()

    cmd_def = ui.commandDefinitions.itemById(COMMAND_ID)
    if cmd_def:
        cmd_def.deleteMe()

    _handlers.clear()
