#include "Executor.h"

#include <Arduino.h>

Executor::Executor()
{
}

void Executor::initialize()
{
    Serial.println(F("[INFO] Executor Initialize"));
}

void Executor::execute(Experiment& experiment)
{
    Serial.println(F("[INFO] Execute Experiment"));

    experiment.execute();
}

void Executor::shutdown()
{
    Serial.println(F("[INFO] Executor Shutdown"));
}
