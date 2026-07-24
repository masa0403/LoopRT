#include <Arduino.h>
#include "Command.h"

/**
 * @brief ダミー命令を実行する
 */
void Command::execute()
{
    Serial.println("[INFO] Execute Command");
}
