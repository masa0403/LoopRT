#ifndef LOOPRT_RUNTIME_H
#define LOOPRT_RUNTIME_H

#include "Experiment.h"
#include "Executor.h"

class Runtime
{
public:
    Runtime();

    void initialize();
    void run();
    void shutdown();

private:
    Experiment experiment;
    Executor executor;
};

#endif