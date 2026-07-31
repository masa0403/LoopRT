#ifndef LOOPRT_COMMAND_READER_H
#define LOOPRT_COMMAND_READER_H

#include "Command.h"

class CommandReader
{
public:
    CommandReader();

    Command* read();

};

#endif
