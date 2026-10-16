#ifndef F_CPU
#define F_CPU 3333333UL
#endif

#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

/*
 * Diagnostic firmware for wiring and programming verification.
 *
 * PA3 (Arduino Nano D8) is directly mirrored to PA7
 * (Arduino Nano D10).
 *
 * This is intentionally a diagnostic experiment, not the final
 * edge-triggered implementation. It distinguishes:
 *   - target code not being written/executed,
 *   - PA3-D8 wiring or common-GND problems,
 *   - PA7-D10 wiring or output problems.
 */

int main(void)
{
    uint8_t pa3_high;

    /* PA7 output, initial LOW */
    VPORTA.DIR |= PIN7_bm;
    VPORTA.OUT &= (uint8_t)~PIN7_bm;

    /* PA3 input */
    VPORTA.DIR &= (uint8_t)~PIN3_bm;

    /* Defined input level when D8 is not actively driving */
    PORTA.PIN3CTRL = PORT_PULLUPEN_bm | PORT_ISC_INTDISABLE_gc;

    for (;;)
    {
        pa3_high = ((VPORTA.IN & PIN3_bm) != 0u);

        if (pa3_high != 0u)
        {
            VPORTA.OUT |= PIN7_bm;
        }
        else
        {
            VPORTA.OUT &= (uint8_t)~PIN7_bm;
        }

        _delay_ms(1.0);
    }
}
