from looprt import send_commands



PORT = "/dev/ttyUSB0"

commands = [
    # 初期状態の確認
    "PI(7)\n",
    "PI(8)\n",

    "D(200)\n",

    # 炎のゆらめきを複数回観測
    "PI(7)\n",
    "PI(8)\n",
    "D(200)\n",

    "PI(7)\n",
    "PI(8)\n",
    "D(200)\n",

    "PI(7)\n",
    "PI(8)\n",
    "D(200)\n",

    "PI(7)\n",
    "PI(8)\n",
    "D(200)\n",

    "PI(7)\n",
    "PI(8)\n",
    "D(200)\n",

    "PI(7)\n",
    "PI(8)\n",
    "D(200)\n",

    "PI(7)\n",
    "PI(8)\n",
    "D(200)\n",

    "E\n"
]
result = send_commands(PORT, commands)

print(result)

