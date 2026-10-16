#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>

/*
 * ATtiny202
 *
 * PA3: 立ち上がりエッジ入力
 * PA7: ソフトウェアPWM出力
 *
 * PA7は、エッジ検出後に約300 msかけて
 * LOW -> HIGH または HIGH -> LOWへ変化する。
 *
 * ATtiny202の初期クロックは4 MHzを想定する。
 */

#define PA3_MASK       PIN3_bm
#define PA7_MASK       PIN7_bm

#define PWM_STEPS      100U
#define RAMP_PERIOD_MS 300U

/*
 * TCB割り込み周期:
 * 4 MHz / 2 = 2 MHz
 * 200カウント = 100 us
 */
#define TCB_PERIOD     200U

/*
 * 100 us周期で30回ごとにPWMデューティを1段階変更する。
 * 100段階 × 3 ms = 300 ms
 */
#define RAMP_TICKS     30U

volatile uint8_t pwm_counter = 0;
volatile uint8_t pwm_duty = 0;
volatile uint8_t pwm_target = 0;
volatile uint8_t ramp_tick = 0;

static void gpio_init(void)
{
    /* PA3: 入力、内部プルダウン有効 */
    PORTA.DIRCLR = PA3_MASK;
    PORTA.PIN3CTRL = PORT_PULLUPEN_bm;

    /*
     * 内部プルアップを有効にしているため、
     * 外部からLOWを駆動する場合は注意すること。
     *
     * Arduino D8からLOW/HIGHを駆動する通常の実験では、
     * 外部信号を優先するため、内部プルアップを無効にする。
     */
    PORTA.PIN3CTRL = 0;

    /* PA7: 出力、初期LOW */
    PORTA.DIRSET = PA7_MASK;
    PORTA.OUTCLR = PA7_MASK;
}

static void tcb0_init(void)
{
    TCB0.CTRLB = TCB_CNTMODE_INT_gc;
    TCB0.CCMP = TCB_PERIOD - 1U;
    TCB0.INTCTRL = TCB_CAPT_bm;
    TCB0.CTRLA = TCB_CLKSEL_DIV2_gc | TCB_ENABLE_bm;
}

ISR(TCB0_INT_vect)
{
    /*
     * ソフトウェアPWM生成。
     * pwm_counterは0～99を繰り返す。
     */
    if (pwm_counter < pwm_duty) {
        PORTA.OUTSET = PA7_MASK;
    } else {
        PORTA.OUTCLR = PA7_MASK;
    }

    pwm_counter++;
    if (pwm_counter >= PWM_STEPS) {
        pwm_counter = 0;
    }

    /*
     * 約3 msごとにデューティを1段階変更する。
     * 0 -> 100 または 100 -> 0で約300 ms。
     */
    ramp_tick++;
    if (ramp_tick >= RAMP_TICKS) {
        ramp_tick = 0;

        if (pwm_duty < pwm_target) {
            pwm_duty++;
        } else if (pwm_duty > pwm_target) {
            pwm_duty--;
        }
    }

    TCB0.INTFLAGS = TCB_CAPT_bm;
}

int main(void)
{
    uint8_t previous_pa3;
    uint8_t current_pa3;

    gpio_init();

    pwm_counter = 0;
    pwm_duty = 0;
    pwm_target = 0;
    ramp_tick = 0;

    tcb0_init();

    previous_pa3 = (PORTA.IN & PA3_MASK) ? 1U : 0U;

    sei();

    for (;;) {
        current_pa3 = (PORTA.IN & PA3_MASK) ? 1U : 0U;

        /*
         * PA3の立ち上がりエッジを検出したら、
         * PA7の目標状態を反転する。
         *
         * 変化中に次の立ち上がりが来た場合も、
         * 現在の目標状態を反転して戻り方向へ変化させる。
         */
        if (current_pa3 && !previous_pa3) {
            uint8_t new_target;

            if (pwm_target == 0U) {
                new_target = PWM_STEPS;
            } else {
                new_target = 0U;
            }

            pwm_target = new_target;
        }

        previous_pa3 = current_pa3;
    }
}
