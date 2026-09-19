import os
import sys


def disable_input_method() -> None:
    """
    Disable the X11 input method (ibus etc.) for this process on Linux.

    Tk registers every entry/combobox with the input method and waits for an answer each time. With ibus the
    main window then takes minutes to build (and the desktop stalls when the app closes). An `XMODIFIERS`
    value set by the user is kept. The only loss is compose keys/non-Latin input methods inside the app.
    """
    if sys.platform.startswith("linux"):
        os.environ.setdefault("XMODIFIERS", "@im=none")
