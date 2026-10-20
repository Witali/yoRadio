"""Qualify actual donor runtime time snapshots and NVS publication ordering."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
    main=ROOT/'idf/esp32c3-oled-native/main'
    files=[Path(__file__).resolve(),main/'runtime_settings.c',main/'runtime_settings.h',
           ROOT/'tests/native/c3_time_settings_platform.h',ROOT/'tests/native/c3_time_settings_test.c',
           ROOT/'tools/codec_benchmark/run_output_dma_host.py']
    hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    for p in files:
        dest=out/'sources'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
    (out/'freertos').mkdir()
    for name in ('esp_err.h','esp_check.h','esp_log.h','nvs.h','freertos/FreeRTOS.h','freertos/semphr.h'):
        (out/name).write_text('#pragma once\n')
    source=re.sub(r'^#include[^\n]*\n','',(main/'runtime_settings.c').read_text(),flags=re.M)
    unit=out/'runtime.inc';binary=out/'test'
    command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-variable',
             '-pthread','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
             '-I'+host(out),'-I'+host(main),'-I'+host(ROOT/'tests/native'),
             host(ROOT/'tests/native/c3_time_settings_test.c'),'-o',host(binary)]
    def build(body,tag):
        unit.write_text(body)
        try:log=run(command)
        except subprocess.CalledProcessError as error:
            (out/(tag+'-build.log')).write_bytes(error.output);print(error.output.decode(errors='replace'));raise
        (out/(tag+'-build.log')).write_bytes(log)
    build(source,'positive')
    env=['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1']
    try:log=run(env+[host(binary),'all'])+run(env+[host(binary),'invalid_load'])
    except subprocess.CalledProcessError as error:
        (out/'failure.log').write_bytes(error.output);print(error.output.decode(errors='replace'));raise
    (out/'test.log').write_bytes(log);print(log.decode(),end='')
    report=dict(passed=False,scope=__doc__,physical_flash=False,positive=log.decode().strip(),
                negative_controls={},source_sha256=hashes)
    def save(): (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    begin=source.index('esp_err_t runtime_settings_get_time_snapshot(')
    end=source.index('\nstatic esp_err_t save_u8(',begin)
    snapshot=source[begin:end]
    acquire='    ESP_RETURN_ON_ERROR(lock_time_settings(timeout_ms), TAG,\n                        "Time settings snapshot lock");\n'
    assert snapshot.count(acquire)==1
    no_lock=snapshot.replace(acquire,'    if (!s_string_lock) return ESP_ERR_INVALID_STATE;\n    (void)timeout_ms;\n').replace('    xSemaphoreGive(s_string_lock);\n','')
    server_begin=source.index('static esp_err_t set_time_server(')
    server_end=source.index('\nesp_err_t runtime_settings_set_sntp1(',server_begin)
    server=source[server_begin:server_end]
    server_acquire='    ESP_RETURN_ON_ERROR(lock_time_settings(TIME_SETTINGS_LOCK_TIMEOUT_MS), TAG,\n                        "SNTP settings lock");\n'
    assert server.count(server_acquire)==1
    unlocked_server=server.replace(server_acquire,'').replace('    xSemaphoreGive(s_string_lock);\n','')
    publish='if (result == ESP_OK) atomic_store(&s_timezone_hour, hour);'
    assert source.count(publish)==1
    mutants={'unlocked_snapshot':(source[:begin]+no_lock+source[end:],'snapshot_timeout','runtime_settings_get_time_snapshot(&out,5)==ESP_ERR_TIMEOUT'),
             'persist_without_lock':(source[:server_begin]+unlocked_server+source[server_end:],'setter_timeout','nvs_opens==before'),
             'publish_failed_commit':(source.replace(publish,'atomic_store(&s_timezone_hour, hour);'),'failures','equal(old,&now)')}
    for name,(body,case,assertion) in mutants.items():
        build(body,name)
        try:run(['env','ASAN_OPTIONS=detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary),case])
        except subprocess.CalledProcessError as error:
            (out/(name+'.log')).write_bytes(error.output)
            if b'Assertion `' not in error.output or assertion.encode() not in error.output or b'ERROR: AddressSanitizer' in error.output or b'runtime error:' in error.output:
                save();raise AssertionError('unexpected mutant failure '+name) from error
            report['negative_controls'][name]={'case':case,'expected_assertion':assertion,'rejected':True}
        else:save();raise AssertionError('mutant survived '+name)
    build(source,'restored')
    report['source_files_still_match_snapshot']=all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[p.relative_to(ROOT).as_posix()] for p in files)
    assert report['source_files_still_match_snapshot']
    report['passed']=True;save()

if __name__=='__main__':main()
