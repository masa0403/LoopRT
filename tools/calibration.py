from pathlib import Path

from compile_flash import (
    flash_avr,
    compile_nano_sketch,
    upload_nano_sketch,
    compile_avr,
)

from code_utility import (
    save_calib
)

from nano_port import detect_nano_port

from logger import measure_period


LOOPRT_ROOT = Path(__file__).resolve().parent.parent


CALIB_SOURCE = (
    LOOPRT_ROOT
    / "target"
    / "attiny202"
    / "calibration"
    / "blink.c"
)

CALIB_OUTPUT = (
    LOOPRT_ROOT
    / "target"
    / "attiny202"
    / "build"
    / "calibration"
)

NANO_CALIB_SKETCH = (
    LOOPRT_ROOT
    / "firmware"
    / "host"
    / "calibration"
    / "calib.ino"
)


def calibrate_attiny202():

    print("[CALIB] ATtiny202 F_CPU calibration")

    port = detect_nano_port()

    # ---------------------------------------------------------
    # Step 1: Nano → JTAG2UPDI
    # ---------------------------------------------------------

    print("[CALIB] Flashing JTAG2UPDI to Nano")

    jtag2updi_hex = (
        LOOPRT_ROOT
        / "firmware"
        / "host"
        / "JTAG2UPDI.hex"
    )

    flash_avr(
        jtag2updi_hex,
        "nano",
        port,
    )

    # ---------------------------------------------------------
    # Step 2: ATtiny202へcalibration用blinkを書き込む
    # ---------------------------------------------------------

    print("[CALIB] Compiling ATtiny202 calibration firmware")

    CALIB_OUTPUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    elf_path, hex_path = compile_avr(
        CALIB_SOURCE,
        "attiny202",
        CALIB_OUTPUT,
        "20000000UL",
    )

    print("[CALIB] Flashing ATtiny202")

    flash_avr(
        hex_path,
        "attiny202",
        port,
    )

    # ---------------------------------------------------------
    # Step 3: Nano → calibration logger
    # ---------------------------------------------------------

    print("[CALIB] Flashing calibration logger to Nano")

    compile_nano_sketch(
        NANO_CALIB_SKETCH
    )

    upload_nano_sketch(
        NANO_CALIB_SKETCH,
        port,
    )

    # ---------------------------------------------------------
    # Step 4: 周期測定
    # ---------------------------------------------------------

    print("[CALIB] Measuring clock period")

    period = measure_period()

    # ---------------------------------------------------------
    # Step 5: F_CPU計算
    # ---------------------------------------------------------

    expected = 2.0

    ratio = expected / period

    f_cpu_real = int(
        20000000 * ratio
    )

    print(
        f"[CALIB] Computed F_CPU = "
        f"{f_cpu_real} Hz"
    )

    # ---------------------------------------------------------
    # Step 6: 保存
    # ---------------------------------------------------------

    save_calib({
        "attiny202": f_cpu_real
    })

    print("[CALIB] Calibration saved")

    return f_cpu_real