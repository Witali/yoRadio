#!/usr/bin/env python3
"""Save recording comparison statistics and diagnostics, excluding music PCM."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CASES=('abba64','groovesalad16','groovesalad32','groovesalad64','groovesalad128')


def save_evidence(work,output):
    output.mkdir(parents=True,exist_ok=True)
    def save(path,name):
        dest=output/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes())
    def json_file(name,data):
        dest=output/name;dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    summaries=[]
    for name in CASES:
        result=json.loads((work/name/'comparison.json').read_text())
        previous=json.loads((ROOT/'tests/results/esp32c3-aac-high-history-20261003/pc18'/name/'result.json').read_text())
        provenance=previous['provenance']['recording']
        if result['input_sha256']!=provenance['sha256'] or result['input_bytes']!=provenance['bytes']:
            raise ValueError('Recording differs from retained corpus: '+name)
        save(work/name/'comparison.json',name+'/comparison.json')
        for mode in ('candidate','reference'):
            path=work/name/mode
            record=json.loads((path/'result.json').read_text())
            if record['provenance']['recording']['sha256']!=result['input_sha256']:
                raise ValueError('Capture used different input')
            if record['full_precision_history']!=(mode=='reference'):
                raise ValueError('Wrong storage role')
            raw=(path/'qemu.log').read_bytes()
            digest=hashlib.sha256(raw).hexdigest()
            if digest!=result['log_sha256'][mode] or digest!=record['provenance']['qemu_log_sha256']:
                raise ValueError('Raw capture log changed')
            kept=[];removed=0;pcm_bytes=0
            for line in raw.splitlines(keepends=True):
                if line.startswith(b'AAC_RECORD_PCM_DATA '):
                    payload=line.split(b' hex=',1)[1].strip()
                    pcm_bytes+=len(bytes.fromhex(payload.decode('ascii')));removed+=1
                else:kept.append(line)
            if pcm_bytes!=result['channel_samples']*2:
                raise ValueError('Incorrect stripped PCM count')
            dest=output/name/mode;dest.mkdir(parents=True,exist_ok=True)
            (dest/'diagnostics.log.gz').write_bytes(gzip.compress(b''.join(kept),mtime=0))
            json_file(name+'/'+mode+'/raw-log.json',dict(sha256=digest,bytes=len(raw),
                omitted_recording_pcm_lines=removed,omitted_recording_pcm_bytes=pcm_bytes,
                raw_capture_retained_locally=True))
            save(path/'result.json',name+'/'+mode+'/result.json')
            if (path/'command.json').exists():save(path/'command.json',name+'/'+mode+'/command.json')
        summaries.append(dict(case=name,profile=provenance['ffprobe']['streams'][0]['profile'],
            **{k:result[k] for k in ('rate','channels','frame_count','channel_samples','different',
               'max_error_lsb','over_three','rms_error_lsb','mean_error_lsb','precision_pass','input_sha256')}))
    json_file('summary.json',dict(cases=summaries,channel_samples=sum(r['channel_samples'] for r in summaries),
        precision_pass=all(r['precision_pass'] for r in summaries),precision_limit_lsb=3,
        max_error_lsb=max(r['max_error_lsb'] for r in summaries),production_qualified=False,
        source_audio_and_raw_pcm='Retained in ignored local test directories; not included in this evidence'))
    for mode,build_name in [('candidate','build-qemu-aac-gap-pc19-side'),('reference','build-qemu-aac-late-reference')]:
        build=ROOT/'idf/esp32c3-oled-native'/build_name
        expected=json.loads((work/'abba64'/mode/'result.json').read_text())['provenance']
        for name,field in [('yoradio_esp32c3_oled_native.elf','elf_sha256'),('sdkconfig','sdkconfig_sha256')]:
            if hashlib.sha256((build/name).read_bytes()).hexdigest()!=expected[field]:raise ValueError('Build changed during recording runs')
        for case in CASES:
            provenance=json.loads((work/case/mode/'result.json').read_text())['provenance']
            if any(provenance[k]!=expected[k] for k in ('elf_sha256','sdkconfig_sha256','codec_sha256')):
                raise ValueError('Mixed builds in one role')
        save(build/'sdkconfig',mode+'/sdkconfig');save(build/'config/sdkconfig.h',mode+'/sdkconfig.h')
        log=ROOT/'.build/aac-late-sbr'/f'{build_name}.log'
        (output/mode/'build.log.gz').write_bytes(gzip.compress(log.read_bytes(),mtime=0))
        for path in (build/'esp-idf/main/compact5').glob('*.json'):save(path,mode+'/compact5/'+path.name)
    sources=['idf/esp32c3-oled-native/main/qemu_aac_recording.c',
        'idf/esp32c3-oled-native/main/qemu_aac_late_sbr.c','idf/esp32c3-oled-native/main/CMakeLists.txt',
        'tools/codec_benchmark/run_aac_recording_capture.py','tools/codec_benchmark/compare_aac_recording_pcm.py',
        'tools/codec_benchmark/save_aac_recording_evidence.py','tests/test-aac-recording-capture.py',
        'tests/test-aac-recording-evidence.py']
    for source in sources:save(ROOT/source,'sources/'+source)
    checksums={p.relative_to(output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted(output.rglob('*')) if p.is_file() and p.name!='checksums.json'}
    json_file('checksums.json',checksums)
    print('Saved',len(checksums),'evidence files, excluding real-recording PCM')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();save_evidence(args.work,args.output)
