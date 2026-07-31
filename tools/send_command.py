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

for command in commands:
    ser.write((command + "\n").encode())
    time.sleep(0.1)

ser.close()
