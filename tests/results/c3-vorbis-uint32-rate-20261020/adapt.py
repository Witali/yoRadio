"""Historical initial assembly; final explicit C3 guards are in adaptation.diff.

This script is retained as preparation history, not as an archive or campaign
runner. The final pack.py/verify.py bytes are independently source-checked.
"""
from pathlib import Path
import ast
import difflib
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
BASE = ROOT / '.build/cyd-vorbis-uint32-rate-archive-prep-02'
PINS = {'pack.py': '7728dc4e5f02032bce95a4788c0cb211bbd64615f275a9cf5766582b8b4d7778',
        'verify.py': '56b82cd3962762b8cf9fa350ca16a9eaf1a1b9db040e148a2236ba317f206cec'}


def replace(source, before, after):
    if source.count(before) != 1:
        raise RuntimeError('Nonunique adaptation anchor: ' + repr(before))
    return source.replace(before, after, 1)


def main():
    originals = {name: (BASE / name).read_bytes() for name in PINS}
    for name, data in originals.items():
        if hashlib.sha256(data).hexdigest() != PINS[name] or (HERE / name).exists():
            raise RuntimeError('Frozen base changed or destination exists')
    pack = originals['pack.py'].decode().replace('cyd', 'c3').replace('CYD', 'C3')
    pack = pack.replace('c3-vorbis-public-header-audit-01', 'cyd-vorbis-public-header-audit-01')
    pack = pack.replace("'c3-vorbis-uint32-rate-caller-prep-01', ", '')
    pack = replace(pack, "        'caller-prep': repo / '.build/c3-vorbis-uint32-rate-caller-prep-01',\n", '')
    start = pack.index("    host = json.loads((extras['caller-prep']")
    stop = pack.index('    for path in sorted(Path(__file__)', start)
    pack = pack[:start] + '''    canonical = json.loads((extras['source-change'] / 'canonical-host-tests.command.json').read_bytes())
    add(repo / '.build/cyd-vorbis-format-command-01.py', 'extras/capture.py', canonical['runner_sha256'])
    for name in ('rate_protocol.py', 'test_rate_protocol.py'):
        add(repo / 'tests/c3_vorbis_rate' / name, 'extras/canonical-tests/' + name,
            sha((extras['sdk-prep'] / name).read_bytes()))
    host = json.loads((extras['sdk-prep'] / 'host-tests.command.json').read_bytes())
    manifest['supporting_host_inputs'] = {}
    canonical_fixture = repo / 'tests/target/c3_vorbis_format_qemu/main/fixture.h'
    for row in host['inputs_before']:
        path = Path(row['path']).resolve()
        if path.is_relative_to(extras['sdk-prep']):
            key = 'extras/sdk-prep/' + path.relative_to(extras['sdk-prep']).as_posix()
        else:
            need(path == canonical_fixture.resolve(), 'Unexpected external host-test source')
            key = 'extras/canonical-fixture.h'
        add(path, key, row['sha256'])
        manifest['supporting_host_inputs'][row['path']] = key
''' + pack[stop:]
    verify = originals['verify.py'].decode().replace('cyd', 'c3').replace('CYD', 'C3')
    changes = {
        'b7e1999c349f9353a5690eaf5b05a0387db1bcad365d7f079c4a6c52ae493156': '83ce582554970e1a4bb70587e036c45af7bfb84519d3d7d87580eb4b9b1d38de',
        'd23fd5cb2ad7d8c3a87ebcda2197421245f571dea5724de3d328058264e491c2': 'f3d8b3ff1cb8d2cef675eb742be35f3e6a4533b3e10fbd368aacd929a10fcac0',
        '53a9c81ae3293e99c0ea0fe9ef48b62ee2b78fde184fd080151b83f34dc9da79': '3440dc6f58e8b8ae7ceaba18a05815321ea60a2a3640f6e681c81100e5d72050',
        '3d97389d3e8befd2ebf6642172cbe9f285d12954aed0b0bd8168d832ba3d7483': '684b668f3a09b970f566bb1a95f7fb22952a6f70b0dde4ddd02d9437b6404f04',
        'bf9aee429042a512439f1fdf2ab5594e7e3812ff45bb52fdda8cc1c3c7f61ad8': '19c3cdee677d86f80cb5b6cee9a842dc134f2ec4414c73bbb587e910a38c0ff5',
        '7101770dc6db2667b3c477cc31365dd1acd6db4e': '9a97f6c54ec638111ce55cd36581b3c192f15207',
        '92ba997358f50994d41422438c78bf2d7ee86dc1efc265f5356a66e221ae2e58': '311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909',
        'ca3b95dfc83b6984ae91c509bf859e4334fcc74654d2fe8b68bfc34f06126cc6': '232650ec81ae5e10ecbe1b2c86de2d1adf8f1b793f5ef343241c6e510db3e71f'}
    for before, after in changes.items():
        verify = replace(verify, before, after)
    verify = replace(verify, "== row['elf_machine'] == 94", "== row['elf_machine'] == 243")
    verify = verify.replace("b'#ifdef LIMIT_TO_64kHz\\n'", "b'#ifdef LIMIT_TO_64kHz\\r\\n'")
    verify = verify.replace("layout. */\\n#ifdef LIMIT_TO_64kHz\\n'", "layout. */\\r\\n#ifdef LIMIT_TO_64kHz\\r\\n'")
    verify = replace(verify, "'vorbis_repair/COPYING', 'compat/vorbis_repair/enable.cmake'", "'vorbis_repair/COPYING'")
    verify = replace(verify, "sha(read('extras/caller-prep/rate_protocol.py'))", "sha(read('extras/sdk-prep/rate_protocol.py'))")
    verify = replace(verify, "['-Wno-frame-address', '-mlongcalls', '-fno-builtin-memcpy', '-fno-builtin-memset', '-fno-builtin-bzero',\n             '\"-specs=' + norm(meta['origin']) + '/build/specs/picolibc.specs\"']",
        "['-march=rv32imc_zicsr_zifencei', '-mtune=esp-base',\n             '\"-specs=' + norm(meta['origin']) + '/build/specs/picolibc.specs\"', '-D__PICOLIBC_ERRNO_FUNCTION=__errno']")
    verify = verify.replace('Preserved six-line Xtensa cflags/specs', 'Preserved four-line RV32 cflags/specs')
    verify = replace(verify, "'CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ': '240'", "'CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ': '160'")
    verify = replace(verify, "'CONFIG_IDF_TARGET_ESP32': '1', 'CONFIG_YORADIO_VORBIS_REPAIR': '1'", "'CONFIG_IDF_TARGET_ESP32C3': '1', 'CONFIG_FREERTOS_UNICORE': '1'")
    verify = replace(verify, "'__LONG_MAX__': '0x7fffffffL', '__XTENSA__': '1'", "'__LONG_MAX__': '0x7fffffffL', '__riscv': '1', '__riscv_xlen': '32'")
    verify = replace(verify, "'CONFIG_FREERTOS_UNICORE' not in macros and", "macros.get('CONFIG_FREERTOS_UNICORE') == '1' and")
    verify = verify.replace('SMP/optional policy compile context', 'Unicore/optional policy compile context')
    verify = replace(verify, "desc['target'] == 'esp32'", "desc['target'] == 'esp32c3'")
    verify = replace(verify, "config.get('IDF_TARGET') == 'esp32' and config.get('ESP_DEFAULT_CPU_FREQ_MHZ') == 240 and\n             config.get('FREERTOS_UNICORE') is False and config.get('YORADIO_VORBIS_REPAIR') is True", "config.get('IDF_TARGET') == 'esp32c3' and config.get('ESP_DEFAULT_CPU_FREQ_MHZ') == 160 and\n             config.get('FREERTOS_UNICORE') is True")
    verify = replace(verify, "expected_flash = {'0x1000':", "expected_flash = {'0x0':")
    # Preserve the generic capture receipt for canonical19; prep23 has a different actual schema.
    start = verify.index("    identity('extras/caller-prep/test_rate_protocol.py'")
    stop = verify.index("    return dict(result='OFFLINE_VERIFIED'", start)
    verify = verify[:start] + '''    identity('extras/sdk-prep/test_rate_protocol.py', TESTS)
    identity('extras/sdk-prep/target/c3_vorbis_uint32_rate_qemu/main/main.c', CALLER)
    identity('extras/sdk-prep/rate_protocol.py', PROTOCOL)
    identity('extras/canonical-tests/test_rate_protocol.py', TESTS)
    identity('extras/canonical-tests/rate_protocol.py', PROTOCOL)
    prep_host = load('extras/sdk-prep/host-tests.command.json')
    need(prep_host['schema'] == 'c3-rate-pure-host-tests-v1' and type(prep_host['returncode']) is int and
         prep_host['returncode'] == 0 and prep_host['timed_out'] is False and prep_host['interrupted'] is False and
         prep_host['inputs_unchanged'] is True and prep_host['inputs_before'] == prep_host['inputs_after'] and
         len(prep_host['inputs_before']) == 7, 'Actual C3 prep23 host receipt')
    need(set(manifest['supporting_host_inputs']) == {row['path'] for row in prep_host['inputs_before']}, 'Host source binding set')
    for row in prep_host['inputs_before']:
        key = manifest['supporting_host_inputs'][row['path']]
        need(key.startswith('extras/sdk-prep/') or key == 'extras/canonical-fixture.h', 'Host source role scope')
        identity(key, row['sha256'])
        need(len(read(key)) == row['bytes'], 'Host source size')
    for row in prep_host['logs']:
        key = 'extras/sdk-prep/' + PureWindowsPath(row['path']).name
        identity(key, row['sha256'])
        need(len(read(key)) == row['bytes'], 'Prep23 log size')
    need(re.search(r'Ran 23 tests in .*\\n\\nOK\\s*$', read('extras/sdk-prep/host-tests.stderr.log').decode().replace('\\r\\n', '\\n')), 'Actual twenty-three prep methods')
    host = load('extras/source-change/canonical-host-tests.command.json')
    need(host['status'] == 'TERMINAL' and type(host['returncode']) is int and host['returncode'] == 0 and
         type(host['owned_pid']) is int and host['owned_pid'] > 0 and not host.get('timed_out', False) and
         not host.get('interrupted', False), 'Actual canonical19 host receipt')
    identity('extras/capture.py', host['runner_sha256'])
    stderr_key = None
    for origin, row in host['logs'].items():
        key = 'extras/source-change/' + PureWindowsPath(origin).name
        identity(key, row['sha256'])
        need(len(read(key)) == row['bytes'], 'Canonical19 log size')
        if key.endswith('.stderr.log'):
            stderr_key = key
    need(stderr_key and re.search(r'Ran 19 tests in .*\\n\\nOK\\s*$', read(stderr_key).decode().replace('\\r\\n', '\\n')), 'Actual nineteen canonical methods')
''' + verify[stop:]
    for name, value in [('pack.py', pack), ('verify.py', verify)]:
        ast.parse(value)
        with (HERE / name).open('xb') as stream:
            stream.write(value.encode())
    diff = ''.join(''.join(difflib.unified_diff(originals[name].decode().splitlines(True), value.splitlines(True),
        fromfile='CYD02/' + name, tofile='C3-01/' + name)) for name, value in [('pack.py', pack), ('verify.py', verify)])
    (HERE / 'adaptation.diff').write_bytes(diff.encode())
    (HERE / 'source-relation.json').write_bytes((json.dumps(dict(base_pins=PINS,
        scope='Independent C3 platform/source/pins/host-proof adaptation; no evidence packed or validated',
        source_algorithms_or_campaigns_modified=False), indent=2) + '\n').encode())
    print('C3 source proposal written; no packer/verifier execution')


if __name__ == '__main__':
    main()
