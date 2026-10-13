"""Check the experimental frame walker against ffprobe packet boundaries.

No firmware/board mutation. Synthetic extra MP3 files remain in .build.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.build/c3-stream-frames'


def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout


def native(path):
    value = str(path.resolve()).replace('\\', '/')
    return '/mnt/' + value[0].lower() + value[2:] if os.name == 'nt' else value


def linux(args):
    return run(['wsl.exe', '--exec', *args] if os.name == 'nt' else args)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    binary = OUT / 'test'
    source = ROOT / 'tests/native/esp32c3_stream_frames_test.c'
    header = ROOT / 'idf/esp32c3-oled-native/main/stream_frames.h'
    linux(['gcc', '-std=c11', '-O2', '-g', '-Wall', '-Wextra', '-Werror',
           '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
           '-I', native(header.parent), native(source), '-o', native(binary)])
    print(linux([native(binary)]), end='')
    report = dict(compiler=linux(['gcc', '--version']).splitlines()[0],
                  ffprobe=run(['ffprobe', '-version']).splitlines()[0],
                  ffmpeg=run(['ffmpeg', '-version']).splitlines()[0], cases=[],
                  source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (source, header)})
    corpus = []
    folder = ROOT / 'tests/fixtures/esp32c3_calibration'
    for spec in json.loads((folder/'manifest.json').read_text())['fixtures']:
        if spec['codec'] in ('mp3', 'aac'):
            corpus.append((folder/spec['file'], spec['sha256'], None))
    folder = ROOT / 'tests/fixtures/aac_stream_format'
    for name, spec in json.loads((folder/'manifest.json').read_text())['files'].items():
        corpus.append((folder/name, spec['sha256'], None))
    # Exercise all MPEG Layer III rate/version groups, CBR/VBR, mono/stereo.
    for rate in (8000,11025,12000,16000,22050,24000,32000,44100,48000):
        for channels in (1,2):
            path = OUT/f'mp3-{rate}-{channels}.mp3'
            command = ['ffmpeg','-v','error','-y','-f','lavfi','-i',
                       f'sine=frequency=997:sample_rate={rate}:duration=0.35',
                       '-ac',str(channels),'-c:a','libmp3lame',
                       *(['-b:a','24k' if rate<32000 else '128k'] if channels==1 else ['-q:a','3']),
                       '-write_xing','0','-id3v2_version','0','-write_id3v1','0',str(path)]
            run(command)
            corpus.append((path,hashlib.sha256(path.read_bytes()).hexdigest(),command))
    references = []
    for path, digest, command in corpus:
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest
        skip = 0
        while data[skip:skip+3] == b'ID3':
            p=data[skip:skip+10]; assert len(p)==10
            skip += 10 + (p[6]<<21) + (p[7]<<14) + (p[8]<<7) + p[9]
            if p[3]==4 and p[5]&16: skip+=10
        raw = OUT/(path.stem+'.elementary'+path.suffix)
        raw.write_bytes(data[skip:])
        oracle = json.loads(run(['ffprobe','-v','error','-select_streams','a:0',
            '-show_packets','-show_entries','packet=pos,size','-of','json',str(raw)]))
        expected = [(int(p['pos']),int(p['size'])) for p in oracle['packets']]
        output = linux([native(binary),native(raw)])
        rows = [list(map(int,line.split()[1:])) for line in output.splitlines() if line.startswith('FRAME ')]
        assert [(r[0],r[1]) for r in rows] == expected, path.name
        assert sum(r[1] for r in rows)==len(data)-skip
        references.append((data[skip:],rows))
        report['cases'].append(dict(name=path.name,sha256=digest,frames=len(rows),
            bytes=len(data)-skip,chunk_cases=3,reference='ffprobe pos/size',result='PASS',
            generation_command=command))
        print(path.name, 'PASS', len(rows), 'frames', flush=True)
    # Independent oracle is the concatenation of the individual ffprobe packet
    # boundaries. ffprobe itself does not demux alternating raw codec families.
    mixed = b''; expected=[]
    for index in (0,2,0,3,0,len(references)-1,2):
        data,rows=references[index]
        expected.extend([[r[0]+len(mixed),*r[1:]] for r in rows])
        mixed+=data
    path=OUT/'mp3-aac-transitions.bin';path.write_bytes(mixed)
    output=linux([native(binary),native(path)])
    actual=[list(map(int,line.split()[1:])) for line in output.splitlines() if line.startswith('FRAME ')]
    assert actual==expected
    report['mixed']=dict(frames=len(actual),bytes=len(mixed),chunk_cases=3,
        sha256=hashlib.sha256(mixed).hexdigest(),result='PASS',
        reference='concatenated per-file ffprobe boundaries; no decoder or queue test')
    (OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Mixed MP3/AAC boundaries and byte replay: PASS',len(actual),'frames')


if __name__ == '__main__':
    main()
