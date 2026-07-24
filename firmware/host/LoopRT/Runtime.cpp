#include <Arduino.h>
#include "Runtime.h"
void Runtime::initialize()
{
    Serial.println("[INFO] Runtime Initialize");

    flash.initialize();

    experiment.initialize();

    experiment.execute();
}

void Runtime::shutdown()
{
    Serial.println("[INFO] Runtime Shutdown");
}
