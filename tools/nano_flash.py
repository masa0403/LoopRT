from pathlib import Path
import subprocess

from build_arduino_cli import setup_arduino_cli


def compile_nano_sketch(
    ino_path: Path,
    fqbn="arduino:avr:nano"
):
    arduino_cli = setup_arduino_cli()

    subprocess.check_call([
        arduino_cli,
        "compile",
        "--fqbn",
        fqbn,
        str(ino_path)
    ])


def upload_nano_sketch(
    ino_path: Path,
    port: str,
    fqbn="arduino:avr:nano"
):
    arduino_cli = setup_arduino_cli()

    subprocess.check_call([
        arduino_cli,
        "upload",
        "--port",
        port,
        "--fqbn",
        fqbn,
        "--verify",
        str(ino_path)
    ])