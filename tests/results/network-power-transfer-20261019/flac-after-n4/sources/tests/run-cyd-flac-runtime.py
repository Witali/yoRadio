"""Execute the actual CYD decoder task with the real shared FLAC adapter/core.

The RTOS FIFO and blocking-send scheduler are scripted platform seams. Native
state, decoder task, callback, queue sizing, adapter and segmented core execute
under ASan/UBSan. This does not measure hardware heap/stack/DMA/timing or assert
FLAC CRC/MD5/full malformed-stream conformance. The retained vendor task path is
covered separately by run-cyd-lifecycle.py, whose codec calls are host doubles.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = 'idf/esp32-cyd2usb-native/main'
CORE = 'yoRadio/src/audioI2S/flac_decoder'
ADAPTER = 'idf/components/custom_flac'
TEST = 'tests/native/cyd_flac_runtime'


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def function(source, name):
    match = re.search(r'^(?:static )?[^\n]*\b' + name + r'\(', source, re.M)
    assert match, name
    end = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    files = [Path(__file__).relative_to(ROOT).as_posix(), TEST+'/task.c', TEST+'/allocations.cpp', TEST+'/registration.c',
             MAIN+'/audio_service.c', MAIN+'/native_state.c', MAIN+'/native_state.h',
             MAIN+'/native_audio_output.c', MAIN+'/native_health.h', MAIN+'/decoder_registration.c',
             MAIN+'/Kconfig.projbuild', MAIN+'/CMakeLists.txt',
             'idf/components/native_stream/include/audio_completion.h',
             CORE+'/flac_decoder.cpp', CORE+'/flac_decoder.h',
             ADAPTER+'/custom_flac_adapter.cpp', ADAPTER+'/custom_flac_adapter.h',
             'tools/audio_test_server/generate_flac_depths.py', 'tests/native/flac_bounds/Arduino.h']
    files += [p.relative_to(ROOT).as_posix() for p in (ROOT/'tests/native/flac_depths').rglob('*.h')]
    hashes = {}
    for name in files:
        data = (ROOT/name).read_bytes(); hashes[name] = hashlib.sha256(data).hexdigest()
        target = out/'sources'/name; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
    frozen = out/'sources'; generated = out/'generated'; generated.mkdir()
    (generated/'freertos').mkdir()
    (generated/'freertos/FreeRTOS.h').write_text('''#pragma once
#include <stddef.h>
#include <stdint.h>
#include <assert.h>
#include <pthread.h>
#include <stdlib.h>
typedef pthread_mutex_t *SemaphoreHandle_t;
#define pdTRUE 1
#define pdMS_TO_TICKS(x) (x)
#define portMAX_DELAY UINT32_MAX
static inline SemaphoreHandle_t xSemaphoreCreateMutex(void) {
    SemaphoreHandle_t p=(SemaphoreHandle_t)malloc(sizeof(*p)); assert(p); assert(!pthread_mutex_init(p,NULL)); return p;
}
static inline int xSemaphoreTake(SemaphoreHandle_t p,unsigned t) {(void)t;assert(!pthread_mutex_lock(p));return 1;}
static inline void xSemaphoreGive(SemaphoreHandle_t p) {assert(!pthread_mutex_unlock(p));}
size_t strlcpy(char *,const char *,size_t);
''')
    (generated/'freertos/semphr.h').write_text('#include "FreeRTOS.h"\n')
    source = (frozen/MAIN/'audio_service.c').read_text()
    start = source.index('#ifdef CONFIG_YORADIO_FLAC_DECODER_CUSTOM\ntypedef struct')
    callback = source[start:source.index('static void decoder_release(',start)]
    legacy_start = source.index('#ifdef YORADIO_CUSTOM_LEGACY_DECODER\ntypedef struct')
    callback = source[legacy_start:start] + callback
    production = ''.join(function(source,name) for name in ('simple_decoder_type','codec_name','state_set_decoder_bitrate','publish_stream_info','send_pcm','send_pcm_end'))
    production = function((frozen/MAIN/'native_audio_output.c').read_text(),'native_audio_output_supports_pcm') + production
    production += callback + function(source,'decoder_release') + function(source,'decoder_task')
    (generated/'production.inc').write_text(production)
    (generated/'registration.inc').write_text(re.sub(r'^#include[^\n]*\n','',(frozen/MAIN/'decoder_registration.c').read_text(),flags=re.M))
    spec = importlib.util.spec_from_file_location('fixtures',frozen/'tools/audio_test_server/generate_flac_depths.py')
    generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
    manifest = generator.generate(out/'fixtures')
    large = generator.generate(out/'large-fixtures',large_blocks=True)
    rows = [(out/'fixtures',row) for row in manifest['fixtures']]
    rows += [(out/'large-fixtures',row) for row in large['fixtures']]
    commands = []
    def execute(command,name,expected=0):
        commands.append(command)
        result = subprocess.run((['wsl.exe','--exec'] if sys.platform == 'win32' else [])+command,
                                stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
        (out/(name+'.log')).write_bytes(result.stdout)
        if expected is not None and result.returncode != expected:
            raise RuntimeError(f'{name}: exit={result.returncode}\n'+result.stdout.decode(errors='replace'))
        return result
    common = ['-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-variable','-Wno-unused-function',
              '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-pthread',
              '-DFLAC_SEGMENTED_WORKSPACE=1','-DFLAC_OUTPUT_FRAMES=512','-DCONFIG_YORADIO_FLAC_DECODER_CUSTOM=1',
              '-I'+host(generated),'-I'+host(frozen/MAIN),'-I'+host(frozen/ADAPTER),
              '-I'+host(frozen/'idf/components/native_stream/include'),
              '-I'+host(frozen/'tests/native/flac_bounds'),'-I'+host(frozen/'tests/native/flac_depths'),'-I'+host(frozen/CORE)]
    units = [('gcc','c11',frozen/TEST/'task.c','task'),('gcc','c11',frozen/MAIN/'native_state.c','state'),
             ('g++','c++14',frozen/TEST/'allocations.cpp','allocations'),
             ('g++','c++14',frozen/ADAPTER/'custom_flac_adapter.cpp','adapter'),
             ('g++','c++14',frozen/CORE/'flac_decoder.cpp','core')]
    objects = []
    for compiler,standard,path,name in units:
        obj = out/(name+'.o'); objects.append(host(obj))
        execute([compiler,'-std='+standard,*common,'-c',host(path),'-o',host(obj)],'build-'+name)
    binary = out/'task'
    link = ['g++','-fsanitize=address,undefined','-fno-pie','-no-pie','-pthread',
            '-Wl,--wrap=malloc,--wrap=realloc,--wrap=free,--wrap=_ZnwmRKSt9nothrow_t,--wrap=_ZdlPv,--wrap=_ZdlPvm']
    execute(link+objects+['-o',host(binary)],'link')
    env = ['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','90']
    selection_checks = []
    for selection in ('vendor','custom'):
        flags = [flag for flag in common if flag != '-DCONFIG_YORADIO_FLAC_DECODER_CUSTOM=1']
        if selection == 'custom': flags += ['-DCONFIG_YORADIO_FLAC_DECODER_CUSTOM=1']
        target = out/('registration-'+selection)
        execute(['gcc','-std=c11',*flags,'-DCONFIG_YORADIO_MP3_DECODER_ESPRESSIF=1','-DCONFIG_YORADIO_AAC_DECODER_ESPRESSIF=1',
                 host(frozen/TEST/'registration.c'),'-no-pie','-o',host(target)],'registration-'+selection+'-build')
        execute(env+[host(target)],'registration-'+selection+'-test')
        selection_checks.append(selection)
    comparisons = []; groups = []
    for folder,row in rows:
        path = folder/row['file']; pcm = folder/(row['file']+'.pcm')
        reference = subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(path),'-f','s16le','-acodec','pcm_s16le','-'])
        assert len(reference) == row['pcm_bytes'] and hashlib.sha256(reference).hexdigest() == row['pcm_sha256']
        pcm.write_bytes(reference)
        for schedule in (0,1,127,2048):
            name = row['name']+'-'+str(schedule)
            execute(env+[host(binary),host(path),host(pcm),str(row['bits']),str(row['channels']),'pcm',str(schedule)],name)
            comparisons.append(dict(name=row['name'],schedule=schedule,pcm_bytes=len(reference),pcm_sha256=row['pcm_sha256']))
    chosen = next(row for row in manifest['fixtures'] if row['name'] == 'flac-24bit-mid-verbatim')
    path = out/'fixtures'/chosen['file']; pcm = path.with_name(path.name+'.pcm')
    original = path.read_bytes(); metadata = bytearray(original[:42]); metadata[4] &= 0x7f
    metadata += b'\x01\x00\x04\x03'+bytes(1027)+b'\x81\x00\x00\x00'
    mixed = out/'metadata.flac'; mixed.write_bytes(metadata+original[42:])
    def case(name,path,mode,extra,reference=pcm):
        result = execute(env+[host(binary),host(path),host(reference),'24','2',mode,str(extra)],name)
        groups.append(dict(name=name,output=result.stdout.decode()))
    case('metadata-cuts',mixed,'cuts',len(metadata))
    case('empty-eof',path,'empty',0)
    case('persistent-oom',path,'oom',0)
    large_row = next(row for row in large['fixtures'] if row['name'] == 'flac-24bit-stereo-verbatim-block8192')
    large_path = out/'large-fixtures'/large_row['file']
    case('persistent-oom-block8192',large_path,'oom',0,large_path.with_name(large_path.name+'.pcm'))
    for mode in (1,2): case('blocked-send-'+str(mode),path,'cancel',mode)
    for mode in (1,2,3): case('owner-transition-'+str(mode),path,'owner',mode)
    case('codec-replacement',path,'codec',0)
    case('codec-drain-reopen',path,'drain',0)
    legacy_obj = out/'custom-legacy.o'; legacy_binary = out/'custom-legacy'
    execute(['gcc','-std=c11',*common,'-DYORADIO_CUSTOM_LEGACY_DECODER=1','-DCONFIG_YORADIO_AAC_DECODER_HELIX=1',
             '-c',host(frozen/TEST/'task.c'),'-o',host(legacy_obj)],'custom-legacy-build')
    execute(link+[host(legacy_obj),*objects[1:],'-o',host(legacy_binary)],'custom-legacy-link')
    for mode in ('pcm','codec'):
        execute(env+[host(legacy_binary),host(path),host(pcm),'24','2',mode,'127' if mode == 'pcm' else '0'],'custom-legacy-'+mode)
        groups.append(dict(name='custom-legacy-'+mode,passed=True))
    for window in (0,65536,65537):
        data = bytearray(original); data[15:18] = window.to_bytes(3,'big')
        target = out/('frame-window-'+str(window)+'.flac'); target.write_bytes(data)
        if window > 65536: case('frame-window-'+str(window),target,'invalid',0)
        else: case('frame-window-'+str(window),target,'pcm',127)
    # Exact semantic mutants execute the same positive fixture. Neither
    # sanitizer crashes nor timeouts count as detection: require assertion.
    mutants = {
        'source-depth-as-pcm': ('.bits_per_sample = info->pcm_bits_per_sample,','.bits_per_sample = info->bits_per_sample,'),
        'terminal-workspace-retained': ('packet_done:\n','packet_done:\n'),
        'ack-before-release': ('                decoder_release(&decoder, &output, &output_size);',
                               '                maintenance_ack(MAINTENANCE_DECODER);\n                decoder_release(&decoder, &output, &output_size);'),
    }
    mutant_results = []
    for name,(before,after) in mutants.items():
        if name == 'terminal-workspace-retained':
            prefix,tail = production.split('packet_done:\n',1)
            before = 'if (flac_decoder) custom_flac_decoder_destroy(flac_decoder);'
            assert before in tail
            changed = prefix+'packet_done:\n'+tail.replace(before,'/* deliberately retained workspace */',1)
        else:
            assert production.count(before) == 1; changed = production.replace(before,after,1)
        mutant_dir = generated/name; mutant_dir.mkdir(); (mutant_dir/'production.inc').write_text(changed)
        obj = out/(name+'.o')
        execute(['gcc','-std=c11','-I'+host(mutant_dir),*common,'-c',host(frozen/TEST/'task.c'),'-o',host(obj)],name+'-build')
        target = out/name; execute(link+[host(obj),*objects[1:],'-o',host(target)],name+'-link')
        fixture = next(row for row in manifest['fixtures'] if row['name'] == 'flac-4bit-stereo-verbatim') if name == 'source-depth-as-pcm' else chosen
        file = out/'fixtures'/fixture['file']
        mode,extra = ('owner','3') if name == 'ack-before-release' else ('pcm','127')
        result = execute(env+[host(target),host(file),host(file.with_name(file.name+'.pcm')),str(fixture['bits']),str(fixture['channels']),mode,extra],name+'-test',None)
        assert result.returncode not in (0,124) and b'Assertion' in result.stdout and b'Sanitizer' not in result.stdout
        mutant_results.append(dict(name=name,detected=True,exit_code=result.returncode))
    (generated/'production.inc').write_text(production)
    report = dict(passed=True,scope=__doc__,physical_hardware=False,sanitizers=['ASan','UBSan'],
                  source_sha256=hashes,generated_sha256={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in generated.rglob('*') if p.is_file()},
                  exact_pcm_comparisons=len(comparisons),pcm=comparisons,lifecycle=groups,registration=selection_checks,mutants=mutant_results,commands=commands)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,pcm_comparisons=len(comparisons),lifecycle=len(groups),mutants=len(mutant_results))))


if __name__ == '__main__': main()
