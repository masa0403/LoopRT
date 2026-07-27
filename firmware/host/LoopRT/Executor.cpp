#include "Executor.h"

#include <Arduino.h>

Executor::Executor()
{
}

void Executor::initialize()
{
    Serial.println(F("[INFO] Executor Initialize"));
}

void Executor::shutdown()
{
    Serial.println(F("[INFO] Executor Shutdown"));
}
