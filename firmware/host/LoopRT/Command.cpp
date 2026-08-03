#include <Arduino.h>

#include "Command.h"

Command::Command()
    : type(CommandType::None)
{
}

Command::Command(CommandType type)
    : type(type)
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
            digitalWrite(13, HIGH);
            Serial.println(F("[INFO] Execute Pin High"));
            break;

        case CommandType::PinLow:
            digitalWrite(13, LOW);
            Serial.println(F("[INFO] Execute Pin Low"));
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