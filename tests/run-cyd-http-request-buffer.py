"""Qualify the narrow SDK6.0.2 completed-GET TX release prototype on the host.

Actual SDK request generation, body sender, cached response reader and request
cleanup span execute with real SDK header/utilities. Transport, response-state
preparation, allocation accounting and private struct layout are explicit host
seams. This is not full auth/redirect/parser/TLS or target ABI/heap evidence.
No installed SDK or production configuration is modified.
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
CASES=['invalid','long-reuse','capacity8192','idempotent','oom','partial-null',
       'states','async','body-pending','write-pending','post','head',
       'write-failure','async-partial','borrowed-body','authorization','cached-body']


def sha(data):return hashlib.sha256(data).hexdigest()


def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def execute(command):
    process=subprocess.run((['wsl.exe','--exec'] if sys.platform=='win32' else [])+command,
                           stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
    return process.returncode,process.stdout


def function(source,name):
    # Match a definition, not the public forward declarations in the SDK source.
    match=re.search(r'^(?:static[ \t]+)?[A-Za-z_]\w*[ \t*]+'+re.escape(name)+r'\s*\([^;{}]*\)\s*\{',source,re.M)
    if not match:raise ValueError('Missing SDK function: '+name)
    position=source.index('{',match.start())+1;depth=1
    while depth:
        if source.startswith('//',position):position=source.index('\n',position)+1
        elif source.startswith('/*',position):position=source.index('*/',position+2)+2
        elif source[position] in ('"',"'"):
            quote=source[position];position+=1
            while source[position]!=quote:position+=2 if source[position]=='\\' else 1
            position+=1
        else:
            depth+=(source[position]=='{')-(source[position]=='}');position+=1
    return source[match.start():position]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--idf',type=Path,default=Path('C:/Work/yoRadio/.idf/v6.0.2'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve()
    if not out.is_relative_to(ROOT/'.build'):
        parser.error('Use a fresh output directory below repository .build/')
    out.mkdir(parents=True,exist_ok=False)
    sdk=args.idf.resolve()/'components/esp_http_client'
    files=[Path(__file__).resolve(),ROOT/'tools/patch_cyd_http_request_buffer.py',
           ROOT/'tests/native/cyd_http_request_buffer/test.c']
    sdk_files=['esp_http_client.c','include/esp_http_client.h','lib/http_header.c',
               'lib/http_utils.c','lib/include/http_header.h','lib/include/http_utils.h']
    report={'passed':False,'scope':__doc__,'physical_hardware':False,'target_abi':False,
            'sanitizers':['ASan','UBSan'],'source_sha256':{},'sdk_sha256':{},
            'patch_guards':{},'cases':{},'negative_controls':{}}
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    for path in files:
        relative=path.relative_to(ROOT);data=path.read_bytes();target=out/'sources/repository'/relative
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);report['source_sha256'][relative.as_posix()]=sha(data)
    for name in sdk_files:
        path=sdk/name;data=path.read_bytes();target=out/'sources/sdk'/name
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);report['sdk_sha256'][str(path)]=sha(data)
    sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location('frozen_patch',out/'sources/repository/tools/patch_cyd_http_request_buffer.py')
    patcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(patcher)
    raw=(out/'sources/sdk/esp_http_client.c').read_bytes();normalized=raw.replace(b'\r\n',b'\n')
    patched=patcher.patch(raw)
    for name,data in [('lf',normalized),('crlf',normalized.replace(b'\n',b'\r\n'))]:
        result=patcher.patch(data);newline=b'\r\n' if name=='crlf' else b'\n'
        encode=lambda text:text.encode().replace(b'\n',newline)
        assert result.count(encode(patcher.ENSURE_BUFFER))==1 and result.endswith(encode(patcher.RELEASE))
        restored=result[:-len(encode(patcher.RELEASE))].replace(encode(patcher.ENSURE_BUFFER),b'',1)
        assert restored==data,'unrelated SDK bytes changed'
        report['patch_guards'][name]={'accepted':True,'unrelated_source_bytes_identical':True,'generated_sha256':sha(result)}
    for name,data in [('unknown',raw+b'\n/* changed SDK */'),('already-patched',patched),
                      ('one-byte-drift',normalized.replace(b'Espressif',b'espressof',1)),
                      ('mixed-line-endings',normalized.replace(b'\n',b'\r\n',1))]:
        try:patcher.patch(data)
        except ValueError:report['patch_guards'][name]={'rejected':True}
        else:raise AssertionError('Unaudited source accepted: '+name)
    (out/'patched').mkdir();(out/'patched/esp_http_client.c').write_bytes(patched)
    report['original_sdk_sha256']=sha(raw);report['patched_sdk_sha256']=sha(patched)
    text=patched.decode().replace('\r\n','\n')
    names=['http_client_prepare_first_line','esp_http_client_request_send','esp_http_client_send_post_data',
           'esp_http_client_cached_buf_cleanup','esp_http_client_is_complete_data_received','esp_http_client_read']
    selected={name:function(text,name) for name in names}
    cleanup=function(text,'esp_http_client_cleanup');start=cleanup.index('    if (client->request) {')
    end=cleanup.index('    if (client->response)',start);cleanup=cleanup[start:end]
    report['sdk_function_sha256']={name:sha(body.encode()) for name,body in selected.items()}
    report['sdk_request_cleanup_span_sha256']=sha(cleanup.encode())
    # Assert even the selected unchanged body/RX/cleanup functions came from the
    # original source; only the request sender and new release API may differ.
    original=normalized.decode()
    assert all(body==function(original,name) for name,body in selected.items() if name!='esp_http_client_request_send')
    wrapper='static void cleanup_sdk_request(esp_http_client_handle_t client) {\n'+cleanup+'}\n'
    base='\n\n'.join(selected.values())+'\n\n'+wrapper+'\n'+patcher.RELEASE
    stubs=out/'stubs';stubs.mkdir()
    (stubs/'esp_err.h').write_text('#pragma once\ntypedef int esp_err_t;\n#define ESP_OK 0\n#define ESP_FAIL (-1)\n#define ESP_ERR_NO_MEM 0x101\n#define ESP_ERR_INVALID_ARG 0x102\n#define ESP_ERR_INVALID_STATE 0x103\n#define ESP_ERR_NOT_FOUND 0x105\n')
    (stubs/'esp_log.h').write_text('#pragma once\n#include <stdio.h>\n#include "esp_err.h"\n#define unlikely(x) (x)\n#define ESP_LOGD(tag,...) do { (void)(tag); if(0)printf(__VA_ARGS__); } while(0)\n#define ESP_LOGE ESP_LOGD\n#define ESP_LOGW ESP_LOGD\n#define ESP_LOG_LEVEL(level,tag,...) do { (void)(level);ESP_LOGD(tag,__VA_ARGS__); } while(0)\n')
    (stubs/'esp_check.h').write_text('#pragma once\n#include "esp_log.h"\n#define ESP_RETURN_ON_FALSE(x,code,tag,...) do { (void)(tag);if(!(x))return(code); } while(0)\n')
    code,log=execute(['gcc','--version']);assert code==0,log;(out/'compiler.log').write_bytes(log)
    report['compiler']=log.decode().splitlines()[0]
    def build(name,contents):
        directory=out/name;directory.mkdir();(directory/'sdk-functions.inc').write_text(contents,encoding='utf-8')
        binary=directory/'test'
        command=['gcc','-std=gnu11','-D_GNU_SOURCE','-O1','-g','-Wall','-Wextra','-Werror',
                 '-Wno-unused-function','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
                 '-I'+host(stubs),'-I'+host(out/'sources/sdk/lib/include'),'-I'+host(directory),
                 host(out/'sources/repository/tests/native/cyd_http_request_buffer/test.c'),
                 host(out/'sources/sdk/lib/http_header.c'),host(out/'sources/sdk/lib/http_utils.c'),'-o',host(binary)]
        (directory/'command.json').write_text(json.dumps(command,indent=2)+'\n')
        status,build_log=execute(command);(directory/'build.log').write_bytes(build_log);assert status==0,build_log.decode(errors='replace')
        return directory,binary
    def run(directory,binary,case,marker=None):
        code,log=execute(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary),case])
        (directory/(case+'.log')).write_bytes(log)
        assert not any(word in log for word in [b'AddressSanitizer',b'LeakSanitizer',b'runtime error:']),log
        if marker:
            assert code==80 and log.startswith(('SEMANTIC_FAILURE:'+marker+':').encode()),(case,code,log)
        else:assert code==0 and re.fullmatch(rb'PASS:'+case.encode()+rb' requested_tx_payload_bytes=\d+\n',log),(case,code,log)
        return code,log
    save()
    directory,binary=build('positive',base)
    for case in CASES:
        code,log=run(directory,binary,case);report['cases'][case]={'passed':True,'exit_status':code,'result':log.decode().strip()};print('PASS '+case,flush=True);save()
    mutations=[
        ('missing-reallocation',patcher.ENSURE_BUFFER,'','long-reuse','tx_buffer_live_before_request_write'),
        ('reduced-reuse-capacity','malloc(client->buffer_size_tx)','malloc(2048)','long-reuse','requested_capacity_restored'),
        ('release-before-response','client->state != HTTP_STATE_RES_ON_DATA_START','false','authorization','headers_sent_cannot_release_tx'),
        ('forget-null-after-release','    client->request->buffer->data = NULL;\n','', 'idempotent','release_nulls_pointer'),
        ('touch-borrowed-body','    free(client->request->buffer->data);\n','    client->post_data = NULL;\n    free(client->request->buffer->data);\n','borrowed-body','release_preserves_borrowed_post_data'),
        ('release-async','client->is_async || ','','async','nonfinal_get_rejected_without_free'),
        ('release-with-body','client->post_len != 0 || ','','body-pending','nonfinal_get_rejected_without_free'),
        ('stale-errno-on-oom','            errno = 0;\n','','oom','oom_keeps_reuse_retryable_without_wire')]
    for name,old,new,case,marker in mutations:
        # Mutations are confined to the two new production spans; cleanup has
        # an identical free line, so never mutate the concatenated source blindly.
        ensure,release=patcher.ENSURE_BUFFER,patcher.RELEASE
        if old in ensure:assert ensure.count(old)==1;ensure=ensure.replace(old,new,1)
        else:assert release.count(old)==1;release=release.replace(old,new,1)
        mutated_sender=selected['esp_http_client_request_send'].replace(patcher.ENSURE_BUFFER,ensure,1)
        body='\n\n'.join(mutated_sender if n=='esp_http_client_request_send' else s for n,s in selected.items())+'\n\n'+wrapper+'\n'+release
        directory,binary=build(name,body);code,log=run(directory,binary,case,marker)
        report['negative_controls'][name]={'detected':True,'exit_status':code,'case':case,'expected_marker':marker};print('CONTROL '+name,flush=True);save()
    report['source_unchanged_after']={name:sha((ROOT/name).read_bytes())==digest for name,digest in report['source_sha256'].items()}
    report['sdk_unchanged_after']={name:sha(Path(name).read_bytes())==digest for name,digest in report['sdk_sha256'].items()}
    assert all(report['source_unchanged_after'].values()) and all(report['sdk_unchanged_after'].values())
    report['generated_sha256']={p.relative_to(out).as_posix():sha(p.read_bytes()) for p in out.rglob('*') if p.is_file() and p.name not in ['test','report.json'] and 'sources' not in p.relative_to(out).parts}
    report['requested_buffer_note']='Current CYD radio config requests4096TX payload bytes; fixture also tests8192capacity. Allocator usable bytes, overhead, fragmentation and physical recovered heap are not measured or claimed.'
    report['passed']=True;save();print('PASS SDK6.0.2 TX release prototype:17cases,8exactcontrols; production integration remains open',flush=True)


if __name__=='__main__':main()
