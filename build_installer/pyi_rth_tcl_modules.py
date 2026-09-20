"""
PyInstaller runtime hook: let Tcl find its modules (e.g. msgcat) in the packaged app.

On Ubuntu/Debian the Tcl modules are collected into `_tcl_data/tcl8`, which is not on Tcl's module path
of the packaged app. Without this the main window fails with `invalid command name "::msgcat::mcmset"`
on systems that do not have Tcl installed.
"""

import os
import sys

_modules_dir = os.path.join(getattr(sys, "_MEIPASS", ""), "_tcl_data", "tcl8")
if os.path.isdir(_modules_dir):
    for _variable in ("TCL8_6_TM_PATH", "TCL9_0_TM_PATH"):
        os.environ.setdefault(_variable, _modules_dir)
