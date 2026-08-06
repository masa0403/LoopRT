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


void Observer::observePwm()
{
    Serial.println(F("[OBSERVE] PWM Start"));

    // ---------------------------------------------------------
    // LOWになるまで待つ
    // ---------------------------------------------------------
    while (digitalRead(7) == HIGH)
    {
    }

    // ---------------------------------------------------------
    // LOW開始
    // ---------------------------------------------------------
    while (digitalRead(7) == LOW)
    {
    }

    unsigned long highStart = micros();

    // ---------------------------------------------------------
    // HIGH終了
    // ---------------------------------------------------------
    while (digitalRead(7) == HIGH)
    {
    }

    unsigned long lowStart = micros();

    // ---------------------------------------------------------
    // 次のHIGH開始
    // ---------------------------------------------------------
    while (digitalRead(7) == LOW)
    {
    }

    unsigned long nextHighStart = micros();

    unsigned long highTime =
        lowStart - highStart;

    unsigned long period =
        nextHighStart - highStart;

    if (period == 0)
    {
        Serial.println(F("[OBSERVE] PWM Invalid"));
        return;
    }

    float duty =
        (float)highTime /
        (float)period *
        100.0;

    float frequency =
        1000000.0 /
        (float)period;

    Serial.print(F("[OBSERVE] PWM Period: "));
    Serial.print(period);
    Serial.println(F(" us"));

    Serial.print(F("[OBSERVE] PWM Duty: "));
    Serial.print(duty);
    Serial.println(F(" %"));

    Serial.print(F("[OBSERVE] PWM Frequency: "));
    Serial.print(frequency);
    Serial.println(F(" Hz"));
}