#ifndef LOOPRT_RUNTIME_H
#define LOOPRT_RUNTIME_H

#include "Flash.h"
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
    Flash flash;
    Experiment experiment;
    Executor executor;
};

#endif
