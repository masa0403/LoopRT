#include <avr/io.h>
#include <stdint.h>

/*
 * ATtiny202 LoopRT command test
 *
 * PA2 -> Host D7
 *      PWM output
 *
 * PA3 <- Host D8
 *      GPIO input
 *
 * PA6 <- Host D9
 *      RC filtered PWM
 *      ADC input
 *
 * Test flow:
 *
 * Host D9
 *   ↓
 *  RC
 *   ↓
 * PA6 ADC
 *   ↓
 * ADC value
 *   ↓
 * PA2 PWM
 *   ↓
 * Host D7
 */

#define PWM_TOP 255

/*
 * Clock
 *
 * tools/target.py により実機F_CPUへ合わせられる。
 */

/**
 * ADC initialize
 */
static void adc_init(void)
{
    /*
     * PA6 = ADC input
     */
    PORTA.PIN6CTRL = PORT_ISC_INPUT_DISABLE_gc;

    /*
     * VDD reference
     *
     * ADC clock:
     * F_CPU / 32
     */
    ADC0.CTRLC =
        ADC_PRESC_DIV32_gc |
        ADC_REFSEL_VDDREF_gc;

    /*
     * Sampling time
     */
    ADC0.SAMPCTRL = 15;

    /*
     * 10-bit ADC
     */
    ADC0.CTRLA =
        ADC_ENABLE_bm |
        ADC_RESSEL_10BIT_gc;

    /*
     * PA6 = AIN6
     */
    ADC0.MUXPOS = ADC_MUXPOS_AIN6_gc;
}

/**
 * PWM initialize
 *
 * PA2 -> TCA0 WO2
 */
static void pwm_init(void)
{
    PORTA.DIRSET = PIN2_bm;

    TCA0.SINGLE.PER = PWM_TOP;

    TCA0.SINGLE.CMP2 = 0;
    TCA0.SINGLE.CMP2BUF = 0;

    TCA0.SINGLE.CTRLB =
        TCA_SINGLE_CMP2EN_bm |
        TCA_SINGLE_WGMODE_SINGLESLOPE_gc;

    /*
     * 20MHz / 16 / 256
     * ≈ 4.88kHz
     */
    TCA0.SINGLE.CTRLA =
        TCA_SINGLE_CLKSEL_DIV16_gc |
        TCA_SINGLE_ENABLE_bm;
}

/**
 * ADC value -> PWM duty
 */
static uint8_t adc_to_pwm(uint16_t adc)
{
    uint32_t duty;

    duty =
        ((uint32_t)adc * PWM_TOP) / 1023;

    if (duty > PWM_TOP)
    {
        duty = PWM_TOP;
    }

    return (uint8_t)duty;
}

/**
 * Main
 */
int main(void)
{
    adc_init();
    pwm_init();

    /*
     * PA3 = GPIO input
     *
     * Pull-upは使用しない。
     * Host D8からH/Lを入力する。
     */
    PORTA.DIRCLR = PIN3_bm;

    while (1)
    {
        /*
         * Host D9
         *   ↓
         * RC
         *   ↓
         * PA6 ADC
         */
        ADC0.COMMAND = ADC_STCONV_bm;

        /*
         * Conversion complete
         */
        while (!(ADC0.INTFLAGS & ADC_RESRDY_bm))
        {
        }

        /*
         * Clear flag
         */
        ADC0.INTFLAGS = ADC_RESRDY_bm;

        /*
         * Read ADC
         */
        uint16_t adc_value = ADC0.RES;

        /*
         * ADC value -> PWM duty
         *
         * PA2 -> Host D7
         */
        TCA0.SINGLE.CMP2BUF =
            adc_to_pwm(adc_value);

        /*
         * PA3 is intentionally only used
         * as a GPIO input.
         *
         * H/L/I command test is performed
         * directly through Host D8.
         */
        (void)PORTA.IN;
    }

    return 0;
}