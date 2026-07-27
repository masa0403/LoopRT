#ifndef LOOPRT_EXECUTOR_H
#define LOOPRT_EXECUTOR_H

#include "Experiment.h"

class Executor
{
public:

    Executor();

    void initialize();

    void execute(Experiment& experiment);

    void shutdown();
};

#endif
