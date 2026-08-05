#ifndef LOOPRT_RUNTIME_H
#define LOOPRT_RUNTIME_H

#include "Experiment.h"
#include "Executor.h"
#include "Observer.h"

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
Observer observer;
};

#endif
