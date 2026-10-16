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
 * When a rising edge is detected on PA3, PA7 is inverted
 * 300 ms later.
 */

static volatile uint8_t pa3_rising_pending = 0u;

ISR(PORTA_PORT_vect)
{
    if ((PORTA.INTFLAGS & PIN3_bm) != 0u)
    {
        /* Clear the PA3 interrupt flag */
        PORTA.INTFLAGS = PIN3_bm;

        /* Record the detected rising edge */
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
     * Enable the internal pull-up as a defined idle state.
     * Arduino Nano D8 actively drives PA3 LOW or HIGH during testing,
     * so the pull-up does not prevent either input state.
     */
    PORTA.PIN3CTRL = PORT_PULLUPEN_bm | PORT_ISC_RISING_gc;

    /* Clear any pending PA3 interrupt before enabling interrupts */
    PORTA.INTFLAGS = PIN3_bm;

    sei();

    for (;;)
    {
        if (pa3_rising_pending != 0u)
        {
            pa3_rising_pending = 0u;

            /*
             * The requested 0.3-second transition is implemented as
             * a 300 ms delay from edge detection to digital inversion.
             */
            _delay_ms(300.0);

            /* Invert PA7 */
            PORTA.OUTTGL = PIN7_bm;
        }
    }
}
