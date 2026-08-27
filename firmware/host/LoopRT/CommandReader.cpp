#include <Arduino.h>

#include "CommandReader.h"
#include "Command.h"

CommandReader::CommandReader()
{
}

/**
 * @brief Serialから1つのCommandを読み取る
 *
 * Command format:
 *
 * H(pin)       GPIO HIGH
 * L(pin)       GPIO LOW
 * P(pin,value) PWM output
 * PI(pin)      PWM input observe
 * D(value)     Delay
 * E            End
 */
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
            // -------------------------------------------------
            // GPIO HIGH
            // H(8)
            // -------------------------------------------------

            case 'H':
            {
                while (Serial.available() == 0)
                {
                }

                char open = Serial.read();

                if (open != '(')
                {
                    return new Command(
                        CommandType::None
                    );
                }

                int pin = Serial.parseInt();

                while (Serial.available() == 0)
                {
                }

                char close = Serial.read();

                if (close != ')')
                {
                    return new Command(
                        CommandType::None
                    );
                }

                return new Command(
                    CommandType::PinHigh,
                    pin,
                    0
                );
            }


            // -------------------------------------------------
            // GPIO LOW
            // L(8)
            // -------------------------------------------------

            case 'L':
            {
                while (Serial.available() == 0)
                {
                }

                char open = Serial.read();

                if (open != '(')
                {
                    return new Command(
                        CommandType::None
                    );
                }

                int pin = Serial.parseInt();

                while (Serial.available() == 0)
                {
                }

                char close = Serial.read();

                if (close != ')')
                {
                    return new Command(
                        CommandType::None
                    );
                }

                return new Command(
                    CommandType::PinLow,
                    pin,
                    0
                );
            }


            // -------------------------------------------------
            // PWM
            // P(9,50)
            // -------------------------------------------------

            case 'P':
            {
                while (Serial.available() == 0)
                {
                }

                char next = Serial.read();

                // ---------------------------------------------
                // PWM Input Observe
                // PI(7)
                // ---------------------------------------------

                if (next == 'I')
                {
                    while (Serial.available() == 0)
                    {
                    }

                    char open = Serial.read();

                    if (open != '(')
                    {
                        return new Command(
                            CommandType::None
                        );
                    }

                    int pin = Serial.parseInt();

                    while (Serial.available() == 0)
                    {
                    }

                    char close = Serial.read();

                    if (close != ')')
                    {
                        return new Command(
                            CommandType::None
                        );
                    }

                    return new Command(
                        CommandType::PwmInput,
                        pin,
                        0
                    );
                }

                // ---------------------------------------------
                // PWM Output
                // P(9,50)
                // ---------------------------------------------

                if (next != '(')
                {
                    return new Command(
                        CommandType::None
                    );
                }

                int pin = Serial.parseInt();

                while (Serial.available() == 0)
                {
                }

                char comma = Serial.read();

                if (comma != ',')
                {
                    return new Command(
                        CommandType::None
                    );
                }

                int value = Serial.parseInt();

                while (Serial.available() == 0)
                {
                }

                char close = Serial.read();

                if (close != ')')
                {
                    return new Command(
                        CommandType::None
                    );
                }

                return new Command(
                    CommandType::Pwm,
                    pin,
                    value
                );
            }

            // -------------------------------------------------
            // GPIO Input
            // I(7)
            // -------------------------------------------------

            case 'I':
            {
                Serial.println(F("[DEBUG] Received I"));

                while (Serial.available() == 0)
                {
                }

                char open = Serial.read();

                Serial.println(F("[DEBUG] Read I argument"));

                if (open != '(')
                {
                    return new Command(
                        CommandType::None
                    );
                }

                int pin = Serial.parseInt();

                Serial.print(F("[DEBUG] I pin = "));
                Serial.println(pin);

                while (Serial.available() == 0)
                {
                }

                char close = Serial.read();

                if (close != ')')
                {
                    return new Command(
                        CommandType::None
                    );
                }

                return new Command(
                    CommandType::Input,
                    pin,
                    0
                );
            }

            // -------------------------------------------------
            // Delay
            // D(500)
            // -------------------------------------------------

            case 'D':
            {
                while (Serial.available() == 0)
                {
                }

                char open = Serial.read();

                if (open != '(')
                {
                    return new Command(
                        CommandType::None
                    );
                }

                int value = Serial.parseInt();

                while (Serial.available() == 0)
                {
                }

                char close = Serial.read();

                if (close != ')')
                {
                    return new Command(
                        CommandType::None
                    );
                }

                return new Command(
                    CommandType::Delay,
                    0,
                    value
                );
            }


            // -------------------------------------------------
            // End
            // E
            // -------------------------------------------------

            case 'E':

                return new Command(
                    CommandType::End
                );


            // -------------------------------------------------
            // 改行
            // -------------------------------------------------

            case '\r':
            case '\n':

                break;


            // -------------------------------------------------
            // Unknown command
            // -------------------------------------------------

            default:

                return new Command(
                    CommandType::None
                );
        }
    }
}