from pathlib import Path
import os
import subprocess


# ------------------------------------------------------------
# Arduino CLI のインストールとパス取得
# ------------------------------------------------------------
def setup_arduino_cli():
    repo_dir = Path(__file__).resolve().parent.parent
    bin_dir = repo_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    arduino_cli = bin_dir / "arduino-cli"

    if not arduino_cli.exists():
        print("[INFO] Installing Arduino CLI...")

        subprocess.check_call(
            [
                "bash",
                "-c",
                "curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh"
            ],
            cwd=str(repo_dir)
        )

        if not arduino_cli.exists():
            raise FileNotFoundError(
                f"Arduino CLI installation failed: {arduino_cli}"
            )

        print("[INFO] Arduino CLI installed.")

    os.environ["PATH"] = f"{bin_dir}:{os.environ['PATH']}"

    return str(arduino_cli)


# ------------------------------------------------------------
# インストール済みツールのパスを探す
# ------------------------------------------------------------
def find_file(base: Path, name: str) -> str:
    for path in base.rglob("bin/" + name):
        if path.is_file():
            return str(path)

    for path in base.rglob("*"):
        if path.is_file() and path.name == name:
            return str(path)

    raise FileNotFoundError(f"{name} not found under {base}")
