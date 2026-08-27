def parse_llm_response(response):
    code_start = response.find("===CODE===")
    commands_start = response.find("===COMMANDS===")
    end = response.find("===END===")

    if code_start == -1:
        raise ValueError("===CODE=== not found")

    if commands_start == -1:
        raise ValueError("===COMMANDS=== not found")

    if end == -1:
        raise ValueError("===END=== not found")

    code = response[
        code_start + len("===CODE==="):
        commands_start
    ].strip()

    commands_text = response[
        commands_start + len("===COMMANDS==="):
        end
    ].strip()

    commands = [
        line.strip()
        for line in commands_text.splitlines()
        if line.strip()
    ]

    return code, commands


if __name__ == "__main__":
    test_response = """
===CODE===
#include <avr/io.h>

int main(void) {
    PORTA |= (1 << 6);
    while(1);
}
===COMMANDS===
H(8)
D(500)
I(8)
E
===END===
"""

    code, commands = parse_llm_response(test_response)

    print("========== CODE ==========")
    print(code)

    print()
    print("========== COMMANDS ==========")
    for command in commands:
        print(repr(command))