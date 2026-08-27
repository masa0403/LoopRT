#include "Runtime.h"

Runtime runtime;

void setup()
{
    Serial.begin(115200);

    while (!Serial)
    {
        ;
    }

    pinMode(13, OUTPUT);
    digitalWrite(13, LOW);

    Serial.println();
    Serial.println("================================");
    Serial.println("LoopRT v0.1");
    Serial.println("================================");
    Serial.println();

    Serial.println("[INFO] Boot");

    runtime.initialize();

    /*
     * LoopRTがPCからの実験命令を
     * 受信できる状態になったことを通知する。
     */
    Serial.println("LoopRT Ready");
}

void loop()
{
    runtime.run();
}