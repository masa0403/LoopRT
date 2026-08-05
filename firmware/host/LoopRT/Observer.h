#ifndef LOOPRT_OBSERVER_H
#define LOOPRT_OBSERVER_H

/**

* @brief Target MCUの状態を観測する
  */
  class Observer
  {
  public:

  Observer();

  void initialize();

  int readPin(int pin);
  };

#endif
