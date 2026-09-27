from pathlib import Path

from openai import OpenAI

from target import flash_target
from looprt import send_commands
from nano_port import detect_nano_port
from prompts2 import SYSTEM_PROMPT, USER_REQUEST


MODEL = "gpt-5.6-luna"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = PROJECT_ROOT / "generated"

SOURCE_PATH = GENERATED_DIR / "generated.c"
COMMANDS_PATH = GENERATED_DIR / "commands.txt"
COMMENTS_PATH = GENERATED_DIR / "comments.txt"

MAX_REPAIRS = 3


client = OpenAI()


# ============================================================
# OpenAI
# ============================================================

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


# ============================================================
# LLM Response Parser
# ============================================================

def parse_response(response_text):
    code_start = "===CODE==="
    commands_start = "===COMMANDS==="
    comment_start = "===COMMENT==="
    status_start = "===STATUS==="
    end_marker = "===END==="

    if status_start not in response_text:
        raise ValueError("===STATUS=== が見つかりません。")

    if end_marker not in response_text:
        raise ValueError("===END=== が見つかりません。")

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status_text = response_text.split(
        status_start,
        1,
    )[1].split(
        end_marker,
        1,
    )[0].strip()

    status = None

    for line in status_text.splitlines():
        line = line.strip()

        if line in ("DONE", "REPAIR"):
            status = line
            break

    if status is None:
        raise ValueError("DONE または REPAIR が見つかりません。")

    # --------------------------------------------------------
    # COMMENT
    # --------------------------------------------------------

    comment = ""

    if comment_start in response_text:
        comment = response_text.split(
            comment_start,
            1,
        )[1].split(
            status_start,
            1,
        )[0].strip()

    # --------------------------------------------------------
    # DONE
    # --------------------------------------------------------
    #
    # DONEの場合、CODE / COMMANDSは不要。
    # ここで正常に返す。
    #

    if status == "DONE":
        return None, None, comment, status

    # --------------------------------------------------------
    # REPAIR
    # --------------------------------------------------------
    #
    # REPAIRの場合はCODE / COMMANDSが必要。
    #

    if code_start not in response_text:
        raise ValueError(
            "REPAIRレスポンスに===CODE===がありません。"
        )

    if commands_start not in response_text:
        raise ValueError(
            "REPAIRレスポンスに===COMMANDS===がありません。"
        )

    # --------------------------------------------------------
    # CODE
    # --------------------------------------------------------

    code = response_text.split(
        code_start,
        1,
    )[1].split(
        commands_start,
        1,
    )[0].strip()

    if code.startswith("```"):
        lines = code.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        code = "\n".join(lines).strip()

    # --------------------------------------------------------
    # COMMANDS
    # --------------------------------------------------------

    commands_text = response_text.split(
        commands_start,
        1,
    )[1].split(
        comment_start,
        1,
    )[0].strip()

    commands = [
        line.strip()
        for line in commands_text.splitlines()
        if line.strip()
    ]

    return code, commands, comment, status


# ============================================================
# Current Generated Files
# ============================================================

def save_current_files(code, commands):
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


# ============================================================
# Generation History
# ============================================================

def save_generation(generation, code, commands):
    GENERATED_DIR.mkdir(exist_ok=True)

    source_path = GENERATED_DIR / f"generated_{generation}.c"
    commands_path = GENERATED_DIR / f"commands_{generation}.txt"

    source_path.write_text(
        code + "\n",
        encoding="utf-8",
    )

    commands_path.write_text(
        "\n".join(commands) + "\n",
        encoding="utf-8",
    )

    print(f"[SAVE] Generation C:        {source_path}")
    print(f"[SAVE] Generation commands: {commands_path}")

    return source_path, commands_path


# ============================================================
# Comments
# ============================================================

def append_comment(generation, status, comment):
    if not comment:
        return

    GENERATED_DIR.mkdir(exist_ok=True)

    with COMMENTS_PATH.open(
        "a",
        encoding="utf-8",
    ) as f:
        f.write(
            f"=== GENERATION {generation} / {status} ===\n"
        )
        f.write(comment)
        f.write("\n\n")

    print(f"[SAVE] Comment: {COMMENTS_PATH}")


# ============================================================
# Debug Log
# ============================================================

def save_debug_log(generation, log_text):
    GENERATED_DIR.mkdir(exist_ok=True)

    log_path = GENERATED_DIR / f"debug_log_{generation}.txt"

    log_path.write_text(
        log_text + "\n",
        encoding="utf-8",
    )

    print(f"[SAVE] Debug log: {log_path}")

    return log_path


# ============================================================
# LoopRT
# ============================================================

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


# ============================================================
# Debug Packet
# ============================================================

def build_debug_packet(
    generation,
    code,
    commands,
    result,
    result_type,
):
    return f"""
=== DEBUG PACKET ===

GENERATION:
{generation}

=== USER REQUEST ===
{USER_REQUEST}

=== CURRENT CODE ===
{code}

=== CURRENT COMMANDS ===
{chr(10).join(commands)}

=== RESULT TYPE ===
{result_type}

=== RAW RESULT ===
{result}

=== END DEBUG PACKET ===

現在のコード、commands、実機結果を比較してください。

USER_REQUESTを満たしているか判断してください。

満たしていれば:

===COMMENT===
今回の実験結果から、要求を満たしたと判断した理由を簡潔に説明してください。
追加の実験が不要であることも必要に応じて説明してください。

===STATUS===
DONE

満たしていなければ:

===CODE===
完全な修正版Cコード

===COMMANDS===
修正版LoopRT commands

===COMMENT===
何が問題だったと判断し、何を変更したのかを要点だけ簡潔に説明してください。

===STATUS===
REPAIR

重要:

RAW RESULTだけを見て原因を決めつけないでください。
CURRENT CODEとCURRENT COMMANDSを含めて判断してください。

出力形式を厳守してください。
"""


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    GENERATED_DIR.mkdir(exist_ok=True)

    previous_response_id = None

    # ========================================================
    # 1. Initial Generation
    # ========================================================

    print("\n" + "=" * 60)
    print("[STEP 1] Initial code generation")
    print("=" * 60)

    previous_response_id, response_text = ask_llm(
        USER_REQUEST
    )

    print("\n========== INITIAL LLM RESPONSE ==========")
    print(response_text)

    current_code, current_commands, comment, status = (
        parse_response(response_text)
    )

    append_comment(
        1,
        status,
        comment,
    )

    # 初回からDONEならそのまま終了
    if status == "DONE":

        print("\n" + "=" * 60)
        print("[AI DECISION] DONE")
        print("[DONE] User request satisfied.")
        print("[STOP] No further experiment will be executed.")
        print("=" * 60)

        raise SystemExit(0)

    # ========================================================
    # 2. Debug / Repair Loop
    # ========================================================

    for repair_count in range(MAX_REPAIRS + 1):

        generation = repair_count + 1

        print("\n" + "=" * 60)
        print(
            f"[GENERATION {generation}] "
            f"Repair count: {repair_count}/{MAX_REPAIRS}"
        )
        print("=" * 60)

        # ----------------------------------------------------
        # Save current generation
        # ----------------------------------------------------

        save_current_files(
            current_code,
            current_commands,
        )

        save_generation(
            generation,
            current_code,
            current_commands,
        )

        print("\n========== CURRENT CODE ==========")
        print(current_code)

        print("\n========== CURRENT COMMANDS ==========")

        for command in current_commands:
            print(command)

        # ----------------------------------------------------
        # Flash
        # ----------------------------------------------------

        print("\n[FLASH] Flashing generated code...")

        try:
            flash_target(SOURCE_PATH)

            flash_result = "Flash successful."

            print("[FLASH] Success.")

        except Exception as e:

            flash_result = (
                "Flash failed:\n"
                + str(e)
            )

            print("\n========== FLASH ERROR ==========")
            print(flash_result)

            save_debug_log(
                generation,
                flash_result,
            )

            if repair_count >= MAX_REPAIRS:
                print(
                    "\n[STOP] Maximum repair count reached "
                    "during Flash."
                )
                break

            # ------------------------------------------------
            # Flash error -> LLM repair
            # ------------------------------------------------

            debug_packet = build_debug_packet(
                generation,
                current_code,
                current_commands,
                flash_result,
                "FLASH ERROR",
            )

            previous_response_id, response_text = ask_llm(
                debug_packet,
                previous_response_id=previous_response_id,
            )

            print(
                "\n========== REPAIR RESPONSE =========="
            )
            print(response_text)

            (
                new_code,
                new_commands,
                comment,
                status,
            ) = parse_response(response_text)

            append_comment(
                generation,
                status,
                comment,
            )

            print(f"[AI DECISION] {status}")

            if status == "DONE":
                print(
                    "[STOP] DONE received after Flash result."
                )
                break

            current_code = new_code
            current_commands = new_commands

            continue

        # ----------------------------------------------------
        # Run LoopRT
        # ----------------------------------------------------

        print("\n[RUN] Running LoopRT experiment...")

        try:
            result = run_experiment(
                current_commands
            )

            result_type = "LOOPRT RESULT"

        except Exception as e:
            result = (
                "LoopRT ERROR:\n"
                + str(e)
            )

            result_type = "LOOPRT ERROR"

        print("\n========== RAW LOOPRT RESULT ==========")
        print(result)

        # ----------------------------------------------------
        # Save raw result
        # ----------------------------------------------------

        debug_log = (
            f"=== GENERATION {generation} ===\n\n"
            f"=== CODE ===\n"
            f"{current_code}\n\n"
            f"=== COMMANDS ===\n"
            f"{chr(10).join(current_commands)}\n\n"
            f"=== RESULT TYPE ===\n"
            f"{result_type}\n\n"
            f"=== RAW RESULT ===\n"
            f"{result}\n"
        )

        save_debug_log(
            generation,
            debug_log,
        )

        # ----------------------------------------------------
        # Ask LLM to evaluate
        # ----------------------------------------------------

        print("\n[AI] Evaluating experiment result...")

        debug_packet = build_debug_packet(
            generation,
            current_code,
            current_commands,
            result,
            result_type,
        )

        previous_response_id, response_text = ask_llm(
            debug_packet,
            previous_response_id=previous_response_id,
        )

        print(
            "\n========== EVALUATION RESPONSE =========="
        )
        print(response_text)

        # ----------------------------------------------------
        # Parse evaluation
        # ----------------------------------------------------

        (
            new_code,
            new_commands,
            comment,
            status,
        ) = parse_response(response_text)

        append_comment(
            generation,
            status,
            comment,
        )

        print(f"\n[AI DECISION] {status}")

        # ----------------------------------------------------
        # DONE
        # ----------------------------------------------------

        if status == "DONE":

            print("\n" + "=" * 60)
            print("[DONE] User request satisfied.")
            print("[STOP] No further experiment will be executed.")
            print("=" * 60)

            # 現在の最終状態を保存
            save_current_files(
                current_code,
                current_commands,
            )

            break

        # ----------------------------------------------------
        # Invalid status
        # ----------------------------------------------------

        if status != "REPAIR":

            print(
                "\n[ERROR] LLM response did not contain "
                "a valid STATUS."
            )

            print("[STOP] Debug loop stopped.")

            break

        # ----------------------------------------------------
        # Repair limit
        # ----------------------------------------------------

        if repair_count >= MAX_REPAIRS:

            print("\n" + "=" * 60)
            print(
                "[STOP] Maximum repair count reached."
            )
            print("=" * 60)

            break

        # ----------------------------------------------------
        # Apply repair
        # ----------------------------------------------------

        print(
            f"\n[REPAIR] Applying repair "
            f"{repair_count + 1}/{MAX_REPAIRS}."
        )

        current_code = new_code
        current_commands = new_commands

    else:

        print(
            "\n[STOP] Debug loop finished."
        )