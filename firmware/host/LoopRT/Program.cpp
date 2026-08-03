#include <Arduino.h>

#include "Program.h"

Program::Program()
{
}

void Program::execute()
{
    while (true)
    {
        Command* command = reader.read();

        command->execute();

        bool end = command->isEnd();

        delete command;

        if (end)
        {
            int state = digitalRead(13);

            if (state == HIGH)
            {
                Serial.println(F("[RESULT] D13 HIGH"));
            }
            else
            {
                Serial.println(F("[RESULT] D13 LOW"));
            }

            break;
        }
    }
}