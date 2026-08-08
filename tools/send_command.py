from looprt import send_commands


PORT = "/dev/ttyUSB0"

commands = [
    "P(0)\n",
    "D\n", 
    "P(i)\n",
    "P(25)\n",
    "D\n",
    "P(i)\n",
    "P(50)\n",
    "D\n",
    "P(i)\n",
    "P(75)\n",
    "D\n",
    "P(i)\n",
    "P(100)\n",
    "D\n",
    "P(i)\n",
    "E\n"
]

result = send_commands(PORT, commands)

print(result)