#include <Arduino.h>

#include "Runtime.h"

Runtime::Runtime()
{
}

void Runtime::initialize()
{
    Serial.println(F("[INFO] Runtime Initialize"));

    pinMode(13, OUTPUT);

    flash.initialize();

    experiment.initialize();

    executor.initialize();
}

void Runtime::run()
{
    executor.execute(experiment);
}

void Runtime::shutdown()
{
    executor.shutdown();

    Serial.println(F("[INFO] Runtime Shutdown"));
}