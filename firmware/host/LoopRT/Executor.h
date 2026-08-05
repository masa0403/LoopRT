#ifndef LOOPRT_EXECUTOR_H
#define LOOPRT_EXECUTOR_H

#include "Experiment.h"
#include "Observer.h"

class Executor
{
public:

    Executor();

    void initialize();

    void execute(Experiment& experiment, Observer& observer);

    void shutdown();
};

#endif