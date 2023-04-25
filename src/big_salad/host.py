import shutil
from pathlib import Path
from subprocess import run

import click

from big_salad.config import LOCAL_BIN, BS_DIR


@click.group(name="ho")
def ho():
    """
    Host scripts...copy a script to local for running and add a shortcut
    """
    pass


@ho.command(name="kbsw")
def keyboard_switch():
    """
    Assume all is already in place and drop the script in the .local/bin directory
    """
    host_script = Path(BS_DIR, "src", "big_salad", "host_scripts", "keyboard_swap.py")
    script_destination = Path(LOCAL_BIN, "kbsw")
    shutil.copy(host_script, script_destination)
    run(["chmod", "+x", str(script_destination)])
