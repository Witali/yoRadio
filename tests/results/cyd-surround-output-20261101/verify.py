"""Authenticate mapped-output host observations as data; run no saved code."""
import argparse
from collections import Counter
from decimal import Decimal, localcontext, ROUND_HALF_UP
from fractions import Fraction
from functools import lru_cache
import hashlib
import itertools
import json
import math
from pathlib import Path, PurePosixPath
import re
import zipfile

FOLDER = Path(__file__).resolve().parent
ROOT = FOLDER.parents[2]
OUTPUT = 'idf/esp32-cyd2usb-native/main/native_audio_output.c'
SPEAKER = 'idf/components/native_stream/include/pcm_speaker_mix.h'
BACKENDS = ('pdm', 'dac', 'legacy')
OUTCOMES = dict(output01=False, output02=False, output03=True, matrix03=True,
                sum01=True, sum02=True, classification01=True, cost01=False, cost02=True)
FALSE_SCOPES = ('physical_hardware', 'native_mcu_executed', 'production_layout_queue_selected',
                'whole_production_pipeline_acceptance', 'full_codec_conformance_claim',
                'universal_numeric_exactness', 'target_throughput_qualified',
                'old_six_suite_current_revision_claim', 'numeric_tolerance_applied',
                'archived_code_executed_by_verifier')


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def policy(manifest):
    need(manifest['schema'] == 1 and manifest['host_output_checkpoint'] is True and
         manifest['enabled_all_channel_normalizer'] is True, 'bounded enabled-normalizer host scope')
    need(all(manifest[name] is False for name in FALSE_SCOPES), 'no enlarged acceptance claims')
    need(set(manifest['campaigns']) == set(OUTCOMES), 'all nine original observations')
    need(all(manifest['campaigns'][name]['expected_pass'] is passed for name, passed in OUTCOMES.items()),
         'preserve all original nonpass outcomes')


@lru_cache(None)
def matrices(channels, precision):
    with localcontext() as context:
        context.prec = precision
        z, one, half = Decimal(0), Decimal(1), Decimal('0.5')
        a, b = one / Decimal(2).sqrt(), Decimal(3).sqrt() / 2
        rows = {
            1: ([one], [one], one),
            2: ([one, z], [z, one], one),
            3: ([one, a, z], [z, a, one], one / (one + a)),
            4: ([one, z, b, half], [z, one, half, b], one / (one + b + half)),
            5: ([one, a, z, b, half], [z, a, one, half, b], 2 / (one + a + b + half)),
            6: ([one, a, z, b, half, a], [z, a, one, half, b, a], 2 / (one + 2*a + b + half)),
            7: ([one, a, z, b, half, a*b, a], [z, a, one, half, b, a*b, a], 2 / (one + 2*a + b + half + a*b)),
            8: ([one, a, z, b, half, b, half, a], [z, a, one, half, b, half, b, a], 2 / (2 + 2*a + 2*b)),
        }
        left, right, factor = rows[channels]
        return tuple(n*factor for n in left), tuple(n*factor for n in right)


@lru_cache(None)
def factor(gain, precision):
    with localcontext() as context:
        context.prec = precision
        return Decimal(10) ** (Decimal(gain)/5120)


def limit(value):
    return min(32767, max(-32768, value))


def ideal(samples, gain, volume, balance, precision):
    channels = len(samples)
    gl = (volume*(16+balance if channels > 1 and balance < 0 else 16)*32768+2032)//4064
    gr = (volume*(16-balance if balance > 0 else 16)*32768+2032)//4064
    with localcontext() as context:
        context.prec = precision
        if channels <= 2:
            if not gain:
                left = int((Decimal(samples[0]*gl)/32768).to_integral_value(rounding=ROUND_HALF_UP))
                right = int((Decimal(samples[1]*gr)/32768).to_integral_value(rounding=ROUND_HALF_UP)) if channels == 2 else 0
                return limit(left if channels == 1 else int(Decimal(left+right)/2))
            value = Decimal(samples[0]*gl+(samples[1]*gr if channels == 2 else 0))
            value *= factor(gain, precision)/(65536 if channels == 2 else 32768)
        else:
            left, right = matrices(channels, precision)
            if all(n == samples[0] for n in samples):
                value = Decimal(samples[0]*(gl+gr)*(1 if channels <= 4 else 2))
            else:
                value = sum(Decimal(n)*(l*gl+r*gr) for n, l, r in zip(samples, left, right))
            value *= factor(gain, precision)/65536
        return limit(int(value.to_integral_value(rounding=ROUND_HALF_UP)))


def static_rows():
    rows = []
    for channels in range(1, 9):
        patterns = [[25000 if c == speaker else 0 for c in range(channels)] for speaker in range(channels)]
        patterns += [[32767]*channels, [-32768]*channels,
                     [30000 if c % 2 == 0 else -30000 for c in range(channels)], [1]*channels, [-1]*channels]
        if channels > 1:
            cancellation = [0]*channels
            cancellation[0] = 30000
            cancellation[1 if channels in (2, 4) else 2] = -30000
            patterns.append(cancellation)
        for bits, gain, volume, balance, pattern in itertools.product(
                (8, 16, 24, 32), (-32768, -1536, 0, 1536, 12288, 32767), (0, 1, 127, 254), (-16, 0, 16), patterns):
            samples = [(n//256)*256 if bits == 8 else n for n in pattern]
            a, b = [ideal(samples, gain, volume, balance, p) for p in (100, 160)]
            need(a == b, 'static independent precision agreement')
            rows.append(dict(channels=channels, bits=bits, gain=gain, volume=volume,
                             balance=balance, samples=samples, expected=a))
    return rows


def function(source, name):
    match = re.search(r'^(?:static )?[^\n;{}()]*\b' + re.escape(name) + r'\(', source, re.M)
    need(match is not None, 'actual source function: ' + name)
    end, depth = source.index('{', match.start())+1, 1
    while depth:
        depth += (source[end] == '{')-(source[end] == '}')
        end += 1
    return source[match.start():end]+'\n'


def generated_units(files):
    prefix = 'output03/sources/'
    # The original Windows runner used read_text/write_text universal newlines;
    # raw source/log/archive byte identities were checked separately above.
    def decoded(name):
        return files[name].decode().replace('\r\n', '\n')
    source = decoded(prefix+OUTPUT)
    harness = decoded(prefix+'tests/native/cyd_surround_output_test.c')
    platform = decoded(prefix+'tests/native/cyd_normalizer_test.c').split('/* PRODUCTION */', 1)[0]
    common = source[source.index('static int16_t scale_sample_q15('):source.index('#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM')]
    constants = '\n'.join(re.findall(r'^#define [^\n]+', source, re.M))+'\n'
    branches = dict(pdm=source.split('#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM', 1)[1].split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC', 1)[0],
                    dac=source.split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC', 1)[1].split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC', 1)[0],
                    legacy=source.split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC', 1)[1])
    for backend in BACKENDS:
        text = '#include "pcm_header_gain.h"\n#include "pcm_channel_layout.h"\n#include "pcm_speaker_mix.h"\n'+constants+common
        p, branch = platform, branches[backend]
        if backend == 'pdm':
            for name in ('pdm_write_resampled', 'pdm_flush', 'reset_resampler'):
                p = p.replace(function(p, name).rstrip(), '', 1)
            names = ('reset_resampler', 'pdm_write_block', 'pdm_flush', 'pdm_queue_sample', 'pdm_write_resampled')
        elif backend == 'dac':
            names = ('dac_write_block',)
        else:
            names = ('legacy_pack_dac_code', 'legacy_fractional_dac_step', 'legacy_write_frames', 'legacy_write_silence')
        for name in names+('native_audio_output_configure', 'native_audio_output_write_pcm',
                           'native_audio_output_discard_pcm', 'native_audio_output_flush_pcm', 'native_audio_output_pause'):
            text += function(branch, name)
        need(files['output03/'+backend+'.inc'].decode().replace('\r\n', '\n') == text, 'unchanged actual producer extraction: '+backend)
        need(files['output03/'+backend+'.c'].decode().replace('\r\n', '\n') == harness.replace('/* PLATFORM */', p).replace('/* PRODUCTION */', text),
             'complete original translation unit: '+backend)
    need('surround_normalizer_calls()>0 && sizeof(s_normalizer_scratch)==512' in harness and
         'normalized<2' in harness and 'channels<=8' in harness and 'PROT_READ' in harness,
         'enabled normalizer, all channels, fixed scratch and immutable mapped input assertions')
    bridge = files[prefix+'tests/native/cyd_surround_output_reference.cpp'].decode()
    need('__real_native_audio_normalizer_process_multichannel_block(samples,frames,channels)' in bridge and
         'frames*channels <= 256' in bridge and 'pthread_equal(owner,pthread_self())' in bridge,
         'real enabled normalizer and sole-owner/scratch wrapper')
    runner = files[prefix+'tests/run-cyd-surround-output.py'].decode()
    need('-fsanitize=address,undefined,float-cast-overflow' in runner and 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1' in runner and
         'adapter/\'native_audio_normalizer.cpp\'' in runner and 'algorithm/\'AudioNormalizer.cpp\'' in runner,
         'actual C++ normalizer objects and sanitizer command policy retained')


def compiled_golden_header(rows):
    header = ''
    for side, name in ((0, 'reference_left'), (1, 'reference_right')):
        header += 'static const long double '+name+'[8][8] = {\n'
        for channels in range(1, 9):
            header += ' {'+','.join(format(n, '.60g')+'L' for n in matrices(channels, 160)[side])+'},\n'
        header += '};\n'
    header += 'typedef struct {unsigned channels,bits;int gain;unsigned volume;int balance;int16_t samples[8];int expected;} surround_vector;\n'
    header += 'static const surround_vector surround_vectors[] = {\n'
    for row in rows:
        header += ' {'+','.join(str(row[k]) for k in ('channels', 'bits', 'gain', 'volume', 'balance'))+', {'+','.join(map(str, row['samples']))+'}, '+str(row['expected'])+'},\n'
    return header+'};\n'


class Envelope:
    """Data-only fixed-settings Q12 envelope/limiter reference, no saved code."""
    lut = tuple(28672+((n << 9)*4095)//((n << 9)+4095) for n in range(585))

    def __init__(self):
        self.gain, self.peak, self.count = 4096, 0, 0

    def process(self, samples):
        self.peak = max(self.peak, *map(abs, samples))
        result = []
        for sample in samples:
            amplified = (sample*self.gain)//4096
            magnitude = abs(amplified)
            if magnitude > 28672:
                over = magnitude-28672
                index = over >> 9
                if index >= 584:
                    magnitude = self.lut[-1]
                else:
                    low, high = self.lut[index:index+2]
                    magnitude = low+((high-low)*(over & 511)+256)//512
            result.append(min(32767, magnitude)*(-1 if amplified < 0 else 1))
        self.count += 1
        if self.count == 480:
            target = min(40960, max(410, (23198*4096)//self.peak)) if self.peak >= 128 else 4096
            step = (abs(target-self.gain)+9)//10
            self.gain += step if target > self.gain else -step if target < self.gain else 0
            self.peak, self.count = 0, 0
        return tuple(result)


def trace_checks(body):
    lines = iter(body.decode().splitlines())
    checks = normalized_checks = 0
    for normalized, bits, channels in itertools.product((False, True), (8, 16, 24, 32), range(1, 9)):
        for group in ([(257, 12288, 1, -7, 0), (127, -1536, 1, -7, 0), (257, 0, 127, 11, 0)],
                      [(513, 1536, 127, 0, 0)], [(127, 1536, 127, 0, 0), (386, 1536, 127, 0, 127)]):
            envelope = Envelope()
            for frames, gain, volume, balance, offset in group:
                for frame in range(offset, offset+frames):
                    samples = []
                    for channel in range(channels):
                        at = (frame*channels+channel)*(bits//8)
                        raw = sum(((n*137+n//11) & 255) << (8*byte) for byte, n in enumerate(range(at, at+bits//8)))
                        signed = raw-(1 << bits) if raw & (1 << (bits-1)) else raw
                        samples.append(signed*256 if bits == 8 else signed//(1 << (bits-16)))
                    samples = envelope.process(samples) if normalized else tuple(samples)
                    record = list(map(int, next(lines).split(',')))
                    need(record[:4] == [channels, gain, volume, balance] and record[4:-1] == list(samples),
                         'complete ordered raw projection and enabled all-channel envelope trace')
                    need(all(ideal(samples, gain, volume, balance, p) == record[-1] for p in (100, 160)),
                         'independent complete-channel Decimal trace')
                    checks += 1
                    normalized_checks += normalized
    need(next(lines, None) is None and checks == 106688 and normalized_checks == 53344, 'complete trace EOF and normalization census')
    return checks, normalized_checks


def rational_identity(samples, gain, volume, balance):
    z = (Fraction(0),)*4
    one, half = (Fraction(1), *z[1:]), (Fraction(1, 2), *z[1:])
    a, b, ab = (z[0], Fraction(1, 2), *z[2:]), (*z[:2], Fraction(1, 2), z[3]), (*z[:3], Fraction(1, 4))
    arrays = {3: ([one, a, z], [z, a, one]), 4: ([one, z, b, half], [z, one, half, b]),
              5: ([one, a, z, b, half], [z, a, one, half, b]), 6: ([one, a, z, b, half, a], [z, a, one, half, b, a]),
              7: ([one, a, z, b, half, ab, a], [z, a, one, half, b, ab, a]),
              8: ([one, a, z, b, half, b, half, a], [z, a, one, half, b, half, b, a])}
    channels = len(samples)
    left, right = arrays[channels]
    gl = (volume*(16+balance if balance < 0 else 16)*32768+2032)//4064
    gr = (volume*(16-balance if balance > 0 else 16)*32768+2032)//4064
    numerator = [sum(n*(l[j]*gl+r[j]*gr) for n, l, r in zip(samples, left, right))*(1 if channels <= 4 else 2) for j in range(4)]
    denominator = [sum(l[j] for l in left)*65536 for j in range(4)]
    ratios = [n/d for n, d in zip(numerator, denominator) if d]
    need(ratios and not any(n for n, d in zip(numerator, denominator) if not d) and all(n == ratios[0] for n in ratios),
         'exact rational matrix identity')
    need(gain % 5120 == 0 or ratios[0] == 0, 'rational gain boundary')
    return ratios[0]*(Fraction(10)**(gain//5120)) if ratios[0] else Fraction(0)


def round_fraction(value):
    n, d = abs(value.numerator), value.denominator
    return limit(((2*n+d)//(2*d))*(1 if value >= 0 else -1))


def round_binary(value):
    return 32767 if value >= 32767 else -32768 if value <= -32768 else int(value+0.5) if value >= 0 else -int(-value+0.5)


def numerical_observations(files, reports, static):
    report = reports['sum02']
    need(report['passed'] and report['static_rows'] == 23904 and report['static_relevant'] == 19872 and
         report['extra_rows'] == 45504 and report['numeric_tolerance_applied'] is False, 'bounded sum review scope')
    extra = json.loads(files['sum02/extra-vectors.json'])
    need(Counter(row['class'] for row in extra) == dict(all_sign_extremes=36288, uniform_odd_half_boundaries=3024,
                                                     dominant_pair_cancellation=3888, seeded_cancellation=2304), 'complete extra-vector classes')
    names = ('current', 'pairwise8', 'pairwise_split', 'kahan', 'neumaier')
    accuracy = {name: dict(rounded_product_sum_mismatches=0, static_gold_mismatches=[], extra_gold_mismatches=[]) for name in names}
    seen = set()
    for line in files['sum02/trace.csv'].decode().splitlines():
        fields = line.split(',')
        kind, index, channels, golden = map(int, fields[:4])
        need(kind in (0, 1) and (kind, index) not in seen, 'unique actual sum-review source row')
        seen.add((kind, index))
        row = (static, extra)[kind][index]
        need(row['channels'] == channels and row['expected'] == golden, 'exact original golden binding')
        values, products = [float.fromhex(n) for n in fields[4:9]], [float.fromhex(n) for n in fields[9:]]
        need(len(products) == channels and all(map(math.isfinite, values+products)), 'finite complete binary64 products')
        correct = math.fsum(products)
        with localcontext() as context:
            context.prec = 160
            need(float(sum(Decimal.from_float(n) for n in products)) == correct, 'independent sum of actual rounded products')
        for name, value in zip(names, values):
            accuracy[name]['rounded_product_sum_mismatches'] += value != correct
            if round_binary(value) != golden:
                accuracy[name]['static_gold_mismatches' if kind == 0 else 'extra_gold_mismatches'].append(index)
    need(seen == {(0, i) for i, row in enumerate(static) if row['channels'] > 2} | {(1, i) for i in range(len(extra))}, 'all65376 observed sums')
    need(accuracy == report['accuracy'], 'every original observed method discrepancy retained')
    for name, counts in zip(names, ((9, 40, 14225), (0, 18, 13020), (9, 34, 12878), (0, 18, 6330), (0, 30, 0))):
        need((len(accuracy[name]['static_gold_mismatches']), len(accuracy[name]['extra_gold_mismatches']),
              accuracy[name]['rounded_product_sum_mismatches']) == counts, 'original exact comparison census: '+name)
    for path, count in (('extra-exact-rational-resolutions.json', 50), ('extra-precision-agreement-ties-corrected.json', 14)):
        rows = json.loads(files['sum02/'+path])
        need(len(rows) == count, 'retained exact extra-oracle correction census')
        for row in rows:
            exact = rational_identity(row['samples'], row['gain'], row['volume'], row['balance'])
            need(exact == Fraction(row['exact_numerator'], row['exact_denominator']) and
                 round_fraction(exact) == row['exact_expected'], 'exact algebra, no epsilon or tolerance')
    need(json.loads(files['sum02/extra-oracle-ambiguous.json']) == [], 'no unresolved extra oracle silently accepted')
    classification = reports['classification01']
    need(classification['verified_identical_emulated_product_rows'] == 10896 and
         classification['classification_counts'] == {'independent_product_rounding_decisive': 30} and
         classification['classes'] == {'all_sign_extremes': 28, 'uniform_odd_half_boundaries': 2}, 'bounded multiplication-stage classification')
    for row in classification['cases']:
        case = row['case']
        exact = rational_identity(case['samples'], case['gain'], case['volume'], case['balance'])
        dot = sum(n*Fraction.from_float(float.fromhex(w)) for n, w in zip(case['samples'], row['weights']))
        products = [float.fromhex(n) for n in row['products']]
        need(round_fraction(exact) == case['expected'] == round_binary(float(dot)) and
             float(dot).hex() == row['correctly_rounded_exact_stored_weight_dot'] and
             math.fsum(products).hex() == row['rounded_product_sum'] and
             round_binary(math.fsum(products)) != case['expected'], 'all30 actual independently rounded-product boundary observations')
    return len(seen)


def verify(require_current=False, self_test=False):
    manifest = json.loads((FOLDER/'manifest.json').read_bytes())
    policy(manifest)
    pin = manifest['archive']
    archive = FOLDER/pin['path']
    need(archive.parent == FOLDER and archive.name == 'captures.zip' and archive.stat().st_size == pin['bytes'] and
         sha(archive.read_bytes()) == pin['sha256'], 'exact original complete archive')
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        need(len(names) == len(set(names)) == manifest['physical_blobs'], 'unique physical archive inventory')
        blobs = {name: z.read(name) for name in names}
    for name, body in blobs.items():
        need(name == 'blobs/'+sha(body) and not body.startswith((b'\x7fELF', b'MZ', b'!<arch>\n')), 'whole nonexecutable physical bytes')
    files, identities = {}, {}
    for row in manifest['files']:
        name, body = row['path'], blobs[row['blob']]
        path = PurePosixPath(name)
        need(not path.is_absolute() and '..' not in path.parts and name not in identities and
             sha(body) == row['sha256'] and len(body) == row['bytes'], 'safe unique complete logical bytes')
        files[name], identities[name] = body, row
    need(len(files) == manifest['logical_files'] and set(blobs) == {row['blob'] for row in manifest['files']}, 'complete physical/logical census')
    for row in manifest['omitted_payloads']:
        need(row['path'] not in identities and row['original_retained_locally'] is True and row['byte_payload_published'] is False and
             row['reasons'] and row['bytes'] > 0 and 'blobs/'+row['sha256'] not in blobs, 'whole original local omission, no alternate copy')
        identities[row['path']] = row
    need(len(identities) == manifest['complete_original_file_census'], 'complete retained original census')

    def identity(name, digest, size=None):
        need(name in identities and identities[name]['sha256'] == digest and
             (size is None or identities[name]['bytes'] == size), 'original source/log/payload binding: '+name)

    reports = {}
    for label, campaign in manifest['campaigns'].items():
        body = files[label+'/report.json']
        need(sha(body) == campaign['original_report_sha256'], 'untouched original report: '+label)
        report = reports[label] = json.loads(body)
        need(report['passed'] is OUTCOMES[label], 'authentic original report outcome: '+label)
        if label.startswith('output'):
            need(report['state'] == ('complete' if OUTCOMES[label] else 'nonpass') and
                 report['physical_hardware'] is False and report['production_layout_queue_selected'] is False and
                 report['full_codec_conformance_claim'] is False, 'original mapped-output scope')
            for name, digest in report['sources'].items():
                identity(label+'/sources/'+name, digest)
        elif label == 'matrix03':
            for row in report['source']:
                identity(label+'/'+row['snapshot'], row['sha256'], row['bytes'])
        elif label.startswith('sum'):
            for name, row in report['sources'].items():
                identity(label+'/'+name, row['sha256'], row['bytes'])
        elif label.startswith('cost'):
            for name, digest in report['sources'].items():
                identity(label+'/'+name, digest)
            need(not report['native_mcu_executed'] and not report['target_timing_measured'], 'compiler-only target-cost scope')
        for command in report.get('commands', []):
            need(command['pid'] > 0 and command['state'] == 'complete' and
                 (command['exit_status'] == 0 or label == 'cost01' and command['name'] == 'object' and command['exit_status'] == 1),
                 'real recorded terminal child status')
            for stream in ('stdout', 'stderr'):
                row = command[stream]
                identity(label+'/'+row.get('path', command['name']+'.'+stream+'.log'), row['sha256'], row['bytes'])
    need(reports['output01']['error'] == 'ValueError' and reports['output01']['variants'] == {} and
         reports['output02']['error'] == 'CalledProcessError' and reports['output02']['variants'] == {} and
         b'vectors=17461 streams=0' in files['output02/failure.log'] and
         b'Assertion' in files['output02/failure.log'], 'both distinct original failures remain nonpass')
    need('output01/pdm.c' not in identities and files['output02/pdm-reference.csv'] == b'', 'no invented execution or completed trace on early failures')
    before, after = reports['output02']['sources'], reports['output03']['sources']
    need({name for name in before if before[name] != after[name]} == {SPEAKER}, 'only compensated-sum helper changes between actual failure and pass')
    old, new = files['output02/sources/'+SPEAKER].decode(), files['output03/sources/'+SPEAKER].decode()
    need(old.split('static inline double psm_value(', 1)[0] == new.split('static inline double psm_value(', 1)[0] and
         'correction += fabs(result) >= fabs(value)' in new, 'exact retained coefficient/preparation bytes and compensated sum')
    need(files['output02/surround_vectors.h'] == files['output03/surround_vectors.h'] and
         files['output02/surround_vectors.json'] == files['output03/surround_vectors.json'], 'unchanged complete original static goldens')
    static = json.loads(files['output03/surround_vectors.json'])
    need(len(static) == 23904 and static == static_rows(), 'all independent static formulas/patterns at100/160 Decimal digits')
    need(files['output03/surround_vectors.h'].decode().replace('\r\n', '\n') == compiled_golden_header(static),
         'every actually compiled golden and long-double matrix matches the independently recomputed data')
    generated_units(files)
    result = 'PASS surround output vectors=23904 packets=384 controls=5 scratch=512'
    need(reports['output03']['all_source_bindings_current'] and reports['output03']['decimal_vectors'] == 23904 and
         set(reports['output03']['variants']) == set(BACKENDS), 'all three original successful producer records')
    trace_body = files['output03/pdm-reference.csv']
    for backend in BACKENDS:
        record = reports['output03']['variants'][backend]
        need(record == dict(passed=True, result=result, decimal_trace_checks=106688) and
             files['output03/'+backend+'.log'].decode().strip() == result and
             files['output03/'+backend+'-reference.csv'] == trace_body, 'every actual producer complete trace/log/oracle record: '+backend)
        for suffix in ('-build.log', '-link.log'):
            need(files['output03/'+backend+suffix] == b'', 'clean sanitizer build/link log: '+backend)
    checks, normalized_checks = trace_checks(trace_body)
    matrix = reports['matrix03']
    need(matrix['all_sources_current'] and matrix['exact_coefficients'] == 72 and matrix['native_summary']['impulses'] == 36 and
         matrix['native_summary']['controls'] == 104 and matrix['final_s16_rounding_qualified'] is False and
         matrix['enabled_normalizer_qualified'] is False, 'helper-only auxiliary acceptance remains bounded')
    identity('matrix03/sources/'+SPEAKER, after[SPEAKER])
    observed_sums = numerical_observations(files, reports, static)
    size_text = files['cost02/size.stdout.log'].decode()
    stack_text = files['cost02/methods.su'].decode()
    costs = {'sum_current': (74, 12, 32), 'sum_pairwise8': (187, 36, 96),
             'sum_kahan': (124, 24, 48), 'sum_neumaier': (230, 36, 80)}
    for name, (text, literal, stack) in costs.items():
        need(re.search(r'\.text\.'+name+r'\s+'+str(text)+r'\s', size_text) and
             re.search(r'\.literal\.'+name+r'\s+'+str(literal)+r'\s', size_text) and
             re.search(r':'+name+r'\t'+str(stack)+r'\tstatic', stack_text), 'original standalone code/stack observation: '+name)
    need(reports['cost01']['failure'] == 'object' and reports['cost02']['compiler_unchanged'] and
         'recursive' in reports['cost02']['target_only_recursive_array_initialization'], 'preserved target warning and explicit candidate-only preparation')
    if require_current:
        for name, digest in manifest['current_source_bindings'].items():
            need(sha((ROOT/name).read_bytes()) == digest, 'current final source binding: '+name)
    controls = 0
    if self_test:
        for name in FALSE_SCOPES:
            changed = dict(manifest, **{name: True})
            try:
                policy(changed)
            except ValueError:
                controls += 1
            else:
                raise ValueError('contradictory scope accepted: '+name)
        for label in ('output01', 'output02', 'cost01'):
            changed = json.loads(json.dumps(manifest))
            changed['campaigns'][label]['expected_pass'] = True
            try:
                policy(changed)
            except ValueError:
                controls += 1
            else:
                raise ValueError('historical nonpass promoted to pass: '+label)
        changed_files = dict(files)
        changed_files['output03/legacy.inc'] += b'\n/* unexpected producer bytes */\n'
        try:
            generated_units(changed_files)
        except ValueError:
            controls += 1
        else:
            raise ValueError('altered actual legacy producer accepted')
        changed_lines = trace_body.decode().splitlines()
        record = changed_lines[53344].split(',')
        record[4] = str(int(record[4])+1)
        changed_lines[53344] = ','.join(record)
        try:
            trace_checks(('\n'.join(changed_lines)+'\n').encode())
        except ValueError:
            controls += 1
        else:
            raise ValueError('altered enabled-normalizer sample accepted')
    print(json.dumps(dict(passed=True, original_campaigns=9, actual_backends=3, static_vectors_per_backend=23904,
                          packets_per_backend=384, metadata_controls_per_backend=5, scratch_bytes=512,
                          authenticated_trace_rows_per_backend=checks, independently_reconstructed_normalized_rows=normalized_checks,
                          bounded_summation_rows=observed_sums, archived_code_executed=False,
                          physical_hardware=False, universal_numeric_exactness=False, target_throughput_qualified=False,
                          current_sources_checked=require_current, contradiction_controls_rejected=controls)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-current', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    verify(args.require_current, args.self_test)
