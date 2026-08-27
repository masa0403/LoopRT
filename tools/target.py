#LoopRT/tools/target.py
from pathlib import Path
import sys
from nano_flash import (
    compile_nano_sketch,
    upload_nano_sketch,
)

from nano_port import detect_nano_port

from code_utility import load_calib
from calibration import calibrate_attiny202

from compile_flash import (
    compile_avr,
    flash_avr,
)

# =========================================================
# LoopRT Root
# =========================================================

LOOPRT_ROOT = Path(__file__).resolve().parent.parent


# =========================================================
# Target MCU
# =========================================================

TARGET_SOURCE = (
    LOOPRT_ROOT
    / "firmware"
    / "target"
    / "attiny202"
    / "test_202.c"
)

TARGET_OUTPUT = (
    LOOPRT_ROOT
    / "firmware"
    / "target"
    / "attiny202"
    / "build"
)


# =========================================================
# Nano JTAG2UPDI firmware
# =========================================================

JTAG2UPDI_HEX = (
    LOOPRT_ROOT
    / "firmware"
    / "host"
    / "JTAG2UPDI.hex"
)


# =========================================================
# Nano LoopRT firmware
# =========================================================

LOOPRT_SKETCH = (
    LOOPRT_ROOT
    / "firmware"
    / "host"
    / "LoopRT"
    / "LoopRT.ino"
)


# =========================================================
# Target Flash
# =========================================================

def flash_target(source_path):

    print("[INFO] Target Flash")

    # ---------------------------------------------------------
    # Nanoのポートを取得
    # ---------------------------------------------------------

    port = detect_nano_port()

    # ---------------------------------------------------------
    # Step 1: NanoをJTAG2UPDI化
    # ---------------------------------------------------------

    print("[INFO] Flashing JTAG2UPDI to Nano")

    flash_avr(
        JTAG2UPDI_HEX,
        "nano",
        port,
    )

    # ---------------------------------------------------------
    # Step 2: F_CPU calibrationを取得
    # ---------------------------------------------------------

    calib = load_calib()

    if "attiny202" not in calib:
        print("[INFO] ATtiny202 F_CPU calibration not found.")
        print("[INFO] Starting automatic calibration...")

        calibrate_attiny202()

        calib = load_calib()

        if "attiny202" not in calib:
            raise RuntimeError(
                "ATtiny202のF_CPU calibrationに失敗しました。"
            )

    f_cpu = f"{calib['attiny202']}UL"

    print(f"[INFO] F_CPU: {f_cpu}")

    # ---------------------------------------------------------
    # Step 3: ATtiny202をコンパイル
    # ---------------------------------------------------------

    print("[INFO] Target: attiny202")
    print(f"[INFO] Source: {source_path}")
    print(f"[INFO] F_CPU: {f_cpu}")

    TARGET_OUTPUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    elf_path, hex_path = compile_avr(
        source_path,
        "attiny202",
        TARGET_OUTPUT,
        f_cpu,
    )

    # ---------------------------------------------------------
    # Step 4: ATtiny202へFlash
    # ---------------------------------------------------------

    print("[INFO] Programmer: Nano (JTAG2UPDI)")

    flash_avr(
        hex_path,
        "attiny202",
        port,
    )

    print("[INFO] Target Flash Complete")


    # ---------------------------------------------------------
    # Step 5: NanoへLoopRT Flash
    # ---------------------------------------------------------

    print("[INFO] LoopRT Flash")

    port = detect_nano_port()

    print("[INFO] Compile LoopRT")

    compile_nano_sketch(
        LOOPRT_SKETCH
    )

    print("[INFO] Upload LoopRT")

    upload_nano_sketch(
        LOOPRT_SKETCH,
        port,
    )

    print("[INFO] LoopRT Flash Complete")