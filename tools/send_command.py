import serial
import time

PORT = "/dev/ttyUSB0"
BAUDRATE = 115200

ser = serial.Serial(PORT, BAUDRATE, timeout=1)

time.sleep(2)

commands = [
    "H",
    "D",
    "L",
    "D",
    "H",
    "D",
    "L",
    "E",
]

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
            print(line)
            break

ser.close()