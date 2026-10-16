#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>

/*
 * ATtiny202
 *
 * PA3: 立ち上がりエッジ入力
 * PA7: 出力
 *
 * PA3の立ち上がりエッジを検出すると、
 * PA7の出力状態を反転する。
 * 反転後の状態は約300 ms後に確定する。
 *
 * ATtiny202の初期クロック4 MHzを想定する。
 */

#define PA3_MASK       PIN3_bm
#define PA7_MASK       PIN7_bm

/*
 * TCB0割り込み周期:
 * 4 MHz / 2 = 2 MHz
 * 2000カウント = 1 ms
 */
#define TCB_PERIOD     2000U
#define TRANSITION_MS  300U

volatile uint8_t pa7_state = 0;
volatile uint8_t pa7_target = 0;
volatile uint16_t transition_remaining = 0;

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
     * TCB周期割り込みモード。
     * 4 MHz / 2 / 2000 = 1 kHz、周期1 ms。
     */
    TCB0.CTRLB = TCB_CNTMODE_INT_gc;
    TCB0.CCMP = TCB_PERIOD - 1U;
    TCB0.INTCTRL = TCB_CAPT_bm;
    TCB0.CTRLA = TCB_CLKSEL_CLKDIV2_gc | TCB_ENABLE_bm;
}

ISR(TCB0_INT_vect)
{
    if (transition_remaining > 0U) {
        transition_remaining--;

        if (transition_remaining == 0U) {
            pa7_state = pa7_target;

            if (pa7_state != 0U) {
                PORTA.OUTSET = PA7_MASK;
            } else {
                PORTA.OUTCLR = PA7_MASK;
            }
        }
    }

    TCB0.INTFLAGS = TCB_CAPT_bm;
}

int main(void)
{
    uint8_t previous_pa3;
    uint8_t current_pa3;

    gpio_init();

    pa7_state = 0;
    pa7_target = 0;
    transition_remaining = 0;

    tcb0_init();

    /*
     * 起動時のPA3状態を基準値とする。
     * 起動時にPA3がHIGHでも、立ち上がりエッジとはみなさない。
     */
    previous_pa3 = (PORTA.IN & PA3_MASK) ? 1U : 0U;

    sei();

    for (;;) {
        current_pa3 = (PORTA.IN & PA3_MASK) ? 1U : 0U;

        /*
         * PA3の立ち上がりエッジを検出したら、
         * PA7の目標状態を反転し、300 msタイマを開始する。
         */
        if (current_pa3 && !previous_pa3) {
            if (pa7_target == 0U) {
                pa7_target = 1U;
            } else {
                pa7_target = 0U;
            }

            transition_remaining = TRANSITION_MS;
        }

        previous_pa3 = current_pa3;
    }
}
