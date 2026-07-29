#ifndef LOOPRT_COMMANDLIST_H
#define LOOPRT_COMMANDLIST_H

#include "Command.h"

class CommandList
{
public:

    void execute();

private:

    Command command;
};

#endif
