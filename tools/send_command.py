from looprt import send_commands


PORT = "/dev/ttyUSB0"

commands = [
    # --- 初期状態の観測 (Host D9出力前のPA2状態) ---
    "PI(7)\n",
    "D(200)\n",

    # --- 細分化Dutyスイープ検証 ---
    "P(9,0)\n",    # 0% (完全LOW入力)
    "D(1000)\n",
    "PI(7)\n",
    "D(200)\n",

    "P(9,10)\n",   # 10%
    "D(1000)\n",
    "PI(7)\n",
    "D(200)\n",

    "P(9,30)\n",   # 30%
    "D(1000)\n",
    "PI(7)\n",
    "D(200)\n",

    "P(9,50)\n",   # 50%
    "D(1000)\n",
    "PI(7)\n",
    "D(200)\n",

    "P(9,70)\n",   # 70%
    "D(1000)\n",
    "PI(7)\n",
    "D(200)\n",

    "P(9,90)\n",   # 90%
    "D(1000)\n",
    "PI(7)\n",
    "D(200)\n",

    "P(9,100)\n",  # 100% (完全HIGH入力)
    "D(1000)\n",
    "PI(7)\n",
    "D(200)\n",

    "E\n"
]
result = send_commands(PORT, commands)

print(result)