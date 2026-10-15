#include <avr/io.h>
#include <util/delay.h>

int main(void)
{
    // ★ ここではクロックはいじらず、今のままの内部クロックで動かす
    PORTA.DIRSET = PIN2_bm;

    while (1)
    {
        PORTA.OUTSET = PIN2_bm;
        _delay_ms(1000);   // 「1秒のつもり」

        PORTA.OUTCLR = PIN2_bm;
        _delay_ms(1000);   // 「1秒のつもり」
    }

    return 0;
}
