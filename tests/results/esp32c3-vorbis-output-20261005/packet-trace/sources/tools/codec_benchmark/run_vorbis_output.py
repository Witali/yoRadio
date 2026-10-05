"""Capture real RV32 Vorbis PCM during resizing, repeated retries and EOS.

Runs only disposable QEMU images; never accesses a board. A baseline mismatch
is retained as a decoder failure. Exit 0 requires every requested case to pass.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys

import run_vorbis_lifecycle as life
from vorbis_packets import packets

CASES = {
    # initial output bytes, extra rejected retries, EOS calls, resize OOM,
    # offer a small buffer for every packet, input chunk bytes
    'ample': (16384, 0, 1, 0, 0, 2048),
    'eos-repeat': (16384, 0, 4, 0, 0, 2048),
    'grow-once': (1, 0, 4, 0, 0, 2048),
    'grow-repeated': (1, 2, 4, 0, 0, 2048),
    'every-packet': (1, 2, 4, 0, 1, 2048),
    'resize-oom': (1, 0, 4, 1, 0, 2048),
    'small-chunks': (1, 2, 4, 0, 1, 53),
}


def pcm_from_log(log):
    pcm = bytearray()
    for match in re.finditer(r'^VPCM run=(\d+) offset=(\d+) data=([0-9a-f]+)\r?$', log, re.M):
        if int(match[1]) != 1 or int(match[2]) != len(pcm):
            raise ValueError('Missing/duplicate/out-of-order PCM capture')
        pcm.extend(bytes.fromhex(match[3]))
    return bytes(pcm)


def assess(log, options, reference=None, raw_reference=False):
    pcm = pcm_from_log(log)
    rows = life.records(log, 'RESULT')
    begins = life.records(log, 'BEGIN')
    output = life.records(log.replace('VOUTPUT_', 'VTEST_'), 'RESULT')
    # Keep output-specific records separate from the lifecycle result records.
    output = [r for r in output if 'retries' in r]
    retries = life.records(log.replace('VOUTPUT_', 'VTEST_'), 'RETRY')
    eos = life.records(log.replace('VOUTPUT_', 'VTEST_'), 'EOS')
    complete = life.records(log, 'COMPLETE')
    if re.search(r'Guru Meditation|assert failed|abort\(\)|CORRUPT HEAP', log):
        return dict(status='CRASH', passed=False, rows=rows), pcm
    if len(rows)!=2 or len(begins)!=2 or len(output)!=2 or complete!=[{'runs':2}]:
        raise ValueError('Incomplete/duplicate output test')
    if [r['run'] for r in rows]!=[1,2] or [r['run'] for r in output]!=[1,2]:
        raise ValueError('Invalid cycle order')
    if rows[0]['pcm']!=len(pcm) or rows[0]['sha256']!=hashlib.sha256(pcm).hexdigest():
        raise ValueError('PCM capture disagrees with target hash/count')
    if reference is None: reference = rows[0]
    recovered = (rows[1]['result']==0 and all(rows[1][k]==reference[k] for k in ('pcm','samples','sha256')))
    memory_ok = all(life.clean(r) and (r['free'],r['largest'])==(b['free'],b['largest'])
                    for r,b in zip(rows,begins))
    eof_ok = len([r for r in eos if r['run']==1])==(0 if raw_reference else options[2])
    if options[3]:
        first_ok = rows[0]['result']==-2 and output[0]['resize_oom']==1
    else:
        first_ok = rows[0]['result']==0 and eof_ok and all(
            rows[0][k]==reference[k] for k in ('pcm','samples','sha256'))
    progress_ok = all(r['consumed']==r['pcm']==0 for r in retries)
    passed = first_ok and recovered and memory_ok and progress_ok
    return dict(status='PASS' if passed else 'FAIL', passed=passed, rows=rows,
                output=output, retries=retries, eos=eos, memory_ok=memory_ok,
                recovery_ok=recovered, retry_input_preserved=progress_ok), pcm


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--deps', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--qemu', required=True)
    parser.add_argument('--bios', required=True)
    parser.add_argument('--reference', type=Path, help='Earlier run; ample PCM must remain identical')
    parser.add_argument('--fixture', type=Path, default=life.ROOT/'tests/fixtures/esp32c3_calibration/vorbis-q10.ogg')
    parser.add_argument('--case', action='append', choices=CASES)
    parser.add_argument('--raw-reference', action='store_true', help='Bypass Ogg and feed every audio packet with ample PCM space')
    args=parser.parse_args()
    if args.output.exists(): parser.error('Choose a new output directory')
    output=args.output.resolve(); output.mkdir(parents=True)
    build=args.build.resolve()
    for name,digest in life.ARCHIVES.items():
        assert life.sha(args.deps/'esp-adf-libs/esp_audio_codec/lib/esp32c3'/name)==digest
    config=(build/'sdkconfig').read_text()
    assert 'CONFIG_YORADIO_QEMU_VORBIS_LIFECYCLE=y' in config
    sources=list(life.SOURCES)+['tools/codec_benchmark/run_vorbis_output.py',
        'tools/codec_benchmark/vorbis_packets.py',
        'idf/esp32c3-oled-native/main/qemu_vorbis_output.inc',
        'idf/esp32c3-oled-native/main/decoder_pcm.h',
        'idf/esp32c3-oled-native/main/vorbis_repair_abi.h']
    sources += [p.relative_to(life.ROOT).as_posix() for p in sorted(
        (life.ROOT/'idf/esp32c3-oled-native/main/vorbis_repair').glob('*')) if p.is_file()]
    report=dict(source_sha256=life.snapshot_sources(output,sources), archive_sha256=life.ARCHIVES,
        fixture_sha256=life.sha(args.fixture), fixture=str(args.fixture),
        app_sha256=life.sha(build/'yoradio_esp32c3_oled_native.bin'),
        elf_sha256=life.sha(build/'yoradio_esp32c3_oled_native.elf'),
        config_sha256=life.sha(build/'sdkconfig'), hardware_tested=False,
        raw_reference=args.raw_reference, cases=[])
    for name in ('sdkconfig','yoradio_esp32c3_oled_native.bin','bootloader/bootloader.bin',
                 'partition_table/partition-table.bin','ota_data_initial.bin'):
        dest=output/'build'/name; dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(build/name,dest)
    base=output/'base.bin'
    command=[sys.executable,'-m','esptool','--chip','esp32c3','merge-bin','-o',str(base),
             '--flash-mode','dio','--flash-freq','80m','--flash-size','4MB','--pad-to-size','4MB']
    for address,name in (('0x0','bootloader/bootloader.bin'),('0x8000','partition_table/partition-table.bin'),
                         ('0xe000','ota_data_initial.bin'),('0x10000','yoradio_esp32c3_oled_native.bin')):
        command.extend([address,str(build/name)])
    (output/'merge.log').write_bytes(subprocess.check_output(command,stderr=subprocess.STDOUT))
    flash=output/'case.bin'
    guest=subprocess.check_output(['wsl.exe','--exec','wslpath','-a',str(flash)],text=True).strip()
    qemu=['wsl.exe','--exec','timeout','--kill-after=2','300',args.qemu,'-M','esp32c3',
          '-nographic','-no-reboot','-snapshot','-icount','shift=0,align=off,sleep=off','-L',args.bios,
          '-drive',f'file={guest},if=mtd,format=raw']
    report['qemu_command']=qemu
    data=args.fixture.read_bytes(); info,setup=life.headers(data)
    packet_list=packets(data)
    report['audio_packets']=len(packet_list)-3
    report['final_granule']=packet_list[-1]['granule']
    if args.raw_reference:
        data=b''.join(struct.pack('<I',len(p['data']))+p['data'] for p in packet_list[3:])
    reference=None
    for name,options in CASES.items():
        if args.raw_reference and name!='ample': continue
        if args.case and name!='ample' and name not in args.case: continue
        payload=struct.pack('<8I',life.MAGIC,2,5 if args.raw_reference else 4,0,2,len(data),len(info),len(setup))
        payload+=struct.pack('<6I',*options)+data+info+setup
        assert len(payload)<=life.APP1_SIZE
        shutil.copyfile(base,flash)
        with flash.open('r+b') as stream: stream.seek(life.APP1); stream.write(payload)
        with (output/(name+'.log')).open('wb') as log:
            result=subprocess.run(qemu,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,timeout=310)
        log=(output/(name+'.log')).read_text(errors='replace')
        checked,pcm=assess(log,options,reference,args.raw_reference)
        if name=='ample':
            if not checked['passed']: raise ValueError('Ample baseline failed')
            reference=checked['rows'][0]
            if args.reference:
                expected=gzip.decompress((args.reference/'ample.pcm.gz').read_bytes())
                if pcm!=expected: raise ValueError('Changed ample-buffer baseline PCM')
        (output/(name+'.pcm.gz')).write_bytes(gzip.compress(pcm,mtime=0))
        checked.update(name=name, options=options, log_sha256=life.sha(output/(name+'.log')),
                       pcm_sha256=hashlib.sha256(pcm).hexdigest(),returncode=result.returncode)
        report['cases'].append(checked)
        (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(name,checked['status'], 'bytes',len(pcm), flush=True)
    report['all_passed']=all(c['passed'] for c in report['cases'])
    report['full_matrix']=set(c['name'] for c in report['cases'])==set(CASES)
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return 0 if report['all_passed'] else 2


if __name__=='__main__':sys.exit(main())
