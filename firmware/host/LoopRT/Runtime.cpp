#include <Arduino.h>

#include "Runtime.h"
#include "PinConfig.h"

Runtime::Runtime()
{
}

void Runtime::initialize()
{
    Serial.println(F("[INFO] Runtime Initialize"));

    experiment.initialize();

    executor.initialize();

    observer.initialize();
}

void Runtime::run()
{
    pinMode(PinConfig::TARGET_OBSERVER_PIN, INPUT);
    pinMode(PinConfig::TARGET_CONTROL_PIN, OUTPUT);
    pinMode(PinConfig::PWM_OUTPUT_PIN, OUTPUT);

    executor.execute(experiment, observer);
}

void Runtime::shutdown()
{
    executor.shutdown();

    Serial.println(F("[INFO] Runtime Shutdown"));
}