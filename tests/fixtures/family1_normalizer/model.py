"""Independent integer model for one fixed enabled-normalizer profile.

No production DSP/codec code is imported. The existing Decimal module supplies
only the separately qualified final speaker/header/player projection.
"""
from array import array
from decimal import Decimal, ROUND_HALF_UP, localcontext
import hashlib
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PROFILE = dict(enabled=True, gain_db=20, target_dbfs=-20, time_ms=100,
               rate=48000, channels=8, volume=127, balance=0, header_gain_q8=1536)
FRAMES, RESET_FRAME = 9600, 5448


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def soft_limit(value):
    """Construct the rational LUT nodes independently; no captured table read."""
    sign, magnitude = (-1 if value < 0 else 1), abs(value)
    if magnitude > 28672:
        index, fraction = divmod(magnitude - 28672, 512)
        def node(k):
            excess = k * 512
            return 28672 + excess * 4095 // (excess + 4095)
        if index >= 584:
            magnitude = node(584)
        else:
            low, high = node(index), node(index + 1)
            magnitude = low + ((high - low) * fraction + 256) // 512
    return sign * min(32767, magnitude)


def normalize(pcm, resets=(), wrong=None):
    need(sys.byteorder == 'little' and len(pcm) == FRAMES * 8 * 2, 'complete fixed-profile C8 S16LE')
    need(list(resets) == sorted(set(resets)) and all(0 < x < FRAMES for x in resets), 'ordered explicit interior resets')
    need(wrong in (None, 'disabled', 'detector_first_two', 'process_first_two', 'gain_before_detector'), 'declared finite control')
    source = array('h'); source.frombytes(pcm)
    output = array('h'); gain, block_peak, count = 4096, 0, 0
    updates, detector_witness_frames = [], 0
    for frame in range(FRAMES):
        if frame in resets:
            gain, block_peak, count = 4096, 0, 0
        samples = source[frame * 8:(frame + 1) * 8]
        peak = max(abs(x) for x in samples)
        detector_witness_frames += peak > max(abs(x) for x in samples[:2])
        if wrong == 'disabled':
            output.extend(samples); continue
        if wrong == 'detector_first_two':
            peak = max(abs(x) for x in samples[:2])
        if wrong == 'gain_before_detector':
            # Header gain applied prematurely to the detector. User volume
            # remains in the final projection; this isolates the order error.
            with localcontext() as context:
                context.prec = 100
                factor = Decimal(10) ** (Decimal(1536) / 5120)
                peak = int((Decimal(peak) * factor).to_integral_value(rounding=ROUND_HALF_UP))
        block_peak = max(block_peak, peak); count += 1
        output.extend(soft_limit(sample * gain // 4096) if wrong != 'process_first_two' or c < 2 else sample
                      for c, sample in enumerate(samples))
        if count == 480:
            target = 4096 if block_peak < 128 else min(40960, max(410, 3277 * 4096 // block_peak))
            difference = target - gain
            gain += (1 if difference > 0 else -1) * ((abs(difference) + 9) // 10) if difference else 0
            updates.append(dict(after_frame=frame + 1, gain_q12=gain, peak=block_peak))
            block_peak, count = 0, 0
    body = output.tobytes()
    return body, dict(bytes=len(body), sha256=sha(body), updates=updates,
                      later_channel_detector_frames=detector_witness_frames,
                      resets=list(resets), tail_detector_frames=count)


def projection_module():
    path = ROOT / 'tests/prepare-cyd-family1-task-output.py'
    spec = importlib.util.spec_from_file_location('family1_normalizer_decimal_projection', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def final_pcm(normalized, module=None):
    module = module or projection_module()
    a, first = module.mono(normalized, 8, 1, 1536, 127, 100)
    b, second = module.mono(normalized, 8, 1, 1536, 127, 160)
    need(a == b and first == second, 'complete final mono stable at100/160 digits; zero tolerance')
    return a, first


def prepare(pcm, out):
    """Pure data preparation over independent direct-public reference bytes."""
    out = Path(out)
    need(out.is_dir() and not any(out.iterdir()), 'fresh empty caller-owned model output')
    projection = projection_module(); cases, witnesses = [], []
    for index, resets in [(1, (RESET_FRAME,)), (2, ())]:
        normalized, state = normalize(pcm, resets)
        mono, pin = final_pcm(normalized, projection)
        need(state['later_channel_detector_frames'] > 0 and any(x['gain_q12'] != 4096 for x in state['updates']), 'active adaptive all-channel fixture')
        (out / ('case' + str(index) + '.pcm')).write_bytes(mono)
        cases.append(dict(case=index, reset_frames=list(resets), normalized=state, final_pcm=pin))
        for wrong in ('disabled', 'detector_first_two', 'process_first_two', 'gain_before_detector'):
            candidate, unused = normalize(pcm, resets, wrong)
            rendered, bad = final_pcm(candidate, projection)
            count = sum(a != b for a, b in zip(array('h', mono), array('h', rendered)))
            need(count > 0 and bad['sha256'] != pin['sha256'], 'fixed wrong-model witness: ' + wrong)
            witnesses.append(dict(case=index, wrong=wrong, different_samples=count, wrong_sha256=bad['sha256']))
    return dict(passed=True, prepared_only=True, native_launch='UNRELEASED', native_executed=False,
                independent_integer_model=True, production_normalizer_imported=False,
                same_vendor_decoder_reference=True, independent_codec_conformance=False,
                profile=PROFILE, source_pcm=dict(bytes=len(pcm), sha256=sha(pcm)),
                decimal_precisions=[100, 160], new_tolerance=False, cases=cases, witnesses=witnesses)
