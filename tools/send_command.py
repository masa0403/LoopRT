from looprt import send_commands



PORT = "/dev/ttyUSB0"

commands = [
    "I(7)\n",
    "H(7)\n",
    "I(7)\n",
    "L(7)\n",
    "I(7)\n",
    "E\n"
]
result = send_commands(PORT, commands)

print(result)

