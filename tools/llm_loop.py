import argparse
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


def save_request(run_dir, user_request):
    """
    Save the original user request for this run.
    """

    path = run_dir / "request.txt"

    path.write_text(
        user_request.strip() + "\n",
        encoding="utf-8",
    )


def load_resume_context(generation_path):
    """
    Load a previous generation as the starting context
    for a new LoopRT run.

    Expected structure:

    runs/
    └── YYYYMMDD_HHMMSS/
        ├── request.txt
        └── generation_04/
            ├── code.c
            ├── commands.txt
            ├── comment.txt
            └── result.txt
    """

    generation_dir = Path(generation_path).expanduser().resolve()

    if not generation_dir.is_dir():
        raise FileNotFoundError(
            f"Generation directory not found: {generation_dir}"
        )

    run_dir = generation_dir.parent
    request_path = run_dir / "request.txt"

    required_files = {
        "request": request_path,
        "code": generation_dir / "code.c",
        "commands": generation_dir / "commands.txt",
        "comment": generation_dir / "comment.txt",
        "result": generation_dir / "result.txt",
    }

    for name, path in required_files.items():
        if not path.is_file():
            raise FileNotFoundError(
                f"Required resume file not found ({name}): {path}"
            )

    context = {
        name: path.read_text(encoding="utf-8")
        for name, path in required_files.items()
    }

    context["generation_dir"] = generation_dir

    return context


def build_resume_prompt(context):
    """
    Build the initial prompt for resuming from a previous generation.
    """

    return f"""
You are continuing a previous LoopRT hardware experiment.

This is a new run. Use the previous files as the starting context.
Do not restart the task from scratch.

=== ORIGINAL USER REQUEST ===

{context["request"]}

=== PREVIOUS C CODE ===

{context["code"]}

=== PREVIOUS LOOPRT COMMANDS ===

{context["commands"]}

=== PREVIOUS LLM COMMENT ===

{context["comment"]}

=== PREVIOUS EXPERIMENT RESULT ===

{context["result"]}

=== TASK ===

Continue development from the previous generation.

Use the previous code and commands as the starting point.
Analyze the previous comment and raw experiment result.
Preserve working parts and make only necessary changes.

The previous experiment may have failed or reached the repair limit.
Do not assume the requested behavior has been verified.

Generate the complete C code and complete LoopRT command sequence
for the next experiment.

The next experiment must be executed on real hardware before
the task can be declared complete.

Your response MUST use exactly this structure:

===CODE===
full C code
===COMMANDS===
one LoopRT command per line
===COMMENT===
brief explanation of the previous result and the changes
===STATUS===
REPAIR
===END===

Return REPAIR so the normal LoopRT experiment loop executes.
Do not declare DONE before the next hardware experiment.
"""


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
    user_request,
    code,
    commands,
    result_type,
    raw_result,
):
    return f"""
GENERATION: {generation}

USER_REQUEST:
{user_request}

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
Follow the instructions in the COMMENT GUIDELINES section below.
===STATUS===
DONE or REPAIR
===END===


[COMMENT GUIDELINES]

Write a concise, structured development report using the following sections in order.
Keep each section brief and avoid repeating the code or full experiment logs.

[Objective]
State the overall goal and what the current experiment is intended to verify.

[Changes]
Summarize the important implementation changes in this generation.

[Results]
Summarize actual experiment results, including measured values when available.
Clearly distinguish measured facts from assumptions.

[Assessment]
State what has been verified, what remains unverified, and any detected problems.
Do not claim success without sufficient experimental evidence.

[Development Plan]
Maintain a concise, ordered list of implementation and verification steps.
For each step, include an ID, a short description, and one status:
NOT_STARTED, IN_PROGRESS, IMPLEMENTED, VERIFIED, or BLOCKED.

Preserve the existing plan across generations.
Update statuses only when supported by implementation or experimental evidence.
Keep completed steps when they are important for understanding the current state.

[Current Step]
Identify the step being worked on and briefly explain why it is the appropriate next step.

[Next Action]
Specify the single most useful next implementation or experiment.
If the current goal has been achieved and adequately verified, state that no further action is required.

[Verification Criteria]
State the observable conditions required to consider the current step complete.
Use measurable criteria where possible.

[General Rules]
- Treat the user's original request as the overall project goal.
- Prefer incremental, testable changes over implementing the entire project at once.
- Diagnose failures before making unrelated changes.
- If observations are insufficient to identify the cause, propose the smallest experiment that can distinguish between plausible causes.
- Preserve previously verified functionality unless changing it is necessary.
- Never mark a step VERIFIED merely because code was generated or compiled. Require relevant experimental evidence.
- Treat timeouts and missing observations as inconclusive unless other evidence supports a specific interpretation.
- Use the previous generation's COMMENT as context when available.
- Keep the report compact and understandable without relying on unstated assumptions.
- Do not invent results, measurements, or verification evidence.
"""


# ============================================================
# Main
# ============================================================

def main():

    # --------------------------------------------------------
    # Parse arguments
    # --------------------------------------------------------

    parser = argparse.ArgumentParser(
        description="LoopRT LLM development loop"
    )

    parser.add_argument(
        "resume_generation",
        nargs="?",
        help=(
            "Path to a previous generation directory. "
            "Example: runs/20261011_214148/generation_04"
        ),
    )

    args = parser.parse_args()

    # --------------------------------------------------------
    # Load initial context
    # --------------------------------------------------------

    if args.resume_generation:
        context = load_resume_context(
            args.resume_generation
        )

        user_request = context["request"].strip()

        initial_input = build_resume_prompt(context)

        print("[INFO] Resuming from previous generation:")
        print(context["generation_dir"])

    else:
        user_request = USER_REQUEST
        initial_input = USER_REQUEST

    # --------------------------------------------------------
    # Create new run
    # --------------------------------------------------------

    run_dir = create_run_directory()

    save_request(
        run_dir,
        user_request,
    )

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

    response = ask_llm(initial_input)

    previous_response_id = response.id

    code, commands, comment, status = parse_response(
        response.output_text
    )

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
                user_request,
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
                user_request,
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
            user_request,
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