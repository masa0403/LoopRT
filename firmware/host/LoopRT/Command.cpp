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

        case CommandType::PinHigh:
            Serial.println(F("[INFO] Execute Pin High"));
            digitalWrite(13, HIGH);
            break;

        case CommandType::PinLow:
            Serial.println(F("[INFO] Execute Pin Low"));
            digitalWrite(13, LOW);
            break;

        case CommandType::Delay:
            Serial.println(F("[INFO] Execute Delay"));
            delay(1000);
            break;

        case CommandType::End:
            Serial.println(F("[INFO] Execute End"));
            break;
    }
}

bool Command::isEnd() const
{
    return type == CommandType::End;
}
