#define F_CPU 4000000UL

#include <avr/io.h>
#include <stdint.h>
#include <util/delay.h>

/*
 * ATtiny202
 *
 * PA3: 立ち上がりエッジ入力
 * PA7: 出力
 *
 * PA3の立ち上がりエッジを検出すると、
 * 約300 ms後にPA7の状態を反転する。
 *
 * 初期状態:
 * PA7 = LOW
 *
 * ATtiny202の初期クロック4 MHzを想定する。
 */

#define PA3_MASK PIN3_bm
#define PA7_MASK PIN7_bm

static void gpio_init(void)
{
    /* PA3: 入力 */
    PORTA.DIRCLR = PA3_MASK;
    PORTA.PIN3CTRL = 0;

    /* PA7: 出力、初期状態LOW */
    PORTA.DIRSET = PA7_MASK;
    PORTA.OUTCLR = PA7_MASK;
}

int main(void)
{
    uint8_t previous_pa3;
    uint8_t current_pa3;
    uint8_t pa7_state = 0;

    gpio_init();

    /*
     * 起動時のPA3状態を基準値とする。
     * 起動時にPA3がHIGHでも、立ち上がりエッジとはみなさない。
     */
    previous_pa3 = (PORTA.IN & PA3_MASK) ? 1U : 0U;

    for (;;) {
        current_pa3 = (PORTA.IN & PA3_MASK) ? 1U : 0U;

        /*
         * PA3の立ち上がりエッジを検出。
         * 300 ms経過後にPA7の状態を反転する。
         */
        if (current_pa3 && !previous_pa3) {
            _delay_ms(300.0);

            pa7_state ^= 1U;

            if (pa7_state != 0U) {
                PORTA.OUTSET = PA7_MASK;
            } else {
                PORTA.OUTCLR = PA7_MASK;
            }
        }

        previous_pa3 = current_pa3;
    }
}
