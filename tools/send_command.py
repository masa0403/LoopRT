from looprt import send_commands


PORT = "/dev/ttyUSB0"

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

result = send_commands(PORT, commands)

print(result)