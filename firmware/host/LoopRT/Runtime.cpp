#include <Arduino.h>

#include "Runtime.h"

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
    // D7 = Target MCU PA3からの観測入力
    pinMode(7, INPUT);
    pinMode(8, OUTPUT);

    executor.execute(experiment, observer);
}

void Runtime::shutdown()
{
executor.shutdown();

Serial.println(F("[INFO] Runtime Shutdown"));

}
