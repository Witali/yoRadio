#!/usr/bin/env python3
"""Run original RV32 Vorbis lifetime/OOM cases in disposable QEMU instances.

Never opens a serial port or contacts a board. Exit 2 preserves observed decoder
failures; exit 1 means incomplete/invalid test evidence; exit 0 means all gates
pass for this corpus. Run with the ESP-IDF Python environment (esptool).
"""
import argparse
import bisect
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
APP1 = 0x1E0000
APP1_SIZE = 0x1D0000
MAGIC = 0x564C4631
ARCHIVES = {
    'libesp_audio_codec.a': '311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909',
    'libesp_audio_simple_dec.a': '232650ec81ae5e10ecbe1b2c86de2d1adf8f1b793f5ef343241c6e510db3e71f',
}
SOURCES = ('idf/esp32c3-oled-native/main/qemu_vorbis_lifecycle.c',
           'idf/esp32c3-oled-native/main/qemu_vorbis_output.inc',
           'idf/esp32c3-oled-native/main/decoder_pcm.h',
           'idf/esp32c3-oled-native/main/CMakeLists.txt',
           'idf/esp32c3-oled-native/main/Kconfig.projbuild',
           'idf/esp32c3-oled-native/sdkconfig.qemu-vorbis-lifecycle.defaults',
           'tools/codec_benchmark/run_vorbis_lifecycle.py')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def snapshot_sources(output, names=SOURCES):
    """Freeze the executed sources before the first VM, including this runner."""
    identities = {}
    for name in names:
        destination = output / 'sources' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
        identities[name] = sha(destination)
    return identities


def ogg_crc(data):
    crc = 0
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            crc = ((crc << 1) ^ (0x04C11DB7 if crc & 0x80000000 else 0)) & 0xFFFFFFFF
    return crc


def headers(data):
    """Extract the three complete header packets, including continued pages."""
    packets, packet, pos = [], bytearray(), 0
    while len(packets) < 3:
        if data[pos:pos+4] != b'OggS' or pos+27 > len(data):
            raise ValueError('Missing/truncated Ogg page')
        count = data[pos+26]
        laces = data[pos+27:pos+27+count]
        end = pos+27+count+sum(laces)
        if len(laces) != count or end > len(data):
            raise ValueError('Truncated Ogg header/body')
        page = bytearray(data[pos:end])
        checksum, = struct.unpack_from('<I', page, 22)
        page[22:26] = bytes(4)
        if ogg_crc(page) != checksum:
            raise ValueError('Ogg CRC mismatch')
        offset = pos+27+count
        for size in laces:
            packet.extend(data[offset:offset+size])
            offset += size
            if size < 255:
                packets.append(bytes(packet))
                packet.clear()
        pos = end
    for kind, packet in zip((1, 3, 5), packets):
        if packet[:7] != bytes([kind])+b'vorbis':
            raise ValueError('Unexpected Vorbis header order')
    # The Espressif raw API receives payloads after the type/signature prefix.
    return packets[0][7:], packets[2][7:]


def records(log, name):
    result = []
    for line in log.splitlines():
        marker = 'VTEST_'+name+' '
        if marker not in line:
            continue
        fields = dict(re.findall(r'(\w+)=([^\s]+)', line.split(marker, 1)[1]))
        for key in fields.keys()-{'kind', 'ptr', 'old', 'caller', 'op', 'sha256'}:
            fields[key] = int(fields[key])
        result.append(fields)
    return result


def clean(row):
    return (row['live'] == row['requested'] == row['actual'] == row['bad_owners'] == 0
            and row['integrity'] == 1)


def symbol_table(nm_output):
    entries = []
    for line in nm_output.splitlines():
        match = re.fullmatch(r'([0-9a-fA-F]+) ([0-9a-fA-F]+) [TtWw] (.+)', line)
        if match:
            address, size, name = match.groups()
            entries.append((int(address,16), int(size,16), name))
    return sorted(entries)


def allocation_ledger(log, symbols=()):
    """Retain every traced allocation and its owning function from this ELF."""
    starts = [s[0] for s in symbols]
    events = []
    for line in log.splitlines():
        for name in ('ALLOC', 'FREE', 'INJECT', 'BAD_OWNER'):
            parsed = records(line,name)
            if not parsed:
                continue
            row = parsed[0]
            caller = int(row['caller'],16)
            index = bisect.bisect_right(starts,caller-1)-1
            function = None
            if index >= 0:
                address,size,symbol = symbols[index]
                if address <= caller-1 < address+size:
                    function = f'{symbol}+0x{caller-address:x}'
            events.append(dict(row,event=name,caller_function=function))
    return events


def assess(log, *, cycles, fail_at=0, direct=False, reference=None):
    """Never classify a truncated run, missing injection or bad PCM as a pass."""
    if 'VTEST_HARNESS_ERROR' in log:
        raise ValueError('Harness overflow/progress failure')
    register = records(log, 'REGISTER')
    begins = records(log, 'BEGIN')
    rows = records(log, 'RESULT')
    injections = records(log, 'INJECT')
    if len(register) != 1 or not begins:
        raise ValueError('Missing/duplicate registration or test start')
    if fail_at and (len(injections) != 1 or injections[0]['attempt'] != fail_at):
        raise ValueError('Requested allocation failure was not reached exactly once')
    if not fail_at and injections:
        raise ValueError('Unexpected injection')
    panic = bool(re.search(r'Guru Meditation|assert failed|abort\(\) was called|CORRUPT HEAP', log))
    completion = records(log, 'COMPLETE')
    boundary_test = direct in (2, 3)
    expected = cycles if boundary_test else cycles + bool(fail_at or direct)
    base = dict(registration=register[0], rows=rows, injections=injections,
                bad_owners=records(log, 'BAD_OWNER'), retained=records(log, 'RETAINED'))
    if panic:
        return dict(base, status='CRASH', decoder_gate_pass=False, complete=False)
    if (len(completion) != 1 or completion[0]['runs'] != expected or
            len(rows) != expected or [r['run'] for r in rows] != list(range(1, expected+1))):
        raise ValueError('Missing/duplicate test completion or result')
    if len(begins) != expected or [r['run'] for r in begins] != list(range(1, expected+1)):
        raise ValueError('Missing/duplicate begin')
    for r in rows:
        if r['injected'] != int(bool(fail_at) and r['run']==1 and not boundary_test):
            raise ValueError('Result contradicts injection count')
        if r['samples']*2 != r['pcm'] or not re.fullmatch('[0-9a-f]{64}',r['sha256']):
            raise ValueError('Invalid PCM count/hash')
    if not fail_at and not direct:
        first = rows[0]
        pcm_ok = first['pcm'] > 0 and first['samples']*2 == first['pcm']
        same = all((r['sha256'], r['pcm'], r['attempts']) ==
                   (first['sha256'], first['pcm'], first['attempts']) for r in rows)
        recovered = all((r['free'], r['largest']) == (b['free'], b['largest'])
                        for r, b in zip(rows, begins))
        passed = pcm_ok and same and recovered and all(clean(r) and r['result'] == 0 for r in rows)
        return dict(base, status='PASS' if passed else 'BASELINE_FAILURE',
                    decoder_gate_pass=passed, complete=True, reference=first,
                    exact_heap_recovery=recovered)
    if reference is None:
        raise ValueError('Recovery needs the valid-stream PCM reference')
    recovery = rows[-1]
    recovery_ok = (clean(recovery) and recovery['result'] == 0 and
                   (recovery['pcm'], recovery['sha256']) == (reference['pcm'], reference['sha256']) and
                   recovery['free'] == begins[0]['free'] and recovery['largest'] == begins[0]['largest'])
    if boundary_test:
        boundary = records(log, 'REGISTRATION' if direct == 2 else 'SERVICE')
        if len(boundary) != 1 or boundary[0]['injected'] != 1:
            raise ValueError('Missing/duplicate registration or service failure result')
        boundary = boundary[0]
        passed = (recovery_ok and -9 <= boundary['result'] <= -1 and boundary['integrity'] == 1
                  and boundary['free_before'] == boundary['free_after']
                  and boundary['largest_before'] == boundary['largest_after'])
        passed = passed and (boundary['live'] == 0 if direct == 2 else
                             boundary['null_handle'] == boundary['released'] == 1)
        return dict(base, complete=True, recovery_ok=recovery_ok, boundary=boundary,
                    decoder_gate_pass=passed, status='HANDLED' if passed else 'UNSAFE_RETURN')
    first = rows[0]
    # -100 is the harness's no-progress observation, not a handled SDK error.
    safe_error = -9 <= first['result'] <= -1 and clean(first)
    # A failed optional allocation may have a lossless fallback. Keep this
    # outcome separate from an explicit error; never accept truncated PCM.
    tolerated = (not direct and first['result'] == 0 and clean(first) and
                 (first['pcm'], first['sha256']) == (reference['pcm'], reference['sha256']))
    passed = recovery_ok and (safe_error or tolerated)
    return dict(base, complete=True, recovery_ok=recovery_ok, decoder_gate_pass=passed,
                status=('HANDLED' if safe_error else 'TOLERATED') if passed else 'UNSAFE_RETURN')


def payload(data, info, setup, *, direct=False, fail_at=0, cycles=1):
    result = struct.pack('<8I', MAGIC, 1, int(direct), fail_at, cycles,
                         len(data), len(info), len(setup))+data+info+setup
    if len(result) > APP1_SIZE:
        raise ValueError('Fixture does not fit disposable app1')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, default=ROOT/'idf/esp32c3-oled-native/build-qemu-vorbis-lifecycle')
    parser.add_argument('--deps', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--qemu', required=True)
    parser.add_argument('--bios', required=True)
    parser.add_argument('--wsl', action='store_true')
    parser.add_argument('--cycles', type=int, default=100)
    parser.add_argument('--baseline-only', action='store_true')
    parser.add_argument('--pcm-reference', type=Path,
                        help='Independent raw-packet capture when an intentional EOF fix restores PCM')
    parser.add_argument('--case', action='append', default=[], help='Run named fault cases only, plus baseline; never full qualification')
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args()
    if not 1 <= args.cycles <= 1000:
        parser.error('cycles must be 1..1000 (qualification requires at least 100)')
    if args.output.exists():
        parser.error('Use a new output directory to preserve previous evidence')
    args.output.mkdir(parents=True)
    build, output = args.build.resolve(), args.output.resolve()
    cfg = (build/'config/sdkconfig.h').read_text()
    if '#define CONFIG_YORADIO_QEMU_VORBIS_LIFECYCLE 1' not in cfg:
        raise ValueError('Wrong test image')
    repaired = '#define CONFIG_YORADIO_VORBIS_REPAIR 1' in cfg
    sources = list(SOURCES)
    if repaired:
        sources.extend(('idf/esp32c3-oled-native/main/vorbis_repair_abi.h',
                        'idf/esp32c3-oled-native/main/decoder_registration.c',
                        'idf/esp32c3-oled-native/main/decoder_registration.h',
                        'idf/esp32c3-oled-native/main/decoder_resources.h',
                        'idf/esp32c3-oled-native/sdkconfig.qemu-vorbis-repair.defaults'))
        sources.extend(path.relative_to(ROOT).as_posix() for path in sorted(
            (ROOT/'idf/esp32c3-oled-native/main/vorbis_repair').glob('*')) if path.is_file())
    for name, digest in ARCHIVES.items():
        if sha(args.deps/'esp-adf-libs/esp_audio_codec/lib/esp32c3'/name) != digest:
            raise ValueError('Pinned archive mismatch: '+name)
    fixture_dir = ROOT/'tests/fixtures/esp32c3_calibration'
    entry = next(x for x in json.loads((fixture_dir/'manifest.json').read_text())['fixtures'] if x['codec'] == 'vorbis')
    fixture_path = fixture_dir/entry['file']
    if sha(fixture_path) != entry['sha256']:
        raise ValueError('Fixture hash mismatch')
    data = fixture_path.read_bytes()
    info, setup = headers(data)
    idf_version = (ROOT/'idf/esp32c3-oled-native/idf-version.txt').read_text().strip()
    nm_candidates = list(args.deps.glob(f'tools-{idf_version}/tools/riscv32-esp-elf/*/riscv32-esp-elf/bin/riscv32-esp-elf-nm.exe'))
    if len(nm_candidates)!=1:
        raise ValueError('Expected one pinned RV32 nm tool')
    nm_text = subprocess.check_output([str(nm_candidates[0]),'-n','-S','--defined-only',
        str(build/'yoradio_esp32c3_oled_native.elf')],text=True)
    (output/'symbols.txt').write_text(nm_text)
    symbols = symbol_table(nm_text)
    baseflash = output/'base-flash.bin'
    merge = [sys.executable, '-m', 'esptool', '--chip', 'esp32c3', 'merge-bin', '-o', str(baseflash),
             '--flash-mode', 'dio', '--flash-freq', '80m', '--flash-size', '4MB', '--pad-to-size', '4MB']
    for offset, name in (('0x0','bootloader/bootloader.bin'), ('0x8000','partition_table/partition-table.bin'),
                         ('0xe000','ota_data_initial.bin'), ('0x10000','yoradio_esp32c3_oled_native.bin')):
        merge.extend([offset, str(build/name)])
    with (output/'merge.log').open('w') as log:
        subprocess.run(merge, stdout=log, stderr=subprocess.STDOUT, check=True)
    def guest(path):
        return subprocess.check_output(['wsl.exe','--exec','wslpath','-a',str(path)], text=True).strip() if args.wsl else str(path)
    flash = output/'case-flash.bin'
    flash_guest = guest(flash)
    command = (['wsl.exe','--exec','timeout','--kill-after=2',str(args.timeout)] if args.wsl else [])
    command += [args.qemu, '-M','esp32c3', '-nographic','-no-reboot','-snapshot',
                '-icount','shift=0,align=off,sleep=off','-L',args.bios,
                '-drive',f'file={flash_guest},if=mtd,format=raw']
    report = dict(archive_sha256=ARCHIVES, fixture=entry,
                  elf_sha256=sha(build/'yoradio_esp32c3_oled_native.elf'),
                  app_sha256=sha(build/'yoradio_esp32c3_oled_native.bin'),
                  config_sha256=sha(build/'sdkconfig'),
                  source_sha256=snapshot_sources(output, sources), qemu_command=command,
                  decoder_repair=repaired,
                  boundary_failure_tests=repaired,
                  cases=[], hardware_tested=False, production_qualified=False)
    def save():
        (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    def execute(name, *, direct=False, fail_at=0, cycles=1, info_data=info, setup_data=setup, reference=None):
        if name != 'baseline' and args.case and name not in args.case:
            return None
        shutil.copyfile(baseflash, flash)
        content = payload(data, info_data, setup_data, direct=direct, fail_at=fail_at, cycles=cycles)
        with flash.open('r+b') as f:
            f.seek(APP1); f.write(content)
        logfile = output/(name+'.log')
        with logfile.open('w') as log:
            process = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, timeout=args.timeout+5)
        text = logfile.read_text(errors='replace')
        outcome = assess(text, cycles=cycles, fail_at=fail_at, direct=direct, reference=reference)
        ledger = allocation_ledger(text,symbols)
        (output/(name+'-allocations.json')).write_text(json.dumps(ledger,indent=2)+'\n')
        outcome.update(name=name, fail_at=fail_at, direct=direct, cycles=cycles,
                       returncode=process.returncode, log_sha256=sha(logfile),
                       allocation_ledger_sha256=sha(output/(name+'-allocations.json')),
                       command_payload_sha256=hashlib.sha256(content).hexdigest())
        report['cases'].append(outcome); save()
        print(name, outcome['status'], flush=True)
        return outcome
    baseline = execute('baseline', cycles=args.cycles)
    if not baseline['decoder_gate_pass']:
        raise ValueError('Baseline failed; saved evidence, allocation sweep not started')
    reference = baseline['reference']
    if repaired:
        original = json.loads((ROOT/'tests/results/esp32c3-vorbis-lifecycle-20261004/report.json').read_text())['cases'][0]['reference']
        report['original_pcm_match'] = all(reference[key] == original[key] for key in ('pcm','samples','sha256'))
        save()
        if args.pcm_reference:
            import gzip
            independent = json.loads((args.pcm_reference/'report.json').read_text())
            pcm = gzip.decompress((args.pcm_reference/'ample.pcm.gz').read_bytes())
            expected = independent['cases'][0]['rows'][0]
            if (not independent['raw_reference'] or not independent['all_passed'] or
                independent['fixture_sha256'] != report['fixture']['sha256'] or
                independent['archive_sha256'] != ARCHIVES or
                hashlib.sha256(pcm).hexdigest() != expected['sha256'] or
                len(pcm) != expected['pcm'] or
                any(reference[k] != expected[k] for k in ('pcm','samples','sha256'))):
                raise ValueError('Independent packet reference did not match repaired PCM')
            report['pcm_reference'] = dict(reference=expected,
                report_sha256=sha(args.pcm_reference/'report.json'),
                fixture_sha256=independent['fixture_sha256'], raw_packet_reference=True)
            save()
        elif not report['original_pcm_match']:
            raise ValueError('Repaired decoder changed the original valid-stream PCM')
    attempts = reference['attempts']
    report['expected_allocation_failures'] = attempts
    report['allocation_requests_by_phase'] = dict(Counter(
        str(row['phase']) for row in records((output/'baseline.log').read_text(),'ALLOC') if row['run']==1))
    if not args.baseline_only:
        for index in range(1, attempts+1):
            execute(f'oom-{index:04d}', fail_at=index, reference=reference)
        malformed = {
            'invalid-info-version': (b'\x01'+info[1:], setup),
            'truncated-info': (info[:1], setup),
            'truncated-setup': (info, setup[:1]),
            'invalid-codebook-sync': (info, setup[:1]+bytes([setup[1]^0xFF])+setup[2:]),
        }
        for name, (bad_info,bad_setup) in malformed.items():
            execute(name, direct=True, info_data=bad_info, setup_data=bad_setup, reference=reference)
        if repaired:
            for index in range(1, baseline['registration']['attempts']+1):
                execute(f'registration-{index:04d}', direct=2, fail_at=index, reference=reference)
            for index in (1, 2):
                execute(f'service-open-{index:04d}', direct=3, fail_at=index, reference=reference)
    if set(args.case) - {c['name'] for c in report['cases']}:
        raise ValueError('Unknown or unexecuted requested case')
    report['coverage_complete'] = not args.baseline_only and not args.case and args.cycles >= 100
    report['status_counts'] = dict(Counter(c['status'] for c in report['cases']))
    report['decoder_gate_pass'] = report['coverage_complete'] and all(c['decoder_gate_pass'] for c in report['cases'])
    save()
    print(json.dumps(report['status_counts']), flush=True)
    return 0 if report['decoder_gate_pass'] else 2


if __name__ == '__main__':
    sys.exit(main())
