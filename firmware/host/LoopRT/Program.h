#ifndef LOOPRT_PROGRAM_H
#define LOOPRT_PROGRAM_H

#include "CommandReader.h"

class Program
{
public:

    Program();

    void execute();

private:

    CommandReader reader;
};

#endif
