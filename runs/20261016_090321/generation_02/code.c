#ifndef F_CPU
#define F_CPU 3333333UL
#endif

#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <stdint.h>

/*
 * ATtiny202 pin assignment:
 *   PA3: rising-edge input
 *   PA7: digital output, initial LOW
 *
 * On each PA3 rising edge:
 *   1. Detect the edge using the PORT interrupt.
 *   2. Wait 300 ms.
 *   3. Invert PA7.
 *
 * PA7 is a digital GPIO. Therefore, this implementation changes
 * the digital state after 300 ms; it does not generate an analog
 * voltage ramp.
 */

static volatile uint8_t pa3_rising_pending = 0u;

/* PA3 PORT interrupt vector */
ISR(PORTA_PORT_vect)
{
    if ((PORTA.INTFLAGS & PIN3_bm) != 0u)
    {
        /* Clear PA3 interrupt flag */
        PORTA.INTFLAGS = PIN3_bm;

        /* Record the rising edge for processing in main() */
        pa3_rising_pending = 1u;
    }
}

int main(void)
{
    /* PA7 output, initial LOW */
    PORTA.DIRSET = PIN7_bm;
    PORTA.OUTCLR = PIN7_bm;

    /* PA3 input */
    PORTA.DIRCLR = PIN3_bm;

    /*
     * Enable rising-edge interrupt sensing on PA3.
     * No pull-up is enabled because Arduino Nano D8 actively drives
     * both LOW and HIGH during the experiment.
     */
    PORTA.PIN3CTRL = PORT_ISC_RISING_gc;

    /* Discard any stale PA3 interrupt flag before enabling interrupts */
    PORTA.INTFLAGS = PIN3_bm;

    /* Enable global interrupts */
    sei();

    for (;;)
    {
        if (pa3_rising_pending != 0u)
        {
            /*
             * Consume one detected rising edge.
             * Additional edges during this 300 ms interval remain
             * represented by the pending flag.
             */
            pa3_rising_pending = 0u;

            _delay_ms(300.0);

            /* Invert PA7 */
            PORTA.OUTTGL = PIN7_bm;
        }
    }
}
