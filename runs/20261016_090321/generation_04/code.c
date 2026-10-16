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
 * A PA3 LOW-to-HIGH transition starts a 300 ms transition interval.
 * At the end of the interval, PA7 is inverted.
 */

int main(void)
{
    uint8_t previous_pa3;
    uint8_t current_pa3;
    uint8_t transition_active = 0u;
    uint16_t transition_ms = 0u;

    /* PA7 output, initial LOW */
    VPORTA.DIR |= PIN7_bm;
    VPORTA.OUT &= (uint8_t)~PIN7_bm;

    /* PA3 input */
    VPORTA.DIR &= (uint8_t)~PIN3_bm;

    /*
     * Enable a defined idle level for PA3.
     * The Arduino Nano actively drives D8 LOW or HIGH during testing.
     */
    PORTA.PIN3CTRL = PORT_PULLUPEN_bm | PORT_ISC_INTDISABLE_gc;

    /* Initialize the edge detector from the actual input level */
    previous_pa3 = ((VPORTA.IN & PIN3_bm) != 0u);

    for (;;)
    {
        current_pa3 = ((VPORTA.IN & PIN3_bm) != 0u);

        /*
         * Detect PA3 rising edge.
         * An edge received while a transition is active is ignored,
         * because PA7 is already in its requested 300 ms transition.
         */
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
                /*
                 * Use explicit SET/CLR instead of OUTTGL so that the
                 * final digital state is unambiguous.
                 */
                if ((VPORTA.OUT & PIN7_bm) != 0u)
                {
                    VPORTA.OUT &= (uint8_t)~PIN7_bm;
                }
                else
                {
                    VPORTA.OUT |= PIN7_bm;
                }

                transition_active = 0u;
            }
        }

        _delay_ms(1.0);
    }
}
