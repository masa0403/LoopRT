#include <Arduino.h>

#include "Command.h"

Command::Command()
    : type(CommandType::None),
      pin(0),
      value(0)
{
}

Command::Command(CommandType type)
    : type(type),
      pin(0),
      value(0)
{
}

Command::Command(
    CommandType type,
    int pin,
    int value
)
    : type(type),
      pin(pin),
      value(value)
{
}

/**
 * @brief 命令を実行する
 */
void Command::execute()
{
    switch (type)
    {
        case CommandType::None:

            Serial.println(F("[INFO] Execute Command"));

            break;


        case CommandType::Delay:

            Serial.print(F("[INFO] Execute Delay: "));
            Serial.print(value);
            Serial.println(F(" ms"));

            delay(value);

            break;


        case CommandType::PinHigh:

            pinMode(pin, OUTPUT);

            digitalWrite(
                pin,
                HIGH
            );

            Serial.print(F("[HOST] GPIO D"));
            Serial.print(pin);
            Serial.println(F(" HIGH"));

            break;


        case CommandType::PinLow:

            pinMode(pin, OUTPUT);

            digitalWrite(
                pin,
                LOW
            );

            Serial.print(F("[HOST] GPIO D"));
            Serial.print(pin);
            Serial.println(F(" LOW"));

            break;


        case CommandType::Pwm:
        {
            int pwmValue = map(
                value,
                0,
                100,
                0,
                255
            );

            pinMode(
                pin,
                OUTPUT
            );

            analogWrite(
                pin,
                pwmValue
            );

            Serial.print(F("[HOST] PWM D"));
            Serial.print(pin);
            Serial.print(F(" "));
            Serial.print(value);
            Serial.println(F("%"));

            break;
        }


        case CommandType::PwmInput:

            Serial.print(
                F("[INFO] Execute PWM Input Observe D")
            );

            Serial.println(pin);

            break;


        case CommandType::End:

            Serial.println(
                F("[INFO] Execute End")
            );

            break;
    }
}

/**
 * @brief Commandが終了命令か判定する
 */
bool Command::isEnd()
{
    return type == CommandType::End;
}

/**
 * @brief CommandがPWM入力命令か判定する
 */
bool Command::isPwmInput()
{
    return type == CommandType::PwmInput;
}

int Command::getPin() const
{
    return pin;
}