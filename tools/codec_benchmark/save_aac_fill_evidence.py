"""Save bounded FIL evidence, unchanged PCM and the physical integration build."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil

from elftools.elf.elffile import ELFFile
from compare_aac_late_sbr_pcm import parse_capture, read_log
from compare_aac_sbr_gap_pcm import parse_gaps
from run_aac_fill import parse_log

ROOT=Path(__file__).resolve().parents[2]
BASELINE=ROOT/'tests/results/esp32c3-aac-faults-20261004'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def symbols(path):
    wanted=('__wrap_getfill','__wrap_get_sbr_bitstream','aac_fill_skip','aac_fill_sbr')
    with path.open('rb') as file:
        elf=ELFFile(file);table=elf.get_section_by_name('.symtab');result={}
        for name in wanted:
            rows=table.get_symbol_by_name(name)
            assert rows and len(rows)==1 and rows[0]['st_shndx']!='SHN_UNDEF',name
            result[name]=dict(address=rows[0]['st_value'],bytes=rows[0]['st_size'])
        return result


def save(args):
    output=args.output;output.mkdir(parents=True,exist_ok=False)
    records={};logs={}
    for variant in ('plain','pc19'):
        run=args.pc19_run if variant=='pc19' and args.pc19_run else args.runs/variant
        build=ROOT/'idf/esp32c3-oled-native'/('build-qemu-aac-fill-'+variant)
        folder=output/variant;folder.mkdir()
        log=read_log(run/'qemu.log');logs[variant]=log
        result=parse_log(log,plain=variant=='plain')
        provenance=json.loads((run/'result.json').read_text())['provenance']
        for filename,key in (('sdkconfig','sdkconfig_sha256'),('yoradio_esp32c3_oled_native.elf','elf_sha256')):
            assert sha(build/filename)==provenance[key],(variant,key)
        assert sha(run/'qemu.log')==provenance['qemu_log_sha256']
        result['provenance']=provenance;result['linked_hooks']=symbols(build/'yoradio_esp32c3_oled_native.elf')
        save_json(folder/'result.json',result)
        diagnostics='\n'.join(line for line in log.splitlines()
                              if not re.match(r'AAC_(?:LATE|GAP|RECORD)_PCM_DATA ',line))+'\n'
        (folder/'diagnostics.log').write_text(diagnostics,encoding='utf-8',newline='\n')
        shutil.copyfile(build/'sdkconfig',folder/'sdkconfig')
        records[variant]=dict(raw_log_sha256=sha(run/'qemu.log'),raw_log_bytes=(run/'qemu.log').stat().st_size)
    pcm=[]
    for kind,parser in (('late',parse_capture),('gaps',parse_gaps)):
        current=b''.join(row['pcm'] for row in parser(logs['pc19']))
        previous=gzip.decompress((BASELINE/(kind+'.pcm.gz')).read_bytes())
        assert current==previous,kind
        (output/(kind+'.pcm.gz')).write_bytes(gzip.compress(current,mtime=0))
        pcm.append(dict(case=kind,channel_samples=len(current)//2,different=0,max_error_lsb=0,
                        pcm_sha256=hashlib.sha256(current).hexdigest(),
                        baseline=(BASELINE/(kind+'.pcm.gz')).relative_to(ROOT).as_posix()))
    pattern=r'AAC_GAP_WORK case=(\w+) phase=(\d+) frames=(\d+) calls=(\d+) instructions=(\d+)'
    before=re.findall(pattern,(BASELINE/'diagnostics.log').read_text())
    after=re.findall(pattern,logs['pc19'])
    assert len(before)==len(after)==12 and [r[:4] for r in before]==[r[:4] for r in after]
    old=sum(int(r[-1]) for r in before);new=sum(int(r[-1]) for r in after)
    save_json(output/'comparison.json',dict(pcm=pcm,work=dict(reference_instructions=old,
        candidate_instructions=new,delta_percent=100*(new/old-1),unit='QEMU guest instructions, not hardware CPU time')))
    host=output/'host';host.mkdir()
    for filename in ('result.json','test.log','build.log'):
        shutil.copyfile(args.host/filename,host/filename)
    host_result=json.loads((host/'result.json').read_text())
    for name,digest in host_result['hashes'].items():assert sha(ROOT/name)==digest,name
    assert host_result['exit_code']==0 and host_result['valid_cases']==69376
    failure=args.runs/'initial-plain-link-failure.log'
    assert 'undefined reference to `__wrap_getfill' in failure.read_text()
    (output/'initial-plain-link-failure.log.gz').write_bytes(gzip.compress(failure.read_bytes(),mtime=0))
    # Save the successful physical integration build before leaving the build directory.
    build=args.production_build;artifact=ROOT/'firmware/development/esp32c3-aac-fill-network'
    artifact.mkdir(parents=True,exist_ok=True)
    binary=build/'yoradio_esp32c3_oled_native.bin';elf=build/'yoradio_esp32c3_oled_native.elf'
    config=(build/'sdkconfig').read_text()
    assert '# CONFIG_YORADIO_QEMU is not set' in config
    assert '# CONFIG_YORADIO_DEEP_SLEEP_CLOCK is not set' in config
    assert 'CONFIG_ESPTOOLPY_FLASHMODE_DIO=y' in config and 'CONFIG_ESPTOOLPY_FLASHFREQ_80M=y' in config
    shutil.copyfile(binary,artifact/'app.bin')
    production=dict(app_sha256=sha(binary),elf_sha256=sha(elf),sdkconfig_sha256=sha(build/'sdkconfig'),
                    app_bytes=binary.stat().st_size,linked_hooks=symbols(elf),
                    hardware_tested=False,production_qualified=False,
                    purpose='Physical integration build; existing PC18 storage and network diagnostics',
                    deep_sleep=False,flash_mode='dio',flash_frequency_mhz=80)
    save_json(artifact/'manifest.json',production);save_json(output/'production-build.json',production)
    shutil.copyfile(build/'sdkconfig',output/'production-sdkconfig')
    sources=[*['idf/esp32c3-oled-native/main/'+name for name in (
        'CMakeLists.txt','aac_fill_parser.c','aac_fill_parser.h','aac_fill_wrappers.c',
        'aac_compact_owner.c','qemu_aac_fill.c','qemu_aac_test.c')],
        'tests/native/aac_fill_parser_test.c','tests/native/aac_fill_abi_test.c',
        'tests/run-aac-fill-parser.py','tests/test-aac-fill-parser.py',
        'tools/codec_benchmark/run_aac_fill.py','tools/codec_benchmark/save_aac_fill_evidence.py']
    for name in sources:
        target=output/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
    save_json(output/'manifest.json',dict(raw_logs=records,files={p.relative_to(output).as_posix():sha(p)
              for p in sorted(output.rglob('*')) if p.is_file()}))
    print(json.dumps(dict(pcm=pcm,instruction_delta_percent=100*(new/old-1),production=production),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('runs','host','production-build','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--pc19-run',type=Path)
    save(parser.parse_args())
