"""Save metadata checks and exact pre/post PCM comparisons without publishing radio PCM."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil

from compare_aac_late_sbr_pcm import parse_capture,read_log
from compare_aac_sbr_gap_pcm import parse_gaps
from compare_aac_recording_pcm import compare as compare_recording
from run_aac_metadata import parse_log

ROOT=Path(__file__).resolve().parents[2]
BASELINE=ROOT/'tests/results/esp32c3-aac-pc19-20261004'


def sha(data):return hashlib.sha256(data).hexdigest()
def save_json(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs',type=Path,required=True)
    parser.add_argument('--old-recording-log',type=Path,required=True)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();output=args.output;output.mkdir(parents=True,exist_ok=False)
    comparisons=[];logs={};sources={}
    for variant in ('plain','reference','pc19'):
        run=args.runs/variant;folder=output/variant;folder.mkdir()
        raw=(run/'qemu.log').read_bytes();log=read_log(run/'qemu.log');logs[variant]=log
        result=json.loads((run/'result.json').read_text())
        for key,value in parse_log(log).items():assert result[key]==value,(variant,key)
        # All music and synthetic sample payloads are removed from diagnostics.
        diagnostics='\n'.join(line for line in log.splitlines() if not re.match(r'AAC_(?:GAP|LATE|RECORD)_PCM_DATA ',line))+'\n'
        (folder/'diagnostics.log').write_text(diagnostics,encoding='utf-8',newline='\n')
        save_json(folder/'result.json',result)
        sources[variant]=dict(raw_log_sha256=sha(raw),raw_log_bytes=len(raw))
        build=ROOT/'idf/esp32c3-oled-native'/('build-qemu-aac-metadata-'+variant)
        assert sha((build/'sdkconfig').read_bytes())==result['provenance']['sdkconfig_sha256']
        assert sha((build/'yoradio_esp32c3_oled_native.elf').read_bytes())==result['provenance']['elf_sha256']
        shutil.copyfile(build/'sdkconfig',folder/'sdkconfig')
        if variant=='plain':continue
        for kind,parse,baseline_dir in (('gaps',parse_gaps,'pcm'),('late',parse_capture,'previous-pcm')):
            pcm=b''.join(row['pcm'] for row in parse(log))
            baseline=BASELINE/baseline_dir/('candidate.pcm.gz' if variant=='pc19' else 'reference.pcm.gz')
            old=gzip.decompress(baseline.read_bytes())
            assert old==pcm,(variant,kind,'PCM changed')
            (folder/(kind+'.pcm.gz')).write_bytes(gzip.compress(pcm,mtime=0))
            comparisons.append(dict(case=variant+'-'+kind,channel_samples=len(pcm)//2,different=0,
                max_error_lsb=0,reference_pcm_sha256=sha(old),candidate_pcm_sha256=sha(pcm),
                baseline=str(baseline.relative_to(ROOT)).replace('\\','/')))
    recording=compare_recording(read_log(args.old_recording_log),logs['pc19'],args.input.read_bytes())
    assert recording['max_error_lsb']==0 and recording['different']==0
    recording['case']='pc19-groovesalad16'
    recording['old_log_sha256']=sha(args.old_recording_log.read_bytes())
    comparisons.append({k:v for k,v in recording.items() if k not in ('frames','per_channel','signed_histogram')})
    formats=re.findall(r'AAC_RECORD_FORMAT frame=0 label=(\S+) source_channels=(\d+) pcm_channels=(\d+) rate=(\d+) pcm_only=(\d+)',logs['pc19'])
    assert len(formats)==1 and logs['pc19'].count('AAC_RECORD_FORMAT ')==1
    label,source,pcm,rate,pcm_only=formats[0]
    summary=dict(pcm=comparisons,adapter_bytes=json.loads((args.runs/'adapter-sizes.json').read_text()),
                 recording_format=dict(label=label,source_channels=int(source),pcm_channels=int(pcm),
                                       rate=int(rate),pcm_only=bool(int(pcm_only))),
                 hardware_tested=False,production_qualified=False)
    save_json(output/'comparison.json',summary)
    # Snapshot every changed codec implementation and the exact tests/runners.
    source_paths=[
        *['idf/esp32c3-oled-native/main/'+name for name in (
            'CMakeLists.txt','aac_profile.c','aac_profile.h','native_aac_decoder.c','native_aac_decoder.h',
            'aac_sbr_abi.h','aac_compact_owner.c','aac_compact_owner.h','aac_sbr_reserve.h','aac_scratch_reserve.h',
            'audio_service.c','qemu_aac_test.c','qemu_aac_metadata.c','qemu_aac_sbr_gap.c','qemu_aac_recording.c',
            'qemu_aac_late_sbr.c','qemu_aac_smoothing.c')],
        'tests/test-aac-metadata.py','tests/run-esp32c3-stream-format.py','tests/native/esp32c3_stream_format_test.c',
        *['tools/codec_benchmark/'+name for name in ('run_aac_metadata.py','run_aac_bfp16.py',
            'save_aac_metadata_evidence.py','aac_analysis_core.h','compare_aac_late_sbr_pcm.py',
            'compare_aac_sbr_gap_pcm.py','compare_aac_recording_pcm.py','run_aac_recording_capture.py')]]
    for name in source_paths:
        target=output/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
    save_json(output/'manifest.json',dict(raw_logs=sources,files={str(p.relative_to(output)).replace('\\','/'):sha(p.read_bytes())
              for p in sorted(output.rglob('*')) if p.is_file()}))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
