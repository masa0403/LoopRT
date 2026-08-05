#include <Arduino.h>

#include "Experiment.h"

void Experiment::initialize()
{
    Serial.println(F("[INFO] Experiment Initialize"));
}

void Experiment::execute(Observer& observer)
{
    Serial.println(F("[INFO] Experiment Start"));

    program.execute(observer);

    Serial.println(F("[INFO] Experiment Finish"));
}