"""Isolated exact floor1 arithmetic on native ESP32/C3; no decoder executes.

The new campaign losslessly batches every selected scalar of the complete host
corpus. RLE is a transport encoding only: every recovered limb is compared with
the independent integer oracle, never replaced by a checksum.
"""
import argparse, hashlib, importlib.util, json, os, re, shutil, struct, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent
PROJECT = ROOT / 'tests/target/vorbis_floor1_product_qemu'
COMPONENTS = ('native_vorbis_numeric','native_vorbis_packet_frame','native_vorbis_floor1_product')
SDK_HEAD = {'esp32':'7101770dc6db2667b3c477cc31365dd1acd6db4e',
            'esp32c3':'9a97f6c54ec638111ce55cd36581b3c192f15207'}
HOST_PIN = 'd03e736c2e66504c5d2d22e9ae1b4af23ee8871d89c5fdb610caa9a3c118c9ff'
FIXTURE_PIN = 'c3c7eec63324357935ab6407c59405c4b700858e076935d804d006f0847b053c'
PATTERN = {'endpoints':0,'patterns':1,'one':2,'invalid':3,'zero':4}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def file_sha(path):
    return sha(Path(path).read_bytes())


def load_math():
    path = ROOT / 'tests/test-vorbis-floor1-product.py'
    need(file_sha(path) == HOST_PIN, 'unchanged exact host oracle')
    spec = importlib.util.spec_from_file_location('native_floor1_integer_oracle', path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def native_cases(math):
    originals = math.cases()
    result, coverage = [], set()
    for origin, row in enumerate(originals):
        steps = 2 if row['pattern'] == 'endpoints' else 7 if row['id'].startswith('limb-patterns-') else 1
        for offset in range(steps):
            indices = row['indices'][offset::steps]
            case = dict(id=row['id'] + (f'-batch{offset}' if steps > 1 else ''), origin=origin,
                width=row['width'], exponent=row['exponent'], bins=len(indices),
                channels=row['channels'] if not row['width'] else 1, channel=row['channels']-1 if not row['width'] else 0,
                offset=offset, step=steps, pattern=PATTERN[row['pattern']],
                original_bins=len(row['indices']), invalid_sign=row.get('invalid_sign',0),
                controls=bool(row['controls'] and (row['width'] <= 65 or row['id'].startswith('constant-'))),
                indices=indices)
            if row['pattern'] == 'endpoints':
                case.update(index_kind=0,constant=0)
            elif row['id'].startswith('limb-patterns-'):
                case.update(index_kind=1,constant=0)
            elif len(set(indices)) == 1:
                case.update(index_kind=2,constant=indices[0])
            else:
                case.update(index_kind=3,constant=0)
            for bin_index in range(len(indices)):
                key = origin, offset + steps * bin_index
                need(key not in coverage, 'no duplicate selected scalar')
                coverage.add(key)
            result.append(case)
    need(coverage == {(origin,bin_index) for origin,row in enumerate(originals)
                      for bin_index in range(len(row['indices']))}, 'every selected host scalar retained')
    for channel, width in enumerate((1,33,1087)):
        base = dict(result[2*(width-1)])
        base.update(id=f'selected-channel-{channel}-width-{width}',bins=8,channels=3,channel=channel,
                    offset=0,step=1,index_kind=3,indices=[0,0,1,1,128,128,255,255],controls=True,
                    original_bins=8)
        result.append(base)
    need(len(result) == 2957, 'complete native batched campaign')
    return originals, result


def header(cases):
    lines = ['#pragma once','#include <stdint.h>','#include <stdbool.h>',
        'typedef struct { const char *id; const uint8_t *indices; uint32_t width,bins,channels,channel; int32_t exponent; uint32_t pattern,offset,step,index_kind,constant,original_bins; int32_t invalid_sign; bool controls; } f1_case_t;']
    for i, row in enumerate(cases):
        if row['index_kind'] == 3:
            # index_kind3 is addressed through original offset/step (both0/1).
            need(row['offset'] == 0 and row['step'] == 1, 'literal short index table')
            lines.append('static const uint8_t f1_indices_' + str(i) + '[]={' + ','.join(map(str,row['indices'])) + '};')
    lines.append(f'#define F1_CASE_COUNT {len(cases)}')
    lines.append('static const f1_case_t f1_cases[F1_CASE_COUNT]={')
    for i, row in enumerate(cases):
        fields = ['"'+row['id']+'"','f1_indices_'+str(i) if row['index_kind']==3 else 'NULL']
        fields += [str(row[key]) for key in ('width','bins','channels','channel','exponent','pattern','offset','step','index_kind','constant','original_bins','invalid_sign')]
        fields += ['true' if row['controls'] else 'false']
        lines.append(' {'+','.join(fields)+'},')
    lines.append('};')
    return ('\n'.join(lines)+'\n').encode('ascii')


def expected_row(case):
    return dict(width=case['width'],indices=case['indices'],channels=case['channels'],channel=case['channel'],
                exponent=case['exponent'],pattern=list(PATTERN)[case['pattern']])


def expected_scalar(math, originals, case, bin_index):
    original = originals[case['origin']]
    if case['id'].startswith('selected-channel-'):
        # Endpoints are selected by current original-order parity in this extra row.
        original = dict(original,channel=case['channel'])
    return math.sample(original,case['offset']+case['step']*bin_index,original['channel'])


def validate_log(log, cases, originals, math, table, target, data_sha256):
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog|stack overflow|timed out',log,re.I), 'native panic/corruption/timeout')
    need(not any('F1_' in line and not line.startswith('F1_') for line in log.splitlines()), 'foreign/torn product event')
    events = iter(line for line in log.splitlines() if line.startswith('F1_'))
    core = 1 if target == 'esp32' else 0
    line_count = 0
    def take(kind, fixed, extra=()):
        nonlocal line_count
        line = next(events,None)
        need(line is not None,'missing event')
        fields = line.split(' ')
        need(fields[0] == 'F1_'+kind and all(x.count('=')==1 for x in fields[1:]),'ordered event syntax')
        row = dict(x.split('=') for x in fields[1:])
        need(len(row)+1 == len(fields) and set(row)==set(fixed)|set(extra) and
             all(row[key]==str(value) for key,value in fixed.items()),'unique exact event fields')
        line_count += 1
        return row
    def integer(value, maximum=(1<<64)-1):
        need(re.fullmatch(r'0|[1-9][0-9]*',value) is not None,'canonical unsigned integer')
        result = int(value)
        need(result <= maximum,'integer extent')
        return result
    take('BEGIN',dict(cases=len(cases),coordinator=0,worker=core,data=data_sha256))
    take('WORKER',dict(core=core,priority=3,stack=16384))
    total_words = total_samples = total_checks = total_refusals = refused_rows = max_limbs = 0
    digest, metrics = hashlib.sha256(), []
    for i, case in enumerate(cases):
        measured, layout = math.expected_layout(expected_row(case),table)
        product = -1 if case['pattern']==3 else measured
        take('CASE',dict(row=i,id=case['id'],measure=measured,product=product,core=core))
        count = 0
        if product == 0:
            take('LAYOUT',dict(row=i,**layout,core=core))
            count = layout['limb_count']
            max_limbs = max(max_limbs,layout['limbs'])
        else:
            refused_rows += 1
        words, position = [], 0
        while not position or position < count:
            n = min(128,count-position)
            fields = take('WORDS',dict(row=i,start=position,total=count,count=n,core=core),('runs',))
            expanded = []
            if not n:
                need(fields['runs']=='-','empty payload marker')
            else:
                previous = None
                for run in fields['runs'].split(','):
                    match = re.fullmatch(r'([0-9a-f]{8}):([1-9][0-9]*)',run)
                    need(match is not None,'literal RLE witness')
                    value,length = int(match[1],16),integer(match[2],128)
                    need(value != previous and 0 < length <= n-len(expanded),'canonical maximal bounded RLE')
                    expanded.extend([value]*length)
                    previous = value
                need(len(expanded)==n,'complete decompressed chunk')
            words.extend(expanded)
            position += n
            if not count:
                break
        need(len(words)==count,'complete exact output')
        if count:
            word_count = layout['limbs']
            mask = (1<<(32*word_count))-1
            for bin_index, index in enumerate(case['indices']):
                coefficient = table[index]
                shift = case['exponent']+coefficient['exponent']-layout['exponent']
                exact = expected_scalar(math,originals,case,bin_index)*coefficient['mantissa'] << shift
                encoded = (exact & mask).to_bytes(word_count*4,'little')
                observed = b''.join(struct.pack('<I',word) for word in words[bin_index*word_count:(bin_index+1)*word_count])
                need(observed==encoded,'every native exact limb: '+case['id'])
                digest.update(observed)
                total_samples += 1
        end = take('END',dict(row=i,guards=1,unchanged=1,core=core),('refusals','checks'))
        expected_refusals = (25 if case['width'] else 19) if case['controls'] else 0
        refusals = integer(end['refusals'])
        checks = integer(end['checks'])
        need(refusals==expected_refusals and checks>0,'actual refusal and immutability controls')
        total_checks += checks
        total_refusals += refusals
        total_words += count
        metrics.append(dict(id=case['id'],measure_status=measured,product_status=product,layout=layout,
                            exact_words=count,refusals=refusals,checks=checks))
    final = take('COMPLETE',dict(cases=len(cases),refusals=total_refusals,core=core),('checks',))
    # Only the worker increments the counter; its affinity check adds one/row.
    need(integer(final['checks'])==total_checks+len(cases),'complete runtime assertion accounting')
    take('STOP',dict(status='CAPTURED'))
    need(next(events,None) is None,'no extra product events')
    return dict(passed=True,cases=len(cases),exact_samples=total_samples,exact_limb_words=total_words,
        refused_rows=refused_rows,refusal_controls=total_refusals,runtime_assertions=integer(final['checks']),
        maximum_limbs=max_limbs,exact_limb_sha256=digest.hexdigest(),protocol_lines=line_count,
        coordinator_core=0,worker_core=core,rows=metrics)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',choices=SDK_HEAD,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--qemu-timeout',type=int,default=1200)
    args=parser.parse_args()
    need(sys.platform=='win32' and 1<=args.qemu_timeout<=1200,'pinned native Windows launcher')
    out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and out != ROOT/'.build' and not out.exists(),'fresh local campaign')
    out.mkdir(parents=True)
    report=dict(completed=False,passed=False,target=args.target,commands=[],inputs={},tools={},
        target_executed=False,frame_decoder_executed=False,setup_owner_executed=False,Xiph_decoder_executed=False,
        deferred_scopes_resumed=False,production_firmware=False,physical_device=False,numerical_qualified=False)
    def save():
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path, relative):
        target=out/'sources'/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(Path(path).read_bytes())
        report['inputs'][str(Path(path).resolve())]=dict(snapshot=target.relative_to(out).as_posix(),sha256=file_sha(target))
        return target
    private_executables=set()
    def public_argv(argv):
        return [('runtime-path-redacted:'+Path(str(value)).name) if str(value) in private_executables else str(value) for value in argv]
    def run(name,argv,timeout=60):
        argv=list(map(str,argv))
        row=dict(name=name,argv=public_argv(argv),state='starting',timeout_seconds=timeout)
        report['commands'].append(row); save()
        child=None; started=time.monotonic()
        try:
            with (out/(name+'.stdout.log')).open('xb') as stdout,(out/(name+'.stderr.log')).open('xb') as stderr:
                child=subprocess.Popen(argv,cwd=out,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,
                    creationflags=subprocess.CREATE_NO_WINDOW)
                row.update(state='running',pid=child.pid); save()
                child.wait(timeout=timeout)
                row.update(state='complete',exit_status=child.returncode)
        except BaseException as error:
            row.update(state='failed',error_type=type(error).__name__)
            raise RuntimeError('owned native command failed: '+name) from None
        finally:
            if child is not None and child.poll() is None:
                stopped=subprocess.run(['taskkill.exe','/PID',str(child.pid),'/T','/F'],capture_output=True,timeout=15,
                    creationflags=subprocess.CREATE_NO_WINDOW)
                row.update(state='forced_stop_nonpass',tree_stop_returncode=stopped.returncode)
                if child.poll() is None: child.kill()
                child.wait(timeout=15)
            row['elapsed_seconds']=time.monotonic()-started
            for stream in ('stdout','stderr'):
                path=out/(name+'.'+stream+'.log')
                row[stream+'_sha256']=file_sha(path) if path.exists() else None
            if child is not None: row['exit_status']=child.poll()
            save()
        need(row['state']=='complete' and row['exit_status']==0,'native command terminal0: '+name)
        return (out/(name+'.stdout.log')).read_text('utf-8',errors='replace').replace('\r\n','\n')
    save()
    try:
        math=load_math(); originals,cases=native_cases(math)
        body=(json.dumps(dict(schema='native-floor1-product-cases-v1',cases=cases),separators=(',',':'))+'\n').encode()
        (out/'cases.json').write_bytes(body); (out/'cases.h').write_bytes(header(cases))
        data_sha=sha(body)
        freeze(Path(__file__),Path('controller.py'))
        freeze(ROOT/'tests/test-vorbis-floor1-product.py',Path('math.py'))
        fixture=freeze(ROOT/'tests/native/vorbis_floor1_product_host.c',Path('host-fixture.c'))
        need(file_sha(fixture)==FIXTURE_PIN,'unchanged generic refusal helpers')
        upstream=freeze(ROOT/'idf/components/native_vorbis_xiph/upstream/libvorbis/lib/floor1.c',Path('upstream-floor1.c'))
        table=math.table_from_upstream(upstream.read_bytes())
        (out/'factors.json').write_text(json.dumps(table,separators=(',',':'))+'\n',encoding='utf-8')
        for name in COMPONENTS:
            for path in sorted((ROOT/'idf/components'/name).rglob('*')):
                if path.is_file(): freeze(path,Path('components')/name/path.relative_to(ROOT/'idf/components'/name))
        for path in sorted(PROJECT.rglob('*')):
            if path.is_file(): freeze(path,Path('project')/path.relative_to(PROJECT))
        shutil.copytree(out/'sources/project',out/'project')
        shutil.copyfile(out/'cases.h',out/'project/main/cases.h')
        shutil.copyfile(fixture,out/'project/main/host-fixture.c')
        shutil.copyfile(out/'project'/('sdkconfig.'+args.target+'.defaults'),out/'project/sdkconfig.defaults')
        report.update(prepared=True,cases=len(cases),cases_sha256=data_sha,cases_header_sha256=file_sha(out/'cases.h'),
            original_host_cases=len(originals),all_selected_host_scalars_retained=True,
            source_shape_note='Endpoint and pattern calls split into256-bin batches with the same common factor-grid extremes; original selected values retained. Three extra3-channel cases. Other host capacities/shape controls remain separate.')
        save()
        if args.prepare_only:
            print(json.dumps(dict(prepared=True,cases=len(cases)))); return 0
        if args.target=='esp32':
            sdk=REPO/'.idf/v6.0.2'; tools=REPO/'.idf/tools-v6.0.2'
            py=tools/'python_env/idf6.0_py3.12_env/Scripts/python.exe'
            qemu=ROOT/'.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe'
        else:
            sdk=REPO/'.idf/v6.1-9a97f6c54ec6'; tools=REPO/'.idf/tools-v6.1'
            py=tools/'python_env/idf6.1_py3.12_env/Scripts/python.exe'
            qemu=Path('C:/Work/QEMU-ESP32/bin/qemu-system-riscv32.exe')
        ps=Path(shutil.which('pwsh.exe') or '')
        git=Path(shutil.which('git.exe') or shutil.which('git') or '')
        rom=Path('C:/Work/QEMU-ESP32/pc-bios')
        for alias,path in (('powershell',ps),('python',py),('qemu',qemu),('git',git)):
            need(path.is_file(),'installed native tool: '+alias)
            private=bool(re.search(r'(?i)[/\\]Users[/\\]',str(path)))
            if private: private_executables.add(str(path))
            report['tools'][alias]=dict(sha256=file_sha(path),path='runtime-path-redacted' if private else str(path),personal_path_redacted=private)
        report['roms']={path.name:file_sha(path) for path in sorted(rom.glob(args.target+'*rom*.bin'))}
        need(report['roms'],'explicit target ROM')
        need(run('sdk-head',[git,'-c','core.longpaths=true','-C',sdk,'rev-parse','HEAD']).strip()==SDK_HEAD[args.target],'pinned SDK revision')
        need(not run('sdk-clean',[git,'-c','core.longpaths=true','-C',sdk,'status','--porcelain','--untracked-files=no']).strip(),'clean SDK')
        report['sdk_revision']=SDK_HEAD[args.target]
        run('build',[ps,'-NoProfile','-NonInteractive','-File',out/'sources/project/sdk-build.ps1','-Campaign',out,
             '-SdkDirectory',sdk,'-ToolsDirectory',tools,'-PythonExecutable',py,'-Target',args.target,
             '-CasesSha256',data_sha,'-CasesHeaderSha256',file_sha(out/'cases.h')],1200)
        child=json.loads((out/'sdk-child.json').read_text('utf-8-sig'))
        need(child['exit_status']==0 and child['pid']>0,'actual SDK child terminal')
        report['sdk_child']=child
        build=out/'build'; description=json.loads((build/'project_description.json').read_bytes())
        elf=build/description['app_elf']; elf_body=elf.read_bytes()
        need(elf.resolve().is_relative_to(build) and elf_body[:6]==b'\x7fELF\x01\x01' and
             int.from_bytes(elf_body[18:20],'little')==(94 if args.target=='esp32' else 243),'actual native ELF32 machine')
        compiler=Path(description['c_compiler']); nm=compiler.with_name(compiler.name.replace('gcc','nm'))
        database=json.loads((build/'compile_commands.json').read_bytes())
        selected={}
        for name,source in (('fixture',out/'project/main/main.c'),('product',out/'sources/components/native_vorbis_floor1_product/floor1_product.c')):
            found=[row for row in database if Path(row['file']).resolve()==source]
            need(len(found)==1,'one actual compile unit: '+name); selected[name]=found[0]
            need(all(flag in found[0]['command'] for flag in ('-fstack-usage','-fno-fast-math','-ffp-contract=off')),'actual numeric compiler flags')
        report['compile_rows']=selected
        symbols=run('symbols',[nm,'-n','-S',elf])
        need(all(re.search(r'\bnative_vorbis_floor1_'+name+r'$',symbols,re.M) for name in ('scale','scale_measure')),'exercised product symbols')
        need(not re.search(r'\b(?:native_vorbis_(?:frame_decode|setup_owner_replace)|vorbis_synthesis|esp_vorbis_dec_open|floor1_host_fixture_main_not_executed)$',symbols,re.M),'no decoder/owner/unexecuted-main symbols')
        usage=[]
        for row in selected.values():
            path=build/Path(row['output']).with_suffix('.su'); need(path.is_file(),'actual stack record'); usage.append(path)
        report['stack_records']={path.relative_to(out).as_posix():path.read_text('utf-8').splitlines() for path in usage}
        recipe=json.loads((build/'flasher_args.json').read_bytes())
        need(recipe['flash_settings']==dict(flash_mode='dio',flash_size='4MB',flash_freq='40m'),'isolated DIO profile')
        flashes={int(offset,0):(build/name).resolve() for offset,name in recipe['flash_files'].items()}
        need(set(flashes)==({4096,32768,65536} if args.target=='esp32' else {0,32768,65536}) and
             all(path.is_relative_to(build) for path in flashes.values()),'bounded image recipe')
        flash=out/'qemu-flash.bin'
        argv=[py,'-m','esptool','--chip',args.target,'merge-bin','--output',flash,'--flash-mode','dio','--flash-size','4MB','--flash-freq','40m']
        for offset,path in sorted(flashes.items()): argv += [hex(offset),path]
        run('merge',argv+['--pad-to-size','4MB'])
        config=(out/'sdkconfig').read_text()
        need(bool(re.search(r'^CONFIG_FREERTOS_UNICORE=y$',config,re.M))==(args.target=='esp32c3'),'native core profile')
        need('CONFIG_ESP_TASK_WDT_EN=y' in config and 'CONFIG_ESP_TASK_WDT_INIT=y' in config,'watchdog remains enabled')
        qargs=[qemu,'-audiodev','none,id=quiet','-M','esp32,audiodev=quiet'] if args.target=='esp32' else [qemu,'-M','esp32c3']
        qargs += ['-smp','2' if args.target=='esp32' else '1','-L',rom,'-display','none','-monitor','none','-serial','stdio','-no-reboot','-snapshot','-nic','none','-drive','file='+str(flash)+',if=mtd,format=raw']
        log=run('qemu',qargs,args.qemu_timeout)
        report['target_executed']=True
        measured=validate_log(log+'\n'+(out/'qemu.stderr.log').read_text('utf-8',errors='replace'),cases,originals,math,table,args.target,data_sha)
        (out/'measurement.json').write_text(json.dumps(measured,indent=2)+'\n',encoding='utf-8')
        need(measured['exact_samples']==619564 and measured['exact_limb_words']==11817093 and
             measured['maximum_limbs']==36 and measured['refused_rows']==23,'complete retained scalar campaign')
        need(all(file_sha(path)==pin['sha256']==file_sha(out/pin['snapshot']) for path,pin in report['inputs'].items()),'all original and frozen inputs unchanged')
        outputs=[elf,elf.with_suffix('.map'),flash,out/'sdkconfig',out/'sdk-child.json',*usage,*flashes.values()]
        outputs += [build/name for name in ('compile_commands.json','project_description.json','flasher_args.json','CMakeCache.txt','config/sdkconfig.h','build.ninja','CMakeFiles/rules.ninja')]
        report['build_outputs']={path.relative_to(out).as_posix():file_sha(path) for path in outputs}
        report.update(completed=True,passed=True,numerical_qualified=True,
            measurements={key:value for key,value in measured.items() if key!='rows'},measurement_sha256=file_sha(out/'measurement.json'))
        save(); print(json.dumps(dict(completed=True,target=args.target,**report['measurements']))); return 0
    except BaseException as error:
        report.update(error_type=type(error).__name__,error=str(error))
        save(); raise


if __name__=='__main__':
    raise SystemExit(main())
