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
    int state = digitalRead(PinConfig::TARGET_OBSERVER_PIN);

    if (state == HIGH)
    {
        Serial.print(F("[OBSERVE] D"));
        Serial.print(PinConfig::TARGET_OBSERVER_PIN);
        Serial.println(F(" HIGH"));
    }
    else
    {
        Serial.print(F("[OBSERVE] D"));
        Serial.print(PinConfig::TARGET_OBSERVER_PIN);
        Serial.println(F(" LOW"));
    }

    return state;
}

/**
 * @brief PWM信号を一定時間連続観測する
 *
 * 500msの間、PWMの各周期を測定し、
 * Duty / Period / Frequencyの安定性を記録する。
 */
void Observer::observePwm()
{
    const unsigned long OBSERVE_TIME_US = 500000;
    const unsigned long TIMEOUT_US = 100000;

    Serial.print(F("[TARGET] PWM Observe D"));
    Serial.println(PinConfig::TARGET_OBSERVER_PIN);

    Serial.println(F("[TARGET] PWM Observation: 500 ms"));

    // ---------------------------------------------------------
    // 最初のLOWを待つ
    // ---------------------------------------------------------

    unsigned long startWait = micros();

    while (digitalRead(PinConfig::TARGET_OBSERVER_PIN) == HIGH)
    {
        if (micros() - startWait >= TIMEOUT_US)
        {
            Serial.println(F("[TARGET] PWM Timeout"));
            return;
        }
    }

    // ---------------------------------------------------------
    // 最初のHIGHを待つ
    // ---------------------------------------------------------

    startWait = micros();

    while (digitalRead(PinConfig::TARGET_OBSERVER_PIN) == LOW)
    {
        if (micros() - startWait >= TIMEOUT_US)
        {
            Serial.println(F("[TARGET] PWM Timeout"));
            return;
        }
    }

    unsigned long observationStart = micros();

    // ---------------------------------------------------------
    // 統計値
    // ---------------------------------------------------------

    unsigned long cycleCount = 0;

    unsigned long dutySum = 0;
    unsigned long periodSum = 0;
    unsigned long frequencySum = 0;

    unsigned long dutyMin = 1000000;
    unsigned long dutyMax = 0;

    unsigned long periodMin = 1000000;
    unsigned long periodMax = 0;

    unsigned long frequencyMin = 1000000;
    unsigned long frequencyMax = 0;

    // ---------------------------------------------------------
    // 500ms連続観測
    // ---------------------------------------------------------

    unsigned long previousHighStart = observationStart;

    while (micros() - observationStart < OBSERVE_TIME_US)
    {
        // -----------------------------------------------------
        // HIGH -> LOW
        // -----------------------------------------------------

        unsigned long waitStart = micros();

        while (digitalRead(PinConfig::TARGET_OBSERVER_PIN) == HIGH)
        {
            if (micros() - observationStart >= OBSERVE_TIME_US)
            {
                break;
            }

            if (micros() - waitStart >= TIMEOUT_US)
            {
                Serial.println(F("[TARGET] PWM Timeout"));
                return;
            }
        }

        unsigned long lowStart = micros();

        if (micros() - observationStart >= OBSERVE_TIME_US)
        {
            break;
        }

        // -----------------------------------------------------
        // LOW -> HIGH
        // -----------------------------------------------------

        waitStart = micros();

        while (digitalRead(PinConfig::TARGET_OBSERVER_PIN) == LOW)
        {
            if (micros() - observationStart >= OBSERVE_TIME_US)
            {
                break;
            }

            if (micros() - waitStart >= TIMEOUT_US)
            {
                Serial.println(F("[TARGET] PWM Timeout"));
                return;
            }
        }

        unsigned long nextHighStart = micros();

        if (micros() - observationStart >= OBSERVE_TIME_US)
        {
            break;
        }

        // -----------------------------------------------------
        // PWM計算
        // -----------------------------------------------------

        unsigned long highTime =
            lowStart - previousHighStart;

        unsigned long period =
            nextHighStart - previousHighStart;

        if (period == 0)
        {
            continue;
        }

        unsigned long lowTime =
            nextHighStart - lowStart;

        float duty =
            (float)highTime /
            (float)period *
            100.0;

        float frequency =
            1000000.0 /
            (float)period;

        // -----------------------------------------------------
        // 統計値へ追加
        //
        // 小数を扱うため100倍して整数化
        // -----------------------------------------------------

        unsigned long dutyValue =
            (unsigned long)(duty * 100.0);

        unsigned long frequencyValue =
            (unsigned long)(frequency * 100.0);

        dutySum += dutyValue;
        periodSum += period;
        frequencySum += frequencyValue;

        if (dutyValue < dutyMin)
        {
            dutyMin = dutyValue;
        }

        if (dutyValue > dutyMax)
        {
            dutyMax = dutyValue;
        }

        if (period < periodMin)
        {
            periodMin = period;
        }

        if (period > periodMax)
        {
            periodMax = period;
        }

        if (frequencyValue < frequencyMin)
        {
            frequencyMin = frequencyValue;
        }

        if (frequencyValue > frequencyMax)
        {
            frequencyMax = frequencyValue;
        }

        cycleCount++;

        previousHighStart = nextHighStart;
    }

    // ---------------------------------------------------------
    // 結果
    // ---------------------------------------------------------

    if (cycleCount == 0)
    {
        Serial.println(F("[TARGET] PWM No Signal"));
        return;
    }

    unsigned long dutyAvg =
        dutySum / cycleCount;

    unsigned long periodAvg =
        periodSum / cycleCount;

    unsigned long frequencyAvg =
        frequencySum / cycleCount;

    // ---------------------------------------------------------
    // Summary
    // ---------------------------------------------------------

    Serial.print(F("[TARGET] Cycles: "));
    Serial.println(cycleCount);

    Serial.print(F("[TARGET] Duty Avg: "));
    Serial.print(dutyAvg / 100);
    Serial.print(F("."));
    Serial.print(dutyAvg % 100);
    Serial.println(F(" %"));

    Serial.print(F("[TARGET] Duty Min: "));
    Serial.print(dutyMin / 100);
    Serial.print(F("."));
    Serial.print(dutyMin % 100);
    Serial.println(F(" %"));

    Serial.print(F("[TARGET] Duty Max: "));
    Serial.print(dutyMax / 100);
    Serial.print(F("."));
    Serial.print(dutyMax % 100);
    Serial.println(F(" %"));

    Serial.print(F("[TARGET] Duty Range: "));
    Serial.print((dutyMax - dutyMin) / 100);
    Serial.print(F("."));
    Serial.print((dutyMax - dutyMin) % 100);
    Serial.println(F(" %"));

    Serial.print(F("[TARGET] Period Avg: "));
    Serial.print(periodAvg);
    Serial.println(F(" us"));

    Serial.print(F("[TARGET] Period Min: "));
    Serial.print(periodMin);
    Serial.println(F(" us"));

    Serial.print(F("[TARGET] Period Max: "));
    Serial.print(periodMax);
    Serial.println(F(" us"));

    Serial.print(F("[TARGET] Frequency Avg: "));
    Serial.print(frequencyAvg / 100);
    Serial.print(F("."));
    Serial.print(frequencyAvg % 100);
    Serial.println(F(" Hz"));

    Serial.print(F("[TARGET] Frequency Min: "));
    Serial.print(frequencyMin / 100);
    Serial.print(F("."));
    Serial.print(frequencyMin % 100);
    Serial.println(F(" Hz"));

    Serial.print(F("[TARGET] Frequency Max: "));
    Serial.print(frequencyMax / 100);
    Serial.print(F("."));
    Serial.print(frequencyMax % 100);
    Serial.println(F(" Hz"));
}