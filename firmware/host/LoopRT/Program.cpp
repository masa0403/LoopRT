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

        // Command実行直後のTarget MCU状態を観測
        observer.readPin();

        bool end = command->isEnd();

        delete command;

        if (end)
        {
            Serial.println(F("[RESULT] OK"));
            break;
        }
    }
}