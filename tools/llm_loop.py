from pathlib import Path
from datetime import datetime

from openai import OpenAI

from target import flash_target
from looprt import send_commands
from nano_port import detect_nano_port
from prompts2 import SYSTEM_PROMPT, USER_REQUEST


# ============================================================
# Configuration
# ============================================================

MODEL = "gpt-5.6-luna"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = PROJECT_ROOT / "runs"

MAX_REPAIRS = 10


# ============================================================
# OpenAI
# ============================================================

client = OpenAI()


def ask_llm(user_input, previous_response_id=None):
    response = client.responses.create(
        model=MODEL,
        instructions=SYSTEM_PROMPT,
        input=user_input,
        previous_response_id=previous_response_id,
    )

    return response

# ============================================================
# RUN Experiment
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
# Response Parser
# ============================================================

def parse_response(text):
    """
    LLM response:

    ===CODE===
    ...
    ===COMMANDS===
    ...
    ===COMMENT===
    ...
    ===STATUS===
    DONE / REPAIR
    ===END===
    """

    status_start = text.find("===STATUS===")
    end_marker = text.find("===END===")

    if status_start == -1:
        raise RuntimeError("LLM response missing ===STATUS===")

    if end_marker == -1:
        raise RuntimeError("LLM response missing ===END===")

    status = text[
        status_start + len("===STATUS==="):end_marker
    ].strip()

    # --------------------------------------------------------
    # COMMENT
    # --------------------------------------------------------

    comment = ""

    comment_start = text.find("===COMMENT===")

    if comment_start != -1:
        comment_end = text.find("===STATUS===")

        if comment_end != -1:
            comment = text[
                comment_start + len("===COMMENT==="):comment_end
            ].strip()

    # --------------------------------------------------------
    # DONE
    # --------------------------------------------------------

    if status == "DONE":
        return None, None, comment, "DONE"

    # --------------------------------------------------------
    # REPAIR
    # --------------------------------------------------------

    if status != "REPAIR":
        raise RuntimeError(
            f"Unknown LLM status: {status}"
        )

    code_start = text.find("===CODE===")
    commands_start = text.find("===COMMANDS===")

    if code_start == -1:
        raise RuntimeError(
            "LLM REPAIR response missing ===CODE==="
        )

    if commands_start == -1:
        raise RuntimeError(
            "LLM REPAIR response missing ===COMMANDS==="
        )

    code = text[
        code_start + len("===CODE==="):commands_start
    ].strip()

    commands_end = text.find("===COMMENT===")

    if commands_end == -1:
        commands_end = text.find("===STATUS===")

    commands = text[
        commands_start + len("===COMMANDS==="):commands_end
    ].strip()

    # --------------------------------------------------------
    # Remove markdown code fences if LLM added them
    # --------------------------------------------------------

    if code.startswith("```"):
        lines = code.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        code = "\n".join(lines).strip()

    command_list = []

    for line in commands.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith("```"):
            continue

        command_list.append(line)

    return code, command_list, comment, "REPAIR"


# ============================================================
# Run / Generation Directory
# ============================================================

def create_run_directory():
    """
    Create:

    runs/
    └── YYYYMMDD_HHMMSS/
    """

    RUNS_DIR.mkdir(exist_ok=True)

    run_name = datetime.now().strftime("%Y%m%d_%H%M%S")

    run_dir = RUNS_DIR / run_name

    run_dir.mkdir(parents=True, exist_ok=False)

    return run_dir


def save_request(run_dir):
    """
    Save the original USER_REQUEST.
    """

    path = run_dir / "request.txt"

    path.write_text(
        USER_REQUEST.strip() + "\n",
        encoding="utf-8",
    )


def create_generation_directory(run_dir, generation):
    """
    Create:

    generation_01/
    generation_02/
    ...
    """

    generation_dir = (
        run_dir / f"generation_{generation:02d}"
    )

    generation_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    return generation_dir


def save_generation_files(
    generation_dir,
    code,
    commands,
):
    """
    Save the code and LoopRT commands belonging
    to this generation.
    """

    code_path = generation_dir / "code.c"
    commands_path = generation_dir / "commands.txt"

    code_path.write_text(
        code + "\n",
        encoding="utf-8",
    )

    commands_path.write_text(
        "\n".join(commands) + "\n",
        encoding="utf-8",
    )


def save_result(generation_dir, result):
    """
    Save the raw result of the generation.

    This can contain:
    - compiler error
    - flash error
    - LoopRT experiment log
    """

    path = generation_dir / "result.txt"

    path.write_text(
        result.rstrip() + "\n",
        encoding="utf-8",
    )


def save_comment(generation_dir, comment):
    """
    Save the LLM's judgment for this generation.
    """

    path = generation_dir / "comment.txt"

    path.write_text(
        comment.strip() + "\n",
        encoding="utf-8",
    )


# ============================================================
# Debug Packet
# ============================================================

def build_debug_packet(
    generation,
    code,
    commands,
    result_type,
    raw_result,
):
    return f"""
GENERATION: {generation}

USER_REQUEST:
{USER_REQUEST}

CURRENT CODE:
===CODE===
{code}

CURRENT COMMANDS:
===COMMANDS===
{chr(10).join(commands)}

RESULT TYPE:
{result_type}

RAW RESULT:
===RESULT===
{raw_result}

============================================================
TASK
============================================================

Judge the experiment result against USER_REQUEST.

You must determine whether the requested behavior has been
successfully verified on the real hardware.

Consider:

- Whether the generated C code compiled successfully.
- Whether the target MCU was flashed successfully.
- Whether the LoopRT experiment actually executed.
- Whether the observed hardware behavior matches USER_REQUEST.
- Whether the timing behavior is correct.
- Whether input/output behavior is correct.
- Whether special conditions such as ignored inputs were
  actually verified.
- Whether the result is merely a normal operation result,
  or evidence of an abnormal/error condition.
- Whether the current result is sufficient to declare DONE.

If the requested behavior is not yet sufficiently verified,
make the smallest necessary correction.

If repair is required, output the COMPLETE corrected C code
and COMPLETE LoopRT command sequence.

Do not omit unchanged code.

Your response MUST use exactly this structure:

===CODE===
full C code
===COMMANDS===
one LoopRT command per line
===COMMENT===
concise explanation of the result and any required change
===STATUS===
DONE or REPAIR
===END===
"""


# ============================================================
# Main
# ============================================================

def main():

    # --------------------------------------------------------
    # Create run
    # --------------------------------------------------------

    run_dir = create_run_directory()

    save_request(run_dir)

    print()
    print("============================================================")
    print("LoopRT LLM Loop")
    print("============================================================")
    print(f"[RUN] {run_dir}")
    print()

    # --------------------------------------------------------
    # Initial generation
    # --------------------------------------------------------

    print("[INFO] Sending initial request to LLM...")

    response = ask_llm(USER_REQUEST)

    previous_response_id = response.id

    code, commands, comment, status = parse_response(
        response.output_text
    )

    # --------------------------------------------------------
    # Initial DONE
    # --------------------------------------------------------

    if status == "DONE":
        generation_dir = create_generation_directory(
            run_dir,
            1,
        )

        save_generation_files(
            generation_dir,
            "",
            [],
        )

        save_result(
            generation_dir,
            "No experiment executed. LLM returned DONE.",
        )

        save_comment(
            generation_dir,
            comment,
        )

        print("[DONE] LLM returned DONE.")
        return

    # --------------------------------------------------------
    # Generation loop
    # --------------------------------------------------------

    for repair_count in range(MAX_REPAIRS + 1):

        generation = repair_count + 1

        print()
        print("============================================================")
        print(f"[GENERATION {generation:02d}]")
        print("============================================================")

        # ----------------------------------------------------
        # Create generation directory
        # ----------------------------------------------------

        generation_dir = create_generation_directory(
            run_dir,
            generation,
        )

        # ----------------------------------------------------
        # Save code / commands for this generation
        # ----------------------------------------------------

        save_generation_files(
            generation_dir,
            code,
            commands,
        )

        print(
            f"[SAVE] {generation_dir / 'code.c'}"
        )

        print(
            f"[SAVE] {generation_dir / 'commands.txt'}"
        )

        # ----------------------------------------------------
        # Flash
        # ----------------------------------------------------

        print()
        print("[INFO] Flashing target...")

        try:
            flash_target(generation_dir / "code.c")

        except Exception as e:

            error_text = str(e)

            print()
            print("[ERROR] Flash failed:")
            print(error_text)

            # -----------------------------------------------
            # Save flash result
            # -----------------------------------------------

            save_result(
                generation_dir,
                error_text,
            )

            # -----------------------------------------------
            # Ask LLM to repair
            # -----------------------------------------------

            debug_packet = build_debug_packet(
                generation,
                code,
                commands,
                "FLASH_ERROR",
                error_text,
            )

            print()
            print("[INFO] Sending flash error to LLM...")

            response = ask_llm(
                debug_packet,
                previous_response_id,
            )

            previous_response_id = response.id

            (
                new_code,
                new_commands,
                new_comment,
                new_status,
            ) = parse_response(
                response.output_text
            )

            # -----------------------------------------------
            # Save LLM judgment for THIS generation
            # -----------------------------------------------

            save_comment(
                generation_dir,
                new_comment,
            )

            print(
                f"[SAVE] {generation_dir / 'result.txt'}"
            )

            print(
                f"[SAVE] {generation_dir / 'comment.txt'}"
            )

            # -----------------------------------------------
            # DONE
            # -----------------------------------------------

            if new_status == "DONE":

                print()
                print("[DONE] LLM judged the task complete.")
                break

            # -----------------------------------------------
            # REPAIR
            # -----------------------------------------------

            code = new_code
            commands = new_commands

            continue

        # ----------------------------------------------------
        # Flash succeeded
        # ----------------------------------------------------

        print("[INFO] Flash succeeded.")

        # ----------------------------------------------------
        # Detect Nano
        # ----------------------------------------------------

        try:
            port = detect_nano_port()

        except Exception as e:

            error_text = str(e)

            print()
            print("[ERROR] Nano detection failed:")
            print(error_text)

            save_result(
                generation_dir,
                error_text,
            )

            debug_packet = build_debug_packet(
                generation,
                code,
                commands,
                "HOST_ERROR",
                error_text,
            )

            print()
            print("[INFO] Sending host error to LLM...")

            response = ask_llm(
                debug_packet,
                previous_response_id,
            )

            previous_response_id = response.id

            (
                new_code,
                new_commands,
                new_comment,
                new_status,
            ) = parse_response(
                response.output_text
            )

            save_comment(
                generation_dir,
                new_comment,
            )

            if new_status == "DONE":

                print()
                print("[DONE] LLM judged the task complete.")
                break

            code = new_code
            commands = new_commands

            continue

        # ----------------------------------------------------
        # Run LoopRT experiment
        # ----------------------------------------------------

        print()
        print("[INFO] Running LoopRT experiment...")
        print()

        try:
            result = run_experiment(commands)

            # Convert result to string if necessary
            if not isinstance(result, str):
                result_text = str(result)
            else:
                result_text = result

        except Exception as e:

            result_text = str(e)

            print()
            print("[ERROR] LoopRT experiment failed:")
            print(result_text)

            result_type = "LOOPRT_ERROR"

        else:

            result_type = "LOOPRT_RESULT"

        # ----------------------------------------------------
        # Save raw experiment result
        # ----------------------------------------------------

        save_result(
            generation_dir,
            result_text,
        )

        print()
        print(
            f"[SAVE] {generation_dir / 'result.txt'}"
        )

        # ----------------------------------------------------
        # Show result
        # ----------------------------------------------------

        print()
        print("========== LOOPRT RESULT ==========")
        print(result_text)
        print("====================================")

        # ----------------------------------------------------
        # Ask LLM to judge result
        # ----------------------------------------------------

        debug_packet = build_debug_packet(
            generation,
            code,
            commands,
            result_type,
            result_text,
        )

        print()
        print("[INFO] Sending experiment result to LLM...")

        response = ask_llm(
            debug_packet,
            previous_response_id,
        )

        previous_response_id = response.id

        (
            new_code,
            new_commands,
            new_comment,
            new_status,
        ) = parse_response(
            response.output_text
        )

        # ----------------------------------------------------
        # Save LLM judgment
        # ----------------------------------------------------

        save_comment(
            generation_dir,
            new_comment,
        )

        print(
            f"[SAVE] {generation_dir / 'comment.txt'}"
        )

        # ----------------------------------------------------
        # DONE
        # ----------------------------------------------------

        if new_status == "DONE":

            print()
            print("============================================================")
            print("[DONE] LoopRT experiment completed.")
            print("============================================================")
            print()
            print(f"[RUN] Results saved to:")
            print(run_dir)
            print()
            print()
            print("Complete!")
            print()

            break

        # ----------------------------------------------------
        # REPAIR
        # ----------------------------------------------------

        print()
        print("[REPAIR] LLM requested another generation.")

        code = new_code
        commands = new_commands

    else:

        print()
        print("============================================================")
        print("[STOP] Maximum repair count reached.")
        print("============================================================")
        print()
        print(f"[RUN] Results saved to:")
        print(run_dir)


if __name__ == "__main__":
    main()