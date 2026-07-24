#include <Arduino.h>
#include "Runtime.h"

void Runtime::initialize()
{
    Serial.println("[Info] Runtime Initialize");

    flash.initialize();
}

void Runtime::shutdown()
{
    Serial.println("[Info] Runtime Shutdown");
}
