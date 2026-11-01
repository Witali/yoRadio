from pathlib import Path
import hashlib
import json
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
sdk = ROOT.parent.parent / '.idf/v6.0.2'
tool = ROOT.parent.parent / '.idf/tools-v6.0.2/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin/xtensa-esp32-elf-addr2line.exe'
out = ROOT / '.build/cyd-production-boot-replay-20261030-symbolication-01'
out.mkdir(exist_ok=False)
sha = lambda data: hashlib.sha256(data).hexdigest()
result = {'physical_device': False, 'image_or_config_patches': False,
          'tool_sha256': sha(tool.read_bytes()), 'tool_bytes': tool.stat().st_size,
          'helper_sha256': sha(Path(__file__).read_bytes()), 'profiles': {}}
for profile, build in [('pdm', 'gvp'), ('disabled-pdm', 'goff')]:
    capture = ROOT / ('.build/cyd-production-boot-replay-20261030-gpio25-' + profile + '-01')
    report = json.loads((capture / 'report.json').read_text('utf-8'))
    log = (capture / 'qemu.log').read_text('utf-8', errors='replace')
    assert report['completed'] and not report['passed'] and report['all_bound_inputs_current']
    assert report['flash_unchanged_after_snapshot'] and report['facts']['emulated_input_delay_ns'] == 25
    assert report['reason'] == 'guest_panic_observed' and report['qemu_exit_status'] == 0
    pc = re.search(r'^PC\s+:\s+(0x[0-9a-fA-F]+)', log, re.M).group(1)
    fault = re.search(r'EXCVADDR:\s+(0x[0-9a-fA-F]+)', log).group(1)
    panic = re.search(r'Core\s+0 panic\x27ed \(([^)]+)\)', log).group(1)
    line = re.search(r'^Backtrace:\s*(.*)$', log, re.M).group(1)
    frames = [pc] + re.findall(r'(0x[0-9a-fA-F]+):0x[0-9a-fA-F]+', line)
    elf = ROOT / ('.build/srx01/' + build + '/yoradio_cyd2usb_native.elf')
    before = sha(elf.read_bytes())
    assert before == report['facts']['elf_sha256']
    command = [str(tool), '-p', '-f', '-i', '-e', str(elf), *frames]
    started = time.monotonic()
    child = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=20, creationflags=subprocess.CREATE_NO_WINDOW)
    elapsed = time.monotonic() - started
    (out / (profile + '-addr2line.stdout.local-only.txt')).write_bytes(child.stdout)
    (out / (profile + '-addr2line.stderr.local-only.txt')).write_bytes(child.stderr)
    assert child.returncode == 0 and sha(elf.read_bytes()) == before
    text = child.stdout.decode('utf-8', errors='strict')
    functions = [row.split(' at ', 1)[0] for row in text.splitlines()]
    assert functions[0] == 'register_chipv7_phy'
    assert 'esp_phy_load_cal_and_init' in functions and 'esp_phy_enable' in functions
    assert 'wifi_hw_start' in functions and 'ppTask' in functions
    result['profiles'][profile] = {
        'capture': capture.name, 'capture_report_sha256': sha((capture / 'report.json').read_bytes()),
        'console_sha256': sha((capture / 'qemu.log').read_bytes()),
        'elf_sha256': before, 'elf_bytes': elf.stat().st_size,
        'native_status': child.returncode, 'elapsed_seconds': elapsed,
        'stdout_sha256': sha(child.stdout), 'stderr_sha256': sha(child.stderr),
        'raw_tool_output_local_only': True, 'panic_type': panic, 'pc': pc,
        'fault_address': fault, 'frame_addresses': frames, 'function_names': functions,
        'spiffs_failure_observed': 'SPIFFS_ERR_NOT_A_FS' in log or 'SPIFFS mount failed' in log,
        'static_rx_loan_exercised': False, 'full_radio_startup_qualified': False,
        'original_flash_sha256': report['facts']['original_flash_sha256'],
        'all_51_bindings_current_at_capture': len(report['bindings']) == 51 and report['all_bound_inputs_current'],
        'early_mpi_return_log_observed': report['early_mpi_return_log_observed'],
        'display_driver_entry_observed': report['markers']['display_driver_entered']}
result['tool_unchanged'] = sha(tool.read_bytes()) == result['tool_sha256']
assert result['tool_unchanged']
(out / 'report.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'saved': out.name, 'profiles': result['profiles'], 'tool_unchanged': True}))
