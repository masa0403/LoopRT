from pathlib import Path
import os
import subprocess


def setup_arduino_cli():
    base_dir = Path(__file__).resolve().parent.parent / "bin"
    base_dir.mkdir(parents=True, exist_ok=True)

    bin_dir = base_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    arduino_cli = bin_dir / "arduino-cli"

    if arduino_cli.exists():
        os.environ["PATH"] = f"{bin_dir}:{os.environ['PATH']}"
        return str(arduino_cli)

    print("[INFO] Installing Arduino CLI...")

    subprocess.check_call(
        "curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh",
        shell=True,
        cwd=str(base_dir)
    )

    os.environ["PATH"] = f"{bin_dir}:{os.environ['PATH']}"

    print("[INFO] Arduino CLI installed.")

    return str(arduino_cli)