"""Retain radio FLAC measurements and exact sources, without broadcast audio."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from summarize_radio_flac import read, summarize


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save_evidence(work, output, extra_boards=()):
    folders = [('board', work/'board')]+[(f'repeat-{i+1}', path) for i,path in enumerate(extra_boards)]
    for name, folder in folders:
        report = read(folder/'report.json')
        if not any(c['name']=='restore-board' for c in report['cases']):
            raise ValueError('Board run is incomplete: '+name)
    # A fresh destination prevents stale outcomes from an earlier run surviving.
    output.mkdir(parents=True, exist_ok=False)
    def write(name, data):
        target = output/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    def copy(path, name, compressed=False):
        data = path.read_bytes()
        write(name+('.gz' if compressed else ''), gzip.compress(data, mtime=0) if compressed else data)
    def save_json(name, data):
        write(name, (json.dumps(data, indent=2)+'\n').encode())

    write('.gitattributes', b'* -text\n')
    recording = read(work/'recordings/manifest.json')
    analysis = read(work/'analysis/report.json')
    host = read(work/'host-pcm/report.json')
    if read(ROOT/'tools/codec_benchmark/radio_flac_sources.json') != recording['sources']:
        raise ValueError('Source catalog changed since capture')
    for spec in recording['fixtures']+recording['captures']:
        if sha((work/'recordings'/spec['file']).read_bytes()) != spec['sha256']:
            raise ValueError('Local recording changed: '+spec['file'])
    copy(work/'recordings/manifest.json', 'recordings/manifest.json')
    for path in sorted((work/'recordings').glob('*.log')):
        copy(path, 'recordings/'+path.name, compressed=True)
    for folder in ('analysis', 'host-pcm'):
        for path in sorted((work/folder).rglob('*')):
            if path.is_file() and (path.suffix in ('.json','.log') or
                                   'sources' in path.relative_to(work/folder).parts or
                                   path.name == 'observed.cpp'):
                copy(path, folder+'/'+path.relative_to(work/folder).as_posix(), path.suffix=='.log')

    sources = {}
    def freeze(name, expected=None):
        data = (ROOT/name).read_bytes()
        if expected and sha(data) != expected:
            raise ValueError('Test source changed before retention: '+name)
        if name in sources and sources[name] != sha(data):
            raise ValueError('Conflicting tested sources: '+name)
        sources[name] = sha(data)
        write('sources/'+name, data)

    for name, folder in folders:
        report = read(folder/'report.json')
        for filename in ('report.json','status.json','performance.json'):
            copy(folder/filename, name+'/'+filename, filename!='report.json')
        if (folder/'experiment.json').exists():
            copy(folder/'experiment.json', name+'/experiment.json')
        for source,digest in report['test_sources_sha256'].items():
            freeze(source,digest)
        save_json(name+'/summary.json', summarize(folder,recording,analysis))

    experiment = read(work/'board/experiment.json')
    if sha((work/'recordings/manifest.json').read_bytes()) != experiment['fixture_manifest_sha256']:
        raise ValueError('Recording manifest changed')
    freeze('tools/codec_benchmark/capture_radio_flac.py',recording['generator_sha256'])
    freeze('tools/esp32c3_tests/radio_flac_study.py',experiment['runner_sha256'])
    for source in ('tools/codec_benchmark/radio_flac_sources.json',
                   'tools/esp32c3_tests/summarize_radio_flac.py',
                   'tools/codec_benchmark/save_radio_flac_evidence.py',
                   'idf/esp32c3-oled-native/main/cpu_profiler.c',
                   'idf/esp32c3-oled-native/main/native_audio_output_dma.c',
                   'tests/test-radio-flac-study.py','tests/test-radio-flac-evidence.py'):
        freeze(source)

    artifact = ROOT/'firmware/development/esp32c3-flac-dispatch'
    build_path = ROOT/'tests/results/esp32c3-flac-dispatch-20261006/verify/build.json'
    build = read(build_path)
    for filename,field in (('app.bin','firmware_sha256'),('sdkconfig','sdkconfig_sha256')):
        if sha((artifact/filename).read_bytes()) != experiment[field]:
            raise ValueError('Firmware artifact changed: '+filename)
    if build['elf_sha256'] != experiment['firmware']['app_elf_sha256']:
        raise ValueError('Firmware build does not match board experiment')
    for name,digest in host['sources'].items():
        if name in build['source_sha256'] and digest != build['source_sha256'][name]:
            raise ValueError('Host/firmware source mismatch: '+name)
    copy(build_path,'firmware/build.json')
    copy(artifact/'sdkconfig','firmware/sdkconfig')
    copy(artifact/'manifest.json','firmware/artifact.json')
    save_json('provenance.json',dict(board_folders=[name for name,_ in folders],
        tools_sha256=sources, production_qualified=False,
        audio='Broadcast AAC, WAV, FLAC and decoded PCM retained only in ignored local workspace',
        artifact='firmware/development/esp32c3-flac-dispatch/app.bin'))
    manifest = {p.relative_to(output).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes()))
                for p in sorted(output.rglob('*')) if p.is_file()}
    save_json('manifest.json',manifest)
    print('Retained',len(manifest),'files; audio excluded')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--extra-board',type=Path,action='append',default=[])
    args = parser.parse_args()
    save_evidence(args.work,args.output,args.extra_board)
