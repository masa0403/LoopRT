#ifndef F_CPU
#define F_CPU 3333333UL
#endif

#include <avr/io.h>
#include <util/delay.h>

/*
 * PA7 output-path diagnostic.
 *
 * PA7 is forced HIGH continuously.
 * This test does not implement the final PA3 edge-triggered behavior.
 * It verifies whether the programmed ATtiny202 can drive PA7 and
 * whether PA7 is correctly connected to Arduino Nano D10.
 */

int main(void)
{
    /* Configure PA7 as output and force it HIGH */
    VPORTA.DIR |= PIN7_bm;
    VPORTA.OUT |= PIN7_bm;

    for (;;)
    {
        /* Keep PA7 HIGH */
        VPORTA.OUT |= PIN7_bm;
        _delay_ms(10.0);
    }
}
