import serial
import time

def send_commands(port, commands, baudrate=115200):
    ser = serial.Serial(port, baudrate, timeout=1)


    print("[INFO] Waiting for LoopRT Ready...")

    while True:
        line = ser.readline().decode(errors="replace").strip()

        if not line:
            continue

        print(f"[LOOPRT] {line}")

        if line == "LoopRT Ready":
            break

    sequence = "\n".join(commands) + "\n"

    print("[INFO] Send Command Sequence")
    print(repr(sequence))

    #ser.write(sequence.encode()) #一括送信→長文でバッファ満杯になってデバッグがフリーズした
    for command in commands:
        ser.write(command.encode())
        print(f"[INFO] Send Command: {repr(command)}")
        time.sleep(2)

    print("[INFO] Waiting for LoopRT result...")

    while True:
        line = ser.readline().decode(errors="replace").strip()

        if not line:
            continue

        print(f"[LOOPRT] {line}")

        if line.startswith("[RESULT]"):
            ser.close()
            return line

    ser.close()

