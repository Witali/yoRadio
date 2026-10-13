"""Bounded AUTO-prefix wait, Stop and replacement with station watchdog off.

App-only OTA; original private settings stay in RAM and are restored in finally.
The fault server uses paced bytes, not a disconnected or completed HTTP body.
"""
import argparse
import json
from pathlib import Path
import time

from common import Board, Failure, check_recovery_heap, exception_details, fixtures, matches, require, sha
from connection_retry import set_watchdog
from ota import image_info, multipart, snapshot, upload, verify_snapshot, wait_image
from production_health import read_health
from audio_test_server.server import Server


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board',required=True)
    p.add_argument('--host',required=True)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--restore',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    b=Board(a.board); original=b.info()
    require(not b.status()['audio'],'Board must initially be stopped')
    require(original['app_elf_sha256']==image_info(a.restore.read_bytes())['app_elf_sha256'],
            'Restore image does not match original')
    private=snapshot(b); watchdog=private['settings']['getsystem']['watchdog']
    report=dict(controller_sha256=sha(Path(__file__).read_bytes()),initial=original,
                candidate=image_info(a.candidate.read_bytes()),cases=[])
    def save():
        (a.output/'results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def install(path):
        current=b.info(); image=path.read_bytes(); expected=image_info(image)
        if current['app_elf_sha256']==expected['app_elf_sha256']: return
        code,body=upload(b.origin,multipart(image))
        require(code==200 and body==b'OK','OTA failed')
        wait_image(b,expected['app_elf_sha256'],'app1' if current['partition']=='app0' else 'app0',timeout=60)
        b.stop(); time.sleep(2)
    def idle():
        b.stop(); time.sleep(2)
        rows=[]
        for _ in range(3): rows.append(read_health(b)); time.sleep(.3)
        return rows
    spec=dict(fixtures()['he-48000-stereo'],mime=None)
    require(spec['data'].startswith(b'\xff'), 'Expected ADTS fixture')
    save()
    try:
        install(a.candidate)
        set_watchdog(b,False)
        require(b.settings()['getsystem']['watchdog']==0,'Watchdog is still enabled')
        report['watchdog_disabled_verified']=True
        report['idle_before']=idle()
        with Server(a.host,8774,{'prefix':spec},delivery_stats=True,
                    delivery_pauses=[(i,2.0) for i in range(1,10)],pacing_ratio=1.0) as slow, \
             Server(a.host,8773,{'audio':spec},pacing_ratio=1.0) as normal:
            for name in ('deadline-without-watchdog','stop-during-prefix','replace-during-prefix'):
                row=dict(name=name,before=read_health(b),observations=[])
                report['cases'].append(row); previous=len(slow.events)
                try:
                    b.play(f'http://{a.host}:8774/file/prefix')
                    limit=time.perf_counter()+5
                    while len(slow.events)==previous and time.perf_counter()<limit: time.sleep(.05)
                    require(len(slow.events)>previous,'Fault request did not reach server')
                    event=slow.events[previous]; start=event['delivery']['started_at']
                    time.sleep(.5)
                    require(event['sent']<7,'Complete ADTS header arrived before control action')
                    require(not b.status().get('pcm_sample_rate'),'Unexpected decoded PCM before header')
                    if name=='deadline-without-watchdog':
                        while time.perf_counter()-start<14:
                            state=b.status(); row['observations'].append(state)
                            if not state['audio'] and state['format']=='unknown audio format': break
                            time.sleep(.2)
                        row['deadline_seconds']=time.perf_counter()-start
                        require(not state['audio'] and state['format']=='unknown audio format',
                                'Unresolved prefix did not time out with watchdog disabled')
                        require(9.5<=row['deadline_seconds']<=13,'Unexpected probe deadline')
                        require(event['sent']<7 and not event['complete'],
                                'Test ended by header completion or HTTP EOF instead of timeout')
                    elif name=='stop-during-prefix':
                        action=time.perf_counter(); b.stop()
                        for _ in range(6):
                            state=b.status(); row['observations'].append(state)
                            require(not state['audio'] and state['format']=='stopped','Stale prefix revived playback')
                            if 'stop_seconds' not in row: row['stop_seconds']=time.perf_counter()-action
                            time.sleep(.25)
                        require(row['stop_seconds']<2,'Stop response was delayed')
                    else:
                        action=time.perf_counter(); b.play(f'http://{a.host}:8773/file/audio')
                        stable=0
                        while time.perf_counter()-action<12:
                            state=b.status(); row['observations'].append(state)
                            stable=stable+1 if matches(state,spec) else 0
                            if stable>=3: break
                            time.sleep(.25)
                        require(stable>=3,'Replacement stream did not start')
                        row['replacement_seconds']=time.perf_counter()-action
                        active=read_health(b); time.sleep(3)
                        require(matches(b.status(),spec),'Old prefix changed replacement playback')
                        later=read_health(b)
                        row['active_before']=active; row['active_after']=later
                        require(active['output']==later['output'],'Output counters changed during replacement')
                    row['after']=read_health(b)
                    require(row['after']['boot_id']==row['before']['boot_id'],'Unexpected restart')
                    for key in ('allocation_failures','task_watchdog_events'):
                        require(row['after'][key]==row['before'][key],'New allocation/watchdog failure')
                    row['result']='PASS'
                except Exception as error:
                    row['result']='FAIL';row['errors']=exception_details(error)
                    if isinstance(error,Failure):row['check']=str(error)
                finally:
                    b.stop(); save(); print(name,row['result'],flush=True)
                    time.sleep(.5)
            report['idle_after']=idle()
            try:
                check_recovery_heap(report['idle_before'],report['idle_after'])
                report['heap_recovery']='PASS'
            except Failure as error:
                report['heap_recovery']='FAIL';report['heap_recovery_check']=str(error)
            report['fault_server']=slow.events;report['normal_server']=normal.events
            save()
    finally:
        # Attempt firmware restoration even if restoring a setting fails.
        try:
            b.stop();set_watchdog(b,bool(watchdog))
        finally:
            install(a.restore)
        b.stop()
        report['restoration']=dict(image=b.info(),status=b.status(),**verify_snapshot(b,private))
        save();print('RESTORED',flush=True)
    require(len(report['cases']) == 3 and
            all(row['result'] == 'PASS' for row in report['cases']) and
            report.get('heap_recovery') == 'PASS',
            'Prefix control checks failed; see saved results')


if __name__=='__main__':main()
