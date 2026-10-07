"""Compare complete AAC fixtures with FFmpeg and an unmodified FDK decoder.

Build tests/native/aac_eof_reference.cpp against pinned FDK AAC v2.0.3 first.
This checks decoder termination and layouts, not bit-exact PCM equivalence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def execute(command):
    return subprocess.check_output(command, stderr=subprocess.PIPE)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fdk-reference', required=True, type=Path)
    parser.add_argument('--ffmpeg', default='ffmpeg')
    parser.add_argument('--ffprobe', default='ffprobe')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    fixture_dir = ROOT/'tests/fixtures/aac_stream_format'
    manifest = json.loads((fixture_dir/'manifest.json').read_text())
    records = []
    for name, spec in manifest['files'].items():
        path = fixture_dir/name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == spec['sha256']
        frames = json.loads(execute([args.ffprobe, '-v','error','-select_streams','a:0',
            '-show_frames','-show_entries','frame=nb_samples','-of','json',str(path)]))['frames']
        layout = json.loads(execute([args.ffprobe,'-v','error','-select_streams','a:0',
            '-show_entries','stream=sample_rate,channels,profile','-of','json',str(path)]))['streams'][0]
        pcm = execute([args.ffmpeg,'-v','error','-xerror','-i',str(path),'-f','s16le','-acodec','pcm_s16le','-'])
        samples = len(pcm)//(2*layout['channels'])
        assert samples == sum(frame['nb_samples'] for frame in frames)
        assert int(layout['sample_rate']) == spec['sample_rate'] and layout['channels'] == spec['channels']
        fdk = []
        for chunk in (1,7,257,2048):
            result = json.loads(execute([str(args.fdk_reference.resolve()),str(path),str(chunk)]))
            assert result['sample_rate'] == spec['sample_rate'] and result['channels'] == spec['channels']
            assert result['samples_per_channel'] == samples
            fdk.append(dict(chunk_bytes=chunk,**result))
        records.append(dict(fixture=name,sha256=spec['sha256'],ffmpeg=dict(**layout,
            samples_per_channel=samples,decoded_bytes=len(pcm)),fdk=fdk))
        print(name+': reference EOF/layout PASS',flush=True)
    report = dict(scope='Complete-file decode/drain; no cross-decoder PCM equality claim',
        ffmpeg_version=execute([args.ffmpeg,'-version']).decode().splitlines()[0],
        fdk_reference_sha256=hashlib.sha256(args.fdk_reference.read_bytes()).hexdigest(),
        fdk_source='FDK AAC v2.0.3; 716f4394641d53f0d79c9ddac3fa93b03a49f278', cases=records)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')


if __name__ == '__main__':
    main()
