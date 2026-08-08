#include <Arduino.h>

#include "Command.h"
#include "PinConfig.h"

Command::Command()
    : type(CommandType::None)
{
}

Command::Command(CommandType type)
    : type(type)
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
            delay(1000);
            Serial.println(F("[INFO] Execute Delay"));
            break;

        case CommandType::PinHigh:
            digitalWrite(PinConfig::TARGET_CONTROL_PIN, HIGH);
            Serial.println(F("[INFO] Execute Pin High"));
            break;

        case CommandType::PinLow:
            digitalWrite(PinConfig::TARGET_CONTROL_PIN, LOW);
            Serial.println(F("[INFO] Execute Pin Low"));
            break;

        case CommandType::Pwm:
            int pwmValue = map(value, 0, 100, 0, 255);
            pinMode(PinConfig::PWM_OUTPUT_PIN, OUTPUT);
            analogWrite(PinConfig::PWM_OUTPUT_PIN, pwmValue);
            Serial.print(F("[HOST] PWM D9 "));
            Serial.print(value);
            Serial.println(F("%"));
            break;

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