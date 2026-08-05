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

  runtime.run();

  runtime.shutdown();
  }

/**

* Arduinoはsetup()終了後、この関数を永久に実行する。
  */
  void loop()
  {
  }
