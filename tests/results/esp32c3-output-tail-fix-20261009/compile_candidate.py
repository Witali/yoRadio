"""Compile isolated changed C with recorded ESP-IDF commands; no linking/flashing."""
import ctypes
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/codec_benchmark/run_output_dma_host.py').is_file())
PROJECT=REPO/'idf/esp32c3-oled-native'
OUT=ROOT/'candidate-target-objects2';OUT.mkdir(exist_ok=False)
parser=ctypes.windll.shell32.CommandLineToArgvW
parser.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_int)]
parser.restype=ctypes.POINTER(ctypes.c_wchar_p)
def split(command):
    count=ctypes.c_int()
    argv=parser(command,ctypes.byref(count))
    assert argv
    try: return [argv[i] for i in range(count.value)]
    finally: ctypes.windll.kernel32.LocalFree(argv)

staged='build-idf-6.1-r9a97-input-prefill500'
qemu='build-idf-6.1-head9a97-qemu'
cases=[('staged-output',staged,'native_audio_output.c',()),
       ('staged-task',staged,'audio_service.c',()),
       ('direct-task',staged,'audio_service.c',('CONFIG_YORADIO_DIRECT_DMA_PCM=1',)),
       ('direct-profile-task',staged,'audio_service.c',('CONFIG_YORADIO_DIRECT_DMA_PCM=1','CONFIG_YORADIO_PIPELINE_PROFILE=1')),
       ('qemu-output',qemu,'native_audio_output_qemu.c',()),
       ('qemu-task',qemu,'audio_service.c',())]
result=dict(scope='ESP32-C3 compiler object checks, no final linking or hardware qualification',cases=[])
for label,build,name,defines in cases:
    database=PROJECT/build/'compile_commands.json'
    entries=json.loads(database.read_text())
    entry=next(e for e in entries if Path(e['file']).name==name)
    command=split(entry['command'])
    assert not any(x in command for x in ('-MD','-MMD','-MF','-MT','-MQ'))
    candidate=ROOT/'candidate/idf/esp32c3-oled-native/main'/name
    assert command.count('-c')==1 and command.count('-o')==1
    command[command.index('-c')+1]=str(candidate)
    command[command.index('-o')+1]=str(OUT/(label+'.obj'))
    command[1:1]=['-D'+d for d in defines]
    run=subprocess.run(command,cwd=OUT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (OUT/(label+'.log')).write_bytes(run.stdout)
    record=dict(name=label,source=str(candidate.relative_to(REPO)),
        source_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest(),
        configuration_sha256=hashlib.sha256((PROJECT/build/'sdkconfig').read_bytes()).hexdigest(),
        base_compile_command=entry,applied_command=command,result='PASS' if run.returncode==0 else 'FAIL')
    result['cases'].append(record)
    (OUT/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(label,record['result'],flush=True)
    if run.returncode: print(run.stdout.decode(errors='replace'));raise SystemExit(run.returncode)
