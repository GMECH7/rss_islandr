import os
import sys

#: Set this environment variable (to any value) to keep the input method of the desktop
KEEP_INPUT_METHOD_VARIABLE = "RSS_KEEP_INPUT_METHOD"


def disable_input_method() -> None:
    """
    Disable the X11 input method (ibus etc.) for this process on Linux.

    Tk registers every entry/combobox with the input method and waits for an answer each time. With ibus the
    main window then takes minutes to build (and the desktop stalls when the app closes). Desktops such as
    Ubuntu already set `XMODIFIERS=@im=ibus`, so the value has to be replaced. The only loss is compose
    keys/non-Latin input methods inside the app.
    """
    if sys.platform.startswith("linux") and not os.environ.get(KEEP_INPUT_METHOD_VARIABLE):
        os.environ["XMODIFIERS"] = "@im=none"
