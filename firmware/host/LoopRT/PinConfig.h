#ifndef LOOPRT_PIN_CONFIG_H
#define LOOPRT_PIN_CONFIG_H

/**
 * @brief LoopRTで使用するピン設定
 */
namespace PinConfig
{
    // Host Nano
    constexpr int TARGET_CONTROL_PIN = 8;
    constexpr int TARGET_OBSERVER_PIN = 7;
    constexpr int PWM_OUTPUT_PIN = 9;
}

#endif