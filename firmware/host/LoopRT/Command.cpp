#include <Arduino.h>

#include "Command.h"

Command::Command()
    : type(CommandType::None)
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
            Serial.println(F("[INFO] Execute Delay"));
            break;

        case CommandType::GpioWrite:
            Serial.println(F("[INFO] Execute GPIO Write"));
            break;
    }
}
