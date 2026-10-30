"""Verify the saved 120 ms synthetic Opus fixture and generation evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FIXTURE_SHA = 'b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def verify():
    manifest = json.loads((HERE / 'manifest.json').read_bytes())
    report_body = (HERE / 'evidence/generation-report.json').read_bytes()
    report = json.loads(report_body)
    need(report['passed'] and report['completed'] and not report['native_decoder_tested'] and
         not report['resize_retry_qualified'] and digest(report_body) == manifest['generation_report_sha256'],
         'actual terminal generation evidence without native resize claims')
    need(report['generator_sha256'] == digest((HERE / 'generate.py').read_bytes()), 'exact executed generator source')
    source = (ROOT / report['source']['path']).resolve()
    need(source.is_relative_to(ROOT / 'tests/fixtures/esp32c3_calibration') and
         source.stat().st_size == report['source']['bytes'] and digest(source.read_bytes()) == report['source']['sha256'],
         'complete unchanged original synthetic lossless source')
    need([row['name'] for row in report['commands']] ==
         ['version', 'encoder-help', 'source-decode', 'encode', 'repeat-encode', 'libopus-playback'],
         'complete unique generation and independent decode commands')
    for row in report['commands']:
        need(row['state'] == 'complete' and row['exit_status'] == 0 and row['pid'] > 0,
             'actual child terminal zero: ' + row['name'])
        for stream in ('stdout', 'stderr'):
            need(digest((HERE / 'evidence' / (row['name'] + '.' + stream + '.log')).read_bytes()) == row[stream + '_sha256'],
                 'every original generation log byte')
    need(report['source_pcm']['frames'] == 528000 and report['source_pcm']['bytes'] == 2112000 and
         report['playback']['bytes'] == 2112000 and report['repeated_encoding_byte_identical'],
         'complete original playback, independent libopus length and repeatability')
    fixture = (HERE / manifest['fixture']['file']).read_bytes()
    need(len(fixture) == report['fixture']['bytes'] == manifest['fixture']['bytes'] == 707097 and
         digest(fixture) == report['fixture']['sha256'] == manifest['fixture']['sha256'] == FIXTURE_SHA,
         'exact immutable encoded fixture')
    spec = importlib.util.spec_from_file_location('reviewed_long_opus_generator', HERE / 'generate.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    measured = module.audit(fixture)
    need(measured == report['audit'], 'independent repeat of every page CRC, packet extent and timeline')
    need(measured['maximum_packet_pcm16_bytes'] == 23040 > manifest['production_initial_pcm_capacity'] == 12288 and
         measured['audio_packet_count'] == 92 and measured['playback_pcm16_bytes'] == 2112000,
         'actual legal maximum-duration output boundary')
    rejected = []

    def reject(name, body):
        try:
            module.audit(body)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('invalid fixture accepted: ' + name)

    reject('crc_corruption', fixture[:-1] + bytes([fixture[-1] ^ 1]))
    reject('truncated_final_page', fixture[:-1])
    last_start = sum(row['encoded_bytes'] for row in measured['pages'][:-1])
    modified = bytearray(fixture)
    modified[last_start + 6:last_start + 14] = (measured['raw_frames'] + 1).to_bytes(8, 'little')
    modified[last_start + 22:last_start + 26] = bytes(4)
    modified[last_start + 22:last_start + 26] = module.crc(modified[last_start:]).to_bytes(4, 'little')
    reject('crc_valid_granule_past_decoded_audio', bytes(modified))
    first_audio = next(index for index, row in enumerate(measured['pages']) if row['completed_audio'])
    page_start = sum(row['encoded_bytes'] for row in measured['pages'][:first_audio])
    page_end = page_start + measured['pages'][first_audio]['encoded_bytes']
    packet_start = page_start + 27 + fixture[page_start + 26]
    need(fixture[packet_start] & 3 == 3, 'real code-3 packet selected for duration guard')
    for name, count in (('zero_frames', 0), ('over_120ms_packet', 7)):
        modified = bytearray(fixture)
        modified[packet_start + 1] = (modified[packet_start + 1] & 0xc0) | count
        modified[page_start + 22:page_start + 26] = bytes(4)
        modified[page_start + 22:page_start + 26] = module.crc(modified[page_start:page_end]).to_bytes(4, 'little')
        reject(name, bytes(modified))
    return dict(passed=True, fixture_sha256=FIXTURE_SHA, pages=measured['page_count'],
                audio_packets=measured['audio_packet_count'], packet_pcm_bytes=23040,
                playback_pcm_bytes=2112000, negative_guards=rejected,
                native_decoder_tested=False, resize_retry_qualified=False,
                ffmpeg_executed=False, archived_program_executed=False)


if __name__ == '__main__':
    print(json.dumps(verify()))
