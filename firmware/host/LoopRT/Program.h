#ifndef LOOPRT_COMMANDLIST_H
#define LOOPRT_COMMANDLIST_H

#include "CommandReader.h"

class Program
{
public:

    void execute();

private:

    CommandReader reader;
};

#endif
