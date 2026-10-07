#!/usr/bin/env python3
"""Capture every native-adapter PCM sample from a complete ADTS recording in QEMU.

Successful capture validates format/consumption/ownership, not cross-image
storage precision. Compare the candidate against a full-precision capture.
"""
import hashlib
import re
import sys

import run_aac_bfp16 as common
from run_aac_late_sbr import parse_log
from run_aac_late_sbr_capture import parse_reference
from compare_aac_sbr_gap_pcm import parse_gaps

RATES = (96000, 88200, 64000, 48000, 44100, 32000, 24000, 22050,
         16000, 12000, 11025, 8000, 7350)


def adts_core_rates(data):
    """Require full, single-raw-block ADTS frames; do not silently trim a capture."""
    offset, rates = 0, []
    while offset < len(data):
        header = data[offset:offset+7]
        if len(header) != 7 or header[0] != 255 or header[1] & 0xf6 != 0xf0:
            raise ValueError('Missing ADTS sync or partial header')
        index = (header[2] >> 2) & 15
        length = ((header[3] & 3) << 11) | (header[4] << 3) | (header[5] >> 5)
        if index >= len(RATES) or header[6] & 3:
            raise ValueError('Unsupported ADTS rate or multiple raw blocks in this capture test')
        if length < (7 if header[1] & 1 else 9) or offset+length > len(data):
            raise ValueError('Invalid length or partial ADTS payload')
        rates.append(RATES[index])
        offset += length
    if not rates:
        raise ValueError('Empty ADTS recording')
    return rates


def parse_recording(log, data=None):
    log = log.replace('\r\n', '\n')
    parse_gaps(log)  # Also requires full synthetic regression and image completion.
    begin = re.findall(r'^AAC_RECORD_BEGIN bytes=(\d+) rate=(\d+) channels=(\d+)$', log, re.MULTILINE)
    end = re.findall(r'^AAC_RECORD_PASS consumed=(\d+) frames=(\d+) channel_samples=(\d+) '
                     r'calls=(\d+) poison_patterns=2 heap=valid$', log, re.MULTILINE)
    if len(begin) != 1 or len(end) != 1:
        raise ValueError('Incomplete or duplicate recording run')
    size, rate, channels = map(int, begin[0])
    consumed, total_frames, samples, calls = map(int, end[0])
    if consumed != size or not size or not 1 <= channels <= 2 or rate not in RATES or calls < total_frames:
        raise ValueError('Invalid input consumption or format')
    rows = []
    for line in log.splitlines():
        if line.startswith('AAC_RECORD_PCM_FRAME '):
            m = re.fullmatch(r'AAC_RECORD_PCM_FRAME frame=(\d+) rate=(\d+) channels=(\d+) bytes=(\d+)', line)
            if not m:
                raise ValueError('Malformed recording frame')
            index, hz, ch, count = map(int, m.groups())
            if index != len(rows) or (hz, ch) != (rate, channels) or count not in (1024*channels*2, 2048*channels*2):
                raise ValueError('Wrong recording frame index, rate, channels or size')
            if rows and len(rows[-1]['pcm']) != rows[-1]['bytes']:
                raise ValueError('Incomplete previous recording frame')
            rows.append(dict(frame=index, rate=hz, channels=ch, bytes=count, pcm=bytearray()))
        elif line.startswith('AAC_RECORD_PCM_DATA '):
            m = re.fullmatch(r'AAC_RECORD_PCM_DATA frame=(\d+) offset=(\d+) hex=([0-9a-f]+)', line)
            if not m or not rows:
                raise ValueError('Malformed recording PCM chunk')
            index, offset = map(int, m.groups()[:2]); pcm = bytes.fromhex(m[3]); row = rows[-1]
            if index != row['frame'] or offset != len(row['pcm']) or len(pcm) != min(256, row['bytes']-offset):
                raise ValueError('Skipped, repeated or oversized recording PCM chunk')
            row['pcm'] += pcm
    if len(rows) != total_frames or any(len(r['pcm']) != r['bytes'] for r in rows):
        raise ValueError('Incomplete recording PCM')
    if sum(r['bytes']//2 for r in rows) != samples:
        raise ValueError('Wrong recording sample total')
    if data is not None:
        rates = adts_core_rates(data)
        if size != len(data) or len(rates) != total_frames:
            raise ValueError('Decoded frame count differs from complete ADTS input')
        for core, row in zip(rates, rows):
            if rate not in (core, core*2) or row['bytes'] != 1024*(rate//core)*channels*2:
                raise ValueError('Lost/doubled samples or unexpected resampling')
    raw = b''.join(row['pcm'] for row in rows)
    if not any(raw):
        raise ValueError('Silent capture cannot qualify PCM accuracy')
    return dict(bytes=size, rate=rate, channels=channels, frames=total_frames,
                channel_samples=samples, calls=calls, pcm_sha256=hashlib.sha256(raw).hexdigest()), rows


if __name__ == '__main__':
    parser = common.make_parser(__doc__, 'recording-capture')
    parser.add_argument('--full-precision', action='store_true')
    args = parser.parse_args()
    if not args.input:
        parser.error('--input must name a complete ADTS recording')
    data = args.input.read_bytes(); adts_core_rates(data)
    config = (args.build/'config/sdkconfig.h').read_text()
    def enabled(key): return '#define CONFIG_YORADIO_'+key+' 1\n' in config
    storage = ('AAC_HIGH_HISTORY', 'AAC_SMOOTHING_HISTORY', 'AAC_LOW_WORKSPACE', 'AAC_ASYMMETRIC_OWNER')
    if args.full_precision:
        if any(enabled(k) for k in (*storage, 'AAC_PS_PC16', 'QEMU_AAC_HIGH_HISTORY_PC19',
                                    'QEMU_AAC_BFP16_TEST', 'QEMU_AAC_PACKED_HISTORY_TEST')):
            parser.error('Reference must retain full-precision native histories')
    elif not all(enabled(k) for k in (*storage, 'QEMU_AAC_POINTER_AUDIT',
                  'QEMU_AAC_HIGH_HISTORY_PC19', 'QEMU_AAC_HIGH_HISTORY_PC19_SIDECAR')):
        parser.error('Candidate must use audited PC19 context storage')
    def check(log):
        result = parse_reference(log) if args.full_precision else parse_log(log, require_retention=True)
        record, _ = parse_recording(log, data)
        result.update(recording_capture=record, full_precision_history=args.full_precision,
                      recording_precision_qualified=False, production_qualified=False)
        return result
    code = common.run(args, log_parser=check, config_key='YORADIO_QEMU_AAC_LATE_SBR_CAPTURE')
    if not code:
        print('Recording capture valid; cross-image PCM precision comparison is still required.')
    sys.exit(code)
