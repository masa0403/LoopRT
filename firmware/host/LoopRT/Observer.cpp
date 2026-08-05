#include <Arduino.h>

#include "Observer.h"

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

* @brief 指定したピンの状態を読む
  */
  int Observer::readPin(int pin)
  {
  int state = digitalRead(pin);

  if (state == HIGH)
  {
  Serial.print(F("[OBSERVE] D"));
  Serial.print(pin);
  Serial.println(F(" HIGH"));
  }
  else
  {
  Serial.print(F("[OBSERVE] D"));
  Serial.print(pin);
  Serial.println(F(" LOW"));
  }

  return state;
  }
