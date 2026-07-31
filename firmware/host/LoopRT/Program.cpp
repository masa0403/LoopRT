#include "Program.h"

Program::Program()
{
}

void Program::execute()
{
    while (true)
    {
        Command* command = reader.read();

        command->execute();

        bool end = command->isEnd();

        delete command;

        if (end)
        {
            break;
        }
    }
}
