#include <Arduino.h>

#include "CommandReader.h"
#include "Command.h"

CommandReader::CommandReader()
{
}

Command* CommandReader::read()
{
    while (true)
    {
        while (Serial.available() == 0)
        {
            ;
        }

        char input = Serial.read();

        switch (input)
        {
            case 'H':
                return new Command(CommandType::PinHigh);

            case 'D':
                return new Command(CommandType::Delay);

            case 'L':
                return new Command(CommandType::PinLow);

            case 'E':
                return new Command(CommandType::End);

            case '\r':
            case '\n':
                break;

            default:
                return new Command(CommandType::None);
        }
    }
}