#include <Arduino.h>
#include "Runtime.h"

/**
 * @brief Runtimeを初期化する
 *
 * 現在は起動ログのみ出力する。
 */
void Runtime::initialize()
{
    Serial.println("[INFO] Runtime Initialize");
}

/**
 * @brief Runtimeを終了する
 *
 * 現在は終了ログのみ出力する。
 */
void Runtime::shutdown()
{
    Serial.println("[INFO] Runtime Shutdown");
}
