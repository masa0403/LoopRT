#ifndef F_CPU
#define F_CPU 3333333UL
#endif

#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

/*
 * ATtiny202 pin assignment
 * PA3: rising-edge input
 * PA7: output, initial LOW
 *
 * The PA7 transition is implemented as:
 *   PA3 rising edge detected
 *   -> wait 300 ms
 *   -> invert PA7
 *
 * PA7 is a digital GPIO, so it cannot physically change through
 * intermediate voltage levels without PWM or external hardware.
 */

int main(void)
{
    uint8_t previous_pa3;
    uint8_t current_pa3;

    /* PA7 output, initial LOW */
    PORTA.DIRSET = PIN7_bm;
    PORTA.OUTCLR = PIN7_bm;

    /* PA3 input */
    PORTA.DIRCLR = PIN3_bm;

    /* No pull-up: PA3 is expected to be driven externally */
    PORTA.PIN3CTRL = PORT_ISC_INTDISABLE_gc;

    /* Initialize edge detector state */
    previous_pa3 = ((PORTA.IN & PIN3_bm) != 0u);

    for (;;)
    {
        current_pa3 = ((PORTA.IN & PIN3_bm) != 0u);

        /* Rising edge: LOW -> HIGH */
        if ((current_pa3 != 0u) && (previous_pa3 == 0u))
        {
            /*
             * Keep the current PA7 state for 300 ms, then invert it.
             * This prevents a new inversion from occurring immediately.
             */
            _delay_ms(300.0);

            PORTA.OUTTGL = PIN7_bm;
        }

        previous_pa3 = current_pa3;

        /* Polling interval */
        _delay_ms(1.0);
    }
}
