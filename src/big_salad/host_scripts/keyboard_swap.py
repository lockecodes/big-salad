#!/usr/bin/python3
from subprocess import run
from gi.repository import Gio


def _is_default_option(options: str) -> bool:
    return options.strip() == "@as []"


def get_xkb_options():
    result = run("gsettings get org.gnome.desktop.input-sources xkb-options".split(" "), capture_output=True)
    return result.stdout.decode(encoding="utf8").strip()


def toggle_xkb_options_on():
    gso = Gio.Settings.new("org.gnome.desktop.input-sources")
    gso.set_strv("xkb-options", ["altwin:swap_alt_win"])


def toggle_xkb_options_off():
    run("gsettings reset org.gnome.desktop.input-sources xkb-options".split(" "))


if __name__ == "__main__":
    options = get_xkb_options()
    if options and not _is_default_option(options):
        print("Alt and Win are already swapped. Toggling off...")
        toggle_xkb_options_off()
        exit(0)
    print("Swapping Alt and Win keys.")
    toggle_xkb_options_on()
