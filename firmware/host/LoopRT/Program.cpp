#include "Program.h"

void Program::execute()
{
    Command* command = reader.read();

    command->execute();

    delete command;
}
