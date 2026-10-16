#ifndef F_CPU
#define F_CPU 3333333UL
#endif

#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

/*
 * ATtiny202 pin assignment:
 *   PA3: rising-edge input
 *   PA7: digital output, initial LOW
 *
 * A PA3 LOW-to-HIGH transition starts a 300 ms interval.
 * At the end of the interval, PA7 is inverted.
 */

int main(void)
{
    uint8_t previous_pa3;
    uint8_t current_pa3;
    uint8_t transition_active = 0u;
    uint16_t transition_ms = 0u;

    /* PA7 output, initial LOW */
    PORTA.DIRSET = PIN7_bm;
    PORTA.OUTCLR = PIN7_bm;

    /* PA3 input */
    PORTA.DIRCLR = PIN3_bm;

    /*
     * Define the idle level when PA3 is not externally driven.
     * Arduino Nano D8 actively drives PA3 LOW or HIGH in the test.
     */
    PORTA.PIN3CTRL = PORT_PULLUPEN_bm | PORT_ISC_INTDISABLE_gc;

    previous_pa3 = ((PORTA.IN & PIN3_bm) != 0u);

    for (;;)
    {
        current_pa3 = ((PORTA.IN & PIN3_bm) != 0u);

        /* Detect PA3 LOW -> HIGH */
        if ((current_pa3 != 0u) &&
            (previous_pa3 == 0u) &&
            (transition_active == 0u))
        {
            transition_active = 1u;
            transition_ms = 300u;
        }

        previous_pa3 = current_pa3;

        if (transition_active != 0u)
        {
            if (transition_ms > 0u)
            {
                transition_ms--;
            }

            if (transition_ms == 0u)
            {
                if ((PORTA.OUT & PIN7_bm) != 0u)
                {
                    PORTA.OUTCLR = PIN7_bm;
                }
                else
                {
                    PORTA.OUTSET = PIN7_bm;
                }

                transition_active = 0u;
            }
        }

        _delay_ms(1.0);
    }
}
