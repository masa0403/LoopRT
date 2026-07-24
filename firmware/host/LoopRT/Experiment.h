#ifndef LOOPRT_EXPERIMENT_H
#define LOOPRT_EXPERIMENT_H

#include "Command.h"

class Experiment
{
public:

    void initialize();

    void execute();

private:
    Command command;
};

#endif
