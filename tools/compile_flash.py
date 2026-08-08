from pathlib import Path
import subprocess
from build_arduino_cli import setup_arduino_cli, find_file


# ------------------------------------------------------------
# AVR Compile
# ------------------------------------------------------------
def compile_avr(source: Path, board: str, output_dir: Path, f_cpu: str):
    tc = resolve_avr_toolchain(board)

    avr_gcc = tc["avr_gcc"]
    avr_objcopy = tc["avr_objcopy"]

    elf_path = output_dir / f"{board}.elf"
    hex_path = output_dir / f"{board}.hex"

    subprocess.check_call([
        avr_gcc,
        "-mmcu=" + tc["mcu"],
        "-Os",
        f"-DF_CPU={f_cpu}",
        "-o", str(elf_path),
        str(source)
    ])

    subprocess.check_call([
        avr_objcopy,
        "-O", "ihex",
        str(elf_path),
        str(hex_path)
    ])

    print(f"[build] F_CPU={f_cpu}")
    print(f"[build] ELF: {elf_path}")
    print(f"[build] HEX: {hex_path}")

    return elf_path, hex_path

# ------------------------------------------------------------
# AVR Flash
# ------------------------------------------------------------
def flash_avr(hex_path: Path, board: str, port: str):
    tc = resolve_avr_toolchain(board)

    #print("\033[1;33m[UPDI] INSERT the 4.7µF–10µF capacitor between RST and GND, then press ENTER...\033[0m")
    #input()

    # ★ tinyAVR のときだけ OSCCFG を 20MHz に設定
    if board in ["attiny202", "attiny402", "attiny412", "attiny1614", "attiny3216"]:
        force_20mhz(board, port)

    avrdude = tc["avrdude"]
    conf = tc["avrdude_conf"]

    # ★ Nano は UPDI ではないので、書き込み方式を切り替える
    if board == "nano":
        subprocess.check_call([
            avrdude,
            "-C", conf,
            "-p", "m328p",
            "-c", "arduino",      # ← これが正しい
            "-P", port,
            "-b", "115200",
            "-v",
            "-U", f"flash:w:{hex_path}:i"
        ])
        print("[flash] Nano flash complete.")
        return

    # ★ tinyAVR の通常書き込み（UPDI）
    mcu_name = {
        "attiny202": "t202",
        "attiny402": "t402",
        "attiny412": "t412",
        "attiny1614": "t1614",
        "attiny3216": "t3216",
    }.get(board, tc["mcu"])

    subprocess.check_call([
        avrdude,
        "-C", conf,
        "-p", mcu_name,
        "-c", "jtag2updi",
        "-P", port,
        "-b", "115200",
        "-v",
        "-U", f"flash:w:{hex_path}:i"
    ])

    print("[flash] Flash complete.")


# ------------------------------------------------------------
# tinyAVR の OSCCFG を 20MHz に強制設定する
# ------------------------------------------------------------
def force_20mhz(board: str, port: str):
    tc = resolve_avr_toolchain(board)
    avrdude = tc["avrdude"]
    conf = tc["avrdude_conf"]

    mcu_name = {
        "attiny202": "t202",
        "attiny402": "t402",
        "attiny412": "t412",
        "attiny1614": "t1614",
        "attiny3216": "t3216",
    }.get(board, tc["mcu"])

    print("[fuse] Setting OSCCFG (fuse2) to 20MHz (0x01)...")

    subprocess.check_call([
        avrdude,
        "-C", conf,
        "-p", mcu_name,
        "-c", "jtag2updi",
        "-P", port,
        "-b", "115200",
        "-v",
        "-U", "fuse2:w:0x01:m"
    ])

    print("[fuse] OSCCFG set to 20MHz.")



# ------------------------------------------------------------
# Nano Compile
# ------------------------------------------------------------
def compile_nano_sketch(ino_path: Path, fqbn="arduino:avr:nano"):
    arduino_cli = setup_arduino_cli()

    subprocess.check_call([
        arduino_cli,
        "compile",
        "--fqbn", fqbn,
        str(ino_path)
    ])



# ------------------------------------------------------------
# Nano Flash
# ------------------------------------------------------------
def upload_nano_sketch(ino_path: Path, port: str, fqbn="arduino:avr:nano"):
    arduino_cli = setup_arduino_cli()

    subprocess.check_call([
        arduino_cli,
        "upload",
        "--port", port,
        "--fqbn", fqbn,
        "--verify",
        str(ino_path)
    ])



DXCORE_TOOLS = Path.home() / ".arduino15/packages/DxCore/tools"



# ------------------------------------------------------------
# Setup Toolchain
# ------------------------------------------------------------
def resolve_avr_toolchain(board: str):
    # AVR
    if board in ["attiny202", "attiny402", "attiny412", "attiny1614", "attiny3216"]:
        avr_gcc = find_file(DXCORE_TOOLS, "avr-gcc")
        avr_objcopy = find_file(DXCORE_TOOLS, "avr-objcopy")
        avrdude = find_file(DXCORE_TOOLS, "avrdude")
        avrdude_conf = find_file(DXCORE_TOOLS, "avrdude.conf")

        return {
            "mcu": board,
            "avr_gcc": avr_gcc,
            "avr_objcopy": avr_objcopy,
            "avrdude": avrdude,
            "avrdude_conf": avrdude_conf
        }

    #Nano
    elif board == "nano":
        return {
            "mcu": "m328p",
            "avr_gcc": "/usr/bin/avr-gcc",
            "avr_objcopy": "/usr/bin/avr-objcopy",
            "avrdude": "/usr/bin/avrdude",
            "avrdude_conf": "/etc/avrdude.conf"
        }

    else:
        raise ValueError(f"Unknown board: {board}")