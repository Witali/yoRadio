"""Verify frozen original CYD output-gain campaigns and exact arithmetic as data."""
import argparse
from decimal import Decimal, ROUND_HALF_UP, localcontext
from functools import lru_cache
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

FOLDER = Path(__file__).resolve().parent
ROOT = FOLDER.parents[2]


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


@lru_cache(maxsize=None)
def factor(gain, precision):
    with localcontext() as context:
        context.prec = precision
        return (Decimal(10).ln() * Decimal(gain) / 5120).exp()


def expected(row, precision):
    gain, left, right, channels, volume, balance = row
    need(-32768 <= gain <= 32767 and -32768 <= left <= 32767 and
         -32768 <= right <= 32767 and 1 <= channels <= 255 and
         0 <= volume <= 254 and -16 <= balance <= 16, 'valid arithmetic inputs')
    gl = (volume * (16 + balance if channels > 1 and balance < 0 else 16) * 32768 + 2032) // 4064
    gr = (volume * (16 - balance if balance > 0 else 16) * 32768 + 2032) // 4064
    with localcontext() as context:
        context.prec = precision
        if gain == 0:
            l = int((Decimal(left * gl) / 32768).to_integral_value(rounding=ROUND_HALF_UP))
            r = int((Decimal(right * gr) / 32768).to_integral_value(rounding=ROUND_HALF_UP))
            value = l if channels == 1 else int(Decimal(l + r) / 2)
        else:
            total = left * gl + (right * gr if channels > 1 else 0)
            value = int((Decimal(total) * factor(gain, precision) /
                         (65536 if channels > 1 else 32768)).to_integral_value(rounding=ROUND_HALF_UP))
    return min(32767, max(-32768, value))


def check_trace(row):
    need(len(row) == 7 and expected(row[:6], 80) == row[6] and
         expected(row[:6], 120) == row[6], 'independent 80/120-digit exact trace')


def function(source, name):
    match = re.search(r'^(?:static )?[^\n;{}()]*\b' + name + r'\(', source, re.M)
    need(match is not None, 'original production function')
    end = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


def verify(require_current=False):
    manifest = json.loads((FOLDER / 'manifest.json').read_bytes())
    need(not manifest['native_mcu'] and not manifest['physical_hardware'] and
         not manifest['production_pipeline_selection_proven'] and
         not manifest['numerical_conformance_claim'], 'exact host qualification scope')
    pin = manifest['archive']
    archive = FOLDER / pin['path']
    need(archive.name == 'captures.zip' and archive.parent == FOLDER and
         archive.stat().st_size == pin['bytes'] and sha(archive.read_bytes()) == pin['sha256'], 'exact archive')
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        need(len(names) == len(set(names)) == manifest['physical_blobs'], 'unique physical census')
        blobs = {name: z.read(name) for name in names}
    for name, body in blobs.items():
        need(name == 'blobs/' + sha(body) and not body.startswith(b'\x7fELF'), 'exact blobs without ELF')
    files = {}
    for row in manifest['files']:
        name = row['path']; p = PurePosixPath(name); body = blobs[row['blob']]
        need(not p.is_absolute() and '..' not in p.parts and name not in files and
             len(body) == row['bytes'] and sha(body) == row['sha256'], 'exact unique logical bytes')
        files[name] = body
    need(len(files) == manifest['logical_files'] and
         set(blobs) == {row['blob'] for row in manifest['files']}, 'complete logical/blob census')
    omitted = manifest['omitted_payloads']
    need(len(omitted) == 65 and len({row['path'] for row in omitted}) == 65 and
         all(row['path'] not in files and row['original_retained_locally'] and
             row['byte_payload_published'] is False for row in omitted), 'whole local-only host binaries')
    reports = {}
    for label, campaign in manifest['campaigns'].items():
        body = files[label + '/report.json']
        need(sha(body) == campaign['original_report_sha256'], 'original report bytes')
        report = json.loads(body); reports[label] = report
        for name, digest in report['sources'].items():
            need(sha(files[label + '/sources/' + name]) == digest, 'every original source binding')
        if label == 'finite-factor-nonpass':
            need(report['passed'] is False and report['state'] == 'nonpass' and
                 report['error'] == 'CalledProcessError' and not report['variants'] and
                 b'native_audio_output_set_header_gain(7 * 256) == ESP_FAIL' in files[label + '/failure.log'],
                 'preserved terminal finite-factor refusal failure')
        else:
            need(report['passed'] is True and set(report['variants']) == {'pdm', 'dac', 'legacy'}, 'original terminal PASS')
            if 'state' in report:
                need(report['state'] == 'complete' and not report['numerical_conformance_claim'], 'terminal scoped gain campaign')
            for backend in ('pdm', 'dac', 'legacy'):
                log = files[label + '/' + backend + '.log'].decode().strip()
                recorded = report['variants'][backend]
                need(log.startswith('PASS ') and '\n' not in log and
                     log == (recorded['result'] if isinstance(recorded, dict) else recorded), 'actual original clean native log')
    need(set(reports) == {'baseline-mix', 'baseline-normalizer', 'baseline-layout', 'initial-gain',
                         'finite-factor-nonpass', 'final-gain', 'final-mix', 'final-normalizer', 'final-layout'}, 'all nine campaigns')
    production_name = 'idf/esp32-cyd2usb-native/main/native_audio_output.c'
    header_name = production_name[:-1] + 'h'
    old = reports['initial-gain']['sources'][production_name]
    need(old == reports['finite-factor-nonpass']['sources'][production_name] and
         old != reports['final-gain']['sources'][production_name], 'preserved pre-fix and corrected source boundaries')
    for suite in ('mix', 'normalizer', 'layout'):
        before, after = reports['baseline-' + suite], reports['final-' + suite]
        need(before['variants'] == after['variants'], 'unchanged legacy results/counts/bounds')
        need(after['sources'][production_name] == reports['final-gain']['sources'][production_name], 'final regression same source')
        for name, digest in before['sources'].items():
            if name.startswith('tests/native/') or '/AudioNormalizer.' in name:
                need(after['sources'][name] == digest, 'legacy assertions/goldens/normalizer unchanged')
    source = files['final-gain/sources/' + production_name].decode().replace('\r\n', '\n')
    need('!isfinite(next.factor * (2.0 * 32768.0))' in source and
         reports['final-gain']['sources'][header_name] == sha(files['final-gain/sources/' + header_name]), 'guarded agreed API')
    common = source[source.index('static int16_t scale_sample_q15('):source.index('#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM')]
    constants = '\n'.join(re.findall(r'^#define [^\n]+', source, re.M)) + '\n'
    for backend in ('pdm', 'dac', 'legacy'):
        inc = files['final-gain/' + backend + '.inc'].decode().replace('\r\n', '\n')
        need(inc.startswith('#include "pcm_header_gain.h"\n' + constants + common), 'actual unchanged shared-reader extraction')
        branch = source.split({'pdm': '#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM',
                               'dac': '#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC',
                               'legacy': '#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC'}[backend], 1)[1]
        for name in ('native_audio_output_configure', 'native_audio_output_write_pcm',
                     'native_audio_output_discard_pcm', 'native_audio_output_flush_pcm', 'native_audio_output_pause'):
            need(function(branch, name) in inc, 'actual backend producer/lifecycle functions')
        unit = files['final-gain/' + backend + '.c'].decode().replace('\r\n', '\n')
        need(inc in unit and '#define NDEBUG' not in unit, 'compiled actual producer with assertions')
    runner = files['final-gain/sources/tests/run-cyd-header-gain.py'].decode()
    need('-fsanitize=address,undefined,float-cast-overflow' in runner and
         'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1' in runner and '-Werror' in runner,
         'sanitizer/leak/cast checks enabled')
    vectors = json.loads(files['final-gain/reference_vectors.json'])
    need(len(vectors) == 13824, 'complete Decimal vector matrix')
    for bits, channels, gain, left, right, volume, balance, result in vectors:
        need(bits in (8, 16, 24, 32) and (bits != 8 or left % 256 == right % 256 == 0), 'projected packed widths')
        check_trace((gain, left, right, channels, volume, balance, result))
    header = ('typedef struct { unsigned bits, channels; int gain, left, right; '
              'unsigned volume; int balance, expected; } gain_vector;\n'
              'static const gain_vector vectors_data[] = {\n' +
              ''.join('    {' + ','.join(map(str, row)) + '},\n' for row in vectors) + '};\n')
    need(files['final-gain/reference_vectors.h'].decode().replace('\r\n', '\n') == header, 'compiled exact Decimal vectors')
    trace_count = 0
    for backend in ('pdm', 'dac', 'legacy'):
        record = reports['final-gain']['variants'][backend]
        need(record['passed'] and '13824 Decimal vectors, 192 stream packets, 65536 cached gain transitions, 6 transactional math refusals' in record['result'], 'full final native outcome')
        rows = files['final-gain/' + backend + '-normalizer-reference.csv'].decode().splitlines()
        need(len(rows) == record['decimal_trace_checks'] == 58537, 'all original trace samples')
        for line in rows:
            check_trace(tuple(map(int, line.split(','))))
        trace_count += len(rows)
    if require_current:
        current = dict(reports['final-gain']['sources'])
        for label in ('final-mix', 'final-normalizer', 'final-layout'):
            for name, digest in reports[label]['sources'].items():
                need(name not in current or current[name] == digest, 'consistent final source bindings')
                current[name] = digest
        for name, digest in current.items():
            need(sha((ROOT / name).read_bytes()) == digest, 'current final source: ' + name)
    controls = 0
    for row in ((1536, 25000, 25000, 2, 127, 0, 16384),
                (12288, 30000, -29900, 2, 1, 0, 0),
                (0, 1, 1, 2, 254, 0, 2),
                (-32768, 32767, -32768, 0, 254, 0, 0)):
        try:
            check_trace(row)
        except ValueError:
            controls += 1
    need(controls == 4, 'early clipping/cancellation/identity/invalid-input negative controls')
    return dict(passed=True, campaigns=9, logical_files=len(files), physical_blobs=len(blobs),
                omitted_host_binaries=len(omitted), decimal_vectors=len(vectors),
                decimal_trace_samples=trace_count, rejected_negative_controls=controls,
                require_current=require_current, physical_hardware=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-current', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify(args.require_current), indent=2))
