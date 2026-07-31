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
    "E",
]

commands = [
    "H",
    "D",
    "L",
    "E",
]

sequence = "\n".join(commands) + "\n"

ser.write(sequence.encode())

ser.close()
