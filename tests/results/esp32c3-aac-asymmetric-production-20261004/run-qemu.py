import json,subprocess,sys
from pathlib import Path
root=Path.cwd()
for name in sys.argv[1:]:
    output=root/'.build/aac-asymmetric-production/qemu'/name
    output.mkdir(parents=True,exist_ok=True)
    cmd=[sys.executable,'-X','utf8','tools/codec_benchmark/run_aac_asymmetric_owner.py',
        '--build','idf/esp32c3-oled-native/build-qemu-aac-asymmetric-production',
        '--production-path','--dependency-root','C:/Work/yoRadio/.idf','--output',str(output),
        '--qemu','/mnt/c/Work/yoRadio/.worktree/esp32c3-stream-format/.build/qemu-cache-host/qemu-system-riscv32',
        '--bios','/mnt/c/Work/QEMU-ESP32/share/qemu','--wsl',
        '--baseline',f'tests/results/esp32c3-aac-low-production-20261003/qemu/{name}/result.json',
        '--previous-wav','.build/aac-low-production/qemu/synthetic/audio.wav']
    if name!='synthetic':
        cmd+=['--input',str(root.parent/'esp32c3-stream-format/.build/aac-bfp16-real-20260930/inputs'/f'{name}.aac'),
              '--ffprobe','C:/Users/rudol/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1.1-full_build/bin/ffprobe.exe']
    with (output/'runner.log').open('wb') as log:result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:
        print(name,'FAIL',flush=True)
        print((output/'runner.log').read_text(encoding='utf-8',errors='replace')[-2000:])
        raise SystemExit(result.returncode)
    data=json.loads((output/'result.json').read_text())
    print(name,'PASS',data['memory'],data['stack'],'PCM difference',data['pcm_vs_previous']['different'],flush=True)
