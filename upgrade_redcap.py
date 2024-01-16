#!/usr/bin/python3
import re
import tempfile

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from pathlib import Path
from looseversion import LooseVersion
import zipfile
import subprocess

console = Console()


def select_upgrade_file():
    download_directory = (Path.home()  / "Downloads")
    upgrade_files = sorted([f.stem.removeprefix('redcap') for f in  download_directory.glob('redcap*.zip')], key=LooseVersion)

    table = Table(title="Available Upgrade Files")

    table.add_column("Option", justify="right", style="cyan", no_wrap=True)
    table.add_column("File", style="magenta")

    for i, f in enumerate(upgrade_files, 1):
        table.add_row(str(i), f)

    console.clear()
    console.print(table)

    result = Prompt.ask("Select an option or 'q' to quit", choices=[str(i) for i in range(1, len(upgrade_files)+1)] + ['q'], default="q")    

    if result.isnumeric():
        return download_directory / f'redcap{upgrade_files[int(result) - 1]}.zip'


def select_server():
    ssh_config = (Path.home()  / ".ssh" / "config")

    with open(ssh_config) as f:
        contents = f.read()

    servers = sorted(re.findall(r'redcap_.*', contents))

    table = Table(title="Available Upgrade Files")

    table.add_column("Option", justify="right", style="cyan", no_wrap=True)
    table.add_column("Server", style="magenta")

    for i, f in enumerate(servers, 1):
        table.add_row(str(i), f)

    console.clear()
    console.print(table)

    result = Prompt.ask("Select an option or 'q' to quit", choices=[str(i) for i in range(1, len(servers)+1)] + ['q'], default="q")    

    if result.isnumeric():
        return servers[int(result) - 1]


upgrade_file = select_upgrade_file()

with tempfile.TemporaryDirectory() as tmpdirname:
    with zipfile.ZipFile(upgrade_file, 'r') as zip_ref:
        console.print(f'Unzipping file {upgrade_file} ...')
        zip_ref.extractall(tmpdirname)

    redcap_folder = next(Path(tmpdirname).glob('redcap/redcap_*'))

    while redcap_folder:
        server = select_server()

        if not server:
            break

        console.clear()
        console.print(f'Sending upgrade package to server...')

        subprocess.check_output(['scp', '-r', redcap_folder, f'{server}:/local/www/htdocs'])

        Prompt.ask("Package copied.  Complete the upgrade in the REDCap front end...")
