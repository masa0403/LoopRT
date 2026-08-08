#include <Arduino.h>

#include "Program.h"

Program::Program()
{
}

void Program::execute(Observer& observer)
{
    while (true)
    {
        Command* command = reader.read();

        command->execute();

        if (command->isPwmInput())
        {
            observer.observePwm();
        }

        Serial.println(F("[DONE]"));

        bool end = command->isEnd();

        delete command;

        if (end)
        {
            Serial.println(F("Experiment End"));
            break;
        }
    }
}