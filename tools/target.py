from pathlib import Path
import sys


# =========================================================
# emb-loop の場所
# =========================================================

EMBLOOP_ROOT = (
    Path.home()
    / "デスクトップ"
    / "GitHub"
    / "embloop"
)

EMBLOOP_EMB = EMBLOOP_ROOT / "emb"


# =========================================================
# emb-loop を Python の import path に追加
#
# これにより、
#
#     PYTHONPATH=/home/.../embloop/emb
#
# を毎回指定する必要がなくなる。
# =========================================================

if str(EMBLOOP_EMB) not in sys.path:
    sys.path.insert(0, str(EMBLOOP_EMB))


# =========================================================
# emb-loop の既存機能を利用
# =========================================================

from host_mcu.code_utility import (
    load_calib,
    detect_nano_port,
)

from host_mcu.compile_flash import (
    compile_avr,
    flash_avr,
)


# =========================================================
# Target MCU
# =========================================================

TARGET_SOURCE = (
    EMBLOOP_EMB
    / "target_mcu"
    / "attiny202"
    / "codes"
    / "test_202.c"
)

TARGET_OUTPUT = (
    EMBLOOP_EMB
    / "target_mcu"
    / "attiny202"
    / "codes_compiled"
)


# =========================================================
# Nano JTAG2UPDI firmware
# =========================================================

JTAG2UPDI_HEX = (
    EMBLOOP_EMB
    / "host_mcu"
    / "host_mcu_codes"
    / "nano"
    / "programmer"
    / "JTAG2UPDI.hex"
)



# =========================================================
# Target Flash
# =========================================================

def flash_target():

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
        raise RuntimeError(
            "ATtiny202のF_CPU calibrationが見つかりません。"
        )

    f_cpu = f"{calib['attiny202']}UL"

    # ---------------------------------------------------------
    # Step 3: ATtiny202をコンパイル
    # ---------------------------------------------------------

    print("[INFO] Target: attiny202")
    print(f"[INFO] Source: {TARGET_SOURCE}")
    print(f"[INFO] F_CPU: {f_cpu}")

    TARGET_OUTPUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    elf_path, hex_path = compile_avr(
        TARGET_SOURCE,
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


