import json
from pathlib import Path

LOOPRT_ROOT = Path(__file__).resolve().parent.parent

CALIB_FILE = (
    LOOPRT_ROOT
    / "config"
    / "avr_fcpu_calib.json"
)

# ---------------------------------------------------------
# F_CPUキャリブレーション結果を.jsonを保存
# ---------------------------------------------------------
def save_calib(data):
    CALIB_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(CALIB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------------------------------------------------------
# F_CPUを.jsonから参照
# ---------------------------------------------------------
def load_calib():
    if CALIB_FILE.exists():
        with open(CALIB_FILE, "r") as f:
            return json.load(f)

    return {}
