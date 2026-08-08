#ifndef LOOPRT_PIN_CONFIG_H
#define LOOPRT_PIN_CONFIG_H

/**
 * @brief LoopRT Host Nano / Target ATtiny202 pin mapping
 *
 * Target ATtiny202      Host Nano
 *
 * PA2                   D7
 * PA0                   D6  (UPDI)
 * PA3                   D8
 * PA6                   D9  (PWM / RC)
 * PA7                   D10
 * PA1                   D11
 */

namespace PinConfig
{
    // ---------------------------------------------------------
    // Target MCU -> Host Nano
    // ---------------------------------------------------------

    constexpr int TARGET_PA2 = 7;
    constexpr int TARGET_PA3 = 8;
    constexpr int TARGET_PA6 = 9;
    constexpr int TARGET_PA7 = 10;
    constexpr int TARGET_PA1 = 11;

    // ---------------------------------------------------------
    // Target MCU programming
    // ---------------------------------------------------------

    constexpr int TARGET_UPDI = 6;
}

#endif