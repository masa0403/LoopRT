#ifndef LOOPRT_PROGRAM_H
#define LOOPRT_PROGRAM_H

#include "CommandReader.h"
#include "Observer.h"

class Program
{
public:

    Program();

    void execute(Observer& observer);

private:

    CommandReader reader;
};

#endif