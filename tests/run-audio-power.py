"""Actual C3/CYD audio control and receive hooks with the real shared power policy.

SDK transport and RTOS/queue operations are explicit deterministic host seams;
there is no RF, electrical power, target scheduler or PCM quality claim.
Maintenance uses the separate full three-owner --network-power campaigns.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
POWER='idf/components/native_network_power'


def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def function(source,name):
    match=re.search(r'^(?:static )?[^\n]*\b'+name+r'\(',source,re.M);assert match,name
    end=source.index('{',match.start())+1;depth=1
    while depth:depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[match.start():end]+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    files=[Path(__file__).relative_to(ROOT).as_posix(),'tests/native/audio_power_control_test.c','tests/native/audio_power_cyd_stream_test.c',POWER+'/native_network_power.c',POWER+'/include/native_network_power.h']
    for project in ['esp32c3-oled-native','esp32-cyd2usb-native']:
        files += ['idf/'+project+'/main/'+name for name in ['audio_service.c','audio_service.h','native_state.c','native_state.h']]
    files += ['idf/esp32-cyd2usb-native/main/native_health.h']
    files += [p.relative_to(ROOT).as_posix() for p in (ROOT/'idf/components/native_stream/include').glob('*.h')]
    files += ['idf/components/native_stream/icy_title.c']
    hashes={}
    for name in files:
        data=(ROOT/name).read_bytes();hashes[name]=hashlib.sha256(data).hexdigest();target=out/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    frozen=out/'sources';commands=[];results={}
    def execute(command,name,expected=0):
        commands.append(command);result=subprocess.run((['wsl.exe','--exec'] if sys.platform=='win32' else [])+command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
        (out/(name+'.log')).write_bytes(result.stdout)
        if expected is not None:assert result.returncode==expected,(name,result.stdout.decode(errors='replace'))
        return result
    env=['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','90']
    for board,project in [('c3','esp32c3-oled-native'),('cyd','esp32-cyd2usb-native')]:
        folder=out/board;folder.mkdir();(folder/'freertos').mkdir()
        (folder/'freertos/FreeRTOS.h').write_text('''#pragma once
#include <assert.h>
#include <pthread.h>
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
typedef pthread_mutex_t *SemaphoreHandle_t;
typedef pthread_mutex_t portMUX_TYPE;
typedef int BaseType_t;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(p) assert(!pthread_mutex_lock(p))
#define portEXIT_CRITICAL(p) assert(!pthread_mutex_unlock(p))
#define pdTRUE 1
#define pdMS_TO_TICKS(x) (x)
#define portMAX_DELAY UINT32_MAX
static inline SemaphoreHandle_t xSemaphoreCreateMutex(void){SemaphoreHandle_t p=malloc(sizeof(*p));assert(p&&!pthread_mutex_init(p,NULL));return p;}
static inline int xSemaphoreTake(SemaphoreHandle_t p,unsigned timeout){(void)timeout;assert(!pthread_mutex_lock(p));return 1;}
static inline void xSemaphoreGive(SemaphoreHandle_t p){assert(!pthread_mutex_unlock(p));}
size_t strlcpy(char *,const char *,size_t);
''')
        (folder/'freertos/semphr.h').write_text('#include "FreeRTOS.h"\n')
        (folder/'esp_err.h').write_text('#pragma once\ntypedef int esp_err_t;\n#define ESP_OK 0\n#define ESP_FAIL (-1)\n#define ESP_ERR_INVALID_ARG (-2)\n#define ESP_ERR_INVALID_STATE (-3)\n#define ESP_ERR_TIMEOUT (-4)\n')
        main=frozen/'idf'/project/'main';source=(main/'audio_service.c').read_text()
        start=source.index('typedef struct {\n    uint32_t generation;\n    native_codec_t requested_codec;');end=source.index('} play_command_t;',start)+len('} play_command_t;')
        types=source[start:end]+'\n';start=source.index('enum { MAINTENANCE_OFF,');end=source.index('static bool maintenance_active(',start);types+=source[start:end]
        if board=='cyd':types+='enum { AUDIO_START_OFF, AUDIO_STARTING, AUDIO_START_READY };\n'
        (folder/'controls-types.inc').write_text(types)
        names=['maintenance_active','state_set_audio']
        if board=='c3':names+=['advance_generation','play_locked']
        names+=['audio_service_play','audio_service_stop']
        if board=='c3':names+=['audio_service_resume']
        controls=''.join(function(source,name) for name in names);(folder/'controls.inc').write_text(controls)
        binary=folder/'controls'
        command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-variable','-Wno-unused-function','-Wno-format-truncation','-pthread','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
                 *(['-DPOWER_CYD=1'] if board=='cyd' else []),'-I'+host(folder),'-I'+host(main),'-I'+host(frozen/POWER/'include'),host(frozen/'tests/native/audio_power_control_test.c'),host(main/'native_state.c'),host(frozen/POWER/'native_network_power.c'),'-o',host(binary)]
        execute(command,board+'-controls-build');result=execute(env+[host(binary)],board+'-controls-test');results[board]=result.stdout.decode()
        if board=='cyd':
            stream_types='\n'.join(re.findall(r'^#define (?:STREAM_CHUNK_SIZE|MAX_HTTP_REDIRECTS|STREAM_READ_TIMEOUT_MS)[^\n]+',source,re.M))+'\n'
            for marker,endmarker in [('typedef struct {\n    uint32_t generation;\n    native_codec_t requested_codec;','} play_command_t;'),('typedef struct {\n    uint32_t generation;\n    native_codec_t codec;\n    uint16_t data_size;','} encoded_packet_t;'),('typedef struct {\n    uint32_t interval;','} stream_headers_t;'),('typedef struct {\n    uint32_t generation;\n    native_codec_t codec;\n    bool first;','} stream_input_t;')]:
                first=source.index(marker);last=source.index(endmarker,first)+len(endmarker);stream_types+=source[first:last]+'\n'
            stream_types+='enum {AUDIO_START_OFF,AUDIO_STARTING,AUDIO_START_READY};\n'+re.search(r'^#define STREAM_INPUT_ACTIVE[^\n]+',source,re.M).group(0)+'\n'
            (folder/'stream-types.inc').write_text(stream_types)
            stream=''.join(function(source,name) for name in ['codec_name','state_set_audio','stream_header_event','open_stream','read_stream','send_encoded','stream_transport_reset','stream_initial_pending','stream_confirmation_expired','send_stream_audio','finish_stream_audio','stream_audio','stream_title','stream_task','audio_service_play','audio_service_stop'])
            (folder/'stream.inc').write_text(stream)
            stream_command=command.copy();stream_command.remove('-DPOWER_CYD=1')
            stream_command[stream_command.index(host(frozen/'tests/native/audio_power_control_test.c'))]=host(frozen/'tests/native/audio_power_cyd_stream_test.c')
            stream_command[1:1]=['-I'+host(frozen/'idf/components/native_stream/include'),host(frozen/'idf/components/native_stream/icy_title.c')]
            stream_command[-1]=host(folder/'stream')
            execute(stream_command,'cyd-stream-build');result=execute(env+[host(folder/'stream')],'cyd-stream-test');results['cyd-receive']=result.stdout.decode()
    report=dict(passed=True,scope=__doc__,physical_hardware=False,sanitizers=['ASan','UBSan'],source_sha256=hashes,commands=commands,controls=results)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(results))


if __name__=='__main__':main()
