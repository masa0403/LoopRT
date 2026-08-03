import serial
import time


def send_commands(port, commands, baudrate=115200):
    ser = serial.Serial(port, baudrate, timeout=1)

    time.sleep(2)

    sequence = "\n".join(commands) + "\n"

    print("[INFO] Send Command Sequence")
    print(repr(sequence))

    ser.write(sequence.encode())

    print("[INFO] Waiting for LoopRT result...")

    while True:
        line = ser.readline().decode(errors="replace").strip()

        if line:
            print(f"[LOOPRT] {line}")

            if line.startswith("[RESULT]"):
                result = line
                ser.close()
                return result

    ser.close()