"""Generate an optional, build-local C3 PDM clock experiment for audited IDF."""
import argparse
import hashlib
from pathlib import Path

SOURCE_SHA256 = 'e1f10fcab65ee36899d0b6f32d16eae3ef24be8e75455c1de45458a7413c8836'
OVERRIDE = '    i2s_ll_tx_set_raw_clk_div(handle->controller->hal.dev, clk_info.mclk_div, 1, 1, 0, 0);'
DECLARATIONS = '''
/* yoRadio C3 experiment: keep the HAL-calculated divider for this audited
 * fixed-rate PCM/DAC configuration. Other modes must not silently opt in. */
#if defined(CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK) || defined(CONFIG_YORADIO_PDM_INTEGER_RATE_COMPENSATION)
#define YORADIO_PDM_PCM_RATE_HZ 48000U
#define YORADIO_PDM_SOURCE_HZ 160000000U
#define YORADIO_PDM_BCLK_DIV 13U
#define YORADIO_PDM_UPSAMPLE_FP 960U
#define YORADIO_PDM_UPSAMPLE_FS 480U
#endif

#ifdef CONFIG_YORADIO_PDM_CLOCK_DIAGNOSTICS
typedef struct {
    uint32_t source_select, integer, x, y, z, yn1, bclk_div, osr, fp, fs;
} yoradio_pdm_clock_snapshot_t;
#endif
'''
GUARD = '''
#if defined(CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK) || defined(CONFIG_YORADIO_PDM_INTEGER_RATE_COMPENSATION)
    ESP_RETURN_ON_FALSE(!handle->is_raw_pdm &&
                       clk_cfg->sample_rate_hz == YORADIO_PDM_PCM_RATE_HZ &&
                       clk_info.sclk == YORADIO_PDM_SOURCE_HZ &&
                       clk_src == I2S_CLK_SRC_PLL_160M &&
                       clk_info.bclk_div == YORADIO_PDM_BCLK_DIV &&
                       clk_cfg->up_sample_fp == YORADIO_PDM_UPSAMPLE_FP &&
                       clk_cfg->up_sample_fs == YORADIO_PDM_UPSAMPLE_FS,
                       ESP_ERR_INVALID_ARG, TAG, "Unsupported PDM rate experiment configuration");
#endif
#ifdef CONFIG_YORADIO_PDM_INTEGER_RATE_COMPENSATION
    ESP_RETURN_ON_FALSE(clk_info.mclk_div == 2U,
                       ESP_ERR_INVALID_ARG, TAG, "Unexpected integer PDM divider");
#endif
#ifdef CONFIG_YORADIO_PDM_CLOCK_DIAGNOSTICS
    yoradio_pdm_clock_snapshot_t yoradio_clock;
#endif
'''
SNAPSHOT = '''
#ifdef CONFIG_YORADIO_PDM_CLOCK_DIAGNOSTICS
    /* Read actual fields under the existing TX setup lock. No logging here. */
    i2s_dev_t *yoradio_hw = handle->controller->hal.dev;
    yoradio_clock = (yoradio_pdm_clock_snapshot_t) {
        .source_select = yoradio_hw->tx_clkm_conf.tx_clk_sel,
        .integer = yoradio_hw->tx_clkm_conf.tx_clkm_div_num,
        .x = yoradio_hw->tx_clkm_div_conf.tx_clkm_div_x,
        .y = yoradio_hw->tx_clkm_div_conf.tx_clkm_div_y,
        .z = yoradio_hw->tx_clkm_div_conf.tx_clkm_div_z,
        .yn1 = yoradio_hw->tx_clkm_div_conf.tx_clkm_div_yn1,
        .bclk_div = yoradio_hw->tx_conf1.tx_bck_div_num + 1U,
        .osr = yoradio_hw->tx_pcm2pdm_conf.tx_pdm_sinc_osr2,
        .fp = yoradio_hw->tx_pcm2pdm_conf1.tx_pdm_fp,
        .fs = yoradio_hw->tx_pcm2pdm_conf1.tx_pdm_fs,
    };
#endif
'''
REPORT = '''
#ifdef CONFIG_YORADIO_PDM_CLOCK_DIAGNOSTICS
    /* Setup-time register readback, not a measurement of crystal accuracy. */
    ESP_LOGI(TAG, "PERF PDM_CLOCK: sclk=%"PRIu32" source=%"PRIu32" integer=%"PRIu32
             " x=%"PRIu32" y=%"PRIu32" z=%"PRIu32" yn1=%"PRIu32" bdiv=%"PRIu32
             " osr=%"PRIu32" fp=%"PRIu32" fs=%"PRIu32,
             clk_info.sclk, yoradio_clock.source_select, yoradio_clock.integer,
             yoradio_clock.x, yoradio_clock.y, yoradio_clock.z, yoradio_clock.yn1,
             yoradio_clock.bclk_div, yoradio_clock.osr, yoradio_clock.fp, yoradio_clock.fs);
#endif
'''


def patch(source):
    text = source.decode('utf-8').replace('\r\n', '\n')
    if hashlib.sha256(text.encode()).hexdigest() != SOURCE_SHA256:
        raise ValueError('Unaudited PDM driver; review clock setup and locking before enabling this experiment')
    start = text.index('static esp_err_t i2s_pdm_tx_set_clock(')
    end = text.index('\nstatic ', start + 1)
    body = text[start:end]
    assert body.count(OVERRIDE) == 1
    body = body.replace(OVERRIDE, '#ifndef CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK\n' + OVERRIDE + '\n#endif')
    marker = '    ESP_RETURN_ON_ERROR(esp_clk_tree_enable_src((soc_module_clk_t)clk_src, true), TAG, "clock source enable failed");'
    assert body.count(marker) == 1
    body = body.replace(marker, GUARD + marker)
    marker = '    portEXIT_CRITICAL(&g_i2s.spinlock);'
    assert body.count(marker) == 1
    body = body.replace(marker, SNAPSHOT + marker + REPORT)
    # HAL writes and start-time update sequencing remain unchanged. RX is untouched.
    return (text[:start] + DECLARATIONS + body + text[end:]).encode()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    blob = patch(args.input.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not args.output.exists() or args.output.read_bytes() != blob:
        args.output.write_bytes(blob)
