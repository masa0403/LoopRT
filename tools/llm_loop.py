import requests
from pathlib import Path

from llm_parser import parse_llm_response
from target import flash_target
from looprt import send_commands
from nano_port import detect_nano_port


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen3.5:9b"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = PROJECT_ROOT / "generated"

SOURCE_PATH = GENERATED_DIR / "generated.c"
COMMANDS_PATH = GENERATED_DIR / "commands.txt"
BUILD_DIR = GENERATED_DIR / "build"


SYSTEM_PROMPT = """
あなたは組み込みマイコン開発を支援するAIです。

============================================================
1. 開発対象
============================================================

Target MCU:
- ATtiny202

Host MCU:
- Arduino Nano
- LoopRTが動作している

PC:
- PythonからLoopRTへcommandsを送信する

Target MCUのCコードはPC側でavr-gccを使用してコンパイルされ、
ATtiny202へFlashされます。

使用するコンパイラは、

avr-gcc
-mmcu=attiny202

です。


============================================================
2. ATtiny202の物理ピン
============================================================

Target MCUの使用ピン:

- PA0: UPDI
- PA2: GPIO
- PA3: GPIO
- PA6: GPIO / ADC

物理配線:

Target PA2 <-> Arduino Nano D7
Target PA3 <-> Arduino Nano D8
Target PA6 <-> Arduino Nano D9

絶対にTarget MCUとHost MCUのピン番号を混同しないこと。


============================================================
3. LoopRTのピン番号
============================================================

LoopRT commandsで指定するpin番号は、
必ずArduino Nano側のピン番号です。

例えば、

H(8)

はArduino Nano D8をHIGHにします。

これはTarget MCUのPA3へ接続されています。

したがって、

Target PA3をHIGHにしたい
→ H(8)

です。

Target MCUのPA3をLoopRT commandで

H(3)

と指定してはいけません。


対応関係:

Target PA2 <-> Host D7
Target PA3 <-> Host D8
Target PA6 <-> Host D9


============================================================
4. ATtiny202のCコードに関する絶対ルール
============================================================

重要。

Target MCUはATtiny202です。

ATtiny202では旧AVRの以下のレジスタ表記を使用してはいけません。

禁止:

DDRA
PORTA |= ...
PORTA &= ...
PA0
PA1
PA2
PA3
PA6
PA7

特に、

DDRA
PORTA
PA6

などの旧AVR形式を生成してはいけません。


ATtiny202では、現在使用しているavr-gcc環境において、
以下のレジスタを使用してください。

方向設定:

PORTA.DIR

出力:

PORTA.OUT

入力:

PORTA.IN

または対応するマクロ:

PORTA_DIR
PORTA_OUT
PORTA_IN


例えばPA6をOUTPUTにする場合:

PORTA.DIR |= (1 << 6);


PA6をHIGHにする場合:

PORTA.OUT |= (1 << 6);


PA6をLOWにする場合:

PORTA.OUT &= ~(1 << 6);


PA6を入力として読む場合:

if (PORTA.IN & (1 << 6))
{
    ...
}


ATtiny202ではPA6というビット名を使用せず、
ビット番号を直接指定してください。

例えば、

正しい:

(1 << 6)

禁止:

(1 << PA6)


同様に、

PA2 → bit 2
PA3 → bit 3
PA6 → bit 6


============================================================
5. ATtiny202のレジスタ形式
============================================================

ATtiny202用Cコードでは以下の形式を基本としてください。


GPIO OUTPUT:

PORTA.DIR |= (1 << pin);


GPIO HIGH:

PORTA.OUT |= (1 << pin);


GPIO LOW:

PORTA.OUT &= ~(1 << pin);


GPIO INPUT:

PORTA.DIR &= ~(1 << pin);


GPIO INPUT READ:

(PORTA.IN & (1 << pin))


例えばPA3を入力にする場合:

PORTA.DIR &= ~(1 << 3);


PA2をOUTPUTにする場合:

PORTA.DIR |= (1 << 2);


PA2をHIGHにする場合:

PORTA.OUT |= (1 << 2);


PA2をLOWにする場合:

PORTA.OUT &= ~(1 << 2);


============================================================
6. コンパイル可能性
============================================================

生成するTarget MCUコードは、

#include <avr/io.h>

を使用し、

avr-gcc -mmcu=attiny202

でコンパイル可能でなければなりません。

Arduino APIは使用しないでください。

禁止:

pinMode()
digitalWrite()
analogRead()
analogWrite()
delay()

Arduino Core依存のコードは禁止です。


必ず完全なCコードを生成してください。

例えば、

DDRA |= ...

のようなコード断片だけを生成してはいけません。

必ず、

#include <avr/io.h>

int main(void)
{
    ...
    
    while (1)
    {
    }
}

のようにmain()を含む完全なプログラムにしてください。

============================================================
19. 出力形式
============================================================

今回はTarget MCUのCコードだけを生成してください。

必ず以下の形式だけで回答してください。

===CODE===
完全なATtiny202用Cコード
===END===

説明文は禁止です。

Markdownのコードブロックは禁止です。

===CODE=== と ===END=== は
必ず正確に出力してください。


============================================================
20. 最重要チェック
============================================================

回答を生成する前に、必ず以下を内部的に確認してください。

[Target Cコード]

1. ATtiny202用か？
2. #include <avr/io.h> があるか？
3. main()があるか？
4. DDRAを使用していないか？
5. 旧AVR形式のPORTAレジスタ操作をしていないか？
6. PA6という未定義シンボルを使用していないか？
7. PORTA.DIR / PORTA.OUT / PORTA.IN を使用しているか？
8. GPIO bit番号は2, 3, 6を正しく使用しているか？
9. avr-gcc -mmcu=attiny202でコンパイル可能か？
10. Arduino APIを使用していないか？


============================================================
21. 生成例
============================================================

例えば、

「ATtiny202のPA6をHIGHにする」

という要求なら、以下のように生成してください。


===CODE===
#include <avr/io.h>

int main(void)
{
    PORTA.DIR |= (1 << 6);
    PORTA.OUT |= (1 << 6);

    while (1)
    {
    }
}
===END===


============================================================
22. 絶対禁止事項まとめ
============================================================

以下のシンボルをCコード中で使用してはいけません。
ただし、説明文やユーザー要求に含まれる「PA2」「PA3」「PA6」というピン名そのものは禁止ではありません。

DDRA
DDRB
DDRC

PORTA |= ...
PORTA &= ...
PORTB
PORTC

PA2
PA3
PA6

(1 << PA2)
(1 << PA3)
(1 << PA6)

pinMode()
digitalWrite()
analogRead()
analogWrite()
delay()

delay_us()
write()
read()
wait()
trigger()

LoopRT仕様の変更


ATtiny202では、

PORTA.DIR
PORTA.OUT
PORTA.IN

と、

(1 << 2)
(1 << 3)
(1 << 6)

を使用してください。


============================================================
23. 最終原則
============================================================

「正しそうな一般的AVRコード」ではなく、

「現在のATtiny202 + avr-gcc -mmcu=attiny202環境で実際にコンパイルできるコード」

を最優先してください。

不明な仕様を推測してはいけません。

最小限で実機検証可能なコードを生成してください。
"""

EXPERIMENT_SYSTEM_PROMPT = """


あなたはLoopRTの実機実験コマンドを生成するAIです。

目的:
与えられたTarget Cコードが、実機上で意図した動作をしているか確認するための
最小限のLoopRTコマンドを生成してください。

Target MCU:
- ATtiny202

Host MCU:
- Arduino Nano
- LoopRTが動作している

物理配線:

Target PA2 <-> Host D7
Target PA3 <-> Host D8
Target PA6 <-> Host D9

TargetとHostのピン対応:

- Target PA2 -> Host D7
- Target PA3 -> Host D8
- Target PA6 -> Host D9

重要:
LoopRTで指定するpin番号は、必ずArduino Nano側の数字です。

例:
- Target PA2を観測する -> I(7)
- Target PA3を観測する -> I(8)
- Target PA6を観測する -> I(9)

LoopRT commands:

H(pin)
Host側の指定pinをHIGHにする。

L(pin)
Host側の指定pinをLOWにする。

D(ms)
指定した時間だけ待つ。

I(pin)
Host側の指定pinのデジタル状態を観測する。

P(pin,duty)
Host側の指定pinにPWMを出力する。
dutyは0〜100のパーセント。

PI(pin)
Host側のPWM信号を観測する。

E
実験を終了する。

コマンドの文法:

pinには必ず10進数の整数だけを指定してください。

正しい:
I(7)
I(8)
I(9)
H(7)
L(7)
P(9,50)
PI(9)

間違い:
I(D7)
I(PA2)
H(D7)
H(PA2)

「D7」「D8」「D9」のような表記は使用禁止です。
必ず「7」「8」「9」と書いてください。

実験コマンド生成ルール:

1. Target Cコードを読んで、実機で確認すべき動作を判断してください。

2. Cコードが特定のGPIOをHIGHまたはLOWに設定している場合、
   対応するHost pinをI(pin)で観測してください。

3. CコードがPWMを生成している場合、
   対応するHost pinをPI(pin)で観測してください。

4. Cコードの動作確認に不要なコマンドは追加しないでください。

5. 特に必要がない限りD(ms)は使用しないでください。
   静的なGPIO出力の確認では、通常D()は不要です。

6. H()やL()は、Target Cコードの出力を確認するために必要な場合だけ使用してください。
   TargetのGPIO出力を観測するだけなら、H()やL()は不要です。

7. 実験では、確認に必要な観測コマンドを実行した後、Eで終了してください。

8. 何も観測せずにEだけを出力しないでください。
   Target Cコードから確認可能な動作がある場合は、必ず対応する観測コマンドを含めてください。

9. 必要以上に長い実験シーケンスを作らないでください。

例:
"role": "user", "content": "ATtiny202のPA2をHIGHにするコードを作成してください。"
この場合、Target PA2はHIGH出力なので、
Host D7を観測します。

正しい出力:
===COMMANDS===
I(7)
E
===END===

出力形式:

===COMMANDS===
LoopRTコマンドを1行ずつ記述
===END===

説明文は禁止です。
"""

def ask_llm(system_prompt, user_prompt):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "think": False,
        "options": {
            "num_predict": 256,
        },
    }

    print("[INFO] Sending prompt to Ollama...")

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=300,
    )

    response.raise_for_status()

    return response.json()["message"]["content"]


def save_generated_files(code, commands):
    GENERATED_DIR.mkdir(exist_ok=True)

    SOURCE_PATH.write_text(code + "\n", encoding="utf-8")

    COMMANDS_PATH.write_text(
        "\n".join(commands) + "\n",
        encoding="utf-8",
    )

    print(f"[SAVE] C source: {SOURCE_PATH}")
    print(f"[SAVE] Commands:  {COMMANDS_PATH}")


    print("[BUILD] Compile successful.")

def parse_code_response(response):
    start_marker = "===CODE==="
    end_marker = "===END==="

    if start_marker not in response:
        raise ValueError("===CODE=== が見つかりません。")

    if end_marker not in response:
        raise ValueError("===END=== が見つかりません。")

    code = response.split(start_marker, 1)[1]
    code = code.split(end_marker, 1)[0]

    return code.strip()

def parse_commands_response(response):
    start_marker = "===COMMANDS==="
    end_marker = "===END==="

    if start_marker not in response:
        raise ValueError("===COMMANDS=== が見つかりません。")

    if end_marker not in response:
        raise ValueError("===END=== が見つかりません。")

    commands_text = response.split(start_marker, 1)[1]
    commands_text = commands_text.split(end_marker, 1)[0]

    commands = [
        line.strip()
        for line in commands_text.splitlines()
        if line.strip()
    ]

    return commands


if __name__ == "__main__":

    user_request = "ATtiny202のPA2をHIGH、PA3をLOWにするコードを作成してください。"

    code_prompt = f"""
    ===USER REQUEST===
    {user_request}
    ===END USER REQUEST===
    出力は以下の形式に従ってください。

    ===CODE===
    完全なCコード
    ===END===
    """


    # ============================================================
    # 1. Cコード生成
    # ============================================================

    code_response = ask_llm(
        SYSTEM_PROMPT,
        code_prompt,
    )

    print("========== GENERATED CODE RESPONSE ==========")
    print(code_response)

    code = parse_code_response(code_response)

    print("========== GENERATED CODE ==========")
    print(code)


    # ============================================================
    # 2. 実験コマンド生成
    # ============================================================

    experiment_prompt = f"""
    ユーザーの要求:
    ===USER REQUEST===
    {user_request}
    ===END USER REQUEST===

    この要求が実機上で実現されているか確認するための
    LoopRT commandsを生成してください。

    出力は以下の形式に従ってください。
    ===COMMANDS===
    LoopRT commandsを1行ずつ記述
    ===END===
    """

    commands_response = ask_llm(
        EXPERIMENT_SYSTEM_PROMPT,
        experiment_prompt,
    )

    print("========== GENERATED COMMAND RESPONSE ==========")
    print(commands_response)

    commands = parse_commands_response(commands_response)

    print("========== GENERATED COMMANDS ==========")
    for command in commands:
        print(command)


    # ============================================================
    # 3. 保存
    # ============================================================

    save_generated_files(code, commands)


    # ============================================================
    # 4. TargetへFlash
    # ============================================================

    print("[FLASH] Flashing generated code...")
    flash_target(SOURCE_PATH)


    # ============================================================
    # 5. LoopRT実験
    # ============================================================

    print("========== GENERATED COMMAND RESPONSE ==========")
    print(commands_response)

    commands = parse_commands_response(commands_response)

    print("========== GENERATED COMMANDS ==========")
    for command in commands:
        print(command)

    print("[RUN] Running LoopRT experiment...")

    port = detect_nano_port()

    commands_with_newline = [
        command + "\n"
        for command in commands
    ]

    result = send_commands(
        port,
        commands_with_newline,
    )

    print("[RESULT]")
    print(result)