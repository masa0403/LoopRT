#ifndef LOOPRT_RUNTIME_H
#define LOOPRT_RUNTIME_H

#include "Flash.h"

class Runtime
{
public:
    void initialize();
    void shutdown();

private:
    Flash flash;
};

#endif
