#include <Arduino.h>
#include "Experiment.h"

/**
 * @brief Experimentを初期化する
 */
void Experiment::initialize()
{
    Serial.println("[INFO] Experiment Initialize");
}

/**
 * @brief 実験開始
 */
void Experiment::execute()
{
    Serial.println("[INFO] Experiment Start");

    step();

    Serial.println("[INFO] Experiment Finish");
}

/**
 * @brief 実験命令を1つ実行する
 *
 * 現在はダミー命令のみ。
 */
void Experiment::step()
{
    Serial.println("[INFO] Execute Command");
}
