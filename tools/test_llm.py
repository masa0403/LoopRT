import json
import urllib.request


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen3.5:9b"


messages = [
    {
        "role": "system",
        "content": """
あなたはLoopRTの組み込み開発AIです。

Target MCU:
ATtiny202

開発環境:
AVR-GCC / megaTinyCore

重要:
- PA0はUPDIに使用するためGPIOとして使用しない
- PA2, PA3, PA6を主なTarget GPIOとして使用する
- LoopRTから実験コマンドを送信してTarget MCUを操作・観測する
- 実験結果を見てコードを修正する
"""
    }
]


def ask_llm(user_message):
    messages.append({
        "role": "user",
        "content": user_message,
    })

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    answer = result["message"]["content"]

    messages.append({
        "role": "assistant",
        "content": answer,
    })

    return answer


if __name__ == "__main__":

    print(ask_llm(
        "PA6をHIGHにする最小限のコードを書いてください。"
    ))

    print("\n" + "=" * 60 + "\n")

    print(ask_llm(
        "先ほどのコードを使って実験すると、PA6はHIGHになりました。"
        "次にPA6をLOWにする処理を追加してください。"
    ))