"""Pinned-source clock calculation; this is not a measurement of live registers."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

SDK = Path('C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6')
ROOT = Path('.build/c3-heap-pacing-20261009')
paths = {
    'driver': SDK/'components/esp_driver_i2s/i2s_pdm.c',
    'defaults': SDK/'components/esp_driver_i2s/include/driver/i2s_pdm.h',
    'low_level': SDK/'components/esp_hal_i2s/esp32c3/include/hal/i2s_ll.h',
    'soc': SDK/'components/soc/esp32c3/include/soc/soc_caps.h',
    'clocks': SDK/'components/soc/esp32c3/include/soc/clk_tree_defs.h',
    'application': Path('idf/esp32c3-oled-native/main/native_audio_output.c'),
}
text = {k:p.read_text() for k,p in paths.items()}
assert re.search(r'SOC_I2S_HW_VERSION_2\s+\(1\)', text['soc'])
assert re.search(r'SOC_I2S_SUPPORTS_PCM2PDM\s+\(1\)', text['soc'])
assert re.search(r'I2S_CLK_SRC_DEFAULT\s*=\s*SOC_MOD_CLK_PLL_F160M', text['clocks'])
assert re.search(r'I2S_LL_PDM_BCK_FACTOR\s+\(64\)', text['low_level'])
default = re.search(r'#define I2S_PDM_TX_CLK_DAC_DEFAULT_CONFIG\(rate\).*?\n}', text['defaults'], re.S)[0]
assert '.bclk_div = 13,' in default and '.up_sample_fp = 960,' in default
assert '.up_sample_fs = (rate) / 100,' in default
assert 'I2S_PDM_TX_CLK_DAC_DEFAULT_CONFIG(PDM_OUTPUT_SAMPLE_RATE)' in text['application']
assert re.search(r'#define PDM_OUTPUT_SAMPLE_RATE 48000U', text['application'])
assert 'clk_info->mclk_div = clk_info->sclk / clk_info->mclk;' in text['driver']
assert re.search(r'i2s_hal_set_tx_clock\(.*?\n#if SOC_I2S_HW_VERSION_2\s*'
                 r'/\*.*?\*/\s*i2s_ll_tx_set_raw_clk_div\(handle->controller->hal.dev, '
                 r'clk_info.mclk_div, 1, 1, 0, 0\);', text['driver'], re.S)

sample_rate = 48000
source = 160_000_000
oversampling = 64 * (960 // (sample_rate // 100))
bclk_div = 13
requested_mclk = sample_rate * oversampling * bclk_div
integer_divider = source // requested_mclk
precise_divider = Fraction(source, requested_mclk)
predicted_rate = Fraction(source, integer_divider * bclk_div * oversampling)
result = dict(scope=__doc__.strip(), requested_sample_rate_hz=sample_rate,
              assumed_nominal_source_hz=source, pdm_clocks_per_pcm_frame=oversampling,
              bclk_div=bclk_div, desired_mclk_divider=str(precise_divider),
              integer_mclk_divider_written_by_workaround=integer_divider,
              raw_fraction_fields=dict(x=1, y=1, z=0, yn1=0),
              predicted_pcm_rate_fraction=str(predicted_rate),
              predicted_pcm_rate_hz=float(predicted_rate),
              predicted_rate_ratio=float(predicted_rate/sample_rate),
              predicted_error_ppm=float((predicted_rate/sample_rate-1)*1_000_000),
              predicted_extra_audio_seconds_per_600_wall_seconds=float((predicted_rate/sample_rate-1)*600),
              caveat='Assumes configured PLL and effective integer-only divider; needs live register or output measurement. '
                     'Do not remove the SDK noise workaround or change BCLK alone based on this calculation.',
              source_sha256={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in paths.items()})
dest = ROOT/'clock-sources'
dest.mkdir(exist_ok=True)
for k,p in paths.items(): (dest/(k+p.suffix)).write_bytes(p.read_bytes())
(ROOT/'pdm-clock-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
