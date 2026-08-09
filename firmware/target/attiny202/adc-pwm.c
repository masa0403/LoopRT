#include <avr/io.h>
#include <stdlib.h>

// ADC初期化：フリーランニングモード
void ADC0_init(void) {
    // PA6のデジタル入力バッファを無効化 (ノイズ低減)
    PORTA.PIN6CTRL &= ~PORT_ISC_gm;
    PORTA.PIN6CTRL |= PORT_ISC_INPUT_DISABLE_gc;

    // AIN6チャンネル選択 (PA6)
    ADC0.MUXPOS = ADC_MUXPOS_AIN6_gc;

    // 基準電圧: VDDREF, クロック分周: CLK_PER/32
    ADC0.CTRLC = ADC_REFSEL_VDDREF_gc | ADC_PRESC_DIV32_gc;

    // 10bitモード, フリーランニングモード(FREERUN), ADC有効化
    ADC0.CTRLA = ADC_ENABLE_bm | ADC_FREERUN_bm | ADC_RESSEL_10BIT_gc;

    // 最初の変換を開始
    ADC0.COMMAND = ADC_STCONV_bm;
}

// TCA0 (PWM) 初期化 (PA2 / WO2)
void TCA0_init(void) {
    // PA2を出力ピンに設定
    PORTA.DIRSET = PIN2_bm;

    // Single Slope PWM モード有効化 (WO2出力)
    TCA0.SINGLE.CTRLB = TCA_SINGLE_CMP2EN_bm | TCA_SINGLE_WGMODE_SINGLESLOPE_gc;

    // 周期設定 (8bit PWM: TOP = 255)
    TCA0.SINGLE.PER = 255;

    // 初期Duty比 0
    TCA0.SINGLE.CMP2BUF = 0;

    // クロック選択 (DIV16) & タイマースタート
    TCA0.SINGLE.CTRLA = TCA_SINGLE_CLKSEL_DIV16_gc | TCA_SINGLE_ENABLE_bm;
}

int main(void) {
    ADC0_init();
    TCA0_init();

    // 最初のADC完了待ち
    while (!(ADC0.INTFLAGS & ADC_RESRDY_bm));
    ADC0.INTFLAGS = ADC_RESRDY_bm;

    // フィルタ初期値 (16bit固定小数点: 重み64用)
    uint32_t filtered_adc = (uint32_t)ADC0.RES << 8;
    uint8_t current_duty = 0;

    while (1) {
        // ADCの新しい変換結果が完了している場合のみ処理
        if (ADC0.INTFLAGS & ADC_RESRDY_bm) {
            ADC0.INTFLAGS = ADC_RESRDY_bm; // フラグクリア
            
            uint16_t raw_adc = ADC0.RES;

            // 1. 強力な重み付け (1/64) による平滑化フィルタ
            // RC回路の残留リプル（微小な脈流）を強力にカット
            filtered_adc = (filtered_adc * 63 + ((uint32_t)raw_adc << 8)) / 64;
            uint16_t stable_adc = filtered_adc >> 8;

            // 2. デッドゾーン（不感帯）および限界値クランプ処理
            // 0V付近・5V付近の端数ノイズによる波形揺れ・不審パルスを排除
            uint8_t new_duty;
            if (stable_adc < 12) {        // 約0.05V以下は完全0%
                new_duty = 0;
            } else if (stable_adc > 1010) { // 約4.95V以上は完全100% (255)
                new_duty = 255;
            } else {
                new_duty = (uint8_t)(stable_adc >> 2); // 10bit(0~1023) -> 8bit(0~255)
            }

            // 3. ヒステリシス処理 (±2を超える変化のみ反映)
            if (abs((int)new_duty - (int)current_duty) >= 2) {
                current_duty = new_duty;
                // バッファレジスタへ安全書き込み
                TCA0.SINGLE.CMP2BUF = current_duty;
            }
        }
    }

    return 0;
}