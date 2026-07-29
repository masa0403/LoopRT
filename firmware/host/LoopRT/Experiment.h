#ifndef LOOPRT_EXPERIMENT_H
#define LOOPRT_EXPERIMENT_H

#include "CommandList.h"

class Experiment
{
public:

    void initialize();

    void execute();

private:
    CommandList commands;
};

#endif
