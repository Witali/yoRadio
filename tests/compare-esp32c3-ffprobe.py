"""Record parser differences on controlled files; known gaps are not passes.

This is an audit, not a production qualification gate. No firmware mutation.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.build/ffmpeg-parser-audit'


def execute(args):
    return subprocess.run(args,capture_output=True,text=True)


def native(path):
    path=str(path.resolve()).replace('\\','/')
    return '/mnt/'+path[0].lower()+path[2:] if os.name=='nt' else path


def linux(args):
    result=execute(['wsl.exe','--exec',*args] if os.name=='nt' else args)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    return result.stdout


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    binary=OUT/'compare'
    main=ROOT/'idf/esp32c3-oled-native/main'
    source=ROOT/'tests/native/esp32c3_parser_audit.c'
    linux(['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror',
        '-fsanitize=address,undefined','-fno-omit-frame-pointer','-I',native(main),
        native(source),'-o',native(binary)])
    def fixture(folder,name):
        manifest=json.loads((folder/'manifest.json').read_text())
        entry=(manifest['files'][name] if 'files' in manifest else
               next(row for row in manifest['fixtures'] if row['file']==name))
        data=(folder/name).read_bytes()
        assert hashlib.sha256(data).hexdigest()==entry['sha256']
        return data
    aac=fixture(ROOT/'tests/fixtures/aac_stream_format','he-48000-stereo.aac')
    mp3=fixture(ROOT/'tests/fixtures/esp32c3_calibration','mp3-320.mp3')
    while mp3[:3]==b'ID3':
        skip=10+(mp3[6]<<21)+(mp3[7]<<14)+(mp3[8]<<7)+mp3[9]
        if mp3[3]==4 and mp3[5]&16:skip+=10
        mp3=mp3[skip:]
    first_aac=((aac[3]&3)<<11)|(aac[4]<<3)|(aac[5]>>5)
    tag=b'ID3\x04\x00\x00\x00\x00\x00\x00'
    # Preserve payload/physical frame lengths, replace only the bitrate index
    # of this known 320 kb/s MPEG-1/48 kHz fixture. This is a header-routing
    # experiment, not certification of every possible free-format MP3 file.
    free_format=bytearray(mp3)
    for offset in range(0,len(free_format),960):
        assert free_format[offset:offset+3]==b'\xff\xfb\xe4'
        free_format[offset+2]&=15
    cases={
        'clean-aac':aac,
        'clean-mp3':mp3,
        'false-mp3-before-aac':b'\xff\xfb\x90\x00'+bytes(28)+aac,
        'false-aac-before-mp3':b'\xff\xf1\x4c\x80\x01\x9f\xfc'+bytes(25)+mp3,
        'aac-interframe-id3':aac[:first_aac]+tag+aac[first_aac:],
        'aac-interframe-junk':aac[:first_aac]+bytes(17)+aac[first_aac:],
        'mp3-id3v1-tail':mp3+b'TAG'+bytes(125),
        'aac-truncated-payload':aac[:-3],
        'mp3-free-format-headers':bytes(free_format),
    }
    report=dict(ffprobe=execute(['ffprobe','-version']).stdout.splitlines()[0],cases=[],
        scope='Current C headers versus complete ffprobe demux/parser pipeline; not equivalent APIs',
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (source,main/'stream_probe.h',main/'stream_frames.h',main/'stream_tags.h')})
    for name,data in cases.items():
        path=OUT/name;path.write_bytes(data) # No filename-extension format hint.
        ours=json.loads(linux([native(binary),native(path)]))
        result=execute(['ffprobe','-v','error','-show_packets','-show_streams',
            '-show_entries','packet=pos,size:stream=codec_name,profile,sample_rate,channels',
            '-of','json',str(path)])
        reference=json.loads(result.stdout or '{}')
        row=dict(name=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
                 ours=ours,ffprobe=dict(exit_code=result.returncode,**reference,stderr=result.stderr))
        if name=='mp3-free-format-headers':
            forced=execute(['ffprobe','-v','error','-f','mp3','-show_streams',
                            '-of','json',str(path)])
            row['forced_mp3']=dict(exit_code=forced.returncode,
                **json.loads(forced.stdout or '{}'),stderr=forced.stderr)
        report['cases'].append(row)
        print(name,'ours',ours,'ffprobe',reference.get('streams',[]),
              'packets',len(reference.get('packets',[])),flush=True)
    (OUT/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
