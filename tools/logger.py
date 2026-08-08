import serial
import time
from nano_port import detect_nano_port


# ---------------------------------------------------------
# Step 4: Nano で周期測定
# ---------------------------------------------------------
def measure_period():
    print("Waiting for Nano measurement...")

    ser = serial.Serial(detect_nano_port(), 115200, timeout=10)

    for _ in range(50):  # 最大50回試す（約5秒）
        line = ser.readline().decode().strip()
        if line.startswith("PERIOD:"):
            ser.close()
            period = float(line.split(":")[1])
            print(f"Measured period = {period} sec")
            return period

        time.sleep(0.1)

    ser.close()
    raise RuntimeError("Nanoから周期が受信できませんでした")


def receive_serial_log(duration_sec=10):
    port = detect_nano_port()

    ser = serial.Serial(port, 115200, timeout=0.2)

    time.sleep(2)      # リセット待ち
    wait_ready(ser)    # READYを待つ
    ser.reset_input_buffer()

    logs = []

    start = time.time()

    while time.time() - start < duration_sec:

        if ser.in_waiting:

            line = ser.readline().decode(
                "utf-8",
                errors="replace"
            ).strip()

            print(line)

            logs.append(line)

    ser.close()

    return logs

def wait_ready(ser, timeout=5):
    start = time.time()

    while time.time() - start < timeout:
        line = ser.readline().decode(errors="replace").strip()

        if line:
            print(line)

        if line == "#SYS,STATUS,READY":
            return True

    return False