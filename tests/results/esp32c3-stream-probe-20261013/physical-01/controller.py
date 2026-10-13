"""Physical AUTO detection without MIME; app-only OTA and verified restoration."""
import argparse
import json
from pathlib import Path
import time

from common import Board, Failure, exception_details, fixtures, matches, require, sha
from ota import image_info, multipart, snapshot, upload, verify_snapshot, wait_image
from production_health import read_health
from audio_test_server.server import Server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', required=True)
    parser.add_argument('--host', required=True)
    parser.add_argument('--port', type=int, default=8773)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--restore', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    board = Board(args.board)
    original = board.info()
    require(not board.status()['audio'], 'Board must initially be stopped')
    require(original['app_elf_sha256'] == image_info(args.restore.read_bytes())['app_elf_sha256'],
            'Restore app does not match active firmware')
    private = snapshot(board)  # Never serialize credentials, stations or their hashes.
    report = dict(controller_sha256=sha(Path(__file__).read_bytes()), initial=original,
                  candidate=image_info(args.candidate.read_bytes()), cases=[])

    def save():
        (args.output/'results.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')

    def install(path):
        current = board.info()
        image = path.read_bytes()
        expected = image_info(image)
        if current['app_elf_sha256'] == expected['app_elf_sha256']:
            return
        code, body = upload(board.origin, multipart(image))
        require(code == 200 and body == b'OK', 'OTA failed')
        wait_image(board, expected['app_elf_sha256'],
                   'app1' if current['partition']=='app0' else 'app0', timeout=60)
        board.stop()
        time.sleep(2)

    available = fixtures()
    names = ('mp3-320','flac-level8','vorbis-q10','opus-510','lc-48000-stereo',
             'he-48000-stereo','hev2-44100-stereo')
    specs = {name: dict(available[name], mime=None) for name in names}
    for name in ('he-48000-stereo','hev2-44100-stereo'):
        spec = specs[name]
        tag = b'ID3\x04\x00\x00\x00\x00\x00\x20' + b'\xff\xfb\x90\x00'*8
        data = tag+spec['data']
        specs[name+'-id3'] = dict(spec, data=data, sha256=sha(data))
    negative = {'unknown': b'\x00'*5000, 'partial': b'\xff',
                'truncated-id3': b'ID3\x04\x00\x00\x00\x00\x00\x20'}
    for name, data in negative.items():
        specs[name] = dict(data=data, seconds=.1, codec='aac', mime=None, sha256=sha(data))
    report['fixtures'] = {name:dict(bytes=len(spec['data']), sha256=sha(spec['data']),
                                  mime=None) for name,spec in specs.items()}
    save()
    try:
        install(args.candidate)
        report['installed'] = board.info()
        with Server(args.host,args.port,specs,pacing_ratio=1.0,
                    delivery_pauses=[(i,.02) for i in range(1,10)]) as server:
            for name, spec in specs.items():
                row = dict(name=name, before=read_health(board), observations=[])
                report['cases'].append(row)
                started = time.monotonic()
                try:
                    board.play(f'http://{args.host}:{args.port}/file/{name}')
                    if name in negative:
                        deadline = started+12
                        while time.monotonic()<deadline:
                            state=board.status(); row['observations'].append(state)
                            if not state['audio'] and state['format']=='unknown audio format': break
                            time.sleep(.2)
                        require(not state['audio'] and state['format']=='unknown audio format',
                                'Unknown input was not rejected explicitly')
                    else:
                        deadline=started+12
                        stable=0
                        while time.monotonic()<deadline:
                            state=board.status(); row['observations'].append(state)
                            stable=stable+1 if matches(state,spec) else 0
                            if stable==3: break
                            time.sleep(.3)
                        require(stable==3, 'Expected format did not start')
                        row['active_before']=read_health(board)
                        time.sleep(3)
                        row['active_after']=read_health(board)
                        require(matches(board.status(),spec), 'Playback stopped inside active window')
                        require(row['active_after']['output']==row['active_before']['output'],
                                'Output counters changed in active window')
                        deadline=started+spec['seconds']+12
                        while time.monotonic()<deadline:
                            state=board.status()
                            if not state['audio']: break
                            time.sleep(.3)
                        row['eof']=state
                        require(not state['audio'] and state['format']=='stream ended', 'Wrong EOF status')
                    row['after']=read_health(board)
                    require(row['before']['boot_id']==row['after']['boot_id'], 'Unexpected restart')
                    for key in ('allocation_failures','task_watchdog_events'):
                        require(row['before'][key]==row['after'][key], 'Runtime allocation/watchdog failure')
                    row['result']='PASS'
                except Exception as error:
                    row['result']='FAIL'; row['errors']=exception_details(error)
                    if isinstance(error,Failure): row['check']=str(error)
                finally:
                    row['seconds']=time.monotonic()-started
                    save(); print(name,row['result'],flush=True)
                    board.stop(); time.sleep(.5)
            report['server']=server.events
            save()
    finally:
        try:
            board.stop()
        finally:
            install(args.restore)
        board.stop()
        report['restoration']=dict(image=board.info(),status=board.status(),**verify_snapshot(board,private))
        save(); print('RESTORED',flush=True)


if __name__=='__main__':
    main()
