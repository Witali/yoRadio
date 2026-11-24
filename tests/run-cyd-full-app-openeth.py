"""Boot the diagnostic CYD application and sample its real WebUI over QEMU OpenETH."""
import argparse
from contextlib import ExitStack
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import runpy
import shlex
import socket
import ssl
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
FATAL = re.compile(r'Guru Meditation|assert failed:|abort\(\) was called|watchdog got triggered|'
                   r'SPIFFS mount failed|Audio service failed|Radio control failed|Web server failed|'
                   r'opencores\.emac: no mem for receive buffer', re.I)
RX_WAIT = re.compile(r'CYD_OPENETH_RX_WAIT request=(\d+) heap=(\d+) largest=(\d+) dma=(\d+)')
OPUS_OPEN = re.compile(r'^CYD_OPENETH_OPUS_OPEN channels=(\d+) result=(-?\d+) free=(\d+) largest=(\d+) '
                       r'remaining=(\d+) remaining_largest=(\d+)$', re.M)
TLS_RX_EVENT = re.compile(r'^CYD_OPENETH_TLS_RX (loan|return)$', re.M)
RECLAIM_EVENT = re.compile(r'^CYD_OPENETH_RECLAIM ([a-z0-9_= ]+)$', re.M)
TLS_OVERLAP = re.compile(r'^CYD_OPENETH_TLS_OVERLAP heap_rx_before=(\d+) heap_rx_after=(\d+)$', re.M)
HEAP_RX_EVENT = re.compile(r'^CYD_OPENETH_TLS_HEAP_RX (loan|return)$', re.M)
# The pinned Opus fixture's EOS granule 528312 minus pre-skip 312 gives
# 528000 mono output samples. PDM pads to 512-sample writes and counts the
# 704 bias samples written after DMA preload, at two bytes per sample.
PDM_OPUS_EOF_BYTES = 1058176
OPUS_EOF_PCM_FRAMES = 528000
FULL_TLS_PLAINTEXT_BYTES = 16384
TLS12_AES_GCM_OVERHEAD = 24
# An exact SPIFFS asset read can spend several host seconds scanning flash
# on the emulated ESP32 before the HTTP response starts.
WEB_ASSET_TIMEOUT_SECONDS = 25


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def flash_parts(build):
    spec = json.loads((build / 'flasher_args.json').read_bytes())
    if spec['extra_esptool_args']['chip'] != 'esp32' or spec['flash_settings']['flash_size'] != '4MB':
        raise ValueError('Expected a classic ESP32 4 MiB image')
    flash = bytearray(b'\xff' * (4 * 1024 * 1024))
    parts = []
    end = 0
    for address, name in sorted((int(offset, 0), name) for offset, name in spec['flash_files'].items()):
        source = (build / name).resolve(strict=True)
        if not source.is_relative_to(build):
            raise ValueError('Flash component is outside the diagnostic build')
        body = source.read_bytes()
        if not end <= address < address + len(body) <= len(flash):
            raise ValueError('Overlapping or invalid flash component extent')
        end = address + len(body)
        flash[address:end] = body
        parts.append(dict(file=source.relative_to(build).as_posix(), offset=address,
                          bytes=len(body), sha256=digest(body)))
    if {p['offset'] for p in parts} != {0x1000, 0x8000, 0xe000, 0x10000, 0x370000}:
        raise ValueError('Unexpected bootloader, application or SPIFFS layout')
    return flash, parts


def request(port, uri, method='GET', *, timeout=8):
    persistent = isinstance(port, http.client.HTTPSConnection)
    connection = port if persistent else http.client.HTTPConnection('127.0.0.1', port, timeout=timeout)
    if persistent:
        connection.timeout = timeout
        if connection.sock:
            connection.sock.settimeout(timeout)
    try:
        connection.request(method, uri)
        response = connection.getresponse()
        data = response.read(64 * 1024 + 1)
        if response.status != 200 or len(data) > 64 * 1024:
            raise RuntimeError(f'{uri}: HTTP {response.status}, {len(data)} bytes')
        return data
    except TimeoutError as error:
        raise TimeoutError(f'{method} {uri} timed out') from error
    finally:
        if not persistent:
            connection.close()


def sample(port):
    report = json.loads(request(port, '/api/native/health'))
    if report['schema'] != 1 or report['cores'] != 2:
        raise RuntimeError('Unexpected production health endpoint schema or core count')
    if not 0 < report['minimum_heap'] <= report['heap'] or not 0 < report['largest'] <= report['heap']:
        raise RuntimeError('Invalid production heap sample')
    sample = {key: report[key] for key in ('boot_id', 'reset_reason', 'uptime_ms', 'heap', 'largest',
                                          'minimum_heap', 'tasks', 'memory', 'cpu',
                                          'allocation_failures', 'last_allocation_failure', 'decoder_failure',
                                          'stream_failure', 'output', 'output_driver')}
    if 'input' in report:
        sample['input'] = report['input']
    return sample


def require_clean_health(report, expected_allocation_failures=0):
    for group, key in (('decoder_failure', 'sequence'), ('stream_failure', 'sequence'), ('output', 'failures')):
        if report[group][key] != 0:
            raise RuntimeError(f'Unexpected {group} counter')
    if report['allocation_failures'] != expected_allocation_failures:
        raise RuntimeError('Unexpected allocation failure count')


def finalize_webui_checks(port, guest, report, websocket_peers=None, *, through_eof=False):
    if websocket_peers is not None:
        closed = websocket_peers.close()
        report['websocket'] = websocket_peers.summary()
        if not closed:
            raise RuntimeError('A live WebSocket peer failed or did not close')
    if not through_eof or not report['passed']:
        return
    if guest is None or guest.poll() is not None:
        raise RuntimeError('Guest stopped before the final post-EOF resource check')

    # The EOF observer has already checked the final asset and peer commands.
    # Close peers first, then make health the last WebUI request so it also
    # covers those operations and this final status read while QEMU is live.
    status = json.loads(request(port, '/api/native/status'))
    if not isinstance(status, dict):
        raise RuntimeError('Invalid final post-EOF status')
    report['post_eof_status'] = {key: status.get(key) for key in
                               ('audio', 'connecting', 'format', 'generation')}
    final = sample(port)
    report['post_eof_health'] = final
    expected_allocations = int('input_reclaim_pcm_reference' in report)
    require_clean_health(final, expected_allocation_failures=expected_allocations)
    if (any(final['output'][key] for key in ('write_errors', 'configure_errors', 'flush_errors')) or
            any(final['output_driver'][key] for key in ('errors', 'timeouts', 'short_writes', 'saturated'))):
        raise RuntimeError('Unexpected output fault after the final WebUI/peer checks')
    eof = report['eof_health']
    if (final['boot_id'] != eof['boot_id'] or final['boot_id'] != report['health'][0]['boot_id'] or
            final['uptime_ms'] < eof['uptime_ms']):
        raise RuntimeError('Guest reset during the final post-EOF WebUI/peer checks')
    if report['post_eof_status'] != report['eof_status']:
        raise RuntimeError('Playback state or generation changed after EOF')
    if guest.poll() is not None:
        raise RuntimeError('Guest stopped during the final post-EOF resource check')
    report['observed'].append('clean resources after final WebUI and peer closure')


def observe_tls_record_headers(context, lengths):
    def record(_connection, direction, _version, content_type, _message_type, header):
        # CPython passes OpenSSL's record-header messages as type 0x100.
        # Retain only outgoing TLS 1.2 application ciphertext lengths.
        if (direction == 'write' and content_type == 0x100 and len(header) == 5 and
                header[:3] == b'\x17\x03\x03' and len(lengths) < 128):
            lengths.append(int.from_bytes(header[3:], 'big'))

    context._msg_callback = record


def flac_streaminfo(data):
    # RFC 9639 section 8.2. The first metadata block is STREAMINFO.
    if len(data) < 42 or data[:4] != b'fLaC' or data[4] & 0x7f or data[5:8] != b'\x00\x00\x22':
        raise ValueError('Missing FLAC STREAMINFO')
    fields = int.from_bytes(data[18:26], 'big')
    rate = fields >> 44
    channels = ((fields >> 41) & 7) + 1
    bits = ((fields >> 36) & 31) + 1
    frames = fields & ((1 << 36) - 1)
    md5 = data[26:42]
    if (rate, channels, bits) != (48000, 2, 16) or not frames or not any(md5):
        raise ValueError('Expected 48 kHz stereo PCM16 FLAC with sample count and MD5')
    return frames, md5.hex()


def station_fixture(codec):
    folder = ROOT / 'tests/fixtures/esp32c3_calibration'
    filename, mime = {'opus': ('opus-510.ogg', 'audio/ogg'),
                      'vorbis': ('vorbis-q10.ogg', 'audio/ogg'),
                      'flac': ('flac-level8.flac', 'audio/flac')}[codec]
    fixture, = [row for row in json.loads((folder / 'manifest.json').read_bytes())['fixtures'] if row['file'] == filename]
    data = (folder / fixture['file']).read_bytes()
    if digest(data) != fixture['sha256']:
        raise ValueError(f'{filename} differs from its fixture manifest')
    frames, md5 = flac_streaminfo(data) if codec == 'flac' else (528000, None)
    result = dict(data=data, seconds=frames / 48000, codec=codec, mime=mime,
                  pcm_frames=frames, pcm_channels=2, pcm_md5=md5)
    if codec == 'vorbis':
        # Complete direct-public Espressif PCM, qualified on LX6 and RV32:
        # results/cyd-espressif-reuse-20261030/NATIVE.md. This is an integration
        # identity, not an independent numeric Vorbis-conformance oracle.
        result['pcm_sha256'] = 'e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910'
        result['source_channels'] = 2
    return result


def helix_mp3_fixture(mono):
    segment = (ROOT / 'tests/fixtures/helix_mono/mpeg1.mp3').read_bytes()
    if digest(segment) != 'd26ac21143727b0cd9305413748ebf95954e3c93b7e647f384c508f06c26ee35':
        raise ValueError('Unexpected 48 kHz Helix M/S test segment')
    # 18 MPEG-1 Layer III frames per segment with 1152 samples each.
    repetitions = 28
    frames = repetitions * 18 * 1152
    return dict(data=segment * repetitions, seconds=frames / 48000, codec='mp3',
                mime='audio/mpeg', pcm_frames=frames, pcm_channels=1 if mono else 2,
                pcm_md5=None, source_channels=2)


def aac_fixture(profile):
    if profile == 'lc':
        folder = ROOT / 'tests/fixtures/esp32c3_calibration'
        filename = 'aac-lc-320.aac'
        info, = [row for row in json.loads((folder / 'manifest.json').read_bytes())['fixtures']
                 if row['file'] == filename]
        repetitions, core_rate = 1, 48000
    elif profile == 'he':
        folder = ROOT / 'tests/fixtures/aac_stream_format'
        filename = 'he-48000-stereo.aac'
        info = json.loads((folder / 'manifest.json').read_bytes())['files'][filename]
        repetitions, core_rate = 20, 24000
    else:
        raise ValueError('Unknown AAC fixture profile')
    segment = (folder / filename).read_bytes()
    if digest(segment) != info['sha256']:
        raise ValueError('AAC source differs from its fixture manifest')
    at, adts_frames = 0, 0
    rates = (96000, 88200, 64000, 48000, 44100, 32000, 24000, 22050,
             16000, 12000, 11025, 8000, 7350)
    while at < len(segment):
        head = segment[at:at + 7]
        if len(head) != 7 or head[0] != 255 or head[1] & 246 != 240:
            raise ValueError('Incomplete AAC fixture ADTS header')
        rate_index = (head[2] >> 2) & 15
        channels = ((head[2] & 1) << 2) | (head[3] >> 6)
        size = ((head[3] & 3) << 11) | (head[4] << 3) | (head[5] >> 5)
        if (rate_index >= len(rates) or rates[rate_index] != core_rate or channels != 2 or
                size < (7 if head[1] & 1 else 9) or size > len(segment) - at or head[6] & 3):
            raise ValueError('Unexpected AAC fixture ADTS geometry')
        at += size
        adts_frames += 1
    if not adts_frames:
        raise ValueError('Empty AAC fixture')
    frames = adts_frames * repetitions * 1024 * (48000 // core_rate)
    # Measured from complete direct-public LX6 reference decoding; never
    # concatenate the short segment's PCM digests to construct this identity.
    reference = {'lc': '95c66ea66a1af8cfdd70a38441f83a2599b7e690ccdd336bb462b8c41ef45ff0',
                 'he': '44d9a67ecc2e6a6d382951442fb7bdf687510c784e2e9137036cbe0a38b6f362'}
    return dict(data=segment * repetitions, seconds=frames / 48000, codec='aac', mime='audio/aac',
                pcm_frames=frames, pcm_channels=2, pcm_rate=48000, pcm_md5=None,
                pcm_sha256=reference[profile], aac_profile=profile,
                adts_frames=adts_frames * repetitions, core_rate=core_rate,
                source_sha256=info['sha256'], repetitions=repetitions)


def ogg_page(header, crc, sequence, flags, granule, laces, body):
    if len(laces) > 255 or sum(laces) != len(body):
        raise ValueError('Invalid lacing for the Ogg fixture')
    page = bytearray(header[:27])
    page[5] = flags
    page[6:14] = granule.to_bytes(8, 'little')
    page[18:22] = sequence.to_bytes(4, 'little')
    page[22:26] = bytes(4)
    page[26] = len(laces)
    page += laces + body
    page[22:26] = crc(page).to_bytes(4, 'little')
    return bytes(page)


def ogg_laces(packet):
    return bytes([255]) * (len(packet) // 255) + bytes((len(packet) % 255,))


def shorten_opus_pages(fixture):
    original = fixture['data']
    reader = runpy.run_path(str(ROOT / 'tests/fixtures/opus_header_gain/generate.py'))
    parse, crc = reader['parse'], reader['crc']
    pages, packets = parse(original)
    audio = packets[2:]
    final = int.from_bytes(original[pages[-1]['offset'] + 6:pages[-1]['offset'] + 14], 'little')
    # This pinned fixture contains 551 audio packets of 960 samples each.
    if len(audio) != 551 or final != 528312:
        raise ValueError('Unexpected source for the short-page Opus fixture')
    result = [original[:pages[1]['end']]]
    for first in range(0, len(audio), 8):
        group = audio[first:first + 8]
        finished = first + len(group)
        eos = finished == len(audio)
        lace = b''.join(map(ogg_laces, group))
        result.append(ogg_page(original, crc, first // 8 + 2, 4 if eos else 0,
                               final if eos else finished * 960, lace, b''.join(group)))
    body = b''.join(result)
    shorter, copied = parse(body)
    if copied != packets:
        raise ValueError('Ogg repaging altered the original packets')
    fixture['data'] = body
    return dict(sha256=digest(body), pages=len(shorter),
                largest_page=max(page['end'] - page['offset'] for page in shorter))


def pad_opus_frame(packet, length):
    if packet[0] & 3 or length <= len(packet) + 2:
        raise ValueError('Expected one Opus frame and room for Code 3 padding')
    # Code 3 with one CBR frame. Each 255 in the padding length uses one byte
    # of header and adds 254 bytes of ignored trailing data (RFC 6716 §3.2.5).
    extended, last = divmod(length - len(packet) - 2, 255)
    body = (bytes((packet[0] | 3, 0x41)) + b'\xff' * extended + bytes((last,))
            + packet[1:] + bytes(extended * 254 + last))
    if len(body) != length:
        raise ValueError('Unexpected padded Opus packet length')
    return body


def opus_page_boundary(fixture, boundary):
    original = fixture['data']
    reader = runpy.run_path(str(ROOT / 'tests/fixtures/opus_header_gain/generate.py'))
    parse, crc = reader['parse'], reader['crc']
    pages, packets = parse(original)
    final = int.from_bytes(original[pages[-1]['offset'] + 6:pages[-1]['offset'] + 14], 'little')
    if len(packets) != 553 or final != 528312:
        raise ValueError('Unexpected source for the page boundary fixture')
    if boundary == 'tags':
        packets[1] = packets[1].ljust(65025, b'\0')
        result = [original[:pages[0]['end']],
                  ogg_page(original, crc, 1, 0, 2**64 - 1, b'\xff' * 255, packets[1]),
                  ogg_page(original, crc, 2, 1, 0, b'\0', b'')]
        for page in pages[2:]:
            header = original[page['offset']:page['payload']]
            result.append(ogg_page(header, crc, len(result), header[5],
                                   int.from_bytes(header[6:14], 'little'),
                                   header[27:], original[page['payload']:page['end']]))
        maximum = 65307
    elif boundary == 'audio':
        # An audio page of 65,306 bytes has one completed lace of 254 and all
        # other laces 255. The continued packet stays under the 61,440 B cap.
        packets[2] = pad_opus_frame(packets[2], 3824)
        packets[3] = pad_opus_frame(packets[3], 61255)
        result = [original[:pages[1]['end']],
                  ogg_page(original, crc, 2, 0, 960, ogg_laces(packets[2]) + b'\xff'*240,
                           packets[2] + packets[3][:61200]),
                  ogg_page(original, crc, 3, 1, 1920, bytes((55,)), packets[3][61200:])]
        for first in range(4, len(packets), 42):
            group = packets[first:first + 42]
            finished = first + len(group)
            eos = finished == len(packets)
            result.append(ogg_page(original, crc, len(result) + 1, 4 if eos else 0,
                                   final if eos else (finished - 2) * 960,
                                   b''.join(map(ogg_laces, group)), b''.join(group)))
        maximum = 65306
    else:
        raise ValueError('Unknown Ogg Opus boundary fixture')
    body = b''.join(result)
    checked, copied = parse(body)
    if copied != packets or max(p['end'] - p['offset'] for p in checked) != maximum:
        raise ValueError('Ogg boundary fixture differs from the expected packets or page geometry')
    fixture['data'] = body
    return dict(boundary=boundary, sha256=digest(body), pages=len(checked), largest_page=maximum)


def family1_fixture(manifest):
    manifest = manifest.resolve(strict=True)
    if not manifest.is_relative_to(ROOT / '.build'):
        raise ValueError('Use a locally generated Family 1 fixture under .build')
    spec = json.loads(manifest.read_bytes())
    file = (manifest.parent / 'family1.ogg').resolve(strict=True)
    if file.parent != manifest.parent or spec['file'] != file.name:
        raise ValueError('Family 1 manifest must bind its adjacent Ogg file')
    body = file.read_bytes()
    if len(body) != spec['bytes'] or digest(body) != spec['sha256']:
        raise ValueError('Family 1 fixture differs from the manifest')
    channels = spec['channels']
    # The generator writes one complete Opus identification packet on the BOS page.
    if (channels not in (4, 6, 8) or len(body) < 49 + channels or body[:6] != b'OggS\0\x02' or
            body[26:28] != bytes((1, 21 + channels)) or
            body[28:38] != b'OpusHead' + bytes((1, channels)) or body[46] != 1):
        raise ValueError('Expected a four-, six- or eight-channel Opus Family 1 stream')
    if (spec['packet_ms'] not in (20, 120) or spec['frames'] != 14 * 48000 or
            len(spec['metrics']) != channels or any(
                type(row[key]) is not int or row[key] <= 0
                for row in spec['metrics'] for key in ('energy', 'crossings'))):
        raise ValueError('Unexpected Family 1 fixture geometry or reference metrics')
    return dict(data=body, seconds=spec['frames'] / 48000, codec='opus', mime='audio/ogg',
                pcm_frames=spec['frames'], pcm_channels=channels, pcm_md5=None, family1=spec)


def tls_station(material, fixture, wire_lengths=None):
    sys.path.insert(0, str(ROOT / 'tools'))
    from audio_test_server.server import Server

    chunk_bytes = 1024 if wire_lengths is None else FULL_TLS_PLAINTEXT_BYTES
    server = Server('127.0.0.1', 0, {'station': fixture},
                    material / 'server.pem', material / 'server-key.pem', pacing_ratio=0.5, chunk_bytes=chunk_bytes)
    if wire_lengths is not None:
        observe_tls_record_headers(server.http.socket.context, wire_lengths)
    return server


def require_full_tls_records(event, body_bytes, wire_lengths):
    full, tail = divmod(body_bytes, FULL_TLS_PLAINTEXT_BYTES)
    expected = [FULL_TLS_PLAINTEXT_BYTES + TLS12_AES_GCM_OVERHEAD] * full
    if tail:
        expected.append(tail + TLS12_AES_GCM_OVERHEAD)
    gcm_ciphers = ('ECDHE-RSA-AES128-GCM-SHA256', 'ECDHE-RSA-AES256-GCM-SHA384')
    if (not full or event['tls_version'] != 'TLSv1.2' or event['tls_cipher'] not in gcm_ciphers or
            not wire_lengths or not TLS12_AES_GCM_OVERHEAD < wire_lengths[0] < expected[0] or
            wire_lengths[1:] != expected):
        raise RuntimeError('Missing exact TLS 1.2 AES-GCM file record evidence')


def check_asset(port):
    expected = (ROOT / 'yoRadio/data/www/script.js.gz').read_bytes()
    data = request(port, '/script.js', timeout=WEB_ASSET_TIMEOUT_SECONDS)
    if data != expected:
        raise RuntimeError('WebUI did not serve the exact packaged SPIFFS asset')
    return dict(bytes=len(data), sha256=digest(data))


def guest_log(log_path):
    if log_path.stat().st_size > 2 * 1024 * 1024:
        raise RuntimeError('QEMU UART log exceeded its bound')
    return log_path.read_text(encoding='utf-8', errors='replace')


def pcm_probe_progress(uart):
    progress = re.findall(r'^CYD_OPENETH_PCM_PROGRESS frames=(\d+)\s*$', uart, re.M)
    return int(progress[-1]) if progress else 0


def pcm_probe_flushes(uart):
    return [dict(frames=int(frames), status=int(status)) for frames, status in
            re.findall(r'^CYD_OPENETH_PCM_FLUSH frames=(\d+) status=(-?\d+)\s*$', uart, re.M)]


def uses_pcm_probe(backend, fixture):
    return backend != 'pdm' or fixture['codec'] != 'opus' or 'family1' in fixture


def output_progress(health, uart, pcm_probe):
    if not pcm_probe:
        return health['output_driver']['written_bytes']
    return pcm_probe_progress(uart)


def require_family1_metrics(uart, reference_metrics):
    rows = re.findall(r'^CYD_OPENETH_PCM_CHANNEL index=(\d+) energy=(\d+) crossings=(\d+)\s*$',
                      uart, re.M)
    measured = [(int(energy), int(crossings)) for index, energy, crossings in rows]
    if [int(index) for index, _, _ in rows] != list(range(len(reference_metrics))):
        raise RuntimeError('Missing ordered PCM metrics for all Family 1 channels')
    for index, ((energy, crossings), reference) in enumerate(zip(measured, reference_metrics)):
        if (abs(energy - reference['energy']) * 100 > reference['energy'] * 5 or
                abs(crossings - reference['crossings']) * 100 > reference['crossings'] * 2):
            raise RuntimeError(f'Family 1 channel {index} disagrees with the libopus reference')
    return [dict(energy=energy, crossings=crossings) for energy, crossings in measured]


def observe_eof(port, server, event, guest, log_path, generation, report, web_socket=None, websocket_peers=None):
    backend = report['audio_backend']
    fixture = server.fixtures['station']
    # The legacy driver emits x16 stereo words. The model caps the DAC clock
    # at 96 kHz and consumes one 16-bit slot per tick.
    until = time.monotonic() + (360 if backend == 'legacy_dac' else 90)
    while time.monotonic() < until:
        if FATAL.search(guest_log(log_path)) or guest.poll() is not None:
            raise RuntimeError('Guest stopped or logged a failure before EOF')
        status = json.loads(request(port, '/api/native/status'))
        if status['generation'] != generation:
            raise RuntimeError('Playback changed generation before EOF')
        if not status['audio'] and not status['connecting']:
            report['eof_status'] = {key: status[key] for key in ('audio', 'connecting', 'format', 'generation')}
            if status['format'] != 'stream ended':
                raise RuntimeError(f"Playback ended as {status['format']!r}")
            if event['complete']:
                break
        time.sleep(0.75)
    else:
        raise RuntimeError('Guest EOF and full TLS response were not both observed')

    final = sample(port)
    report['eof_health'] = final
    driver = final['output_driver']
    body_bytes = len(fixture['data'])
    if event['sent'] != body_bytes:
        raise RuntimeError('TLS peer did not write the exact fixture length')
    if 'tls_application_payload_lengths' in report:
        if len(server.events) != 1:
            raise RuntimeError('Expected a single full-record TLS connection')
        require_full_tls_records(event, body_bytes, report['tls_application_payload_lengths'])
        report['observed'].append('full-sized TLS 1.2 records')
    if not uses_pcm_probe(backend, fixture):
        if not driver['requested_bytes'] == driver['written_bytes'] == PDM_OPUS_EOF_BYTES:
            raise RuntimeError('Unexpected PDM byte count after EOF')
    else:
        uart = guest_log(log_path)
        if pcm_probe_flushes(uart) != [dict(frames=fixture['pcm_frames'], status=0)]:
            raise RuntimeError('Unexpected decoded PCM frame count or flush result after EOF')
        if not 0 < driver['requested_bytes'] == driver['written_bytes']:
            raise RuntimeError('Incomplete driver writes after EOF')
        if 'family1' in fixture:
            report['family1_pcm_metrics'] = require_family1_metrics(uart, fixture['family1']['metrics'])
        elif fixture.get('pcm_sha256') is not None:
            pcm_digests = re.findall(r'^CYD_OPENETH_PCM_SHA256 ([0-9a-f]{64})\s*$', uart, re.M)
            if pcm_digests != [fixture['pcm_sha256']]:
                raise RuntimeError('Decoded PCM differs from the complete public decoder SHA-256')
            report['pcm_sha256'] = pcm_digests[0]
        elif fixture['pcm_md5'] is not None or fixture['codec'] == 'mp3':
            pcm_digests = re.findall(r'^CYD_OPENETH_PCM_MD5 ([0-9a-f]{32})\s*$', uart, re.M)
            if fixture['pcm_md5'] is not None and pcm_digests != [fixture['pcm_md5']]:
                raise RuntimeError('Decoded PCM differs from FLAC STREAMINFO MD5')
            if len(pcm_digests) != 1:
                raise RuntimeError('Expected a single PCM MD5 after EOF')
            report['pcm_md5'] = pcm_digests[0]
    report['observed'] += ['complete TLS response', 'ordered EOF with exact output count']
    if any(driver[key] for key in ('errors', 'timeouts', 'short_writes', 'saturated')):
        raise RuntimeError('Unexpected audio driver fault after EOF')
    if web_socket is not None:
        if port.sock is not web_socket:
            raise RuntimeError('WebUI TLS socket changed during the overlap run')
        report['web_tls_connection_preserved'] = True
    report['web_asset_after_eof'] = check_asset(port)
    if websocket_peers is not None:
        websocket_peers.require_status('eof', audio=False, generation=generation)
    report['observed'].append('WebUI after EOF')
    reference_md5 = report.get('input_reclaim_pcm_reference')
    if reference_md5 is not None:
        uart = guest_log(log_path)
        if pcm_probe_flushes(uart) != [dict(frames=OPUS_EOF_PCM_FRAMES, status=0)]:
            raise RuntimeError('Unexpected decoded PCM count after reclaim')
        recorded = re.findall(r'^CYD_OPENETH_PCM_MD5 ([0-9a-f]{32})\s*$', uart, re.M)
        if recorded != [reference_md5]:
            raise RuntimeError('PCM differs from the same stream decoded without allocator pressure')
        if TLS_RX_EVENT.findall(uart) != ['loan', 'return']:
            raise RuntimeError('Expected the static RX reserve to stay loaned until playback ended')
        require_clean_health(final, expected_allocation_failures=1)
        report['pcm_md5'] = recorded[0]
        report['observed'] += ['identical PCM after input reclaim', 'static RX returned at EOF']
    else:
        require_clean_health(final)
    if web_socket is not None:
        def web_rx_returned(uart):
            activity = HEAP_RX_EVENT.findall(uart)
            loans = 0
            for event in activity:
                loans += 1 if event == 'loan' else -1
                if loans < 0:
                    raise RuntimeError('Unmatched HTTPS RX release')
            return len(activity) // 2 if activity and loans == 0 else None
        report['web_heap_rx_releases'] = wait_for_observation(
            guest, log_path, web_rx_returned, 'HTTPS RX release after the final static response', timeout=15)


def start_station(port):
    radio = json.loads(request(port, '/api/native/radio'))
    if radio['count'] != 1 or radio['station'] != 'OpenETH fixture':
        raise RuntimeError('The expected SPIFFS station was not loaded')
    request(port, '/api/native/radio?action=play&station=1', 'POST')


def wait_for_observation(guest, log_path, observe, description, timeout=40):
    until = time.monotonic() + timeout
    while time.monotonic() < until:
        uart = guest_log(log_path)
        if FATAL.search(uart) or guest.poll() is not None:
            raise RuntimeError(f'Guest stopped or logged a failure while waiting for {description}')
        result = observe(uart)
        if result is not None:
            return result
        time.sleep(0.2)
    raise RuntimeError(f'Did not observe {description}')


def observe_radio_ota_lifecycle(port, server, guest, log_path, report, image):
    sys.path.insert(0, str(ROOT))
    from tools.cyd_tests.ota import ESP_RST_SW, multipart, upload

    origin = f'http://127.0.0.1:{port}'
    boot = report['health'][-1]['boot_id']
    original = json.loads(request(port, '/api/native/ota'))
    if original['partition'] != 'app0' or len(image) > original['max_size']:
        raise RuntimeError('Expected the staged OTA image in slot app0 with a spare slot')
    phases = report['ota_lifecycle'] = {}

    def active(previous_generation, session):
        def observe(uart):
            status = json.loads(request(port, '/api/native/status'))
            if (not status['audio'] or status['generation'] == previous_generation
                    or status['codec'] != 'OGG' or status['pcm_channels'] != 2):
                return None
            if TLS_RX_EVENT.findall(uart) != ['loan', 'return'] * (session - 1) + ['loan']:
                return None
            if not pcm_probe_progress(uart.rsplit('CYD_OPENETH_TLS_RX loan', 1)[-1]):
                return None
            if len(server.events) != session:
                return None
            event = server.events[-1]
            if event.get('tls_version') != 'TLSv1.2' or not event['sent'] or event['complete']:
                return None
            health = sample(port)
            require_clean_health(health)
            return status['generation'], health
        return wait_for_observation(guest, log_path, observe, f'PCM and reserved RX in TLS session {session}')

    def stop(session):
        request(port, '/api/native/radio?action=stop', 'POST')

        def stopped(uart):
            status = json.loads(request(port, '/api/native/status'))
            if (not status['audio'] and not status['connecting'] and status['format'] == 'stopped'
                    and TLS_RX_EVENT.findall(uart) == ['loan', 'return'] * session):
                health = sample(port)
                require_clean_health(health)
                return health
            return None
        return wait_for_observation(guest, log_path, stopped, f'Stop and return of RX from TLS session {session}')

    request(port, '/api/native/radio?action=smartstart&enabled=0', 'POST')
    start_station(port)
    first, _ = active(None, 1)
    stopped = stop(1)
    if stopped['boot_id'] != boot:
        raise RuntimeError('Unexpected reboot during Stop')
    start_station(port)
    second, _ = active(first, 2)
    phases['stop_and_reconnect'] = dict(first_generation=first, next_generation=second,
                                        released_heap=stopped['heap'])
    report['observed'].append('Stop returns TLS RX and a new Play borrows it again')

    rejected = upload(origin, multipart(image[:8192]))
    phases['truncated_upload'] = dict(status=rejected.status, sent_bytes=rejected.sent_bytes)
    if (rejected.status, rejected.body) != (400, b'Firmware image verification failed'):
        raise RuntimeError('Expected the incomplete application to reach OTA image verification and fail')
    resumed, playing = active(second, 3)
    if playing['boot_id'] != boot or json.loads(request(port, '/api/native/ota')) != original:
        raise RuntimeError('Truncated OTA changed the boot or running application')
    if check_asset(port) != report['web_asset']:
        raise RuntimeError('Unexpected WebUI asset after aborted OTA')
    phases['truncated_upload']['resumed_generation'] = resumed
    report['observed'].append('OTA verification failure resumes radio in the same boot')

    status = json.loads(request(port, '/api/native/status'))
    if not status['audio'] or status['generation'] != resumed or server.events[-1]['complete']:
        raise RuntimeError('The resumed TLS station must be active when starting the complete OTA')
    accepted = upload(origin, multipart(image))
    phases['complete_upload'] = dict(status=accepted.status, sent_bytes=accepted.sent_bytes)
    if (accepted.status, accepted.body) != (200, b'OK'):
        raise RuntimeError(f'Complete OTA returned HTTP {accepted.status}')

    def rebooted(uart):
        try:
            health = sample(port)
        except (OSError, http.client.HTTPException):
            return None
        if health['boot_id'] == boot:
            return None
        installed = json.loads(request(port, '/api/native/ota'))
        if health['reset_reason'] != ESP_RST_SW or installed['partition'] != 'app1':
            raise RuntimeError('Expected a software restart into the alternate OTA slot')
        if installed['app_elf_sha256'] != original['app_elf_sha256']:
            raise RuntimeError('OTA image ELF hash differs from the uploaded application')
        if TLS_RX_EVENT.findall(uart) != ['loan', 'return'] * 3:
            raise RuntimeError('Radio did not release reserved RX before OTA restart')
        require_clean_health(health)
        return health

    booted = wait_for_observation(guest, log_path, rebooted, 'WebUI in alternate OTA slot', timeout=100)
    if check_asset(port) != report['web_asset']:
        raise RuntimeError('Unexpected WebUI asset after the OTA restart')
    start_station(port)
    fourth, reloaded = active(None, 4)
    if booted['boot_id'] != reloaded['boot_id']:
        raise RuntimeError('Unexpected second reboot after OTA')
    stop(4)
    phases['complete_upload'].update(partition='app1', reset_reason=booted['reset_reason'],
                                      playback_generation=fourth)
    phases['reserved_rx_events'] = TLS_RX_EVENT.findall(guest_log(log_path))
    report['observed'] += ['same-image OTA activates the alternate slot and restarts',
                           'post-OTA WebUI and fresh TLS audio']


def observe_channel_rejection(port, server, guest, log_path, report):
    start_station(port)
    until = time.monotonic() + 30
    status = None
    while time.monotonic() < until:
        uart = guest_log(log_path)
        if FATAL.search(uart) or guest.poll() is not None:
            raise RuntimeError('Guest stopped or logged a failure during channel rejection')
        status = json.loads(request(port, '/api/native/status'))
        if not status['audio'] and status['format'] == 'audio supports up to two channels':
            break
        time.sleep(0.2)
    else:
        raise RuntimeError(f'Channel limit status missing before the deadline: {status["format"]}')
    rejected = sample(port)
    fault = rejected['decoder_failure']
    channels = server.fixtures['station']['pcm_channels']
    if (fault['sequence'] != 1 or fault['completion'] != 12 or fault['result'] != channels
            or fault['generation'] != status['generation'] or rejected['allocation_failures']
            or rejected['stream_failure']['sequence'] or rejected['output']['failures']
            or rejected['output_driver']['written_bytes'] != report['health'][-1]['output_driver']['written_bytes']
            or OPUS_OPEN.search(uart)):
        raise RuntimeError('Expected channel rejection before decoder allocation or PCM output')
    peers = [event for event in server.events if event.get('tls_version') and event['sent'] > 0]
    if len(peers) != 1:
        raise RuntimeError('Expected one actual TLS audio response before channel rejection')
    report['channel_rejection'] = fault
    report['web_asset_after_rejection'] = check_asset(port)
    report['observed'] += ['encoded channel limit over verified TLS', 'WebUI after channel rejection']


def observe_input_reclaim(health, uart):
    event, = RECLAIM_EVENT.findall(uart)
    proof = {key: int(value) for key, value in (field.split('=') for field in event.split())}
    released = proof['released_after'] - proof['released_before']
    if not (0 < proof['request'] and proof['largest'] < proof['request'] and proof['recovered'] == 1
            and 0 < released <= proof['budget']
            and proof['minimum'] <= proof['resident_after'] == proof['resident_before'] - released):
        raise RuntimeError('The failed Mbed TLS allocation did not recover through bounded idle-slot release')
    if (health['last_allocation_failure'] != {'size': proof['request'], 'caps': proof['caps']}
            or health['input']['released'] != proof['released_after']
            or TLS_RX_EVENT.findall(uart) != ['loan']):
        raise RuntimeError('Missing allocator, live RX or production input-pool evidence for reclaim')
    require_clean_health(health, expected_allocation_failures=1)
    return proof


def observe_playback(port, server, guest, log_path, report, through_eof, web_socket=None, websocket_peers=None):
    backend = report['audio_backend']
    fixture = server.fixtures['station']
    codec = fixture['codec']
    pcm_probe = uses_pcm_probe(backend, fixture)
    reclaim = 'input_reclaim_pcm_reference' in report
    overlap = web_socket is not None
    name = {'opus': 'Opus', 'vorbis': 'Vorbis', 'flac': 'FLAC', 'mp3': 'MP3', 'aac': 'AAC'}[codec]
    status_codec = 'OGG' if codec in ('opus', 'vorbis') else name
    start_station(port)
    until = time.monotonic() + 40
    while time.monotonic() < until:
        uart = guest_log(log_path)
        if FATAL.search(uart) or guest.poll() is not None:
            raise RuntimeError('Guest stopped or logged a failure during playback')
        status = json.loads(request(port, '/api/native/status'))
        if codec == 'aac' and status['audio'] and status['codec'] == 'AAC' and 'aac_first_pcm' not in report:
            report['aac_first_pcm'] = {key: status[key] for key in
                                      ('codec', 'format', 'pcm_sample_rate_hz', 'pcm_channels')}
        if ((not reclaim or RECLAIM_EVENT.search(uart))
                and (not overlap or TLS_OVERLAP.search(uart))
                and status['audio'] and status['codec'] == status_codec
                and ('source_channels' not in fixture or status['channels'] == fixture['source_channels'])
                and status['pcm_sample_rate_hz'] == fixture.get('pcm_rate', 48000)
                and status['pcm_channels'] == fixture['pcm_channels']):
            first = sample(port)
            report['first_active_health'] = first
            initial = output_progress(first, uart, pcm_probe)
            if initial > 0:
                break
        time.sleep(0.2)
    else:
        raise RuntimeError(f'No active {codec} playback with output writes before the deadline')
    if reclaim:
        report['input_reclaim_pressure'] = observe_input_reclaim(first, uart)
        report['observed'].append('failed Mbed TLS allocation recovered through idle-slot release')
    if overlap:
        if TLS_OVERLAP.findall(uart) != [('1', '1')]:
            raise RuntimeError('Expected one ordinary TLS RX buffer alongside the reserved radio RX')
        report['tls_overlap'] = {'heap_rx_before': 1, 'heap_rx_after': 1}
        report['observed'].append('allocator recovery with radio TLS and WebUI HTTPS both live')
    report['playing_health'] = [first]
    if websocket_peers is not None:
        websocket_peers.require_status('playing', audio=True, generation=status['generation'])
    if overlap:
        # The static asset route deliberately closes its connection. Use a
        # regular WebUI API response before checking EOF on this same socket.
        capabilities = json.loads(request(port, '/api/native/capabilities'))
        if capabilities['firmware'] != 'esp32-cyd2usb-native' or not capabilities['radio']:
            raise RuntimeError('Expected the real WebUI capabilities over HTTPS')
        report['https_capabilities_during_playback'] = True
    else:
        report['web_asset_during_playback'] = check_asset(port)
    end = time.monotonic() + 5
    while time.monotonic() < end:
        if FATAL.search(guest_log(log_path)) or guest.poll() is not None:
            raise RuntimeError('Guest stopped or logged a failure during WebUI sampling')
        second = sample(port)
        report['health_during_webui'] = second
        status_after = json.loads(request(port, '/api/native/status'))
        if not status_after['audio'] or status_after['generation'] != status['generation']:
            raise RuntimeError('Playback stopped or changed generation during WebUI sampling')
        after = output_progress(second, guest_log(log_path), pcm_probe)
        if after > initial:
            break
        time.sleep(0.2)
    else:
        raise RuntimeError('Audio output did not progress during the WebUI observation')
    events = [event for event in server.events if event.get('tls_version') and event['sent'] > 0]
    if len(events) != 1:
        raise RuntimeError('Expected one actual TLS audio response')
    report['playing_health'].append(second)
    report['tls_peer'] = {key: events[0][key] for key in ('tls_version', 'tls_cipher', 'sent')}
    report['playback'] = {key: status[key] for key in ('codec', 'format', 'pcm_sample_rate_hz', 'pcm_channels')}
    if 'source_channels' in fixture:
        report['playback']['channels'] = status['channels']
    if pcm_probe:
        report['pcm_progress_during_webui'] = [initial, after]
    report['observed'] += [f'{name} audio over verified TLS',
                           'audio progress across HTTPS WebUI API' if overlap else 'audio progress across WebUI asset read']
    if not through_eof:
        request(port, '/api/native/radio?action=stop', 'POST')
    if through_eof:
        if report['health'][-1]['output_driver']['writes'] != 0:
            raise RuntimeError('EOF check requires an idle driver before Play')
        observe_eof(port, server, events[0], guest, log_path, status['generation'], report, web_socket, websocket_peers)
    require_clean_health(first, expected_allocation_failures=int(reclaim))
    require_clean_health(second, expected_allocation_failures=int(reclaim))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', required=True, type=Path)
    parser.add_argument('--qemu', required=True, type=Path)
    parser.add_argument('--rom', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--tls-material', type=Path, help='Local disposable CA and server certificate/key directory')
    parser.add_argument('--codec', choices=('opus', 'vorbis', 'flac', 'mp3', 'aac'), default='opus',
                        help='Select the TLS audio fixture (default: opus)')
    parser.add_argument('--aac-profile', choices=('he', 'lc'), default='he',
                        help='AAC fixture profile; requires --codec aac (default: he)')
    parser.add_argument('--opus-family1', type=Path,
                        help='Use a manifest from prepare-opus-family1.py instead of stereo Opus')
    parser.add_argument('--expect-channel-limit', action='store_true',
                        help='Require rejection of the Family 1 fixture and WebUI after the error')
    parser.add_argument('--through-eof', action='store_true',
                        help='Require the full TLS response, exact audio output, and WebUI after EOF')
    parser.add_argument('--full-tls-records', action='store_true',
                        help='Serve and verify actual maximum-size TLS 1.2 application records')
    parser.add_argument('--websocket-clients', type=int, choices=(0, 1, 2), default=0,
                        help='Keep real, continuously drained HTTP WebUI WebSocket peers through playback and EOF')
    parser.add_argument('--radio-ota-lifecycle', action='store_true',
                        help='Check TLS RX reuse and failed/successful OTA during playback in disposable QEMU')
    parser.add_argument('--expect-input-reclaim', metavar='PCM_MD5',
                        help='Verify a recovered allocation and match PCM to the no-pressure control')
    parser.add_argument('--web-https-fixture', type=Path,
                        help='Stage the local diagnostic HTTPS NVS and hold one verified WebUI connection')
    layout = parser.add_mutually_exclusive_group()
    layout.add_argument('--short-opus-pages', action='store_true',
                        help='Use eight original Opus packets per page for the HTTPS overlap fixture')
    layout.add_argument('--opus-page-boundary', choices=('tags', 'audio'),
                        help='Use a maximum-size comment or audio page in the HTTPS overlap fixture')
    args = parser.parse_args()
    build, qemu, rom = (path.resolve(strict=True) for path in (args.build, args.qemu, args.rom))
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / '.build') or output == ROOT / '.build':
        raise ValueError('Use a fresh output directory under the project .build')
    config = json.loads((build / 'config/sdkconfig.json').read_bytes())
    if not (config['IDF_TARGET'] == 'esp32' and config['ETH_USE_OPENETH'] and not config['FREERTOS_UNICORE']):
        raise ValueError('Expected a dual-core CYD OpenETH diagnostic build')
    backends = [name for name in ('PDM', 'DAC', 'LEGACY_DAC') if config.get('YORADIO_NATIVE_AUDIO_OUTPUT_' + name)]
    if len(backends) != 1:
        raise ValueError('Expected exactly one CYD audio backend')
    backend = backends[0].lower()
    material = args.tls_material.resolve(strict=True) if args.tls_material else None
    if material is not None and (not material.is_relative_to(ROOT / '.build') or
                                 not config.get('MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE')):
        raise ValueError('TLS workload requires local test credentials and a diagnostic CA bundle')
    if args.through_eof and not material:
        parser.error('--through-eof requires the TLS fixture')
    if args.through_eof and args.codec == 'opus' and not config.get('YORADIO_OGG_TIMELINE'):
        parser.error('Opus --through-eof requires the Ogg timeline')
    if args.codec == 'flac' and not args.through_eof:
        parser.error('--codec flac requires --through-eof and the PCM MD5 probe')
    if args.codec == 'vorbis' and not args.through_eof:
        parser.error('--codec vorbis requires --through-eof and the PCM SHA-256 probe')
    if args.codec == 'mp3' and not (args.through_eof and config.get('YORADIO_MP3_DECODER_HELIX')):
        parser.error('--codec mp3 requires Helix, --through-eof and the PCM MD5 probe')
    if args.codec == 'aac' and not (args.through_eof and config.get('YORADIO_AAC_DECODER_ESPRESSIF')
                                   and config.get('YORADIO_AAC_PLUS')):
        parser.error('--codec aac requires public Espressif AAC-Plus, --through-eof and the PCM SHA-256 probe')
    if args.opus_family1 and (args.codec != 'opus' or not (args.through_eof or args.expect_channel_limit)):
        parser.error('--opus-family1 requires Opus and an EOF or channel limit check')
    stereo_only = config.get('YORADIO_AUDIO_STEREO_ONLY', False)
    if args.expect_channel_limit:
        if not (args.opus_family1 and material and stereo_only) or args.through_eof:
            parser.error('--expect-channel-limit requires a stereo-only build, TLS and --opus-family1')
    elif args.opus_family1 and stereo_only:
        parser.error('Family 1 playback requires CONFIG_YORADIO_AUDIO_STEREO_ONLY disabled')
    if args.full_tls_records and not args.through_eof:
        parser.error('--full-tls-records requires --through-eof')
    if args.radio_ota_lifecycle and (not material or args.through_eof or args.opus_family1
                                    or not config.get('YORADIO_TLS_STATIC_RX_RESERVE')
                                    or args.codec != 'opus'):
        parser.error('--radio-ota-lifecycle requires stereo TLS/Opus, the static RX and PCM probes')
    if args.expect_input_reclaim is not None and not (
            args.full_tls_records and args.codec == 'opus' and not args.opus_family1
            and config.get('YORADIO_TLS_STATIC_RX_RESERVE') and config.get('YORADIO_TLS_INPUT_RECLAIM')
            and re.fullmatch(r'[0-9a-f]{32}', args.expect_input_reclaim)):
        parser.error('--expect-input-reclaim requires the TLS RX and reclaim probes, full stereo Opus and a PCM MD5')
    web_https = args.web_https_fixture.resolve(strict=True) if args.web_https_fixture else None
    websocket_factory = None
    if args.websocket_clients:
        if web_https or args.radio_ota_lifecycle or args.expect_channel_limit or args.expect_input_reclaim is not None:
            parser.error('--websocket-clients requires the ordinary HTTP WebUI idle or EOF scenario')
        if material and not args.through_eof:
            parser.error('--websocket-clients with radio TLS requires --through-eof')
        peer_helper = ROOT / 'tests/target/cyd_full_app_openeth_qemu/websocket_peers.py'
        try:
            websocket_factory = runpy.run_path(str(peer_helper))['WebSocketPeers']
        except ImportError:
            parser.error('--websocket-clients requires the installed websockets Python package')
    if web_https is not None and (not args.expect_input_reclaim or not web_https.is_relative_to(ROOT / '.build')):
        parser.error('--web-https-fixture requires the local fixture and --expect-input-reclaim')
    if args.short_opus_pages and not web_https:
        parser.error('--short-opus-pages requires the HTTPS overlap fixture')
    if args.opus_page_boundary and not (web_https and config.get('YORADIO_OGG_OPUS_RAW')):
        parser.error('--opus-page-boundary requires the HTTPS overlap fixture and packet-level Opus')
    flac_decoder = None
    if args.codec == 'flac':
        decoders = [name for name in ('ESPRESSIF', 'CUSTOM') if config.get('YORADIO_FLAC_DECODER_' + name)]
        if len(decoders) != 1:
            raise ValueError('Expected exactly one CYD FLAC decoder')
        flac_decoder = decoders[0].lower()
    fixture = None
    if material:
        if args.codec == 'mp3':
            fixture = helix_mp3_fixture(config.get('YORADIO_AUDIO_MONO', False))
        elif args.codec == 'aac':
            fixture = aac_fixture(args.aac_profile)
        else:
            fixture = family1_fixture(args.opus_family1) if args.opus_family1 else station_fixture(args.codec)
    repaging = shorten_opus_pages(fixture) if args.short_opus_pages else None
    if args.opus_page_boundary:
        repaging = opus_page_boundary(fixture, args.opus_page_boundary)
    flash, parts = flash_parts(build)
    if web_https:
        nvs = (web_https / 'nvs.bin').read_bytes()
        if len(nvs) != 0x5000 or flash[0x9000:0xe000] != b'\xff' * len(nvs):
            raise ValueError('Expected the erased 20 KiB NVS layout')
        flash[0x9000:0xe000] = nvs
        parts.append(dict(file='diagnostic-web-nvs', offset=0x9000, bytes=len(nvs), sha256=digest(nvs)))
    output.mkdir(parents=True)
    flash_path = output / 'qemu-flash.bin'
    flash_path.write_bytes(flash)
    flash_sha = digest(flash)
    web_port = local_port()
    web_guest_port = 443 if web_https else 80
    machine = 'esp32,st7789=on,audiodev=quiet'
    if backend == 'dac':
        machine += ',dac-rate=48000'
    elif backend == 'legacy_dac':
        machine += ',dac-rate=96000'
    command = [str(qemu), '-global', 'driver=ssi.esp32.spi,property=input-delay-ns,value=25',
               '-audiodev', 'none,id=quiet', '-M', machine, '-smp', '2',
               '-L', str(rom), '-display', 'none', '-monitor', 'none', '-serial', 'stdio',
               '-no-reboot', '-snapshot', '-nic',
               f'user,model=open_eth,restrict=on,hostfwd=tcp:127.0.0.1:{web_port}-:{web_guest_port}',
               '-drive', f'file={str(flash_path).replace(",", ",,")},if=mtd,format=raw']
    if args.radio_ota_lifecycle:
        command.remove('-no-reboot')
    log_path = output / 'qemu.log'
    report_path = output / 'report.json'
    report = dict(state='STARTING', scope='OpenETH full-application idle boot', passed=False,
                  flash_parts=parts, flash_sha256=flash_sha, qemu_sha256=digest(qemu.read_bytes()),
                  config_sha256=digest((build / 'config/sdkconfig.json').read_bytes()),
                  openeth=True, audio_backend=backend, physical_tested=False, command=command,
                  runner_sha256=digest(Path(__file__).read_bytes()),
                  task_watchdog_seconds=config['ESP_TASK_WDT_TIMEOUT_S'],
                  web_asset_io_timeout_seconds=WEB_ASSET_TIMEOUT_SECONDS,
                  native_diagnostics=config.get('YORADIO_NATIVE_DIAGNOSTICS', False))
    if args.full_tls_records:
        report['tls_application_payload_lengths'] = []
    if args.expect_input_reclaim is not None:
        report['input_reclaim_pcm_reference'] = args.expect_input_reclaim
    if repaging:
        report['opus_repaging'] = repaging
    if flac_decoder is not None:
        report['flac_decoder'] = flac_decoder
    if args.codec == 'aac':
        report['aac_fixture'] = {key: fixture[key] for key in ('aac_profile', 'adts_frames', 'core_rate',
            'pcm_rate', 'pcm_channels', 'pcm_frames', 'pcm_sha256', 'source_sha256', 'repetitions')}
        report['aac_fixture']['input_bytes'] = len(fixture['data'])
        report['aac_fixture']['input_sha256'] = digest(fixture['data'])
    if args.opus_family1:
        report['opus_family1'] = fixture['family1']

    def save():
        report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    save()
    guest = None
    server = None
    websocket_peers = None
    stack = ExitStack()
    try:
        web = web_port
        if web_https:
            context = ssl.create_default_context(cafile=str(web_https / 'ca.pem'))
            context.minimum_version = context.maximum_version = ssl.TLSVersion.TLSv1_2
            context.set_ecdh_curve('prime256v1')
            web = http.client.HTTPSConnection('127.0.0.1', web_port, context=context)
            stack.callback(web.close)
        web_protocol = 'HTTPS' if web_https else 'HTTP'
        if material:
            server = stack.enter_context(tls_station(material, fixture,
                                                     report.get('tls_application_payload_lengths')))
        if server:
            host_port = server.http.server_port
            net = command.index('-nic') + 1
            if args.radio_ota_lifecycle:
                if os.name == 'nt':
                    forward = f'cmd:tcp-loopback:{host_port}'
                else:
                    relay = ROOT / 'tests/target/cyd_full_app_openeth_qemu/tcp_relay.py'
                    forward = 'cmd:' + shlex.join([Path(sys.executable).as_posix(), relay.as_posix(), str(host_port)])
            else:
                forward = f'tcp:127.0.0.1:{host_port}'
            command[net] += ',guestfwd=tcp:10.0.2.100:18080-' + forward.replace(',', ',,')
            report['scope'] = 'OpenETH full-application boot and TLS audio with concurrent WebUI'
            if args.radio_ota_lifecycle:
                report['scope'] += ', Stop/Play and OTA'
            if args.through_eof:
                report['scope'] += ' through EOF'
            if args.full_tls_records:
                report['scope'] += ' with full TLS records'
        with log_path.open('xb') as log:
            guest = subprocess.Popen(command, cwd=output, stdin=subprocess.DEVNULL, stdout=log,
                                     stderr=subprocess.STDOUT,
                                     creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            report.update(state='RUNNING', qemu_pid=guest.pid)
            save()
            deadline = time.monotonic() + 100
            while time.monotonic() < deadline:
                uart = guest_log(log_path)
                if FATAL.search(uart) or guest.poll() is not None:
                    raise RuntimeError('Guest stopped or logged a startup failure')
                if 'CYD_OPENETH_READY' in uart and f'Native {web_protocol} server started' in uart:
                    try:
                        first = sample(web)
                    except (OSError, http.client.HTTPException):
                        time.sleep(0.2)
                        continue
                    break
                time.sleep(0.2)
            else:
                raise RuntimeError('OpenETH/WebUI startup deadline exceeded')
            if 'ST7789: SPI2 DMA' not in uart or 'Pipeline ready:' not in uart:
                raise RuntimeError('Expected the production TFT and audio tasks')
            report['health'] = [first]
            save()
            require_clean_health(first)
            asset = None if web_https else check_asset(web)
            if websocket_factory is not None:
                websocket_peers = websocket_factory(args.websocket_clients)
                websocket_peers.open(web)
                websocket_peers.require_status('idle', audio=False)
                report['websocket_peer_helper_sha256'] = digest(peer_helper.read_bytes())
            second = sample(web)
            verified_socket = web.sock if web_https else None
            if web_https:
                if not verified_socket or verified_socket.version() != 'TLSv1.2':
                    raise RuntimeError('Expected the provisioned WebUI to keep a verified TLS 1.2 session')
                report['web_tls_version'] = verified_socket.version()
            if second['uptime_ms'] < first['uptime_ms']:
                raise RuntimeError('Guest reset between the resource samples')
            report.update(health=[first, second],
                          observed=['ST7789', 'OpenETH IPv4', 'audio tasks', f'{web_protocol} health'])
            if asset:
                report['web_asset'] = asset
                report['observed'].append('SPIFFS WebUI asset')
            save()
            require_clean_health(second)
            if server:
                try:
                    if args.expect_channel_limit:
                        observe_channel_rejection(web, server, guest, log_path, report)
                    elif args.radio_ota_lifecycle:
                        application, = [part for part in parts if part['offset'] == 0x10000]
                        start = application['offset']
                        image = bytes(flash[start:start + application['bytes']])
                        observe_radio_ota_lifecycle(web, server, guest, log_path, report, image)
                    elif web_https:
                        observe_playback(web, server, guest, log_path, report, args.through_eof, verified_socket)
                    else:
                        observe_playback(web, server, guest, log_path, report, args.through_eof,
                                         websocket_peers=websocket_peers)
                except (OSError, RuntimeError, ValueError, KeyError, http.client.HTTPException):
                    if guest.poll() is None:
                        try:
                            report['last_reachable_health'] = sample(web)
                        except (OSError, RuntimeError, ValueError, KeyError, http.client.HTTPException):
                            pass
                    raise
            report['passed'] = True
    except (OSError, RuntimeError, ValueError, KeyError, http.client.HTTPException) as error:
        report['reason'] = str(error)
    finally:
        try:
            finalize_webui_checks(web, guest, report, websocket_peers, through_eof=args.through_eof)
        except (OSError, RuntimeError, ValueError, KeyError, http.client.HTTPException) as error:
            report['passed'] = False
            report.setdefault('reason', str(error))
        if guest is not None:
            if guest.poll() is None:
                report['controller_stop'] = True
                guest.terminate()
                guest.wait(timeout=10)
            report['qemu_exit_status'] = guest.returncode
        stack.close()
        if server:
            report['peer_observations'] = [{key: event.get(key) for key in ('tls_version', 'tls_cipher', 'sent', 'complete')}
                                           for event in server.events[:16]]
        report['flash_unchanged'] = digest(flash_path.read_bytes()) == flash_sha
        if log_path.is_file():
            uart = log_path.read_bytes()
            report['uart_sha256'] = digest(uart)
            uart_text = uart.decode('utf-8', errors='replace')
            report['guest_fault_observed'] = bool(FATAL.search(uart_text))
            if backend != 'pdm' or (fixture and uses_pcm_probe(backend, fixture)):
                report['pcm_probe_last_progress'] = pcm_probe_progress(uart_text)
                report['pcm_probe_flushes'] = pcm_probe_flushes(uart_text)
            if args.opus_family1:
                report['opus_open_heap'] = [dict(zip(('channels', 'result', 'free', 'largest',
                    'remaining', 'remaining_largest'), map(int, fields)))
                    for fields in OPUS_OPEN.findall(uart_text.replace('\r\n', '\n'))]
            pressure = RX_WAIT.findall(uart_text)
            report['openeth_rx_pressure'] = dict(wait_episodes=len(pressure),
                recovered=uart_text.count('CYD_OPENETH_RX_RECOVERED'),
                samples=[dict(zip(('request', 'heap', 'largest', 'dma_largest'), map(int, fields))) for fields in pressure[:32]])
        report['passed'] = bool(report['passed'] and report['flash_unchanged'] and not report.get('guest_fault_observed'))
        report['state'] = 'TERMINAL_PASS' if report['passed'] else 'TERMINAL_NONPASS'
        save()
    print(report['state'], report.get('reason', report.get('observed')))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
