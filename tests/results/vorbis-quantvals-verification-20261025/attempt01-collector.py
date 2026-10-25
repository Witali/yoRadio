"""Create-only selected quantvals evidence. No prepared program is executed."""
from pathlib import Path
import ast
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/'tests/results/vorbis-quantvals-20261025'
VERIFIER = ROOT/'.build/verify-vorbis-quantvals-20261025-template-01.py'
CHECKPOINT = ROOT/'.build/vorbis-quantvals-checkpoint-20261025.md'
GROUPS = {'host'+str(i): '.build/vorbis-quantvals-host-20261025-0'+str(i) for i in range(1, 5)}
GROUPS.update(validation='.build/vorbis-quantvals-validation-20261025-01',
              esp32='.build/vorbis-quantvals-esp32-20261025-01',
              esp32c3='.build/vorbis-quantvals-esp32c3-20261025-01')
CANONICAL = ['tests/test-vorbis-quantvals.py', 'tests/test-vorbis-quantvals-protocol.py', 'tests/run-vorbis-quantvals-qemu.py',
             'tests/test-vorbis-floor1-render.py', '.build/cyd-vorbis-format-command-01.py',
             'docs/CYD_VORBIS_TRANSFER_DESIGN.md', 'docs/ESP32_CYD_C3_TRANSFER_PLAN.md']
for profile in ('esp32-cyd2usb-native', 'esp32c3-oled-native'):
    CANONICAL += ['idf/'+profile+'/main/'+name for name in
                  ('vorbis_repair/setup.c', 'vorbis_repair_abi.h',
                   'vorbis_repair/README.md', 'vorbis_repair/COPYING')]
COMMANDS = ('sdk-head', 'sdk-clean', 'build', 'dependencies', 'symbols', 'merge',
            'qemu', 'sdk-head-after', 'sdk-clean-after')
OBSERVED = {}


def need(ok, reason):
    if not ok: raise ValueError(reason)


def norm(path): return str(path).replace('\\', '/').rstrip('/')
def sha(data): return hashlib.sha256(data).hexdigest()


def identity(path):
    path = path.resolve()
    need(path.is_file(), 'selected ordinary file exists: '+str(path))
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024*1024), b''): digest.update(part)
    pin = (path.stat().st_size, digest.hexdigest())
    need(path not in OBSERVED or OBSERVED[path] == pin, 'selected input changed')
    OBSERVED[path] = pin
    return pin


def read(path):
    path = path.resolve()
    need(path.is_relative_to(ROOT), 'saved body must stay within task checkout')
    data = path.read_bytes()
    need(identity(path) == (len(data), sha(data)), 'selected read identity')
    return data


def report(group): return json.loads(read(ROOT/GROUPS[group]/'report.json'))


def preflight():
    need(not DEST.exists() and DEST.parent.is_dir(), 'fresh archive destination')
    ast.parse(read(VERIFIER), filename=str(VERIFIER))
    need(bool(read(CHECKPOINT)), 'root checkpoint exists before archive creation')
    host = report('host4')
    need(host['completed'] is True and host['passed'] is True and host['cases'] == 35975 and
         host['target_cases'] == 2179 and host['baseline']['signed_power_overflow_detected'] is True,
         'actual final host campaign complete')
    for target in ('esp32', 'esp32c3'):
        r = report(target)
        need(all(r[k] is True for k in ('completed', 'passed', 'finite_integer_root_qualified',
             'whole_setup_compiled', 'source_inputs_unchanged')) and r['target'] == target and
             r['observed']['cases'] == 2179 and r['result'] == 'FINITE_QUANTVALS_EXACT',
             'actual target campaign complete: '+target)
        need(tuple(c['name'] for c in r['commands']) == COMMANDS and
             all(c['state'] == 'complete' and c['exit_status'] == 0 and
                 type(c['pid']) is int and c['pid'] > 0 and not c['timed_out'] and not c['interrupted']
                 for c in r['commands']), 'nine successful target commands')
        need(r['sdk_child']['exit_status'] == 0 and r['sdk_child']['pid'] > 0,
             'actual owned SDK child terminal')
    for name, code in (('host', 1), ('host02', 1), ('host03', 0), ('host04', 0), ('esp32', 0), ('esp32c3', 0),
                       ('protocol-before', 1), ('protocol-after', 0), ('reader-replay', 0)):
        outer = json.loads(read(ROOT/GROUPS['validation']/(name+'.json')))
        need(outer['status'] == 'TERMINAL' and outer['returncode'] == code and
             type(outer['owned_pid']) is int and outer['owned_pid'] > 0 and
             not outer.get('timed_out') and not outer.get('interrupted') and not outer.get('error_type'),
             'actual normal outer receipt: '+name)
    replay = json.loads(read(ROOT/GROUPS['validation']/'reader-replay-result.json'))
    need(replay['completed'] is True and replay['passed'] is True and replay['inputs_unchanged'] is True and
         replay['final_reader_replayed_on_actual_saved_data'] is True and replay['sdk_or_qemu_or_decoder_executed'] is False,
         'actual final pure reader replay against both saved native runs')


def main():
    preflight()
    selected = {}
    inventories = {}
    for group, relative in GROUPS.items():
        base = ROOT/relative
        if group.startswith('host') or group == 'validation':
            paths = sorted(p for p in base.rglob('*') if p.is_file())
            inventories[group] = [norm(p.relative_to(base)) for p in paths]
        else:
            r = report(group)
            paths = [p for p in base.iterdir() if p.is_file()]
            paths += [p for sub in ('sources', 'project') for p in (base/sub).rglob('*') if p.is_file()]
            paths += [base/name for name in r['build_outputs']]
            paths += [base/name for name in ('build/build.ninja', 'build/CMakeFiles/rules.ninja', 'build/config/sdkconfig.h')]
        selected.update({group+'/'+norm(p.relative_to(base)): p for p in paths})
    selected.update({'canonical/'+name: ROOT/name for name in CANONICAL})
    m = dict(schema='vorbis-quantvals-evidence-v1', checkout=norm(ROOT), groups=GROUPS,
             files={}, origins={}, omissions={}, elf_headers={}, complete=False,
             whole_dependency_closure=False, raw_decoder_qualified=False,
             full_G6_qualified=False, production_firmware=False, physical_device=False,
             scope='Finite integer-root arithmetic only; no codec/PCM/radio/resource qualification.')
    DEST.mkdir(); (DEST/'objects').mkdir()

    def put(alias, data):
        need(alias not in m['files'], 'unique alias')
        digest = sha(data); object_name = 'objects/'+digest+'.gz'
        if not (DEST/object_name).exists(): (DEST/object_name).write_bytes(gzip.compress(data, mtime=0))
        m['files'][alias] = dict(bytes=len(data), sha256=digest, object=object_name)

    def capture(alias, path, omit=False):
        size, digest = identity(path)
        row = dict(path=norm(path.resolve()), bytes=size, sha256=digest)
        if omit:
            row['reason'] = 'Executable/library/ELF/flash identity only; omitted body has no verified binary semantics.'
            m['omissions'][alias] = row
        else: put(alias, read(path)); row['alias'] = alias
        m['origins'][norm(path.resolve()).casefold()] = row
        if path.suffix.lower() == '.elf':
            with path.open('rb') as stream: header = stream.read(52)
            put(alias+'.header52', header); m['elf_headers'][alias] = alias+'.header52'

    for alias, path in sorted(selected.items()):
        omit = path.name == 'test' or path.suffix.lower() in ('.elf', '.exe', '.o', '.obj', '.a', '.dll') or (
            alias.startswith(('esp32/', 'esp32c3/')) and path.suffix.lower() == '.bin')
        capture(alias, path, omit)
    tools = {}
    for target in ('esp32', 'esp32c3'):
        tools.update(report(target)['tools'])
    for name in ('host', 'host02', 'host03', 'host04', 'esp32', 'esp32c3', 'protocol-before', 'protocol-after', 'reader-replay'):
        outer = json.loads(read(ROOT/GROUPS['validation']/(name+'.json')))
        tools[outer['argv'][0]] = outer['executable_sha256']
    for index, (name, digest) in enumerate(sorted(tools.items())):
        need(identity(Path(name))[1] == digest, 'recorded external tool/ROM identity')
        capture('identities/'+str(index), Path(name), True)
    put('collector.py', read(Path(__file__)))
    verifier = read(VERIFIER); put('verifier.py', verifier); (DEST/'verifier.py').write_bytes(verifier)
    readme = b'''Selected integer-root evidence. Run python verifier.py offline.
The checker launches/imports no SDK, decoder, reference, compiler or archived helper.
It independently checks exact big-integer roots, C fixture rows, all ordered
target events and actual owned command/cleanup receipts. Integrity success is
finite arithmetic qualification only. Omitted executable/ELF/flash bodies have
identity-only records; a saved52-byte ELF header checks native architecture,
not whole binary semantics. SDK dependencies/build trees are not fully saved.
No PCM, raw decoder, fullG6, radio, resource or physical qualification follows.
Historical host01/02 failures and smaller host03 success are preserved separately.
The executed controller is the original frozen reader; a later pure-reader
comma correction has separate actual before/after unit and saved-data replay
receipts, not a claim that the SDK/QEMU executed the amended controller.
'''
    for name, data in (('README.md', readme), ('CHECKPOINT.md', read(CHECKPOINT)),
                       ('.gitattributes', b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n')):
        put(name, data); (DEST/name).write_bytes(data)
    for group, names in inventories.items():
        base = ROOT/GROUPS[group]
        need(names == sorted(norm(p.relative_to(base)) for p in base.rglob('*') if p.is_file()),
             'selected host/validation inventory unchanged')
    for path, pin in tuple(OBSERVED.items()): need(identity(path) == pin, 'publication input changed')
    m.update(complete=True, selected_sources_unchanged=True, aliases=len(m['files']),
             objects=len(list((DEST/'objects').iterdir())))
    data = (json.dumps(m, indent=2)+'\n').encode('utf-8'); (DEST/'manifest.json').write_bytes(data)
    print(json.dumps(dict(path=str(DEST), manifest_sha256=sha(data), aliases=m['aliases'],
                         objects=m['objects'], omissions=len(m['omissions']))))


if __name__ == '__main__': main()
