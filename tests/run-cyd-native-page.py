"""Run the actual compact CYD page script, including OTA, Wi-Fi and time edits.

Browser DOM/fetch/WebSocket boundaries are controlled Node seams. Semantic
mutants run only against frozen alternate page files; production is unchanged.
These tests do not replace browser layout or physical-device qualification.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
    page=ROOT/'idf/esp32-cyd2usb-native/main/web_pages.cpp';test=ROOT/'tests/cyd-native-page.test.js'
    files=[Path(__file__).resolve(),page,test];hashes={f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    for f in files:
        target=out/'sources'/f.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(f.read_bytes())
    node=shutil.which('node');assert node,'Node is required'
    def execute(source,pattern=None):
        command=[node,'--test','--test-reporter=tap']
        if pattern:command+=['--test-name-pattern','^'+re.escape(pattern)+'$']
        command.append(str(test));environment=os.environ.copy();environment['CYD_NATIVE_PAGE_SOURCE']=str(source)
        result=subprocess.run(command,cwd=ROOT,env=environment,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
        return result.returncode,result.stdout,command
    code,log,command=execute(page);(out/'positive.log').write_bytes(log)
    if code:raise RuntimeError(log.decode(errors='replace'))
    count=int(re.search(rb'^# tests (\d+)',log,re.M).group(1))
    report={'passed':False,'scope':__doc__,'physical_hardware':False,'source_sha256':hashes,'command':command,'positive_groups':count,'negative_controls':{}}
    source=page.read_text(encoding='utf-8')
    keep='Wi-Fi first-row editor preserves all five IDs and omits untouched SSIDs and passwords'
    historical='unchanged non-UTF8 legacy SSID presentation is omitted even when replacement text exceeds the byte cap'
    blank='Wi-Fi blank password keeps existing secret and persistence failure keeps the new input'
    opened='open network requires an explicit action and sends set with an empty password'
    time_query='time saves exact four query fields without a body and announces persistence without claiming synchronization'
    late='periodic polling is sequential and an old time GET cannot overwrite a completed edit'
    capabilities='legacy upload capability does not enable native Wi-Fi editing and unconfirmed success never claims restart'
    mutations={
        'drop_other_profiles':("wifiMetadata.profiles.map(row => ({id:row.id,password_action:'keep'}))","wifiMetadata.profiles.slice(0,1).map(row => ({id:row.id,password_action:'keep'}))",keep),
        'rewrite_legacy_ssid':('if (changed) first.ssid = ssid;','first.ssid = ssid;',historical),
        'blank_password_clears':('else if (password) { first.password_action','else if (password || profiles.length) { first.password_action',blank),
        'implicit_open':("else if (!profiles.length) throw new Error('Для новой сети укажите пароль или выберите открытую сеть');","else if (!profiles.length) first.password = '';",opened),
        'wrong_offset_sign':("utc_offset_minutes:el('time-offset').value","utc_offset_minutes:String(-Number(el('time-offset').value))",time_query),
        'stale_time_response':('if (epoch === timeRequestEpoch) renderTime(state);','if (true) renderTime(state);',late),
        'overlapping_polls':(' || pollBusy) return;',') return;',late),
        'legacy_capability_fallback':("const wifiSupported = () => capabilities.nativeWiFiApi === '/api/native/wifi' &&","const wifiSupported = () => (capabilities.nativeWiFiApi === '/api/native/wifi' || capabilities.wifi_upload === true) &&",capabilities),
    }
    for name,(old,new,case) in mutations.items():
        assert source.count(old)==1,name;alternate=out/(name+'.cpp');alternate.write_text(source.replace(old,new),encoding='utf-8')
        code,log,command=execute(alternate,case);(out/(name+'.log')).write_bytes(log)
        assert code and b'not ok' in log and b"code: 'ERR_ASSERTION'" in log and case.encode() in log,(name,log)
        assert b'SyntaxError' not in log and b'ReferenceError' not in log and b'TypeError' not in log,(name,log)
        report['negative_controls'][name]={'case':case,'status':code,'expected_failure':'ERR_ASSERTION','command':command,'rejected':True}
    report['source_files_still_match_snapshot']=all(hashlib.sha256(f.read_bytes()).hexdigest()==hashes[f.relative_to(ROOT).as_posix()] for f in files)
    assert report['source_files_still_match_snapshot'];report['passed']=True
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',count,'actual page groups +',len(mutations),'exact semantic mutants')
if __name__=='__main__':main()
