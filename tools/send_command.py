from looprt import send_commands


PORT = "/dev/ttyUSB0"

commands = [
    "H(8)\n",
    "D(500)\n",
    "L(8)\n",
    "D(500)\n",

    "P(9,25)\n",
    "D(500)\n",
    "PI(7)\n",

    "P(9,50)\n",
    "D(500)\n",
    "PI(7)\n",

    "P(9,75)\n",
    "D(500)\n",
    "PI(7)\n",

    "E\n"
]

result = send_commands(PORT, commands)

print(result)