from pywinauto import Desktop

desktop = Desktop(backend="uia")


def get_window(title: str):
    return desktop.window(title=title)


def get_buttons(window):
    return window.descendants(control_type="Button")
