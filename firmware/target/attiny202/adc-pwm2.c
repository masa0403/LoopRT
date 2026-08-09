#include <avr/io.h>

void clock_init(void) {
    uint8_t temp = CLKCTRL.MCLKCTRLB & ~CLKCTRL_PEN_bm;
    CCP = CCP_IOREG_gc;
    CLKCTRL.MCLKCTRLB = temp;
}

void adc_init(void) {
    PORTA.PIN6CTRL = PORT_ISC_INPUT_DISABLE_gc;
    
    ADC0.CTRLC = ADC_PRESC_DIV32_gc | ADC_REFSEL_VDDREF_gc;
    ADC0.SAMPCTRL = 15; 
    ADC0.CTRLA = ADC_ENABLE_bm | ADC_RESSEL_10BIT_gc;
    ADC0.MUXPOS = ADC_MUXPOS_AIN6_gc;
}

void pwm_init(void) {
    PORTA.DIRSET = PIN2_bm;
    
    TCA0.SINGLE.PER = 255;
    TCA0.SINGLE.CMP2 = 128;
    TCA0.SINGLE.CMP2BUF = 128;
    TCA0.SINGLE.CTRLB = TCA_SINGLE_CMP2EN_bm | TCA_SINGLE_WGMODE_SINGLESLOPE_gc;
    TCA0.SINGLE.CTRLA = TCA_SINGLE_CLKSEL_DIV16_gc | TCA_SINGLE_ENABLE_bm;
}

uint8_t convert_adc_to_duty(uint16_t adc_val) {
    uint32_t duty = ((uint32_t)adc_val * 255) / 1023;
    
    if (duty < 1) duty = 1;
    if (duty > 254) duty = 254;

    return (uint8_t)duty;
}

int main(void) {
    clock_init();
    adc_init();
    pwm_init();

    while (1) {
        // 1. 変換開始
        ADC0.COMMAND = ADC_STCONV_bm;

        // 2. 変換完了まで確実に待機（ポーリング）
        while (!(ADC0.INTFLAGS & ADC_RESRDY_bm));

        // 3. フラグを明示的にクリア (1を書き込むことでクリアされる仕様)
        ADC0.INTFLAGS = ADC_RESRDY_bm;

        // 4. ADC値を読み出してPWMバッファに反映
        uint16_t raw_adc = ADC0.RES;
        TCA0.SINGLE.CMP2BUF = convert_adc_to_duty(raw_adc);
    }

    return 0;
}