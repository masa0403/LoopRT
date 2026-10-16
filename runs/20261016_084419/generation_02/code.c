#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>

/*
 * ATtiny202
 *
 * PA3: 立ち上がりエッジ入力
 * PA7: ソフトウェアPWM出力
 *
 * PA3の立ち上がりエッジを検出すると、
 * PA7の目標状態を反転する。
 * PA7は約300 msかけて目標状態へ変化する。
 *
 * ATtiny202の初期クロック4 MHzを想定する。
 */

#define PA3_MASK       PIN3_bm
#define PA7_MASK       PIN7_bm

#define PWM_STEPS      100U
#define TCB_PERIOD     200U
#define RAMP_TICKS     30U

volatile uint8_t pwm_counter = 0;
volatile uint8_t pwm_duty = 0;
volatile uint8_t pwm_target = 0;
volatile uint8_t ramp_tick = 0;

static void gpio_init(void)
{
    /* PA3: 入力 */
    PORTA.DIRCLR = PA3_MASK;
    PORTA.PIN3CTRL = 0;

    /* PA7: 出力、初期状態LOW */
    PORTA.DIRSET = PA7_MASK;
    PORTA.OUTCLR = PA7_MASK;
}

static void tcb0_init(void)
{
    /*
     * TCB周期割り込みモード
     *
     * 4 MHz / 2 = 2 MHz
     * 200カウント = 100 us
     */
    TCB0.CTRLB = TCB_CNTMODE_INT_gc;
    TCB0.CCMP = TCB_PERIOD - 1U;
    TCB0.INTCTRL = TCB_CAPT_bm;

    /*
     * avr-gccのATtiny202デバイスヘッダでは
     * TCB_CLKSEL_CLKDIV2_gcを使用する。
     */
    TCB0.CTRLA = TCB_CLKSEL_CLKDIV2_gc | TCB_ENABLE_bm;
}

ISR(TCB0_INT_vect)
{
    /*
     * ソフトウェアPWM。
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
     * 100 us × 30回 = 3 msごとに
     * PWMデューティを1段階変更する。
     *
     * 100段階の変化で約300 ms。
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

    /*
     * 起動時のPA3状態を基準値とする。
     * 起動時にPA3がHIGHでも、そこからの立ち上がりとはみなさない。
     */
    previous_pa3 = (PORTA.IN & PA3_MASK) ? 1U : 0U;

    sei();

    for (;;) {
        current_pa3 = (PORTA.IN & PA3_MASK) ? 1U : 0U;

        /*
         * PA3の立ち上がりエッジを検出したら、
         * PA7の目標状態を反転する。
         */
        if (current_pa3 && !previous_pa3) {
            if (pwm_target == 0U) {
                pwm_target = PWM_STEPS;
            } else {
                pwm_target = 0U;
            }
        }

        previous_pa3 = current_pa3;
    }
}
