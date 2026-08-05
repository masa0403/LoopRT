#ifndef LOOPRT_EXPERIMENT_H
#define LOOPRT_EXPERIMENT_H

#include "Program.h"

class Experiment
{
public:

    void initialize();

    void execute(Observer& observer);

private:
    Program program;
};

#endif