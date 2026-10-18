"""Qualify actual C3 Vorbis setup parsing with exact input bounds and fault injection.

ASan/UBSan uses native pointer/long widths: RV32 ABI size/offset assertions are
removed only from generated header copies. The bitreader seam preserves signed
32-bit return values and production rejects packet lengths above INT32_MAX.
Vendor DSP, target ABI layout and physical PCM are not executed by this suite.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'idf/esp32c3-oled-native/main'
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--leg', choices=('vorbis',), default='vorbis')
    parser.add_argument('--vorbis-source', type=Path, default=MAIN/'vorbis_repair/setup.c')
    parser.add_argument('--trace-prefixes', action='store_true')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    sources = [Path(__file__)]
    sanitizers = ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie']
    common = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror']
    try:
        if args.leg in ('all', 'vorbis'):
            folder = out / 'vorbis'
            folder.mkdir(exist_ok=True)
            abi = MAIN / 'vorbis_repair_abi.h'
            text = re.sub(r'^VORBIS_ABI_(?:SIZE|FIELD)\([^;]+;\n', '', abi.read_text(), flags=re.M)
            (folder / 'vorbis_repair_abi.h').write_text(text)
            (folder / 'esp_vorbis_dec.h').write_text('''#pragma once
#include <stdint.h>
typedef int esp_audio_err_t;
#define ESP_AUDIO_ERR_OK 0
#define ESP_AUDIO_ERR_FAIL (-1)
#define ESP_AUDIO_ERR_MEM_LACK (-2)
#define ESP_AUDIO_ERR_INVALID_PARAMETER (-5)
#define ESP_AUDIO_TYPE_VORBIS 1
typedef struct {uint8_t *info_header;uint32_t info_size;uint8_t *setup_header;uint32_t setup_size;} esp_vorbis_dec_cfg_t;
typedef struct {int (*open)(void *,uint32_t,void **);int (*decode)(void);int (*reset)(void);int (*close)(void);} esp_audio_dec_ops_t;
int esp_vorbis_dec_decode(void);
int esp_vorbis_dec_reset(void);
int esp_vorbis_dec_close(void);
int esp_audio_dec_register(int,const esp_audio_dec_ops_t *);
''')
            source = args.vorbis_source.resolve()
            production = source.read_text().replace('#include "../vorbis_repair_abi.h"', '#include "vorbis_repair_abi.h"')
            (folder / 'production.inc').write_text(production)
            # Packet extraction is independent of the production setup parser.
            fixture = ROOT / 'tests/fixtures/esp32c3_calibration/vorbis-q10.ogg'
            data = fixture.read_bytes()
            packets, pending, offset = [], bytearray(), 0
            while offset < len(data) and len(packets) < 3:
                assert data[offset:offset+4] == b'OggS'
                count = data[offset+26]
                sizes = data[offset+27:offset+27+count]
                body = offset+27+count
                for size in sizes:
                    pending.extend(data[body:body+size]); body += size
                    if size < 255:
                        packets.append(bytes(pending)); pending.clear()
                offset = body
            assert packets[0][:7] == b'\1vorbis' and packets[2][:7] == b'\5vorbis'
            fixture_text = ''
            for name, packet in (('info', packets[0][7:]), ('setup', packets[2][7:])):
                fixture_text += 'static const uint8_t fixture_' + name + '[]={' + ','.join(map(str, packet)) + '};\n'
            (folder / 'fixtures.inc').write_text(fixture_text)
            test = ROOT / 'tests/native/codec_warning_vorbis_test.c'
            binary = folder / 'test'
            (folder / 'build.log').write_bytes(run(common + sanitizers +
                (['-DCODEC_TRACE_PREFIX=1'] if args.trace_prefixes else []) +
                ['-I'+host(folder), host(test), '-o', host(binary)]))
            log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1', 'UBSAN_OPTIONS=halt_on_error=1', host(binary)])
            (folder / 'test.log').write_bytes(log)
            results['vorbis_native_width_sanitized'] = log.decode().strip()
            print(log.decode(), end='')
            sources += [abi, source, test, fixture]
    except subprocess.CalledProcessError as error:
        (out / 'failure.log').write_bytes(error.output)
        print(error.output.decode(errors='replace'), file=sys.stderr)
        raise
    for path in sources:
        dest = out / 'sources' / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(path.read_bytes())
    (out / 'report.json').write_text(json.dumps(dict(passed=True, physical_hardware=False,
        vendor_dsp_executed=False, scope=__doc__, results=results,
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in sources}), indent=2)+'\n')


if __name__ == '__main__':
    main()
