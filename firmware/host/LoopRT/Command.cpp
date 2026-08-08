#include <Arduino.h>

#include "Command.h"
#include "PinConfig.h"

Command::Command()
    : type(CommandType::None),
      value(0)
{
}

Command::Command(CommandType type)
    : type(type),
      value(0)
{
}

Command::Command(CommandType type, int value)
    : type(type),
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
            pinMode(PinConfig::TARGET_PA3, OUTPUT);
            digitalWrite(PinConfig::TARGET_PA3, HIGH);

            Serial.println(F("[HOST] GPIO PA3 (D8) HIGH"));
            break;

        case CommandType::PinLow:
            pinMode(PinConfig::TARGET_PA3, OUTPUT);
            digitalWrite(PinConfig::TARGET_PA3, LOW);

            Serial.println(F("[HOST] GPIO PA3 (D8) LOW"));
            break;

        case CommandType::Pwm:
        {
            int pwmValue = map(value, 0, 100, 0, 255);

            pinMode(PinConfig::TARGET_PA6, OUTPUT);
            analogWrite(PinConfig::TARGET_PA6, pwmValue);

            Serial.print(F("[HOST] PWM PA6 (D9) "));
            Serial.print(value);
            Serial.println(F("%"));

            break;
        }

        case CommandType::PwmInput:
            Serial.println(F("[INFO] Execute PWM Input Observe"));
            break;

        case CommandType::End:
            Serial.println(F("[INFO] Execute End"));
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

