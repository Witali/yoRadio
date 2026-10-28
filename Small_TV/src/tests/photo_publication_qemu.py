"""Interrupt real photo operations, then cold boot the exact stopped NOR image."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import socket
import sys
from types import SimpleNamespace

from control_oracle import verify_inputs
from gdb_observer import Observer
from machine_oracle import ELFFile, ROOT
from photo_flash_evidence import journal, ready_frame, materialize
from photo_owner_qemu import multipart, process_handle
from photo_write_budget_qemu import descriptions, running_http, stop_at
from qemu_storage import direct_flash_backing
from verify_jpeg_clock_evidence import protected
import weather_qemu as weather


CASES = ('invalidation-body', 'invalidation-footer', 'source-erased', 'first-chunk',
         'frame-page', 'publication-body', 'publication-footer', 'complete')
GRAY_SHA = 'a3ec07b094d96c0fc6b420ba1a8666639a108c9e925c5f199c3e8f6f8ee10745'


def sha(data):
    """Bind every complete backing and code observation to its exact bytes."""
    return hashlib.sha256(data).hexdigest()


class Guest:
    """Own one process and debugger; cold input is never reseeded or patched."""
    def __init__(self, vm, args, server, folder, initial, report):
        self.vm, self.folder, self.report = vm, folder, report
        self.observer = self.kernel = self.handle = self.session = None
        prior = vm.seed_clock_network
        vm.seed_clock_network = lambda *unused: initial
        try:
            with socket.socket() as reservation:
                reservation.bind(('127.0.0.1', 0)); port = reservation.getsockname()[1]
            options = SimpleNamespace(yoradio=str(ROOT), firmware='reconstructed',
                qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
                rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
                hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),
                network='clock', display='none', persistent=True, paused=True, gdb_port=port,
                http_base_port=0, service_port=server.port)
            self.session, prepared = vm.launch(options, folder)
            self.kernel, self.handle = process_handle(self.session['pid'])
            report.update(pid=self.session['pid'], name=self.session['name'], owners_stopped=False,
                initial_sha256=sha(initial), prepared_sha256=prepared['prepared_flash_sha256'])
            assert self.flash() == initial and sha(initial) == prepared['prepared_flash_sha256']
            (folder/'initial.bin').write_bytes(self.flash())
            self.observer = Observer(port); self.observer.socket.settimeout(900)
            with vm.QMP(self.session['qmp_port'], self.session['name']) as qmp:
                assert direct_flash_backing(qmp, folder)
            self.url = self.session['web_urls']['station']
        except BaseException:
            self.stop(False)
            raise
        finally:
            vm.seed_clock_network = prior

    def flash(self):
        """Read the actual direct raw backend, never a reconstructed RAM substitute."""
        return (self.folder/'flash.bin').read_bytes()

    def ready(self, http, wait_http):
        """Wait for ordinary HTTP service; no LCD or network acceptance is inferred."""
        self.observer.resume(); wait_http(self.url, '/getclocktype'); self.observer.interrupt()
        status, body = running_http(self.observer, http, self.url, '/get_jpeg_write_limit')
        assert status == 200 and json.loads(body) == dict(limit_kib=200)
        status, body = running_http(self.observer, http, self.url, '/getclocktype')
        assert status == 200 and json.loads(body) in (0, 1, 3), 'Use a clock seed without photo prefetch'

    def stop(self, abrupt):
        """Terminate only this pinned owner, or normally close a finished cold control."""
        if self.observer:
            self.observer.close(); self.observer = None
        if self.session:
            if abrupt:
                # Acquire termination rights while the synchronization handle
                # still pins this process identity. Never kill by a process name.
                terminal = self.kernel.OpenProcess(0x100001, False, self.session['pid'])
                if not terminal: raise ctypes.WinError(ctypes.get_last_error())
                self.kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
                self.kernel.TerminateProcess.restype = wintypes.BOOL
                try:
                    if not self.kernel.TerminateProcess(terminal, 91):
                        raise ctypes.WinError(ctypes.get_last_error())
                finally:
                    self.kernel.CloseHandle(terminal)
            elif not self.handle or self.kernel.WaitForSingleObject(self.handle, 0) != 0:
                self.vm.control(self.folder, 'stop')
            if self.handle:
                assert self.kernel.WaitForSingleObject(self.handle, 10000) == 0
                self.kernel.CloseHandle(self.handle); self.handle = None
            self.report.update(owners_stopped=True, abrupt=abrupt)
            self.session = None


def entries_for(elf):
    """Resolve actual wrappers and the source erase boundary in the exact app ELF."""
    entries, _ = descriptions(elf)
    with elf.open('rb') as stream:
        values = {s['st_value'] for s in ELFFile(stream).get_section_by_name('.symtab').iter_symbols()
                  if s.name == 'esp_partition_erase_range' and s['st_value']}
    assert len(values) == 1
    entries['esp_partition_erase_range'] = next(iter(values))
    return entries


def interrupted_operation(guest, entries, plan, executor, http, case, start, arguments):
    """Stop after the selected completed SDK call using hardware breakpoints only."""
    observer = guest.observer
    entry = entries['photo_upload_start_detailed' if start else 'photo_upload_finish_detailed']
    observer.breakpoint(entry)
    pending = executor.submit(http, guest.url, '/start_upload' if start else '/finish_upload',
        arguments, 900, guest.url)
    observer.continue_to(entry); observer.breakpoint(entry, False)
    returned = observer.register(1); observer.breakpoint(returned)
    watched = {entries[name]: name for name in ('flash_program', 'flash_erase', 'esp_partition_erase_range')}
    for address in watched: observer.breakpoint(address)
    events = []
    while len(events) < 2000:
        pc = stop_at(observer, set(watched) | {returned})
        assert pc != returned, 'Requested interruption boundary was not reached'
        name = watched[pc]
        event = dict(function=name, pc=pc, address=observer.register(11),
            bytes=observer.register(13) if name == 'flash_program' else
                  observer.register(12) if name == 'esp_partition_erase_range' else 4096)
        target = False
        if name == 'flash_program':
            for extent in plan['metadata']['extents']:
                if extent['offset'] <= event['address'] < extent['offset'] + extent['bytes']:
                    relative = (event['address'] - extent['offset']) % 4096
                    target = (case.endswith('-body') and relative == 0 or
                              case.endswith('-footer') and relative == 3840)
            if case == 'frame-page':
                target = event['address'] == plan['caches'][4]['extents'][0]['offset']
        if case == 'source-erased' and name == 'esp_partition_erase_range':
            target = event['address'] == 4*102400 and event['bytes'] == 102400
        callback_return = observer.register(1); code = observer.memory(pc, 2)
        observer.breakpoint(pc, False); observer.breakpoint(callback_return)
        observer.continue_to(callback_return)
        event.update(status=observer.register(10), return_pc=callback_return, instruction_sha256=sha(code))
        assert event['status'] == 0 and observer.memory(pc, 2) == code
        observer.breakpoint(callback_return, False); observer.breakpoint(pc)
        events.append(event)
        if target:
            assert not pending.done(), 'HTTP operation completed before the selected interruption'
            return pending, dict(boundary=case, completed_callbacks=events, cut_pc=callback_return)
    raise AssertionError('Unbounded callback trace')


def upload(guest, http, data, finish=True):
    """Use unmodified start, MIME chunks and finish endpoints for a recovery control."""
    chunks = (len(data)+4095)//4096
    assert running_http(guest.observer, http, guest.url, '/start_upload',
        dict(file_number=5, file_size=len(data), total_chunks=chunks)) == (200, b'OK')
    guest.observer.resume()
    try:
        for index in range(chunks):
            assert multipart(guest.url, 5, index, chunks, data[index*4096:(index+1)*4096]) == (200, b'OK')
    finally:
        guest.observer.interrupt()
    if finish:
        # Host observation under icount can outlast a normal small API request.
        # Keep the same explicit900s bound as the existing format harness;
        # firmware guest-time, I/O and write limits remain unchanged.
        guest.observer.resume()
        try:
            assert http(guest.url, '/finish_upload', dict(file_number=5, file_name='file5.jpg'),
                900, guest.url) == (200, b'OK')
        finally:
            guest.observer.interrupt()


def check_cut(case, initial, cut, plan, old, new, source, pixels):
    """Independently check authority, source and full pixels at each cut boundary."""
    head = journal(cut, plan); prior = journal(initial, plan)
    entry = head['entries'][4]
    if case == 'invalidation-body':
        assert head['generation'] == prior['generation']
        ready_frame(cut, plan, 4, old['sha256'], old['rgb565_sha256'])
    elif case == 'invalidation-footer':
        assert head['generation'] == prior['generation']+1 and not entry['ready']
        assert cut[0x264000:0x27d000] == initial[0x264000:0x27d000]
    elif case in ('publication-footer', 'complete'):
        assert head['generation'] == prior['generation']+2
        ready_frame(cut, plan, 4, new['sha256'], new['rgb565_sha256'])
    else:
        assert head['generation'] == prior['generation']+1 and not entry['ready']
    if case == 'source-erased': assert cut[0x264000:0x27d000] == b'\xff'*102400
    if case == 'first-chunk':
        assert cut[0x264000:0x265000] == source[:4096]
        assert cut[0x265000:0x27d000] == b'\xff'*(102400-4096)
    if case in ('frame-page', 'publication-body', 'publication-footer', 'complete'):
        assert cut[0x264000:0x264000+len(source)] == source
        assert cut[0x264000+len(source):0x27d000] == b'\xff'*(102400-len(source))
        frame = materialize(cut, plan['caches'][4]['extents'], 115200)
        if case == 'frame-page': assert frame[:256] == pixels[:256] and frame != pixels
        else: assert frame == pixels
    expected = old if case.startswith('invalidation-') else new if case == 'complete' else None
    return dict(journal=head, expected_visible=dict(exists=expected is not None,
        size=expected['bytes'] if expected else 0))


def main():
    """Check selected operation boundaries and cold recovery on production firmware."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root', type=Path, required=True)
    parser.add_argument('--dependency-root', type=Path, default=Path('C:/Work/yoRadio'))
    parser.add_argument('--seed', type=Path, required=True, help='Stopped matching CMYK6 ready-cache image')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cases', nargs='+', choices=CASES, default=CASES)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    assert len(args.cases) == len(set(args.cases))
    sys.path.insert(0, str(args.qemu_root/'tools')); import small_tv_vm as vm
    from small_tv_http_test import http, wait_http, clean_uart
    weather.vm = vm
    frozen = json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    for row in frozen['files']: assert sha((args.qemu_root/row['file']).read_bytes()) == row['sha256']
    archive = ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    manifest = json.loads((archive/'manifest.json').read_text())
    plan = json.loads((archive/'jpeg-cache-plan.json').read_text())
    elf = ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    assert sha(elf.read_bytes()) == manifest['elf_sha256']
    from jpeg_lossless_fixtures import load, pixels
    fixture = ROOT/'Small_TV/src/tests/fixtures/jpeg_extended'
    images, _, pins = load(fixture/'lossless6-manifest.json')
    rows = json.loads((fixture/'lossless6-manifest.json').read_text())['fixtures']
    old = next(row for row in rows if row['channels'] == 4)
    new = next(row for row in rows if row['channels'] == 3); data = images[new['name']]
    reference_pixels = pixels(3)
    gray = (fixture/'flat-gray-progressive-8.jpg').read_bytes()
    initial = args.seed.read_bytes(); assert len(initial) == 0x400000
    ready_frame(initial, plan, 4, old['sha256'], old['rgb565_sha256'])
    app = next(row for row in manifest['images'] if row['file'] == 'app.bin')
    offset = int(app['offset'], 0); assert sha(initial[offset:offset+app['bytes']]) == app['sha256']
    files = [Path(__file__), elf, args.seed, fixture/'flat-gray-progressive-8.jpg',
        *[archive/name for name in ('app.bin', 'manifest.json', 'source-manifest.json', 'jpeg-cache-plan.json')],
        *[Path(__file__).with_name(name) for name in ('photo_write_budget_qemu.py', 'photo_flash_evidence.py',
            'photo_owner_qemu.py', 'gdb_observer.py', 'qemu_storage.py', 'control_oracle.py', 'weather_qemu.py',
            'verify_jpeg_clock_evidence.py')]]
    pins.update({str(p.resolve()): sha(p.read_bytes()) for p in files})
    report = dict(passed=False, all_functionality_verified=False, network_acceptance=False,
        lcd_acceptance=False, physical_power_cut_tested=False, hardware_tested=False,
        app_sha256=verify_inputs(ROOT, args.dependency_root), elf_sha256=manifest['elf_sha256'],
        source_sha256=manifest['source_sha256'], frozen_inputs=frozen, inputs_sha256=pins, cases=[],
        recovery_source_sha256=sha(gray), finish_host_timeout=900,
        scope='Abrupt process cuts after completed SDK operations; not partial in-page electrical power loss')
    entries = entries_for(elf); report['entries'] = entries
    server = weather.WeatherFixture(); server.set_response(200)
    executor = ThreadPoolExecutor(max_workers=1); guest = pending = None
    try:
        for case in args.cases:
            row = dict(name=case, boots=[]); report['cases'].append(row)
            folder = args.output/case; folder.mkdir()
            warm = {}; row['boots'].append(warm)
            guest = Guest(vm, args, server, folder/'warm', initial, warm); guest.ready(http, wait_http)
            assert guest.flash() == initial
            chunks = (len(data)+4095)//4096
            arguments = dict(file_number=5, file_size=len(data), total_chunks=chunks)
            if case in ('invalidation-body', 'invalidation-footer', 'source-erased'):
                pending, row['trace'] = interrupted_operation(guest, entries, plan, executor,
                    http, case, True, arguments)
            elif case == 'first-chunk':
                assert running_http(guest.observer, http, guest.url, '/start_upload', arguments) == (200, b'OK')
                guest.observer.resume()
                assert multipart(guest.url, 5, 0, chunks, data[:4096]) == (200, b'OK')
                guest.observer.interrupt()
            else:
                upload(guest, http, data, finish=case == 'complete')
                if case != 'complete':
                    pending, row['trace'] = interrupted_operation(guest, entries, plan, executor, http,
                        case, False, dict(file_number=5, file_name='file5.jpg'))
            cut = guest.flash(); (folder/'cut-paused.bin').write_bytes(cut)
            row.update(check_cut(case, initial, cut, plan, old, new, data, reference_pixels))
            assert clean_uart(guest.folder)
            guest.stop(True)
            assert guest.flash() == cut, 'Abrupt process exit changed the paused physical bytes'
            (folder/'cut-stopped.bin').write_bytes(guest.flash()); guest = None
            if pending:
                try:
                    response = pending.result(timeout=30)
                except (OSError, ConnectionError) as error:
                    row['interrupted_http_error'] = type(error).__name__
                else: raise AssertionError(('Interrupted operation returned a response', response))
                pending = None
            cold = {}; row['boots'].append(cold)
            guest = Guest(vm, args, server, folder/'cold', cut, cold); guest.ready(http, wait_http)
            status, body = running_http(guest.observer, http, guest.url, '/get_Photo_File?file=5&chunk=0&size=0')
            row['cold_visible'] = json.loads(body)
            assert status == 200 and row['cold_visible'] == row['expected_visible']
            assert guest.flash() == cut, 'Cold observation mutated the retained image'
            upload(guest, http, gray)
            recovered = guest.flash(); (folder/'recovered.bin').write_bytes(recovered)
            row['recovery'] = ready_frame(recovered, plan, 4, sha(gray), GRAY_SHA)
            mutable = [(0x9000, 0xf000), (0x3e7000, 0x3e8000), (0x264000, 0x27d000)]
            mutable += [(r['offset'], r['offset']+r['bytes']) for r in plan['candidate_extents']]
            protected(initial, cut, mutable); protected(initial, recovered, mutable)
            assert clean_uart(guest.folder)
            guest.stop(False); assert guest.flash() == recovered; guest = None
            row.update(passed=True, cut_sha256=sha(cut), recovery_sha256=sha(recovered))
            vm.save_json(args.output/'report.json', report)
            print('PASS cut/cold/recovery:', case, row['cold_visible'], flush=True)
        assert all(sha(Path(name).read_bytes()) == digest for name, digest in pins.items())
        report['passed'] = True
    except BaseException as error:
        report['error'] = type(error).__name__+': '+str(error)
        raise
    finally:
        if guest: guest.stop(False)
        executor.shutdown(wait=True, cancel_futures=True); server.close()
        vm.save_json(args.output/'report.json', report)
    print('PASS production photo publication boundaries:', len(report['cases']), flush=True)


if __name__ == '__main__': main()
