#include <avr/io.h>
#include <util/delay.h>

int main(void)
{
    // PA2を出力に設定
    PORTA.DIRSET = PIN2_bm;

    while (1)
    {
        // HIGH
        PORTA.OUTSET = PIN2_bm;
        _delay_ms(1000);

        // LOW
        PORTA.OUTCLR = PIN2_bm;
        _delay_ms(1000);
    }

    return 0;
}