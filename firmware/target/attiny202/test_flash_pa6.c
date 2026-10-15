#include <avr/io.h>

int main(void)
{
    PORTA.DIR |= (1 << 6);
    PORTA.OUT |= (1 << 6);

    while (1)
    {
    }
}
