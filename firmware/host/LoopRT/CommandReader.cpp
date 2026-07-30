#include "CommandReader.h"
#include "Command.h"

CommandReader::CommandReader()
{
}

Command* CommandReader::read()
{
    return new Command();
}
