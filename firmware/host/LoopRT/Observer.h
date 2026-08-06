#ifndef LOOPRT_OBSERVER_H
#define LOOPRT_OBSERVER_H

class Observer
{
public:

    Observer();

    void initialize();

    int readPin();

    void observePwm();
};

#endif