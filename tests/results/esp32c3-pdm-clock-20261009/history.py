"""Record the integer PDM workaround in locally installed, identified SDKs."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
SDK_ROOT = Path('C:/Work/yoRadio/.idf')
OVERRIDE = 'i2s_ll_tx_set_raw_clk_div(handle->controller->hal.dev, clk_info.mclk_div, 1, 1, 0, 0);'
PATHS = dict(driver='components/esp_driver_i2s/i2s_pdm.c',
             header='components/esp_driver_i2s/include/driver/i2s_pdm.h')
result = dict(scope='Source comparison only; older SDKs not reflashed in this experiment.', versions=[])
for version in ('v5.5.4', 'v6.0.2', 'v6.0.3', 'v6.1', 'v6.1-9a97f6c54ec6'):
    sdk = SDK_ROOT/version
    revision = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', 'HEAD'], text=True).strip()
    item = dict(version=version, revision=revision, sources={})
    texts = {}
    for name, relative in PATHS.items():
        raw = (sdk/relative).read_bytes()
        text = raw.decode().replace('\r\n', '\n')
        original = subprocess.check_output(['git', '-C', str(sdk), 'show', f'{revision}:{relative}'])
        assert original.decode().replace('\r\n', '\n') == text, 'Local SDK source differs from commit'
        file = ROOT/'history-sources'/version/(name+'.'+('c' if name=='driver' else 'h'))
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(raw)
        item['sources'][name] = dict(path=relative, sha256=hashlib.sha256(raw).hexdigest(),
            normalized_sha256=hashlib.sha256(text.encode()).hexdigest(),
            url=f'https://github.com/espressif/esp-idf/blob/{revision}/{relative}')
        texts[name] = text
    lines = texts['driver'].splitlines()
    positions = [i+1 for i,line in enumerate(lines) if OVERRIDE in line]
    assert len(positions)==1
    item['integer_override_line'] = positions[0]
    item['integer_override'] = lines[positions[0]-1].strip()
    macro = re.search(r'#define I2S_PDM_TX_CLK_DAC_DEFAULT_CONFIG\(rate\).*?\n}', texts['header'], re.S).group()
    item['dac_default_macro'] = macro
    assert '.bclk_div = 13,' in macro
    assert '.up_sample_fp = 960,' in macro
    assert '.up_sample_fs = (rate) / 100,' in macro
    result['versions'].append(item)
(ROOT/'history.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
print('Verified integer workaround and DAC defaults in', len(result['versions']), 'SDK checkouts')
