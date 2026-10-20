"""Read-only narrow native output metrics review and actual Xtensa object checks."""
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
MAIN=ROOT/'idf/esp32-cyd2usb-native/main'
BUILD=ROOT/'idf/esp32-cyd2usb-native/build-c3-transfer'
SDK=Path('C:/Work/yoRadio/.idf/v6.0.2')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def windows_args(value):
    count=ctypes.c_int()
    parse=ctypes.windll.shell32.CommandLineToArgvW
    parse.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(ctypes.c_int)]
    parse.restype=ctypes.POINTER(wintypes.LPWSTR)
    pointer=parse(value,ctypes.byref(count));assert pointer
    values=[pointer[index] for index in range(count.value)]
    ctypes.windll.kernel32.LocalFree.argtypes=[ctypes.c_void_p]
    ctypes.windll.kernel32.LocalFree(ctypes.cast(pointer,ctypes.c_void_p))
    return values


sources=[MAIN/'native_output_metrics.c',MAIN/'native_output_metrics.h',
    ROOT/'tests/run-cyd-output-metrics.py',*[ROOT/'tests/native/cyd_output_metrics'/name for name in ('platform.h','test.c','README.md')]]
source_hashes={str(path):sha(path) for path in sources}
for path in sources:
    target=OUT/'sources'/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
frozen_main=OUT/'sources/idf/esp32-cyd2usb-native/main'
database=json.loads((BUILD/'compile_commands.json').read_text())
row=next(row for row in database if Path(row['file']).name=='native_health.c')
(OUT/'original-command-row.json').write_text(json.dumps(row,indent=2)+'\n')
base=windows_args(row['command'])
compiler=Path(base[0]);tool_dir=compiler.parent
objdump=tool_dir/'xtensa-esp32-elf-objdump.exe';nm=tool_dir/'xtensa-esp32-elf-nm.exe'
config=(BUILD/'config/sdkconfig.h').read_text()
assert not re.search(r'^#define CONFIG_FREERTOS_UNICORE\b',config,re.M)
assert not re.search(r'^#define CONFIG_YORADIO_NATIVE_DIAGNOSTICS\b',config,re.M)
baseline_files=[BUILD/'compile_commands.json',BUILD/'config/sdkconfig.h',BUILD/'yoradio_cyd2usb_native.elf',BUILD/'yoradio_cyd2usb_native.map',
    SDK/'components/freertos/FreeRTOS-Kernel/portable/xtensa/port.c',
    SDK/'components/freertos/FreeRTOS-Kernel/portable/xtensa/include/freertos/portmacro.h',
    SDK/'components/esp_hw_support/include/spinlock.h',SDK/'components/freertos/linker.lf',SDK/'components/esp_common/include/esp_attr.h']
baseline_hashes={str(path):sha(path) for path in baseline_files}
report={'passed':False,'scope':__doc__,'physical_hardware':False,'sdk_object_only':True,'new_helper_integrated':False,
    'source_sha256':source_hashes,'baseline_sha256':baseline_hashes,
    'tools_sha256':{str(path):sha(path) for path in (compiler,objdump,nm)},'commands':[],'variants':{}}


def execute(name,command,cwd=None):
    result=subprocess.run(command,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
    (OUT/(name+'.log')).write_bytes(result.stdout)
    report['commands'].append({'name':name,'command':command,'cwd':str(cwd) if cwd else None,
        'exit_status':result.returncode,'log_sha256':sha(OUT/(name+'.log'))})
    assert result.returncode==0,(name,result.stdout.decode(errors='replace'))
    return result.stdout.decode(errors='replace')


try:
    execute('compiler-version',[str(compiler),'--version'])
    head=execute('sdk-head',['git','-c','core.longpaths=true','-C',str(SDK),'rev-parse','HEAD']).strip()
    assert head=='7101770dc6db2667b3c477cc31365dd1acd6db4e';report['sdk_commit']=head
    for variant,diagnostic in [('quiet',False),('diagnostic',True)]:
        directory=OUT/('objects-'+variant);directory.mkdir(exist_ok=False)
        variant_config=config+('\n#define CONFIG_YORADIO_NATIVE_DIAGNOSTICS 1\n' if diagnostic else '')
        (directory/'sdkconfig.h').write_text(variant_config)
        command=base.copy();assert Path(command[-1])==Path(row['file'])
        command[-1]=str(frozen_main/'native_output_metrics.c')
        command[command.index('-o')+1]=str(directory/'metrics.obj')
        for index,argument in enumerate(command):
            if argument.startswith('-I') and Path(argument[2:])==BUILD/'config':command[index]='-I'+str(directory)
            if argument.startswith('@'):
                original=Path(argument[1:]);baseline_hashes[str(original)]=sha(original)
                response=directory/'cflags';text=original.read_text()
                spec=re.search(r'-specs=([^"\n]+)',text)
                assert spec;spec_source=Path(spec.group(1));baseline_hashes[str(spec_source)]=sha(spec_source)
                (directory/'picolibc.specs').write_bytes(spec_source.read_bytes())
                response.write_text(text.replace(spec.group(1),(directory/'picolibc.specs').as_posix()))
                command[index]='@'+str(response)
        dependencies=directory/'dependencies.d'
        dependency_command=command+['-M','-MF',str(dependencies),'-MT','metrics']
        execute(variant+'-dependencies',dependency_command,cwd=Path(row['directory']))
        body=dependencies.read_text().replace('\\\n',' ');body=body.split(': ',1)[1]
        dependency_paths=[Path(value) for value in shlex.split(body.replace('\\','/'))]
        dependency_hashes={str(path.resolve()):sha(path) for path in dependency_paths}
        execute(variant+'-compile',command,cwd=Path(row['directory']))
        assert all(sha(Path(path))==digest for path,digest in dependency_hashes.items())
        symbols=execute(variant+'-symbols',[str(objdump),'-t',str(directory/'metrics.obj')])
        disassembly=execute(variant+'-disassembly',[str(objdump),'-dr',str(directory/'metrics.obj')])
        undefined=execute(variant+'-undefined',[str(nm),'-u',str(directory/'metrics.obj')])
        assert not re.search(r'\b(?:malloc|calloc|realloc|free|__atomic\w*)\b',undefined)
        assert ('esp_timer_get_time' in undefined)==diagnostic
        assert 'increment' not in symbols
        queue_symbol=next(line for line in symbols.splitlines() if line.endswith(' native_output_metrics_queue_drop'))
        state_symbol=next(line for line in symbols.splitlines() if line.endswith(' s_output_metrics'))
        lock_symbol=next(line for line in symbols.splitlines() if line.endswith(' s_output_metrics_lock'))
        assert '.iram1.' in queue_symbol and '.dram1.' in state_symbol and '.dram1.' in lock_symbol
        sections=re.split(r'Disassembly of section ([^:\n]+):\n',disassembly)
        iram='\n'.join(body for name,body in zip(sections[1::2],sections[2::2]) if name.startswith('.iram1.'))
        assert 'esp_timer_get_time' not in iram and 'increment' not in iram and '__atomic' not in iram
        external=set(re.findall(r'R_XTENSA_32\s+(\w+)',iram))
        # Internal section symbols refer to literal addresses; the only
        # external callees in this IRAM function are the two SDK port APIs.
        assert external<=set(['xPortEnterCriticalTimeout','vPortExitCritical','s_output_metrics','s_output_metrics_lock'])
        report['variants'][variant]={'diagnostic':diagnostic,'dependency_sha256':dependency_hashes,
            'object_sha256':sha(directory/'metrics.obj'),'config_sha256':sha(directory/'sdkconfig.h'),
            'queue_symbol':queue_symbol,'state_symbol':state_symbol,'lock_symbol':lock_symbol,
            'undefined_symbols':undefined.strip().splitlines(),'iram_external_relocations':sorted(external),
            'increment_fully_inlined':True,'warnings_errors':[]}
    elf=BUILD/'yoradio_cyd2usb_native.elf'
    execute('sdk-elf-symbols',[str(objdump),'-t',str(elf)])
    for symbol in ('xPortEnterCriticalTimeout','vPortExitCritical','__assert_func','esp_cpu_compare_and_set'):
        execute('sdk-'+symbol,[str(objdump),'-d','--disassemble='+symbol,str(elf)])
    report['live_inputs_unchanged']={path:sha(Path(path))==digest for group in (source_hashes,baseline_hashes,report['tools_sha256']) for path,digest in group.items()}
    assert all(report['live_inputs_unchanged'].values());report['passed']=True
finally:
    (OUT/'compile-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS actual quiet/diagnostic Xtensa objects: queue IRAM, metrics/lock DRAM, no libatomic/heap/clock ISR calls')
