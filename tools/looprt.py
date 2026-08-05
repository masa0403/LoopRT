import serial

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

    ser.write(sequence.encode())

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

