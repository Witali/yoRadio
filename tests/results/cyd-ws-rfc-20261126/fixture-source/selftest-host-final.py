"""Finalization regression controls; no child, socket, guest or TLS material."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import types

base=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('host_final_fixture',base/'pressure-host.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class ExitedChild:
    returncode=0
    def poll(self):return 0

checks=[]
with tempfile.TemporaryDirectory(prefix='host-final-owned-',dir=base)as folder:
    owned=Path(folder).resolve()
    assert owned.parent==base.resolve() and owned.name.startswith('host-final-owned-')
    for case in ('positive','input-mismatch','missing-input','host-mismatch','dump-error','fatal-marker'):
        work=owned/case;work.mkdir()
        flash=work/'flash.bin';flash.write_bytes(b'controlled fake flash, no key')
        capture=work/'wire.pcap';capture.write_bytes(b'controlled fake capture')
        log=work/'qemu-uart.log'
        log.write_text('network dump write error - stopping dump'if case=='dump-error'else
                       'Guru Meditation'if case=='fatal-marker'else'controlled fixture')
        source=work/'input.txt';source.write_text('original')
        guest=module.Guest.__new__(module.Guest)
        guest.options=types.SimpleNamespace(output=work)
        guest.private=work;guest.child=ExitedChild();guest.health=None;guest.endpoint=None
        guest.started=None;guest.inputs={source:module.pin(source)}
        guest.flash_path=flash;guest.flash_hash=module.pin(flash)['sha256']
        guest.helper={'FATAL':re.compile(r'Guru Meditation')}
        guest.report=dict(state='BOOT_PROBE_PASS',host=module.pin(base/'pressure-host.py'),
                          base_launcher=module.pin(module.LAUNCHER))
        if case=='input-mismatch':source.write_text('changed')
        if case=='missing-input':source.unlink()
        if case=='host-mismatch':guest.report['host']['sha256']='0'*64
        guest.__exit__(None,None,None)
        persisted=json.loads((work/'host.json').read_bytes())
        assert persisted['owned_guest_stopped'] and persisted['capture_stopped']
        assert persisted['state']==('BOOT_PROBE_PASS'if case=='positive'else'TERMINAL_NONPASS')
        if case=='missing-input':assert persisted['final_check_category']=='FileNotFoundError'
        if case=='dump-error':assert persisted['capture_write_errors_absent']is False
        if case=='fatal-marker':assert persisted['fatal_markers_absent']is False
        checks.append(dict(id=case,passed=True))
    # Confirm the exact fresh owned cleanup target before TemporaryDirectory's
    # recursive cleanup; no outside path or link can become its target.
    assert owned.resolve()==owned and owned.parent==base.resolve() and not owned.is_symlink()
out=base/'host-final-selftest.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,checks=checks,guest_used=False,network_used=False,
    subprocess_started=False,host_sha256=hashlib.sha256((base/'pressure-host.py').read_bytes()).hexdigest(),
    runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
print(json.dumps(dict(passed=True,checks=len(checks),guest_used=False)))
