import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0, 'tools/esp32c3_tests')
from common import Board, require
from ota import image_info, snapshot, verify_snapshot, wait_image
from serial.tools.list_ports import comports

root = Path.cwd()
out = root/'tests/results/esp32c3-wifi16-20261001/rom-recovery'
out.mkdir(exist_ok=True)
firmware = root/'firmware/development/esp32c3-aac-bounded-wifi-radio'
manifest = json.loads((firmware/'manifest.json').read_text())
config = (firmware/'sdkconfig').read_text()
require('CONFIG_SPI_FLASH_AUTO_SUSPEND=y' not in config, 'Recovery must disable Auto Suspend')
require('CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y' not in config, 'Recovery must remain awake')
require('CONFIG_YORADIO_QEMU=y' not in config, 'Never flash a QEMU image')
image = (firmware/'app.bin').read_bytes()
expected = image_info(image)
require(expected['sha256'] == manifest['sha256'], 'Recovery image hash mismatch')
ports = [p for p in comports() if p.vid == 0x303a and p.pid == 0x1001]
require(len(ports) == 1 and ports[0].device == 'COM9', 'Ambiguous or absent C3')
require(ports[0].serial_number.upper() == '38:44:BE:44:77:B4', 'Unexpected board')
board = Board('http://192.168.100.4')
before, initial = snapshot(board), board.info()
require(initial['partition'] == 'app1', 'Unexpected active slot')
require(initial['app_elf_sha256'] == 'bcf37075fc7f41b92ca48fdc60d9aaa3f1f85d6f992b8150c73e5202eba0060b',
        'Unexpected initial firmware')
result = dict(before=initial, target=expected, steps=[], result='FAIL')
env = dict(os.environ, PYTHONIOENCODING='utf-8')

def command(name, args, timeout=120):
    value = subprocess.run(args, capture_output=True, text=True, encoding='utf-8',
                           errors='replace', timeout=timeout, env=env,
                           creationflags=subprocess.CREATE_NO_WINDOW)
    (out/(name+'.log')).write_text(value.stdout+'\n'+value.stderr, encoding='utf-8')
    result['steps'].append(dict(name=name, exit_code=value.returncode))
    require(value.returncode == 0, 'Recovery step failed: '+name)
    print(name+': PASS', flush=True)

try:
    board.stop()
    table_path = root/'.build/c3-recovery-partition-table.bin'
    command('read-partitions', [sys.executable, '-m', 'esptool', '--chip', 'esp32c3',
        '-p', 'COM9', '--before', 'usb-reset', '--after', 'no-reset', 'read-flash',
        '0x8000', '0x1000', str(table_path)])
    table = table_path.read_bytes()
    partitions = []
    for pos in range(0, len(table), 32):
        magic, kind, subtype, offset, size, label, flags = struct.unpack('<HBBII16sI', table[pos:pos+32])
        if magic != 0x50aa:
            break
        partitions.append(dict(name=label.split(b'\0')[0].decode(), type=kind, subtype=subtype,
                               offset=offset, size=size, flags=flags))
    selected = [p for p in partitions if p['name'] == initial['partition']]
    require(len(selected) == 1, 'Active partition missing from physical table')
    app = selected[0]
    require((app['type'], app['subtype'], app['offset'], app['size'], app['flags']) ==
            (0, 0x11, 0x1e0000, 0x1d0000, 0), 'Unexpected physical application bounds')
    require(len(image) <= app['size'], 'Image exceeds partition')
    result.update(partitions=partitions, partition_table_sha256=hashlib.sha256(table).hexdigest(),
                  written_offset=app['offset'], written_bytes=len(image))
    command('write-app1', [sys.executable, '-m', 'esptool', '--chip', 'esp32c3',
        '-p', 'COM9', '--before', 'no-reset', '--after', 'no-reset', 'write-flash',
        hex(app['offset']), str(firmware/'app.bin')])
    command('reset', ['C:/Users/rudol/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe',
        '-NoProfile', '-File', 'C:/Work/yoRadio/.agents/skills/flash-reset-esp32c3-oled/scripts/reset_esp32c3_oled.ps1',
        '-Port', 'COM9', '-PythonPath', sys.executable, '-VerifyUrl', board.origin+'/'])
    result['after'] = wait_image(board, expected['app_elf_sha256'], initial['partition'])
    result.update(verify_snapshot(board, before), status=board.status(), result='PASS')
except Exception as error:
    result['error_type'] = type(error).__name__
    raise
finally:
    (out/'recovery.json').write_text(json.dumps(result, indent=2)+'\n')
