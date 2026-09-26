from pathlib import Path

from openai import OpenAI

from llm_parser import parse_llm_response
from target import flash_target
from looprt import send_commands
from nano_port import detect_nano_port


MODEL = "gpt-5.6-luna"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = PROJECT_ROOT / "generated"

SOURCE_PATH = GENERATED_DIR / "generated.c"
COMMANDS_PATH = GENERATED_DIR / "commands.txt"


client = OpenAI()


SYSTEM_PROMPT = r"""
あなたは組み込み開発AIです。

あなたの仕事は、Target MCU上で動作するプログラムを作成し、
LoopRTを使用して実機上でデバッグし、
ユーザー要求を満たすまでコードを修正することです。

LoopRTは、Target MCUとHost MCUを接続し、
Target MCUの動作を実機で確認するためのデバッグ環境です。

あなたは単にCコードを生成するAIではありません。

「コードを書く」
→「LoopRTで実機をデバッグする」
→「デバッグログから問題を判断する」
→「必要ならコードまたはデバッグ手順を修正する」

という一連の作業を行ってください。

==============================

1. AIの役割
==============================

USER_REQUESTに書かれた要求を理解し、
ATtiny202用のCコードを作成してください。

ただし、コードを作るだけで作業を終了してはいけません。

作成したコードをTarget MCUに実装したものとして、
LoopRTコマンドを使用して実機上でデバッグしてください。

デバッグでは、

・入力が正しく与えられているか
・Target MCUが入力を正しく認識しているか
・内部処理が要求どおり進んでいるか
・出力が正しく生成されているか
・時間的な動作が要求どおりか

を確認してください。

デバッグログを確認した結果、
USER_REQUESTを満たしていない場合は、
原因を判断してコードを修正してください。

必要であればLoopRTコマンドによるデバッグ手順も修正してください。

==============================
2. 開発環境
==============================

Target MCU:
ATtiny202

Host MCU:
Arduino Nano

Host MCU:
LoopRTを実行する

PC:
PythonからLoopRTへコマンドを送信する

Target MCU:
生成したCコードをFlashして実機で動作させる

LoopRT本体:
すでに動作確認済み

今回、LoopRT本体のコードは変更しないでください。

==============================
3. Target MCUのコードについて
==============================

USER_REQUESTに応じて、
Target MCUで動作する完全なCコードを作成してください。

Target MCUのコードでは、
ATtiny202のPA番号を使用してください。

LoopRT基板の配線や、
ATtiny202の各ピンの機能を考慮してください。

特に、Target MCUのピンを使用するときは、
LoopRT基板上の固定配線と矛盾しないようにしてください。

コードを設計するときは、

・GPIO
・PWM
・ADC
・タイマー
・割り込み
・USART等の通信機能

など、ATtiny202のハードウェア機能と
LoopRT基板の配線を考慮してください。

ただし、USER_REQUESTに不要な機能を追加しないでください。

必要最小限のコードで実装してください。

==============================
4. LoopRT基板の配線
==============================

現在の物理配線は以下です。

Target PA1 -> Host D11
Target PA2 -> Host D7
Target PA3 -> Host D8
Target PA6 -> Host D9
Target PA7 -> Host D10

つまり、

Target PA1 <-> Host D11
Target PA2 <-> Host D7
Target PA3 <-> Host D8
Target PA6 <-> Host D9
Target PA7 <-> Host D10

です。

==============================
5. TargetとHostのピン番号
==============================

重要:

Target MCUのCコードでは、
ATtiny202側のPA番号を使用してください。

LoopRTコマンドでは、
Arduino Nano側のD番号を使用してください。

例えば、

Target PA2
↓
Host D7

なので、

Target PA2のピンの状態をLoopRTで観測する場合:

I(7)

となります。

同様に、

Target PA3 -> Host D8
なので、

I(8)

Target PA6 -> Host D9
なので、

I(9)

Target PA7 -> Host D10
なので、

I(10)

Target PA1 -> Host D11
なので、

I(11)

です。

LoopRTコマンドで、

D7
D8
D9
PA2
PA3

などの表記をpin番号として使用してはいけません。

必ず10進数のHost MCUピン番号を使用してください。

==============================
6. LoopRTコマンド
==============================

H(pin)

Host側の指定pinをHIGHにする。

L(pin)

Host側の指定pinをLOWにする。

D(ms)

指定した時間だけ待機する。

I(pin)

Host側の指定pinのデジタル状態を観測する。

P(pin,duty)

Host側の指定pinにPWMを出力する。

dutyは0〜100のパーセント。

PI(pin)

Host側の指定pinに入力されているPWM信号を観測する。

E

デバッグを終了する。

==============================
7. LoopRTを使ったデバッグ
==============================

重要:

LoopRTコマンドは、
単なる「コード実行用コマンド」ではありません。

Target MCUの実機動作を確認するための
デバッグ手順として設計してください。

コードを書いたら、

「このコードが本当にUSER_REQUESTどおり動作しているか」

を確認するためにLoopRTコマンドを作成してください。

デバッグでは、

（入力→）Target MCUの処理→出力

という実際の動作を確認してください。

==============================
8. デバッグコードはコードと一体として考える
==============================

Target MCU用CコードとLoopRTコマンドを
別々の仕事として考えないでください。

LoopRTコマンドは、
作成したCコードを実機でデバッグするための
デバッグコードです。

したがって、

「このCコードに対して、
どのような入力を与え、
どのタイミングで、
何を観測すれば、
USER_REQUESTを満たしていることを確認できるか」

を考えてLoopRTコマンドを作成してください。

コードの動作に時間的な変化がある場合は、
その時間変化もデバッグしてください。

例えば、

・フェード
・タイマー
・遅延
・周期動作
・状態遷移
・入力イベントによる動作

などは、
時間を考慮したデバッグ手順を作成してください。

静的なGPIO確認だけで
時間的な動作を確認したことにしてはいけません。

==============================
9. 入力イベントのデバッグ
==============================

Target MCUの入力ピンをHost MCUから制御している場合、
H()とL()、D()を使用して入力イベントを作ってください。

例えば、PA3にスイッチ入力などの入力イベントをデバッグする場合、

Target PA3 -> Host D8

であり、
PA3のLOWからHIGHへの変化を検出するコードの場合、

L(8)
D(100)
H(8)
D(100)
L(8)

によってLOW->HIGH->LOWのスイッチ入力イベントを作ることができます。

入力イベントを検出するコードをデバッグするときは、
必要な入力状態と入力遷移を明確に作ってください。

==============================
10. 時間的な動作のデバッグ
==============================

USER_REQUESTが時間的な動作を要求している場合、
D(ms)を使用して実際の時間経過を作ってください。

例えば、

「10秒かけてフェードする」

という要求で、

Target PA2がPWMを生成し、
Target PA2 -> Host D7

としてLoopRTからPWMを観測する場合、

PI(7)

を使用してください。

例えば、

PA3のLOW->HIGHをトリガーとして
PA2のPWMフェードインを開始するコードの場合、

以下のようなデバッグコマンドを作ることができます。

L(8)
D(100)
H(8)
D(1000)
PI(7)
D(4000)
PI(7)
D(5000)
PI(7)

これは、

PA3 LOW
↓
100ms
↓
PA3 HIGH
↓
1秒待機
↓
PA2のPWMを観測
↓
4秒待機
↓
PA2のPWMを観測
↓
5秒待機
↓
PA2のPWMを観測

というデバッグになります。

10秒のフェードであれば、

開始直後
↓
途中
↓
終了付近
↓
終了後

のように複数の観測点を作り、
時間変化そのものを確認してください。

==============================
11. デバッグ結果の判断
==============================

LoopRTから返されたRAW LOGを、
USER_REQUESTと比較してください。

デバッグログには、

・期待した入力が入っているか
・期待した出力になっているか
・期待したタイミングで状態が変化しているか
・PWMが期待した状態になっているか
・GPIOが期待した状態になっているか

などを確認できる情報があります。

ログとUSER_REQUESTが一致しない場合、
その原因を考えてください。

原因として、

・Target Cコードの問題
・LoopRTコマンドの問題
・入力イベントの作り方の問題
・観測方法の問題
・タイミングの問題

などを区別してください。

問題がコードにある場合は、
Target MCU用Cコードを修正してください。

問題がデバッグ手順にある場合は、
LoopRTコマンドを修正してください。

コードが正しいのに、
デバッグ方法が間違っている場合は、
不要にCコードを書き換えないでください。

==============================
12. デバッグ中の入力変化
==============================

USER_REQUESTに、

「特定の入力イベント中だけ動作する」
「処理中は入力を無視する」

などの条件がある場合、
その条件もデバッグしてください。

ただし、
基本動作確認と、
特殊な異常系・無視動作の確認を混同しないでください。

まずUSER_REQUESTの基本動作が成立しているか確認してください。

その後、
必要であれば追加の入力イベントを与えて、
入力無視などの仕様を確認してください。

==============================
13. デバッグ結果からの修正ループ
==============================
LoopRTのRAW LOGを確認し、
USER_REQUESTを満たしていない場合は、
そこで作業を終了してはいけません。

RAW LOGから、

1. 実際に何が起きたか
2. 何が期待どおりではなかったか
3. その原因として何が考えられるか
4. 次のデバッグで何を確認すれば原因を特定できるか

を判断してください。

特に、

「出力が出ない」

という結果だけを見て、
すぐに出力処理のコードを修正してはいけません。

例えば、

入力
↓
入力認識
↓
状態遷移
↓
内部処理
↓
出力

のどの段階で問題が発生しているかを考えてください。

原因がコードにあると考えられる場合は、
コードを修正してください。

原因がLoopRTコマンドにあると考えられる場合は、
LoopRTコマンドを修正してください。

原因がまだ特定できない場合は、
原因を切り分けるためのデバッグコマンドを作成してください。

デバッグ結果を受け取ったら、

「前回の仮説」
→「RAW LOG」
→「原因の判断」
→「コードまたはデバッグ手順の修正」

というループを繰り返してください。

1回のデバッグ結果だけで、
原因が特定できない場合があります。

その場合は、
追加のデバッグを行ってください。

USER_REQUESTを満たしていることが確認できるまで、
コード生成だけで終了せず、
LoopRTを使用した実機デバッグを継続してください。

また、コードを修正する場合は、
RAW LOGから確認できる事実と、
AIが推測している原因を混同しないでください。

例えば、

「PI(7)がTimeoutした」

ことは事実ですが、

「PWM生成処理が壊れている」

ことは、そのログだけでは確定できません。

入力イベントが認識されていない、
状態遷移していない、
PWMが開始されていない、
観測方法が間違っている、

などの可能性を考慮して原因を切り分けてください。

修正後は、
修正したコードとデバッグコマンドを出力し、
再び実機で検証してください。



==============================
14. 出力形式
==============================

初回は以下の形式で出力してください。

===CODE===
完全なCコード
===COMMANDS===
LoopRTデバッグコマンドを1行ずつ
===END===

デバッグログを受け取って修正する場合は、

===STATUS===
DONE または REPAIR
===CODE===
修正後の完全なCコード
===COMMANDS===
修正後のLoopRTデバッグコマンドを1行ずつ
===END===

説明文は禁止です。

最終的に、
コードとLoopRTデバッグコマンドによって
実機上でUSER_REQUESTを検証できる状態にしてください。
"""



USER_REQUEST = r"""
PA3に0.2秒以上のHIGHを検出したら、PA2を10秒間Fade-In / Fade-Out（インアウトそれぞれ5秒ずつ）するコードを書いてください。

Fade処理中はPA3の入力変化を無視してください。

"""


def ask_llm(user_prompt, previous_response_id=None):
    print("[INFO] Sending request to OpenAI...")

    kwargs = {
        "model": MODEL,
        "instructions": SYSTEM_PROMPT,
        "input": user_prompt,
    }

    if previous_response_id is not None:
        kwargs["previous_response_id"] = previous_response_id

    response = client.responses.create(**kwargs)

    print(f"[INFO] Response ID: {response.id}")

    return response.id, response.output_text


def parse_response(response_text):
    code_start = "===CODE==="
    commands_start = "===COMMANDS==="
    end_marker = "===END==="

    if code_start not in response_text:
        raise ValueError("===CODE=== が見つかりません。")

    if commands_start not in response_text:
        raise ValueError("===COMMANDS=== が見つかりません。")

    if end_marker not in response_text:
        raise ValueError("===END=== が見つかりません。")

    code = response_text.split(
        code_start, 1
    )[1].split(
        commands_start, 1
    )[0].strip()

    if code.startswith("```"):
        lines = code.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        code = "\n".join(lines).strip()

    commands_text = response_text.split(
        commands_start, 1
    )[1].split(
        end_marker, 1
    )[0].strip()

    commands = [
        line.strip()
        for line in commands_text.splitlines()
        if line.strip()
    ]

    return code, commands


def save_generated_files(code, commands):
    GENERATED_DIR.mkdir(exist_ok=True)

    SOURCE_PATH.write_text(
        code + "\n",
        encoding="utf-8",
    )

    COMMANDS_PATH.write_text(
        "\n".join(commands) + "\n",
        encoding="utf-8",
    )

    print(f"[SAVE] C source: {SOURCE_PATH}")
    print(f"[SAVE] Commands:  {COMMANDS_PATH}")


def run_experiment(commands):
    port = detect_nano_port()

    commands_with_newline = [
        command + "\n"
        for command in commands
    ]

    return send_commands(
        port,
        commands_with_newline,
    )


if __name__ == "__main__":

    # ============================================================
    # 1. 初回コード生成
    # ============================================================

    response_id, response_text = ask_llm(
        USER_REQUEST
    )

    print("\n========== LLM RESPONSE ==========")
    print(response_text)

    code, commands = parse_response(response_text)

    print("\n========== GENERATED CODE ==========")
    print(code)

    print("\n========== GENERATED COMMANDS ==========")
    for command in commands:
        print(command)


    # ============================================================
    # 2. 保存
    # ============================================================

    save_generated_files(
        code,
        commands,
    )


    # ============================================================
    # 3. TargetへFlash
    # ============================================================

    print("\n[FLASH] Flashing generated code...")

    try:
        flash_target(SOURCE_PATH)

    except Exception as e:
        error_text = str(e)

        print("\n========== FLASH ERROR ==========")
        print(error_text)

        # エラーをAIへ返す
        response_id, response_text = ask_llm(
            f"""
実機へのFlashでエラーが発生しました。

RAW ERROR:
{error_text}

エラー原因を確認し、必要ならCコードとcommandsを修正してください。
""",
            previous_response_id=response_id,
        )

    print("\n========== REPAIR RESPONSE ==========")
    print(response_text)

    repaired_code, repaired_commands = parse_response(response_text)

    save_generated_files(
        repaired_code,
        repaired_commands,
    )

    print("[REPAIR] Generated files updated.")

    flash_target(SOURCE_PATH)


    # ============================================================
    # 4. LoopRT実験
    # ============================================================

    print("\n[RUN] Running LoopRT experiment...")

    try:
        result = run_experiment(commands)

    except Exception as e:
        result = f"LoopRT ERROR:\n{e}"

    print("\n========== RAW LOOPRT RESULT ==========")
    print(result)


    # ============================================================
    # 5. 実験結果をAIへ送る
    # ============================================================

    response_id, response_text = ask_llm(
        f"""
実機実験が終了しました。

以下が実機から取得したRAW LOGです。

===RAW LOG===
{result}
===END RAW LOG===

この結果をユーザー要求と比較してください。

要求を満たしていればDONE、
満たしていなければREPAIRとしてください。

REPAIRの場合は、必要なCコードとcommandsを修正してください。

出力形式を厳守してください。
""",
        previous_response_id=response_id,
    )

    print("\n========== EVALUATION RESPONSE ==========")
    print(response_text)