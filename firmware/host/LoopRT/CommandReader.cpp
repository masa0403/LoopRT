#include "CommandReader.h"
#include "Command.h"

CommandReader::CommandReader()
    : index(0)
{
}

Command* CommandReader::read()
{
    switch (index++)
    {
        case 0:
            return new Command(CommandType::PinHigh);

        case 1:
            return new Command(CommandType::Delay);

        case 2:
            return new Command(CommandType::PinLow);

        default:
            return new Command(CommandType::End);
    }
}
