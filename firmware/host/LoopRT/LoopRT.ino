#include "Runtime.h"

/**
 * RuntimeはLoopRT全体で一つだけ存在する。
 *
 * 将来的には実験状態や設定などを保持するため、
 * グローバルで生成しておく。
 */
Runtime runtime;

/**
 * Arduino起動時に一度だけ実行される。
 */
void setup()
{
    // シリアル通信開始
    Serial.begin(115200);

    // シリアルモニタの接続待ち
    while (!Serial)
    {
        ;
    }

    Serial.println();
    Serial.println("================================");
    Serial.println("LoopRT v0.1");
    Serial.println("================================");
    Serial.println();

    Serial.println("[INFO] Boot");

    // Runtime開始
    runtime.initialize();

    // Runtime終了
    runtime.shutdown();

    Serial.println();
    Serial.println("LoopRT Ready");
}

/**
 * Arduinoはsetup()終了後、この関数を永久に実行する。
 *
 * 現在のLoopRTには処理はない。
 */
void loop()
{
}
