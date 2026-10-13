"""Sanitize the production prefix detector and actual audio-service send path."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'idf/esp32c3-oled-native/main'
OUT = ROOT / '.build/c3-stream-probe'


def native(path):
    value = str(path.resolve()).replace('\\', '/')
    return '/mnt/' + value[0].lower() + value[2:] if os.name == 'nt' else value


def run(args):
    command = ['wsl.exe', '--exec', *args] if os.name == 'nt' else args
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout + result.stderr


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    audio = (MAIN / 'audio_service.c').read_text()
    start = audio.index('static bool send_stream_audio(')
    end = audio.index('static void stream_bitrate_add(', start)
    (OUT / 'stream-send-under-test.h').write_text(audio[start:end])
    binary = OUT / 'stream-probe-test'
    compile_log = run(['gcc', '-std=c11', '-O2', '-g', '-Wall', '-Wextra', '-Werror',
        '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
        '-I', native(MAIN), '-I', native(OUT),
        native(ROOT / 'tests/native/esp32c3_stream_probe_test.c'), '-o', native(binary)])
    fixtures = []
    folder = ROOT / 'tests/fixtures/esp32c3_calibration'
    mapping = {'mp3': 1, 'aac': 2, 'flac': 3, 'vorbis': 4, 'opus': 4}
    for entry in json.loads((folder/'manifest.json').read_text())['fixtures']:
        fixtures.append((folder/entry['file'], mapping[entry['codec']], entry['sha256']))
    folder = ROOT / 'tests/fixtures/aac_stream_format'
    for name, entry in json.loads((folder/'manifest.json').read_text())['files'].items():
        fixtures.append((folder/name, 2, entry['sha256']))
    command = [native(binary)]
    for path, codec, digest in fixtures:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, path
        command.extend([native(path), str(codec)])
    output = run(command)
    result = {'compiler': run(['gcc', '--version']).splitlines()[0],
              'compile': compile_log, 'test': output,
              'corpus': [{'file': path.relative_to(ROOT).as_posix(), 'codec': codec,
                          'sha256': digest, 'cases': 6} for path, codec, digest in fixtures],
              'source_sha256': {name: hashlib.sha256((MAIN/name).read_bytes()).hexdigest()
                  for name in ('stream_probe.h', 'stream_tags.h', 'audio_service.c', 'audio_completion.h')}}
    (OUT / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(output, end='')


if __name__ == '__main__':
    main()
