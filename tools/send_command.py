from looprt import send_commands


PORT = "/dev/ttyUSB0"

commands = [
    "P(25)\n",
    "D(50)\n",
    "P(i)\n",
    "P(50)\n",
    "D(50)\n",
    "P(i)\n",
    "P(75)\n",
    "D(50)\n",
    "P(i)\n",
    "E\n"
]

result = send_commands(PORT, commands)

print(result)