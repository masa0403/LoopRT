#include <Arduino.h>

#include "Observer.h"
#include "PinConfig.h"

Observer::Observer()
{
}

/**
 * @brief Observerを初期化する
 */
void Observer::initialize()
{
    Serial.println(F("[INFO] Observer Initialize"));
}

/**
 * @brief Observer対象ピンの状態を読む
 */
int Observer::readPin()
{
    int state = digitalRead(PinConfig::OBSERVER_PIN);

    if (state == HIGH)
    {
        Serial.print(F("[OBSERVE] D"));
        Serial.print(PinConfig::OBSERVER_PIN);
        Serial.println(F(" HIGH"));
    }
    else
    {
        Serial.print(F("[OBSERVE] D"));
        Serial.print(PinConfig::OBSERVER_PIN);
        Serial.println(F(" LOW"));
    }

    return state;
}