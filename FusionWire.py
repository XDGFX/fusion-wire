import adsk.core
import traceback
import sys
import os


def run(context):
    try:
        _ADDIN_DIR = os.path.dirname(os.path.abspath(__file__))
        if _ADDIN_DIR not in sys.path:
            sys.path.insert(0, _ADDIN_DIR)

        from commands.CableCommand import entry as cable_command

        cable_command.start()
    except Exception:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox(f"FusionWire failed to start:\n{traceback.format_exc()}")


def stop(context):
    try:
        from commands.CableCommand import entry as cable_command

        cable_command.stop()
    except Exception:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox(f"FusionWire failed to stop:\n{traceback.format_exc()}")
