import json, subprocess, sys
from pathlib import Path
root = Path.cwd()
base = root/'.build/aac-network-memory'
ffprobe = 'C:/Users/rudol/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1.1-full_build/bin/ffprobe.exe'
results = []
for name, transport, case in [('candidate-http32', 'http', 'groovesalad-32-aac'), ('candidate-https64', 'https', 'groovesalad-64-aac')]:
    print('BEGIN', name, flush=True)
    cmd = [sys.executable, '-X', 'utf8', 'tools/esp32c3_tests/public_streams.py', '--board', 'http://192.168.100.4', '--serial-port', 'COM9', '--firmware', 'firmware/development/esp32c3-aac-network-memory/app.bin', '--case', case, '--seconds', '300', '--interval', '0.1', '--transport', transport, '--ffprobe', ffprobe, '--output', str(base/name)]
    code = subprocess.run(cmd).returncode
    results.append(dict(suite=name, exit_code=code))
    (base/'public-exits.json').write_text(json.dumps(results, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('END', name, 'exit', code, flush=True)
    for script, filename in [('network_memory.py', 'network-summary.json'), ('summarize_public_windows.py', 'summary.json')]:
        subprocess.run([sys.executable, '-X', 'utf8', 'tools/esp32c3_tests/'+script, '--input', str(base/name), '--output', str(base/name/filename)], check=True)
