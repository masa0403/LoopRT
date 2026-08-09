#include <avr/io.h>
#include <stdint.h>

#define PWM_TOP 63

/*
 * ATtiny202
 *
 * PA2 -> TCA0 WO2 -> Host D7
 * PA3 -> TCA0 WO0 -> Host D8
 *
 * PWM frequency:
 * 20 MHz / 64 / 64
 * ≈ 4.88 kHz
 */

static uint16_t random_state = 0xACE1;

/**
 * 16-bit LFSR pseudo random generator
 */
static uint16_t random16(void)
{
    uint16_t lsb = random_state & 1;

    random_state >>= 1;

    if (lsb)
    {
        random_state ^= 0xB400;
    }

    return random_state;
}

/**
 * PWM initialize
 */
static void pwm_init(void)
{
    PORTA.DIRSET =
        PIN2_bm |
        PIN3_bm;

    TCA0.SINGLE.CTRLB =
        TCA_SINGLE_WGMODE_SINGLESLOPE_gc |
        TCA_SINGLE_CMP0EN_bm |
        TCA_SINGLE_CMP2EN_bm;

    TCA0.SINGLE.PER = PWM_TOP;

    TCA0.SINGLE.CMP0 = 0;
    TCA0.SINGLE.CMP2 = 0;

    TCA0.SINGLE.CTRLA =
        TCA_SINGLE_CLKSEL_DIV64_gc |
        TCA_SINGLE_ENABLE_bm;
}

/**
 * Set PWM duty
 */
static void set_pwm(
    uint8_t duty_pa2,
    uint8_t duty_pa3
)
{
    if (duty_pa2 > 100)
    {
        duty_pa2 = 100;
    }

    if (duty_pa3 > 100)
    {
        duty_pa3 = 100;
    }

    TCA0.SINGLE.CMP2 =
        ((uint16_t)(PWM_TOP + 1) * duty_pa2) / 100;

    TCA0.SINGLE.CMP0 =
        ((uint16_t)(PWM_TOP + 1) * duty_pa3) / 100;
}

/**
 * 約10ms delay
 */
static void flame_delay(void)
{
    for (volatile uint32_t i = 0; i < 20000; i++)
    {
        __asm__ __volatile__("nop");
    }
}

int main(void)
{
    pwm_init();

    uint8_t brightness_pa2 = 60;
    uint8_t brightness_pa3 = 55;

    /*
     * 瞬停状態
     *
     * 0 = 通常
     * 1 = 瞬停中
     */
    uint8_t blackout_pa2 = 0;
    uint8_t blackout_pa3 = 0;

    /*
     * 瞬停前の明るさ
     */
    uint8_t saved_pa2 = 60;
    uint8_t saved_pa3 = 55;

    /*
     * 瞬停残り時間
     * 10ms単位
     */
    uint8_t blackout_timer_pa2 = 0;
    uint8_t blackout_timer_pa3 = 0;

    /*
     * 次の瞬停までの時間
     * 10ms単位
     */
    uint16_t next_blackout_pa2 =
        80 + (random16() % 180);

    uint16_t next_blackout_pa3 =
        100 + (random16() % 200);

    set_pwm(
        brightness_pa2,
        brightness_pa3
    );

    while (1)
    {
        /*
         * ====================================================
         * PA2
         * ====================================================
         */

        if (blackout_pa2)
        {
            /*
             * 瞬停中
             */
            set_pwm(0, brightness_pa3);

            if (blackout_timer_pa2 > 0)
            {
                blackout_timer_pa2--;
            }

            if (blackout_timer_pa2 == 0)
            {
                /*
                 * 瞬停終了
                 *
                 * 元の明るさへ即復帰
                 */
                blackout_pa2 = 0;
                brightness_pa2 = saved_pa2;
            }
        }
        else
        {
            /*
             * 通常のゆらめき
             *
             * PA2だけ独立して変化
             */
            int8_t change =
                (random16() % 21) - 10;

            int16_t next =
                brightness_pa2 + change;

            if (next < 20)
            {
                next = 20;
            }

            if (next > 90)
            {
                next = 90;
            }

            brightness_pa2 = next;

            /*
             * 瞬停カウントダウン
             */
            if (next_blackout_pa2 > 0)
            {
                next_blackout_pa2--;
            }

            if (next_blackout_pa2 == 0)
            {
                /*
                 * 現在の明るさを保存
                 */
                saved_pa2 = brightness_pa2;

                /*
                 * 30～150msの瞬停
                 */
                blackout_timer_pa2 =
                    3 + (random16() % 13);

                blackout_pa2 = 1;

                /*
                 * 次回までの時間
                 *
                 * 約0.8～2.6秒
                 */
                next_blackout_pa2 =
                    80 + (random16() % 180);
            }
        }

        /*
         * ====================================================
         * PA3
         * ====================================================
         */

        if (blackout_pa3)
        {
            /*
             * 瞬停中
             */
            set_pwm(brightness_pa2, 0);

            if (blackout_timer_pa3 > 0)
            {
                blackout_timer_pa3--;
            }

            if (blackout_timer_pa3 == 0)
            {
                /*
                 * 瞬停終了
                 */
                blackout_pa3 = 0;
                brightness_pa3 = saved_pa3;
            }
        }
        else
        {
            /*
             * PA3も完全に独立してゆらめく
             */
            int8_t change =
                (random16() % 21) - 10;

            int16_t next =
                brightness_pa3 + change;

            if (next < 15)
            {
                next = 15;
            }

            if (next > 90)
            {
                next = 90;
            }

            brightness_pa3 = next;

            /*
             * 瞬停カウントダウン
             */
            if (next_blackout_pa3 > 0)
            {
                next_blackout_pa3--;
            }

            if (next_blackout_pa3 == 0)
            {
                /*
                 * 現在の明るさを保存
                 */
                saved_pa3 = brightness_pa3;

                /*
                 * 30～150msの瞬停
                 */
                blackout_timer_pa3 =
                    3 + (random16() % 13);

                blackout_pa3 = 1;

                /*
                 * 次回までの時間
                 */
                next_blackout_pa3 =
                    100 + (random16() % 200);
            }
        }

        /*
         * 最終的なPWM出力
         */
        if (blackout_pa2)
        {
            set_pwm(0, brightness_pa3);
        }
        else if (blackout_pa3)
        {
            set_pwm(brightness_pa2, 0);
        }
        else
        {
            set_pwm(
                brightness_pa2,
                brightness_pa3
            );
        }

        /*
         * 10msごとに更新
         */
        flame_delay();
    }

    return 0;
}