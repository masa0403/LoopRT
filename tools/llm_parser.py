def parse_llm_response(response):

    code_marker = "===CODE==="
    commands_marker = "===COMMANDS==="
    end_marker = "===END==="

    code_start = response.find(code_marker)
    commands_start = response.find(commands_marker)

    if code_start == -1:
        raise ValueError("===CODE=== not found")

    if commands_start == -1:
        raise ValueError("===COMMANDS=== not found")

    if commands_start <= code_start:
        raise ValueError(
            "===COMMANDS=== appears before ===CODE==="
        )

    end = response.find(
        end_marker,
        commands_start + len(commands_marker),
    )

    # -------------------------------------------------
    # Code
    # -------------------------------------------------

    code = response[
        code_start + len(code_marker):
        commands_start
    ].strip()

    # -------------------------------------------------
    # Commands
    # -------------------------------------------------

    if end == -1:

        print(
            "[WARN] ===END=== not found. "
            "Using end of response."
        )

        commands_text = response[
            commands_start + len(commands_marker):
        ].strip()

    else:

        commands_text = response[
            commands_start + len(commands_marker):
            end
        ].strip()

    commands = [
        line.strip()
        for line in commands_text.splitlines()
        if line.strip()
    ]

    # -------------------------------------------------
    # Basic Validation
    # -------------------------------------------------

    if not code:
        raise ValueError("Generated C code is empty")

    if not commands:
        raise ValueError("Generated commands are empty")

    return code, commands


if __name__ == "__main__":

    test_response = """
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
===COMMANDS===
I(9)
E
"""

    code, commands = parse_llm_response(test_response)

    print("========== CODE ==========")
    print(code)

    print()
    print("========== COMMANDS ==========")

    for command in commands:
        print(repr(command))