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

            case 'P':
            {
                while (Serial.available() == 0)
                {
                }

                char open = Serial.read();

                if (open != '(')
                {
                    return new Command(CommandType::None);
                }

                while (Serial.available() == 0)
                {
                }

                char first = Serial.peek();

                if (first == 'i')
                {
                    Serial.read();

                    while (Serial.available() == 0)
                    {
                    }

                    char close = Serial.read();

                    if (close != ')')
                    {
                        return new Command(CommandType::None);
                    }

                    return new Command(CommandType::PwmInput);
                }

                int value = Serial.parseInt();

                while (Serial.available() == 0)
                {
                }

                char close = Serial.read();

                if (close != ')')
                {
                    return new Command(CommandType::None);
                }

                return new Command(
                    CommandType::Pwm,
                    value
                );
            }

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