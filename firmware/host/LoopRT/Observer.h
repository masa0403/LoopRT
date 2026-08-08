#ifndef OBSERVER_H
#define OBSERVER_H

class Observer
{
public:

    Observer();

    void initialize();

    int readPin(int pin);

    void observePwm(int pin);
};

#endif