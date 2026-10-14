"""Stop/replacement during an incomplete frame after a real codec-family change.

Uses app-only OTA with verified restoration. No private settings are serialized.
Requires ffprobe to place host-side pauses inside a known packet independently
of the firmware parser. Host delivery does not prove a precise firmware PC.
"""
import argparse
import json
from pathlib import Path
import subprocess
import time

from common import Board, Failure, check_recovery_heap, exception_details, fixtures, matches, require, sha
from ota import image_info, multipart, snapshot, upload, verify_snapshot, wait_image
from production_health import read_health
from audio_test_server.server import Server


def pause_position(first, second):
    result=subprocess.run(['ffprobe','-v','error','-show_packets','-show_entries',
        'packet=pos,size','-of','json','-i','pipe:0'],input=second['data'],capture_output=True,check=True)
    packet=json.loads(result.stdout)['packets'][3]
    position,size=int(packet['pos']),int(packet['size'])
    require(size>64,'Fourth reference packet is too small for the pause schedule')
    return len(first['data'])+position+32, len(first['data'])+position+size


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('board','host'):p.add_argument('--'+name,required=True)
    for name in ('candidate','restore','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--cycles',type=int,default=2,choices=range(1,6))
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    b=Board(a.board);original=b.info()
    require(not b.status()['audio'],'Board must initially be stopped')
    require(original['app_elf_sha256']==image_info(a.restore.read_bytes())['app_elf_sha256'],
            'Restore image does not match active firmware')
    require('CONFIG_YORADIO_FRAME_ROUTER=y' in a.candidate.with_name('sdkconfig').read_text(),
            'Candidate must enable the frame router')
    private=snapshot(b);available=fixtures()
    directions=[('mp3-320','he-48000-stereo'),('he-48000-stereo','mp3-320')]
    specs={};positions={}
    for first,second in directions:
        before,after=available[first],available[second];name=first+'-to-'+second
        data=before['data']+after['data']
        specs[name]=dict(data=data,seconds=before['seconds']+after['seconds'],
                         segments=[before,after],codec='auto',mime=None,sha256=sha(data))
        positions[name]=pause_position(before,after)
    report=dict(controller_sha256=sha(Path(__file__).read_bytes()),initial=original,
        candidate=image_info(a.candidate.read_bytes()),cycles=a.cycles,cases=[],
        ffprobe=subprocess.check_output(['ffprobe','-version'],text=True).splitlines()[0],
        fixtures={name:dict(bytes=len(s['data']),sha256=s['sha256'],
                            pause_at=positions[name][0],packet_end=positions[name][1]) for name,s in specs.items()})
    def save():
        (a.output/'results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def install(path):
        current=b.info();image=path.read_bytes();expected=image_info(image)
        if current['app_elf_sha256']==expected['app_elf_sha256']:return
        code,body=upload(b.origin,multipart(image));require(code==200 and body==b'OK','OTA failed')
        wait_image(b,expected['app_elf_sha256'],'app1' if current['partition']=='app0' else 'app0',timeout=60)
        b.stop();time.sleep(2)
    def idle():
        b.stop();time.sleep(2);rows=[]
        for _ in range(3):rows.append(read_health(b));time.sleep(.3)
        return rows
    save()
    try:
        install(a.candidate);report['idle_before']=idle()
        with Server(a.host,8773,available,pacing_ratio=1.0) as normal:
            for cycle in range(a.cycles):
                for first,second in directions:
                    name=first+'-to-'+second;pause,end=positions[name]
                    for action in ('stop','replace'):
                        row=dict(name=name,action=action,cycle=cycle,before=read_health(b),observations=[])
                        report['cases'].append(row)
                        try:
                            with Server(a.host,8774,{name:specs[name]},pacing_ratio=1.0,
                                        delivery_pauses=[(pause+i,2.0) for i in range(5)]) as slow:
                                b.play(f'http://{a.host}:8774/file/{name}')
                                deadline=time.perf_counter()+available[first]['seconds']+15
                                old_seen=False;stable=0
                                while time.perf_counter()<deadline:
                                    state=b.status();row['observations'].append(state)
                                    old_seen=old_seen or matches(state,available[first])
                                    event=slow.events[0] if slow.events else {}
                                    in_pause=bool(event.get('pauses')) and pause<=event.get('sent',0)<end
                                    stable=stable+1 if in_pause and matches(state,available[second]) else 0
                                    if old_seen and stable>=2:break
                                    time.sleep(.2)
                                require(old_seen and stable>=2,'Did not observe both decoders before partial-frame action')
                                require(not event['complete'] and pause<=event['sent']<end,'Control action missed partial packet')
                                row['action_sent_bytes']=event['sent'];started=time.perf_counter()
                                if action=='stop':
                                    b.stop()
                                    for i in range(6):
                                        state=b.status();row['observations'].append(state)
                                        require(not state['audio'] and state['format']=='stopped','Old stream revived after Stop')
                                        if i==0:row['response_seconds']=time.perf_counter()-started
                                        time.sleep(.25)
                                    require(row['response_seconds']<2,'Stop response delayed')
                                else:
                                    target=available['hev2-44100-stereo']
                                    b.play(f'http://{a.host}:8773/file/hev2-44100-stereo')
                                    stable=0
                                    while time.perf_counter()-started<12:
                                        state=b.status();row['observations'].append(state)
                                        stable=stable+1 if matches(state,target) else 0
                                        if stable>=3:break
                                        time.sleep(.25)
                                    require(stable>=3,'Replacement did not start')
                                    row['response_seconds']=time.perf_counter()-started
                                    row['active_before']=read_health(b);time.sleep(2)
                                    require(matches(b.status(),target),'Old stream changed replacement format')
                                    row['active_after']=read_health(b)
                                    require(row['active_before']['output']==row['active_after']['output'],
                                            'Output counters changed in replacement active window')
                            row['server']=slow.events
                            row['idle_after']=idle();row['after']=row['idle_after'][-1]
                            require(row['before']['boot_id']==row['after']['boot_id'],'Unexpected restart')
                            for key in ('allocation_failures','task_watchdog_events'):
                                require(row['before'][key]==row['after'][key],'New allocation/watchdog failure')
                            check_recovery_heap(report['idle_before'],row['idle_after'])
                            row['result']='PASS'
                        except Exception as error:
                            row['result']='FAIL';row['errors']=exception_details(error)
                            if isinstance(error,Failure):row['check']=str(error)
                        finally:
                            b.stop();save();print(cycle,name,action,row['result'],flush=True)
            report['idle_after']=idle();check_recovery_heap(report['idle_before'],report['idle_after'])
            report['heap_recovery']='PASS';report['normal_server']=normal.events;save()
    finally:
        try:b.stop()
        finally:install(a.restore)
        b.stop();report['restoration']=dict(image=b.info(),status=b.status(),**verify_snapshot(b,private))
        save();print('RESTORED',flush=True)
    require(len(report['cases'])==a.cycles*4 and all(r['result']=='PASS' for r in report['cases'])
            and report.get('heap_recovery')=='PASS','Frame-router controls failed; see results')


if __name__=='__main__':main()
