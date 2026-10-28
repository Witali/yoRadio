"""Inspect sealed owned raw-decoder evidence; never execute archived code."""
import argparse
import ast
import hashlib
import importlib.util
import json
import re
import struct
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
FOLDER = 'tests/results/vorbis-decoder-20261028'
ARCHIVE_SHA = 'c01692d4e32e7f477cec7e6b650e4b184c64045ba2573926554af5f0eae15517'
MANIFEST_SHA = '9388aa1cd6c9dab21cd9ebd41fddfb46636c229aa1901270bcc4378b57f6cf67'
PHYSICAL_MEMBERS, PHYSICAL_BYTES = 326, 58141929
LOGICAL_MEMBERS, LOGICAL_BYTES = 1359, 76529126
OMITTED_COUNT, OMITTED_BYTES = 1809, 158778501
FINAL_HOST = 'host-20261028-03'
HOST_STATES = {
    'host-20261028-01': dict(completed=False, passed=False, commands=1),
    'host-20261028-02': dict(completed=False, passed=False, commands=2),
    'host-20261028-03': dict(completed=True, passed=True, commands=3),
}
HOST_ERRORS = {
    'host-20261028-01': "ValueError('owned transport terminal: compiler-version')",
    'host-20261028-02': "ValueError('owned child terminal: compile')",
}
PREFLIGHT_GROUPS = {'preflight-20261028-01'}
NATIVE_GOOD = {'esp32-20261028-02': 'esp32', 'c3-20261028-02': 'esp32c3'}
NATIVE_FAILED = {
    'esp32-20261028-01': dict(target='esp32', error='native command terminal0: build'),
    'c3-20261028-01': dict(target='esp32c3', error='native command terminal0: build'),
}
PROTOCOL_STATES = {'protocol-20261028-01': dict(target='esp32', controls=dict(valid_full_corpus=True,
    malformed_refused=24, synthetic_protocol_reference_only=True, lifecycle_controls=True))}
GROUPS = {'c3-20261028-01', 'c3-20261028-02', 'esp32-20261028-01', 'esp32-20261028-02',
    'fixture-lint-20261028-01', 'host-20261028-01', 'host-20261028-02', 'host-20261028-03',
    'preflight-20261028-01', 'profiles-20261028-01', 'protocol-20261028-01', 'tools', 'receipts'}
EXPLICIT_OMITTED_EXECUTABLES = {'host-20261028-03/decoder'}
PROFILE_GROUP = 'profiles-20261028-01'
LINT_GROUPS = {'fixture-lint-20261028-01': dict(warnings=7, errors=0, commands=['fixture'])}
SEALS = {'receipts/vorbis-decoder-host-final-seal-20261028-01.json':
    'a728489b400b9e26aa8adce6d815c394e31f7b07189726a919b5997b8b8bacfc',
    'receipts/vorbis-decoder-native-final-seal-20261028-01.json':
    '8c1b338784772e8b104da1e7b129dcf0410887f387130d22c9e55428de4a9ec6'}
EXPECTED_HOST_CONTROLS = dict(checks=17082719, undersized=1212, measures=14187,
    open_refusals=589, replace_refusals=589, process_refusals=302, other_refusals=265,
    event_counts=[589, 589, 302, 31, 1, 1, 1, 1], recovery_spans=4017, recovery_pcm_bytes=4035840)
EXPECTED_NATIVE = {'esp32': dict(selected_objects=22, all_objects=562),
                   'esp32c3': dict(selected_objects=22, all_objects=595)}
PINS = {
    'vorbis_synthesis_checkpoint.py': 'dfff6c46c56bf0cbf95a2385ca3584314b720088bd11124247e20605d8712ed5',
    'verify-vorbis-pcm-exact-checkpoint.py': '22a8fbc03d658d569ca95c6d18636f18e3e79cca1e812138659993c14d5f81aa',
    'test-vorbis-synthesis.py': 'f42ab5b669b5a39e0619449a798c00f682bf2f1468664d5376eb63bdda429765',
    'test-vorbis-timing.py': 'f990067645a196972767639c100506be757b9adb8a2d0f8bbd8fe3857f0be33a',
    'test-vorbis-floor1-render.py': 'df9f6c4496836f8e166209d92114e88b20568aac143081d0c4cc3096b6828cb2',
    'test-vorbis-decoder.py': '16166095e826b1dfd95cff357c6d97671a501d13813f7febd2b18ce9e6298763',
    'test-vorbis-decoder-qemu.py': '4f658393b24aa250a669f17732f12cc159db8d38c0102fe81b33fcda695a4ae9',
    'test-vorbis-synthesis-qemu.py': 'ce4859daf4f9a0bd59a1c023b3b01b3e015d7a76a14acca98c8f6e27ce91222b',
    'test-vorbis-floor0-frame.py': 'e92e1470f9806fe9fa2fe3c6903bd8f4015ab735ede11d54b6be5dc9c95c5357',
    'test-vorbis-setup.py': 'ce69b4136ac1b1a4b71e185e6c600330e46cfb8b2b14c3d4a1e54c044afb02ff',
    'test-vorbis-floor-packet.py': '8ab01db0169af95e75f7aa6cc1e7c28df48371f94f445aaa03c08882c17776d7',
    'test-vorbis-residue.py': '1191a648a9070a995b1e256519ce71891f70779d924db651db16c490c856f31d',
    'vorbis_packet_frame_model.py': '5ed0ad7b589fc16de2d99f5aca77e179808aa0553fd22d9907b59369abcd77a9',
}
SOURCE_PINS = {
    'idf/components/native_vorbis_decoder/decoder.c': '5656842a0d3a78a072cc56b7f382a0100b6757473056322acb57cc3081d43f2b',
    'idf/components/native_vorbis_decoder/include/native_vorbis_decoder.h':
        'beb4719b97df3467189292ff214b7e16ad50be2e8d7a269b593cea9d56cf4b5b',
    'tests/native/vorbis_decoder_host.c': 'e2eda6121e629f9d933917b73cf811e0dfb911c76918ea4aa37d633f8ebab9d6',
    'tests/target/vorbis_decoder_qemu/main/main.c': '30c748c6775e95027f604f63db4e314e1c58eefa98153e00d7b4d0850d15d63c',
}
ORIGINAL_SHA = '32ba4c7e401fcfd05238f929fa6874c3048237792d78f36b05a8fade5b861e24'
PCM_SHA = 'b9df479b6cb6ac07b2aff2049f05bb8ba98ef9ce4fdc72acf40a333f47e01d75'
LINKED = ('native_vorbis_decoder_replace', 'native_vorbis_decoder_measure',
    'native_vorbis_decoder_process', 'native_vorbis_decoder_reset', 'native_vorbis_decoder_info',
    'native_vorbis_decoder_clear', 'native_vorbis_setup_owner_replace', 'native_vorbis_frame_decode',
    'native_vorbis_frame_floor0_prepare', 'native_vorbis_imdct_transform_binary64',
    'native_vorbis_synthesis_push', 'native_vorbis_pcm_s16_product_pair')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def contained(name):
    path = PurePosixPath(name)
    return bool(path.parts) and not path.is_absolute() and '..' not in path.parts and \
        path.as_posix() == name and ':' not in name and '\\' not in name


def normalized(name):
    return name.replace('\\', '/')


def elf(body, machine, kind):
    return len(body) >= 52 and body[:6] == b'\x7fELF\x01\x01' and \
        int.from_bytes(body[16:18], 'little') == kind and int.from_bytes(body[18:20], 'little') == machine


def load_readers():
    need(all(isinstance(pin, str) and re.fullmatch('[0-9a-f]{64}', pin)
             for pin in (ARCHIVE_SHA, MANIFEST_SHA, *PINS.values(), *SOURCE_PINS.values())),
         'draft cannot execute before final archive and live-source pins')
    need(all(type(value) is int and value >= 0 for value in (PHYSICAL_MEMBERS, PHYSICAL_BYTES,
        LOGICAL_MEMBERS, LOGICAL_BYTES, OMITTED_COUNT, OMITTED_BYTES)) and FINAL_HOST in HOST_STATES and
        len(NATIVE_GOOD) == 2 and HOST_STATES and GROUPS and EXPECTED_HOST_CONTROLS is not None,
        'final explicit evidence inventory, attempt histories and control totals required')
    # Check all bytes before importing even the shared archive inspector.
    for name, pin in PINS.items():
        need(sha((ROOT/'tests'/name).read_bytes()) == pin, 'pinned live reader: '+name)
    for name, pin in SOURCE_PINS.items():
        need(sha((ROOT/name).read_bytes()) == pin, 'pinned live executed source: '+name)
    spec = importlib.util.spec_from_file_location('decoder_checkpoint_archive_helper',
                                                ROOT/'tests/vorbis_synthesis_checkpoint.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    modules = {name: helper.load_local('tests/'+name, pin, 'decoder_checkpoint_live_'+str(index))
        for index, (name, pin) in enumerate(PINS.items()) if name not in
        ('vorbis_synthesis_checkpoint.py', 'test-vorbis-floor1-render.py')}
    return helper, modules


class Evidence:
    def __init__(self, helper, aliases):
        physical = helper.archive_members(FOLDER, ARCHIVE_SHA, MANIFEST_SHA)
        self.physical = physical
        self.live_source_counts = {}
        self.manifest = json.loads((ROOT/FOLDER/'manifest.json').read_bytes())
        self.members = aliases.resolve_logical_members(physical, self.manifest)
        need((len(physical), sum(map(len, physical.values())), len(self.members),
              sum(map(len, self.members.values()))) ==
             (PHYSICAL_MEMBERS, PHYSICAL_BYTES, LOGICAL_MEMBERS, LOGICAL_BYTES),
             'complete physical and logical archive inventory')
        need({name.split('/')[0] for name in self.members} == GROUPS, 'all and only retained campaign groups')
        self.omitted = {row['path']: row for row in self.manifest['omitted']}
        need(len(self.omitted) == len(self.manifest['omitted']) == OMITTED_COUNT and
             sum(row['bytes'] for row in self.omitted.values()) == OMITTED_BYTES,
             'complete explicitly pinned omitted-file inventory')
        for name, row in self.omitted.items():
            need(contained(name) and name not in self.members and type(row['bytes']) is int and row['bytes'] >= 0 and
                 re.fullmatch('[0-9a-f]{64}', row['sha256']) and
                 (name in EXPLICIT_OMITTED_EXECUTABLES or
                  any(name.startswith(group+'/build/') for group in (*NATIVE_GOOD, *NATIVE_FAILED))),
                 'only explicitly identified derived executables or native build scratch omitted')

    def read(self, name):
        return json.loads(self.members[name])

    def artifact(self, group, name, pin, required=False):
        need(contained(name), 'contained artifact path')
        full = group+'/'+name
        if full in self.members:
            need(sha(self.members[full]) == pin, 'every retained artifact byte')
        else:
            need(not required and full in self.omitted and self.omitted[full]['sha256'] == pin,
                 'every omitted executed artifact has an explicit identity')

    def sources(self, group, report, live=False, target=False, profile=False):
        rows = ((pin['snapshot'].removeprefix('sources/'), pin['sha256']) for pin in report['inputs'].values()) \
            if target else report['sources'].items()
        snapshots = strict = 0
        for name, pin in rows:
            snapshots += 1
            need(contained(name), 'contained immutable source snapshot')
            body = self.members[group+'/sources/'+name]
            need(sha(body) == pin, 'every source/header/packet/reference snapshot byte')
            if not live:
                continue
            relative = None
            if profile: relative = 'idf/components/'+name
            elif name.startswith('components/'): relative = 'idf/'+name
            elif name.startswith(('native/', 'helper/')): relative = 'tests/native/'+name.split('/', 1)[1]
            elif name.startswith('project/'): relative = 'tests/target/vorbis_decoder_qemu/'+name.split('/', 1)[1]
            elif name == 'controller.py': relative = 'tests/test-vorbis-decoder-qemu.py'
            elif name == 'runner.py': relative = 'tests/test-vorbis-decoder.py'
            elif name == 'supervisor-origin.py': relative = 'tests/test-vorbis-floor1-render.py'
            elif name == 'synthesis-reader.py': relative = 'tests/test-vorbis-synthesis.py'
            elif name == 'timing-oracle.py': relative = 'tests/test-vorbis-timing.py'
            elif name.startswith('readers/'): relative = 'tests/'+name.split('/', 1)[1]
            elif name == 'design-reference/synthesis-controller.py': relative = 'tests/test-vorbis-synthesis-qemu.py'
            if relative and (Path(relative).suffix in ('.c', '.h', '.inc', '.py', '.ps1', '.defaults') or
                             Path(relative).name == 'CMakeLists.txt'):
                need((ROOT/relative).read_bytes() == body, 'live source equals actually executed frozen code')
                strict += 1
        if live: self.live_source_counts[group] = dict(snapshots=snapshots, strict=strict)

    def host_commands(self, group, report, successful):
        for row in report['commands']:
            stem = group+'/'+row['name']
            request = self.read(stem+'.request.json')
            need(request['nonce'] == row['nonce'] and request['argv'] == row['child_argv'] and
                 sha(self.members[stem+'.request.json']) == row['request_sha256'], 'exact owned host request binding')
            receipt = row.get('supervisor')
            if not receipt:
                need(not successful and stem+'.receipt.json' not in self.members and row.get('transport_exit') != 0,
                     'honest failed host transport before a child receipt')
                continue
            need(receipt == self.read(stem+'.receipt.json') and receipt['nonce'] == row['nonce'] and
                 receipt['request_sha256'] == row['request_sha256'] and row['transport_exit'] == 0 and
                 not row.get('forced_transport_stop') and receipt['state'] == 'terminal' and receipt['final'] and
                 receipt['new_session'] and receipt['child_pid'] == receipt['owned_pgid'] and
                 receipt['child_reaped'] and receipt['group_gone'] and
                 (not successful or receipt['child_returncode'] == 0), 'owned host child/session terminal and reaped')
        if 'supervisor_sha256' in report:
            body = self.members[group+'/supervisor.py']
            origin = self.members[group+'/sources/supervisor-origin.py']
            templates = [ast.literal_eval(node.value) for node in ast.parse(origin).body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == 'SUPERVISOR' for target in node.targets)]
            need(len(templates) == 1 and templates[0].count('assert 0<timeout<=60') == 1 and
                 body == templates[0].replace('assert 0<timeout<=60', 'assert 0<timeout<=180').encode() and
                 sha(body) == report['supervisor_sha256'], 'exact retained watchdog-only supervisor derivation')

    def native_commands(self, group, report, successful):
        for row in report['commands']:
            for stream in ('stdout', 'stderr'):
                if row.get(stream+'_sha256') is not None:
                    need(sha(self.members[group+'/'+row['name']+'.'+stream+'.log']) == row[stream+'_sha256'],
                         'every native command stream unchanged')
            if successful:
                need(row['state'] == 'complete' and row['exit_status'] == 0 and row['pid'] > 0 and
                     'tree_stop_returncode' not in row, 'actual native child terminal without forced stop')
            elif 'pid' in row:
                need(row.get('exit_status') is not None and row['state'] in ('complete', 'failed') and
                     'tree_stop_returncode' not in row, 'retained native failure terminal')
            else:
                need(row['state'] == 'failed', 'native launch failed before child creation')


def primary_pcm(body, synthesis, model):
    """Recover actual PCM bytes, independently of per-case SHA summaries."""
    reader = synthesis.Reader(body)
    need(reader.take('8s') == b'VSYNOUT1' and reader.take('I') == 31, 'complete actual raw-owner primary capture')
    result, spans = {}, {}
    for index, row in enumerate(model['cases']):
        need(reader.take('6I') == (index, row['rate'], row['channels'], row['short_block'], row['long_block'], 14),
             'primary raw-owner format and packet identity')
        records = synthesis.Reader(reader.raw(reader.take('Q')))
        status, failed_packet, failed_channel, failed_route = reader.take('i3I')
        totals = reader.take('11Q')
        stage = reader.raw(reader.take('I')).decode('ascii')
        need(status == 0 and (failed_packet, failed_channel, failed_route) == (0xffffffff,)*3 and not stage,
             'complete raw-owner stream with no masked failure')
        parts = []
        for packet in range(14):
            fields = records.take('5IQI5IqQ')
            need(fields[0] == packet and fields[-1] == row['frames'][packet]*row['channels'],
                 'every original per-packet PCM span')
            part = records.raw(fields[-1]*2)
            parts.append(part)
            spans[index, packet] = part
        need(records.at == len(records.body), 'no missing or trailing packet records')
        result[row['id']] = b''.join(parts)
        need(len(result[row['id']]) == row['pcm_bytes'], 'every original output byte retained')
    need(reader.at == len(body), 'no trailing primary capture bytes')
    return result, spans


def compare_all_pcm(actual, model, references, xiph):
    maximum_original = maximum_xiph = 0
    for row in model['cases']:
        body = actual[row['id']]
        need(len(body) == row['pcm_bytes'] == len(references[row['id']]) == len(xiph[row['id']]),
             'full zero-lag reference extents without trim/shift/gain/channel fitting')
        errors = []
        for reference in (references[row['id']], xiph[row['id']]):
            errors.append(max((abs(a[0]-b[0]) for a, b in
                zip(struct.iter_unpack('<h', body), struct.iter_unpack('<h', reference))), default=0))
        need(max(errors) <= 2, 'every S16 sample satisfies both unchanged reference bounds')
        maximum_original = max(maximum_original, errors[0])
        maximum_xiph = max(maximum_xiph, errors[1])
    for relation in model['relations']:
        values = [actual[name] for name in relation['cases']]
        need(all(value == values[0] for value in values[1:]) if relation['kind'] == 'equal' else
             any(value != values[0] for value in values[1:]), 'all original fourteen relations')
    need(sum(map(len, actual.values())) == 738560 and len(actual) == 31 and
         sha(b''.join(actual[row['id']] for row in model['cases'])) == PCM_SHA,
         'all 738560 primary bytes equal the previously qualified synthesis output')
    return dict(maximum_original_absolute_error=maximum_original, maximum_xiph_absolute_error=maximum_xiph)


def native_build(evidence, group, report, target, native):
    read, members = evidence.read, evidence.members
    evidence.native_commands(group, report, successful=True)
    need([row['name'] for row in report['commands']] == ['sdk-head', 'sdk-clean', 'build', 'symbols', 'merge', 'qemu'],
         'complete actual SDK/build/link/image/runtime command sequence')
    need(report['completed'] and report['passed'] and report['target'] == target and report['target_executed'] and
         report['numerical_qualified'] and not report['production_firmware'] and not report['physical_device'] and
         not report['Xiph_decoder_executed'] and not report['deferred_scopes_resumed'], 'actual unselected owned native scope')
    need(report['sdk_revision'] == native.SDK_HEAD[target] and
         members[group+'/sdk-head.stdout.log'].decode().strip() == native.SDK_HEAD[target] and
         not members[group+'/sdk-clean.stdout.log'].strip() and
         report['tools']['qemu']['sha256'] == native.QEMU_SHA[target], 'pinned clean SDK and QEMU identities')
    child = json.loads(members[group+'/sdk-child.json'].decode('utf-8-sig'))
    need(child == report['sdk_child'] and child['exit_status'] == 0 and child['pid'] > 0, 'actual SDK child terminal receipt')
    for name, pin in report['build_outputs'].items():
        evidence.artifact(group, name, pin, required=not name.endswith('.obj'))
    description = read(group+'/build/project_description.json')
    machine = 94 if target == 'esp32' else 243
    need(description['target'] == target and elf(members[group+'/build/'+description['app_elf']], machine, 2),
         'actual ELF32 executable for the target ISA')
    expected = EXPECTED_NATIVE[target]
    need(len(report['compile_rows']) == expected['selected_objects'] and
         sum(name.endswith('.obj') for name in report['build_outputs']) == expected['all_objects'],
         'complete selected and SDK native object inventories')
    database = read(group+'/build/compile_commands.json')
    for row in report['compile_rows']:
        need(row in database and all(flag in row['command'] for flag in
             ('-fstack-usage', '-fno-fast-math', '-ffp-contract=off')), 'every actual owned unit and numeric compiler flags')
        relative = normalized(row['output']).rsplit('/build/', 1)[-1]
        name = 'build/'+relative
        body = members[group+'/'+name]
        need(elf(body, machine, 1) and sha(body) == report['build_outputs'][name], 'retained selected native object ABI and identity')
    need(len(report['stack_records']) == expected['selected_objects'] and all(
         members[group+'/'+name].decode().splitlines() == lines for name, lines in report['stack_records'].items()),
         'all actual owned stack frames, without whole-call-chain or physical-stack claims')
    symbols = members[group+'/symbols.stdout.log'].decode().replace('\r\n', '\n')
    need(all(re.search(r'\b'+name+r'$', symbols, re.M) for name in LINKED) and not
         re.search(r'\b(?:vorbis_synthesis|esp_vorbis_dec_open|vorbis_synthesis_pipeline_run)$', symbols, re.M),
         'linked persistent public raw path, without private decoder or batch helper')
    config = members[group+'/sdkconfig'].decode().replace('\r\n', '\n')
    compiled = members[group+'/build/config/sdkconfig.h'].decode().replace('\r\n', '\n')
    settings = ['CONFIG_ESP_TASK_WDT_EN', 'CONFIG_ESP_TASK_WDT_INIT', 'CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0']
    if target == 'esp32': settings.append('CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1')
    need(all(re.search('^'+name+'=y$', config, re.M) and re.search('^#define '+name+' 1$', compiled, re.M)
             for name in settings) and re.search('^#define CONFIG_IDF_TARGET_'+target.upper()+' 1$', compiled, re.M) and
         bool(re.search('^CONFIG_FREERTOS_UNICORE=y$', config, re.M)) == (target == 'esp32c3') and
         bool(re.search('^#define CONFIG_FREERTOS_UNICORE 1$', compiled, re.M)) == (target == 'esp32c3'),
         'actual and compiled target/core/WDT/IDLE protections')
    recipe = read(group+'/build/flasher_args.json')
    offsets = {int(offset, 0): name for offset, name in recipe['flash_files'].items()}
    flash = members[group+'/qemu-flash.bin']
    need(recipe['flash_settings'] == dict(flash_mode='dio', flash_size='4MB', flash_freq='40m') and
         len(flash) == 4*1024*1024 and set(offsets) ==
         ({4096, 32768, 65536} if target == 'esp32' else {0, 32768, 65536}), 'complete isolated merged image geometry')
    for offset, name in offsets.items():
        name = normalized(name)
        need(contained(name), 'contained image recipe path')
        body = members[group+'/build/'+name]
        need(flash[offset:offset+len(body)] == body, 'every actual build binary present in executed merged image')
    argv = report['commands'][-1]['argv']
    need(argv[argv.index('-smp')+1] == ('2' if target == 'esp32' else '1') and
         argv[argv.index('-M')+1] == ('esp32,audiodev=quiet' if target == 'esp32' else 'esp32c3') and
         argv[argv.index('-display')+1] == 'none' and argv[argv.index('-serial')+1] == 'stdio' and
         argv[argv.index('-drive')+1].endswith('qemu-flash.bin,if=mtd,format=raw') and
         all(flag in argv for flag in ('-snapshot', '-no-reboot')), 'actual isolated native launch arguments')


def source_profiles(evidence):
    group = PROFILE_GROUP
    report = evidence.read(group+'/report.json')
    evidence.sources(group, report, live=True, profile=True)
    names = ['lx6-version', 'lx6-decoder', 'lx6-header', 'rv32-version', 'rv32-decoder', 'rv32-header', 'lint-decoder']
    need(report['completed'] and report['passed'] and report['source_only'] and not report['native_executed'] and
         [row['name'] for row in report['commands']] == names and
         report['lint'] == [dict(unit='decoder', warnings=2, errors=0)], 'honest production-owner source-profile lint scope')
    for row in report['commands']:
        need(row['returncode'] == 0 and not row.get('forced_stop'), 'source-profile child terminal')
        for stream in ('stdout', 'stderr'):
            need(sha(evidence.members[group+'/'+row['name']+'.'+stream+'.log']) == row[stream+'_sha256'],
                 'every profile diagnostic stream retained')
    need(len(report['objects']) == 4 and {row['name'] for row in report['objects']} ==
         {target+'-'+unit+'.o' for target in ('lx6', 'rv32') for unit in ('decoder', 'header')}, 'all four C/C++ source objects')
    for row in report['objects']:
        body = evidence.members[group+'/'+row['name']]
        machine = 94 if row['name'].startswith('lx6-') else 243
        need(sha(body) == row['sha256'] and row['machine'] == machine and elf(body, machine, 1),
             'actual profile ELF32 object and target ABI')
    for name, text in report['stack_records'].items():
        need(evidence.members[group+'/'+name].decode().replace('\r\n', '\n') == text, 'every profile stack record retained')
    need(evidence.members[group+'/clang-tidy.yaml'] == (ROOT/'.clang-tidy').read_bytes(), 'unchanged lint configuration')
    diagnostics = evidence.members[group+'/lint-decoder.stdout.log']+evidence.members[group+'/lint-decoder.stderr.log']
    need(len(re.findall(rb': warning:', diagnostics)) == 2 and not re.search(rb': (?:fatal )?error:', diagnostics) and
         diagnostics.count(b'[bugprone-multi-level-implicit-pointer-conversion]') == 2,
         'both reviewed standard C workspace-pointer warnings retained without new suppressions')
    return dict(commands=7, ELF32_objects=4, warnings=2, errors=0, source_only=True)


def alias_controls(evidence, aliases):
    original = evidence.manifest
    variants = {}
    malformed = json.loads(json.dumps(original))
    malformed['logical_files'][0]['path'] = '../outside'
    variants['traversal'] = malformed
    malformed = json.loads(json.dumps(original))
    malformed['logical_files'].append(dict(malformed['logical_files'][0]))
    variants['duplicate'] = malformed
    malformed = json.loads(json.dumps(original))
    malformed['logical_files'][0]['bytes'] += 1
    variants['size'] = malformed
    malformed = json.loads(json.dumps(original))
    malformed['logical_files'][0]['blob'] = 'blobs/'+'0'*64
    variants['blob'] = malformed
    for label, manifest in variants.items():
        try:
            aliases.resolve_logical_members(evidence.physical, manifest)
        except (ValueError, KeyError):
            continue
        raise ValueError('corrupted logical-member inventory accepted: '+label)
    altered = dict(evidence.physical)
    name = next(name for name, body in altered.items() if body)
    body = altered[name]
    altered[name] = bytes([body[0]^128])+body[1:]
    try:
        aliases.resolve_logical_members(altered, original)
    except ValueError:
        pass
    else:
        raise ValueError('altered actual physical blob accepted')
    extra = dict(evidence.physical)
    extra['blobs/'+'0'*64] = b'unreferenced'
    try:
        aliases.resolve_logical_members(extra, original)
    except ValueError:
        pass
    else:
        raise ValueError('unreferenced physical blob accepted')
    return [*variants, 'altered-physical-bytes', 'unreferenced-physical-blob']


def fixture_lint(evidence):
    results = {}
    for group, expected in LINT_GROUPS.items():
        record = evidence.read(group+'/report.json')
        need(record['completed'] and record['passed'] and
             [row['name'] for row in record['commands']] == expected['commands'] and
             record['source_sha256'] == SOURCE_PINS['tests/native/vorbis_decoder_host.c'],
             'complete fixture-only lint bound to actual qualified source')
        for row in record['commands']:
            diagnostics = evidence.members[group+'/'+row['name']+'.stdout.log']+evidence.members[
                group+'/'+row['name']+'.stderr.log']
            need(row['returncode'] == 0 and row['pid'] > 0 and row['warnings'] == row['generated_warnings'] ==
                 expected['warnings'] and row['errors'] == expected['errors'] == 0 and row['system_suppressed'] == 0 and
                 len(re.findall(rb': warning:', diagnostics)) == expected['warnings'] and
                 not re.search(rb': (?:fatal )?error:', diagnostics) and
                 row['source_sha256'] == SOURCE_PINS['tests/native/vorbis_decoder_host.c'] and
                 all(flag in row['argv'] for flag in ('-UNDEBUG', '-fno-fast-math', '-ffp-contract=off')),
                 'all seven displayed/generated warnings preserved, without hidden suppression or decoder execution')
        config = evidence.members[group+'/clang-tidy.yaml']
        need(config == (ROOT/'.clang-tidy').read_bytes() and sha(config) == record['config_sha256'],
             'exact shared lint configuration without custom suppressions')
        review = evidence.read(group+'/review.json')
        need(review['errors'] == 0 and review['displayed_warnings'] == review['generated_warnings'] == 7 and
             review['system_suppressed_warnings'] == review['new_suppressions'] == 0 and
             review['byte_snapshot_warnings']['count'] == 5 and review['null_copy_warning']['count'] == 1 and
             review['widening_warning']['count'] == 1, 'honest reviewed snapshot/custom-buffer/bounded-count warning scope')
        results[group] = dict(warnings=7, errors=0, source_only=True, reviewed_warnings=review)
    return results


def corrupt_primary_controls(body, synthesis, model, compare):
    reader = synthesis.Reader(body)
    reader.raw(12+24)
    length = reader.take('Q')
    record_start = reader.at
    records = synthesis.Reader(reader.raw(length))
    pcm_at = None
    while records.at < len(records.body):
        fields = records.take('5IQI5IqQ')
        if fields[-1] and pcm_at is None: pcm_at = record_start+records.at
        records.raw(fields[-1]*2)
    need(pcm_at is not None, 'actual nonempty PCM corruption witness')
    variants = {'magic': body[:1]+bytes([body[1]^128])+body[2:],
        'format': body[:16]+bytes([body[16]^128])+body[17:],
        'timing': body[:record_start+52]+bytes([body[record_start+52]^128])+body[record_start+53:],
        'PCM': body[:pcm_at+1]+bytes([body[pcm_at+1]^128])+body[pcm_at+2:],
        'truncated': body[:-1], 'trailing': body+b'X'}
    for label, corrupted in variants.items():
        need(corrupted != body, 'actual altered capture control')
        try:
            result = compare(corrupted)
        except (ValueError, struct.error, UnicodeError):
            continue
        if result.get('passed') is False:
            continue
        raise ValueError('corrupted primary capture accepted: '+label)
    return list(variants)


def replay_decoder_controls(host, evidence, report, model, spans, modules, references, xiph):
    group = FINAL_HOST
    synthesis = modules['test-vorbis-synthesis.py']
    timing = modules['test-vorbis-timing.py']
    members = evidence.members
    capture = members[group+'/capture.bin']
    controls = members[group+'/controls.bin']
    supplements = host.supplementary(modules)
    need(len(supplements) == 14 and json.loads(members[group+'/sources/supplements.json']) == supplements and
         members[group+'/sources/supplements.json'] == (json.dumps(supplements, indent=2)+'\n').encode(),
         'all thirteen retained mathematical vectors and legal extreme regenerated with pinned live builders')
    encoded = host.encode(model, supplements, synthesis)
    need(members[group+'/input.bin'] == encoded and len(encoded) == 16595 and
         sha(encoded) == report['input_sha256'] and report['supplement_count'] == 14 and
         report['raw_API_input_bytes'] == 7376 and report['retained_comment_bytes'] == 1798 and
         report['original31_sha256'] == ORIGINAL_SHA and report['previous_PCM_sha256'] == PCM_SHA,
         'complete actual raw-owner input recipe without captured gain/transform/PCM input')
    primary, allocation_totals = host.primary_parts(capture, model)
    need(all(primary[index][packet] == spans[index, packet] for index in range(31) for packet in range(14)) and
         [list(row) for row in allocation_totals] == report['allocation_totals'],
         'all actual primary PCM spans and complete allocator totals')
    qualified = host.compare_controls(controls, model, supplements, primary, timing)
    normalized_controls = dict(qualified, allocation_baselines=[dict(open=list(row['open']),
        packets=[list(requests) for requests in row['packets']]) for row in qualified['allocation_baselines']])
    need(normalized_controls == report['owner_controls'] and qualified['passed'] and
         all(qualified[key] == value for key, value in EXPECTED_HOST_CONTROLS.items()) and
         len(qualified['allocation_baselines']) == 31 and len(qualified['events']) == 1515 and
         sum(qualified['event_counts']) == len(qualified['events']) and
         qualified['full_recovery_PCM_compared'] and qualified['no_zero_sized_callback'] and qualified['no_null_release'],
         'every actual allocation ordinal, committed-info snapshot, recovery PCM byte and balanced cleanup')
    need(qualified['extreme'] == dict(channels=255, short=8192, long=8192, bounded_budget=1048576,
         bounded_status=-4, large_peak_payload=25345820, samples=1044480) and
         len(qualified['numeric_routes']) == 13 and all(actual['id'] == wanted['id'] and
         actual['status'] == wanted['expected_status'] for actual, wanted in zip(qualified['numeric_routes'], supplements)),
         'honest typed mathematical routes, actual 8355840-byte refusal, and every legal-extreme interleaved zero sample')
    need(sha(capture) == report['capture_sha256'] and sha(controls) == report['controls_sha256'] and
         report['sanitizers'] == ['address', 'undefined'] and not members[group+'/execute.stderr.log'] and
         not report['production_selected'] and not report['private_decoder_executed'], 'instrumented actual public-owner scope')
    summary = dict(open=589, replace=589, process=302, undersized=1212, measures=14187, other=265, checks=17082734)
    need(report['terminal_summary'] == summary and summary['checks'] == qualified['checks']+15 and
         members[group+'/execute.stdout.log'].decode().strip() ==
         'DECODER_CAPTURE cases=31 packets=434 pcm_bytes=738560 open={open} replace={replace} process={process} '
         'undersized={undersized} measures={measures} other={other} checks={checks} live=0 bytes=0'.format(**summary),
         'actual terminal assertions equal binary snapshot plus fifteen final serialization/close assertions')
    need([row['name'] for row in report['commands']] == ['compiler-version', 'compile', 'execute'],
         'complete actual host compilation and instrumented runtime sequence')
    argv = report['commands'][1]['child_argv']
    need(all(flag in argv for flag in ('-UNDEBUG', '-fno-fast-math', '-ffp-contract=off', '-Wall', '-Wextra', '-Werror',
         '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-omit-frame-pointer')),
         'all host translation units instrumented with assertions and unchanged rounding assumptions')
    expected_units = [name for name in report['sources'] if name.endswith('.c') and
                      name.startswith(('components/', 'native/'))]
    compiled_units = [normalized(value) for value in argv if value.endswith('.c')]
    need(len(expected_units) == len(compiled_units) == 22 and all(
         sum(path.endswith('/sources/'+name) for path in compiled_units) == 1 for name in expected_units),
         'all and only twenty-two actual public components and fixture compilation units')
    evidence.artifact(group, 'decoder', report['binary_sha256'])
    corrupt = host.corruption_controls(capture, controls, model, supplements, synthesis, references, xiph, timing)
    need(corrupt == report['corruption_controls'] and len(corrupt) == 8 and all(row['rejected'] for row in corrupt),
         'all eight frozen host corrupted-primary/control refusals independently replayed')

    # Decode actual event bytes again to bind the two HTTP-EOF recovery outputs
    # to independently qualified packet13, and locate nonempty recovery corruption.
    reader = host.Reader(controls)
    need(reader.take('8s') == b'VDECCTL1' and reader.take('I') == 31, 'actual lifecycle control format')
    for index in range(31):
        need(reader.take('I') == index, 'all allocation-baseline identities')
        reader.raw(reader.take('Q')*8)
        need(reader.take('I') == 14, 'every packet-allocation inventory')
        for packet in range(14): reader.raw(reader.take('Q')*8)
    need(reader.take('Q') == 1515, 'all actual lifecycle and allocation events')
    first_event = reader.at
    first_pcm = None
    for index in range(1515):
        kind, stream, packet, ordinal, size = reader.take('3I2Q')
        reader.raw(112)
        count = reader.take('I')
        for piece in range(count):
            actual_stream, actual_packet, length = reader.take('3I')
            if length and first_pcm is None: first_pcm = reader.at
            body = reader.raw(length)
            if kind == 7:
                need((actual_stream, actual_packet) == (0, 13) and body == primary[0][13],
                     'both real HTTP-EOF recovery spans equal the independent original last-packet PCM')
        reader.raw(32)
    need(first_pcm is not None, 'nonempty actual recovery-PCM corruption witness')
    corrupt_offsets = {'lifecycle-ordinal': first_event+12, 'committed-info': first_event+28,
                       'actual-recovery-PCM': first_pcm+1}
    for label, at in corrupt_offsets.items():
        bad = controls[:at]+bytes([controls[at]^128])+controls[at+1:]
        try:
            host.compare_controls(bad, model, supplements, primary, timing)
        except (ValueError, struct.error, IndexError, OverflowError):
            continue
        raise ValueError('altered actual lifecycle capture accepted: '+label)
    return {key: value for key, value in qualified.items() if key not in ('allocation_baselines', 'events')} | \
        dict(corruption_controls=corrupt, extra_actual_control_corruptions=list(corrupt_offsets),
             HTTP_EOF_PCM_also_equals_primary=True)


def replay_native(native, evidence, group, target, report, model, references, xiph, saved, primary):
    members = evidence.members
    need(members[group+'/original31.json'] == members[FINAL_HOST+'/sources/original31.json'] and
         members[group+'/saved-Xiph-PCM.bin'] == saved and
         sha(saved) == report['saved_Xiph_capture_sha256'] and
         members[group+'/transport.json'] == native.transport_bytes(model) and
         members[group+'/resource.json'] == native.resource_bytes() and
         members[group+'/cases.h'] == native.header(model) and
         sha(members[group+'/cases.h']) == report['cases_header_sha256'] and
         report['transport_sha256'] == sha(members[group+'/transport.json']) and
         report['resource_sha256'] == sha(members[group+'/resource.json']),
         'compiled raw packet bytes, literal transport metadata and legal resource vector regenerated exactly')
    supplements_body = members[FINAL_HOST+'/sources/supplements.json']
    supplements = json.loads(supplements_body)
    resource = json.loads(members[group+'/resource.json'])
    need(resource['source_sha256'] == sha(supplements_body) and
         resource['builder_sha256'] == PINS['test-vorbis-decoder.py'] and all(
         supplements[13][name] == value for name, value in resource['row'].items()),
         'native resource headers have independent host-builder and original preflight lineage')
    need(report['reference_controller_sha256'] == native.REFERENCE_CONTROLLER_SHA == PINS['test-vorbis-synthesis-qemu.py'] and
         report['original_sha256'] == ORIGINAL_SHA and report['max_abs_error_bound'] == 2 and
         report['original_archive_sha256'] == native.ORIGINAL_ARCHIVE_SHA and
         report['reference_archive_sha256'] == native.REFERENCE_ARCHIVE_SHA and
         report['direct_public_APIs'] == ['replace', 'measure', 'process', 'info', 'reset', 'clear'] and
         report['runtime_profile'] == dict(coordinator_core=0, worker_core=1 if target == 'esp32' else 0,
             worker_priority=3, worker_stack_bytes=16384, watchdog_enabled=True, idle_watchdog_enabled=True),
         'new persistent API execution and unchanged affinity/priority/stack/watchdog profile')
    for name, body in list(members.items()):
        prefix = group+'/sources/project/'
        if name.startswith(prefix):
            need(members[group+'/project/'+name.removeprefix(prefix)] == body,
                 'every compiled project source equals its executed frozen source')
    need(members[group+'/project/main/cases.h'] == members[group+'/cases.h'], 'compiled generated raw header identity')
    need(members[group+'/project/sdkconfig.defaults'] ==
         members[group+'/sources/project/sdkconfig.'+target+'.defaults'], 'actual target SDK defaults equal frozen project profile')
    for row in model['cases']:
        need(members[group+'/reference/'+PurePosixPath(row['reference_path']).name] == references[row['id']],
             'complete preserved native original-reference bytes')
    log = (members[group+'/qemu.stdout.log'].decode('utf-8', errors='replace')+'\n'+
           members[group+'/qemu.stderr.log'].decode('utf-8', errors='replace')).replace('\r\n', '\n')
    actual = native.validate_log(log, model, references, xiph, target, output=None)
    need(actual == evidence.read(group+'/measurement.json') and
         sha(members[group+'/measurement.json']) == report['measurement_sha256'] and
         {key: value for key, value in actual.items() if key != 'rows'} == report['measurements'] and
         actual['passed'] and actual['pcm_sha256'] == PCM_SHA and actual['cases'] == 31 and actual['packets'] == 434 and
         actual['pcm_bytes'] == 738560 and actual['relations'] == 14 and actual['capacity_refusals'] == 434 and
         actual['terminal_refusals'] == 62 and actual['no_allocation_resets'] == 31 and
         actual['warm_packet_retries'] == 62 and actual['balanced_clears'] == 31 and
         actual['protocol_lines'] == 4536 and
         actual['warm_PCM_compared_by_memcmp'] and actual['caller_PCM_payload_accounted_separately'],
         'every actual native packet/lifecycle/allocator event and both-reference sample comparison replayed')
    large = actual['large_resource_control']
    need(large['failed_bytes'] == 8355840 and large['status'] == -4 and large['failures'] == 1 and
         large['attempts'] == 7 and large['allocations'] == 6 and large['peak_bytes'] == 34500 and
         large['attempts'] == large['allocations']+1 and large['allocations'] == large['releases'] and
         large['live'] == large['bytes'] == 0 and large['handle_null'] == 1 and
         large['recovered_by_complete_original31'] and not large['allocator_budget_used'],
         'actual native malloc refusal at legal history size and subsequent complete-corpus recovery')
    protocol = native.protocol_controls(model, references, target)
    need(protocol == report['protocol_controls'] == dict(valid_full_corpus=True, malformed_refused=24,
         synthetic_protocol_reference_only=True, lifecycle_controls=True), 'all twenty-four strict malformed transcript controls')

    # Independently re-expand each actual UART chunk. The per-case digest is
    # supplementary: actual bytes must equal both preserved files and host PCM.
    parts = {(index, packet): bytearray() for index in range(31) for packet in range(14)}
    for line in log.splitlines():
        if not line.startswith('DEC_PCM '): continue
        fields = dict(token.split('=', 1) for token in line.split()[1:])
        identity = int(fields['row']), int(fields['packet'])
        need(identity in parts and int(fields['start']) == len(parts[identity])//2, 'contiguous actual UART sample spans')
        words = []
        for run in fields['runs'].split(','):
            match = re.fullmatch('([0-9a-f]{4}):([1-9][0-9]*)', run)
            need(match is not None, 'literal independently expanded native RLE')
            count = int(match[2])
            need(0 < count <= 128-len(words), 'bounded complete native chunk expansion')
            words.extend([int(match[1], 16)]*count)
        need(len(words) == int(fields['count']), 'every actual UART word retained')
        parts[identity].extend(struct.pack('<'+'H'*len(words), *words))
    bodies = {}
    for index, row in enumerate(model['cases']):
        body = b''.join(bytes(parts[index, packet]) for packet in range(14))
        preserved = members[group+f'/pcm/{index:02}-'+row['id']+'.s16le']
        need(body == preserved == primary[row['id']] and len(body) == row['pcm_bytes'] and
             sha(body) == actual['rows'][index]['pcm_sha256'],
             'every expanded native PCM byte equals the actual retained host and native PCM')
        bodies[row['id']] = body
    bounds = compare_all_pcm(bodies, model, references, xiph)
    return dict(measurements={key: value for key, value in actual.items() if key != 'rows'}, bounds=bounds,
                protocol_controls=protocol, actual_expanded_PCM_equals_host=True,
                warm_verification='Actual fixture full PCM memcmp and semantic result equality; FNV supplementary, no retry retransmission claim')


def check_seals(evidence, report):
    for path, pin in SEALS.items():
        body = evidence.members[path]
        need(sha(body) == pin, 'pinned artifact-only terminal/source/capture seal')
        seal = json.loads(body)
        if path.endswith('vorbis-decoder-host-final-seal-20261028-01.json'):
            need(seal['passed'] and seal['all_sources_frozen_and_live_unchanged'] and seal['all_owned_processes_terminal'] and
                 seal['source_sha256'] == report['sources'] and seal['input_sha256'] == report['input_sha256'] and
                 seal['capture_sha256'] == report['capture_sha256'] and seal['controls_sha256'] == report['controls_sha256'] and
                 seal['terminal_summary'] == report['terminal_summary'] and
                 seal['corruption_controls'] == report['corruption_controls'] and
                 seal['lint_review'] == evidence.read('fixture-lint-20261028-01/review.json'),
                 'host artifact seal binds existing data/source/terminal observations without a rerun')
            need(len(seal['files']) == 492 and len({row['path'] for row in seal['files']}) == 492,
                 'complete original host seal file inventory')
            for row in seal['files']:
                relative = row['path'].removeprefix('.build/vorbis-decoder-')
                need(relative != row['path'] and contained(relative), 'sealed host file maps to exact packaged group')
                if relative in evidence.members:
                    content = evidence.members[relative]
                    need(len(content) == row['bytes'] and sha(content) == row['sha256'], 'every actual host sealed byte retained')
                else:
                    need(relative in evidence.omitted and evidence.omitted[relative]['bytes'] == row['bytes'] and
                         evidence.omitted[relative]['sha256'] == row['sha256'], 'sealed executable omission remains explicitly identified')
        elif path.endswith('vorbis-decoder-native-final-seal-20261028-01.json'):
            need(seal['schema'] == 'vorbis-decoder-native-final-seal-v1' and seal['passed'] and seal['artifact_only'] and
                 not seal['archived_code_executed'] and not seal['compiler_or_QEMU_repeated'] and
                 seal['all_owned_handles_terminal'] and seal['every_original_packet_host_ESP32_C3_byte_equal'] and
                 (seal['cases'], seal['packets'], seal['pcm_bytes'], seal['pcm_sha256']) == (31, 434, 738560, PCM_SHA),
                 'artifact-only terminal native seal with complete byte equality and honest execution scope')
            need(seal['qualified_source_pins'] == {
                 'tests/test-vorbis-decoder-qemu.py': PINS['test-vorbis-decoder-qemu.py'],
                 'idf/components/native_vorbis_decoder/decoder.c': SOURCE_PINS['idf/components/native_vorbis_decoder/decoder.c'],
                 'tests/target/vorbis_decoder_qemu/main/main.c': SOURCE_PINS['tests/target/vorbis_decoder_qemu/main/main.c']} and
                 seal['host']['report_sha256'] == sha(evidence.members[FINAL_HOST+'/report.json']) and
                 seal['host']['capture_sha256'] == report['capture_sha256'], 'native seal binds executed owner/fixture/controller and host')
            for target, actual in seal['groups'].items():
                group = actual['path'].removeprefix('.build/vorbis-decoder-')
                need(NATIVE_GOOD[group] == target and actual['terminal_exit'] == 0,
                     'native seal maps both actual terminal target groups')
                native_report = evidence.read(group+'/report.json')
                measurement = evidence.read(group+'/measurement.json')
                need(actual['report_sha256'] == sha(evidence.members[group+'/report.json']) and
                     actual['measurement_sha256'] == native_report['measurement_sha256'] and
                     actual['source_count'] == evidence.live_source_counts[group]['snapshots'] == 79 and
                     actual['strict_live_source_count'] == evidence.live_source_counts[group]['strict'] == 66 and
                     actual['compile_rows'] == len(actual['own_objects']) == 22 and
                     actual['all_reported_build_outputs'] == len(native_report['build_outputs']) and
                     actual['all_reported_object_outputs'] == EXPECTED_NATIVE[target]['all_objects'] and
                     actual['binary_and_configuration_hashes_unchanged'] and actual['source_snapshots_unchanged'] and
                     actual['measurements'] == native_report['measurements'] and
                     actual['resource'] == measurement['large_resource_control'] and
                     actual['sdk_child_pid'] == native_report['sdk_child']['pid'] and actual['sdk_child_exit'] == 0,
                     'native artifact seal repeats actual source/object/image/config/receipt measurements')
                own = {}
                for row in native_report['compile_rows']:
                    name = 'build/'+normalized(row['output']).rsplit('/build/', 1)[-1]
                    own[name] = sha(evidence.members[group+'/'+name])
                need(own == actual['own_objects'] and actual['tools'] ==
                     {name: tool['sha256'] for name, tool in native_report['tools'].items()},
                     'every sealed native object and installed tool identity matches executed report')
                need(actual['commands'] == [{key: row[key] for key in
                     ('name', 'state', 'pid', 'exit_status', 'elapsed_seconds')} for row in native_report['commands']],
                     'every sealed native command process is the retained terminal child')
                for index, row in enumerate(actual['percase']):
                    metric = measurement['rows'][index]
                    need(row['id'] == metric['id'] and row['bytes'] == metric['pcm_bytes'] and
                         row['sha256'] == metric['pcm_sha256'] and row['every_host_packet_equal'],
                         'native seal per-case output identities and full packet comparison')
            for actual in seal['failed_attempts'].values():
                group = actual['path'].removeprefix('.build/vorbis-decoder-')
                need(group in NATIVE_FAILED and actual['terminal_exit'] == 1 and actual['reason'] == 'WinError623' and
                     actual['report_sha256'] == sha(evidence.members[group+'/report.json']),
                     'native artifact seal preserves both failed activation attempts')
            protocol = seal['protocol']
            group = protocol['path'].removeprefix('.build/vorbis-decoder-')
            need(group in PROTOCOL_STATES and protocol['terminal_exit'] == 0 and
                 protocol['controls'] == PROTOCOL_STATES[group]['controls'] and
                 protocol['report_sha256'] == sha(evidence.members[group+'/report.json']),
                 'native artifact seal preserves the synthetic-only protocol campaign')


def verify():
    helper, modules = load_readers()
    evidence = Evidence(helper, modules['verify-vorbis-pcm-exact-checkpoint.py'])
    malformed_aliases = alias_controls(evidence, modules['verify-vorbis-pcm-exact-checkpoint.py'])
    synthesis = modules['test-vorbis-synthesis.py']
    timing = modules['test-vorbis-timing.py']
    host = modules['test-vorbis-decoder.py']
    native = modules['test-vorbis-decoder-qemu.py']
    original, model, references, xiph, saved = synthesis.original_data()
    need(sha(original) == ORIGINAL_SHA and len(model['cases']) == 31 and len(model['relations']) == 14 and
         model['policy']['max_abs_error'] == synthesis.BOUND == 2, 'unchanged complete raw31/two-reference/bound2 contract')
    report, capture = helper.clean_host(evidence.members, FINAL_HOST)
    evidence.sources(FINAL_HOST, report, live=True)
    evidence.host_commands(FINAL_HOST, report, successful=True)
    need(evidence.members[FINAL_HOST+'/sources/original31.json'] == original and
         evidence.members[FINAL_HOST+'/sources/saved-Xiph-PCM.bin'] == saved, 'both preserved reference data lineages')
    for index, row in enumerate(model['cases']):
        need(evidence.members[FINAL_HOST+f'/sources/reference/{index:02}.s16le'] == references[row['id']],
             'every retained original generated-vector reference byte')
    measured = synthesis.compare(capture, model, references, xiph, timing)
    need(measured['passed'] and measured['streams'] == 31 and measured['packets'] == 434 and
         measured['pcm_bytes'] == 738560 and measured['fixed_S16_bound'] == 2 and
         measured['max_abs_error'] <= 2 and measured['max_xiph_abs_error'] <= 2 and
         len(measured['relations']) == 14 and all(row['passed'] for row in measured['relations']), 'all actual host PCM samples')
    primary, spans = primary_pcm(capture, synthesis, model)
    bounds = compare_all_pcm(primary, model, references, xiph)
    need(measured == report['measurements'], 'complete host numerical measurement reproduced')
    controls = replay_decoder_controls(host, evidence, report, model, spans, modules, references, xiph)
    corruptions = corrupt_primary_controls(capture, synthesis, model,
        lambda body: synthesis.compare(body, model, references, xiph, timing))
    native_results = {}
    for group, target in NATIVE_GOOD.items():
        record = evidence.read(group+'/report.json')
        evidence.sources(group, record, live=True, target=True)
        native_build(evidence, group, record, target, native)
        native_results[target] = replay_native(native, evidence, group, target, record, model, references, xiph, saved, primary)
    histories = {}
    for group, expected in HOST_STATES.items():
        old = evidence.read(group+'/report.json')
        actual = dict(completed=old['completed'], passed=old['passed'], commands=len(old['commands']))
        need(actual == expected, 'every honest host attempt retained')
        evidence.sources(group, old)
        evidence.host_commands(group, old, successful=old['passed'])
        if old.get('capture_sha256'):
            need(sha(evidence.members[group+'/capture.bin']) == old['capture_sha256'], 'historical capture identity')
        if group in HOST_ERRORS:
            need(old['error'] == HOST_ERRORS[group] and 'execute' not in [row['name'] for row in old['commands']],
                 'activation/compiler failure retained before any decoder runtime')
            if group.endswith('-02'):
                diagnostics = evidence.members[group+'/compile.stdout.log']+evidence.members[group+'/compile.stderr.log']
                need(b'misleading-indentation' in diagnostics and old['commands'][-1]['supervisor']['child_returncode'] != 0,
                     'original strict fixture indentation compile error remains an explicit failed attempt')
        histories[group] = actual
    for group in PREFLIGHT_GROUPS:
        old = evidence.read(group+'/report.json')
        evidence.sources(group, old)
        need(old['preflight_only'] and not old['completed'] and not old['passed'] and not old['commands'] and
             evidence.members[group+'/input.bin'] == evidence.members[FINAL_HOST+'/input.bin'] and
             evidence.members[group+'/sources/supplements.json'] == evidence.members[FINAL_HOST+'/sources/supplements.json'],
             'pure preflight history retains complete unchanged data without claiming decoder execution')
        histories[group] = dict(preflight_only=True, commands=0)
    for group, expected in NATIVE_FAILED.items():
        old = evidence.read(group+'/report.json')
        need(not old['completed'] and not old['passed'] and old['target'] == expected['target'], 'native failure preserved')
        evidence.sources(group, old, target=True)
        evidence.native_commands(group, old, successful=False)
        need(old.get('error') == expected['error'] and not old['target_executed'] and
             [row['name'] for row in old['commands']] == ['sdk-head', 'sdk-clean', 'build'] and
             'sdk_child' not in old and group+'/sdk-child.json' not in evidence.members and
             b'WinError 623' in evidence.members[group+'/build.stderr.log'],
             'installed-runtime activation failure retained before compiler child or native execution')
        histories[group] = dict(completed=False, passed=False, commands=len(old['commands']))
    for group, expected in PROTOCOL_STATES.items():
        old = evidence.read(group+'/report.json')
        need(old['completed'] and not old['passed'] and old['protocol_only'] and old['target'] == expected['target'] and
             not old['target_executed'] and not old['commands'] and old['protocol_controls'] == expected['controls'],
             'every historical pure protocol attempt retained')
        histories[group] = expected
    profiles = source_profiles(evidence)
    lint = fixture_lint(evidence)
    # Final fixture lint and artifact-only seal schemas are pinned after root
    # packaging. Their presence cannot substitute for the sample/event checks.
    need(LINT_GROUPS and SEALS, 'final fixture-lint and artifact-only seal schema not yet supplied')
    check_seals(evidence, report)
    return dict(passed=True, host=measured, controls=controls, native=native_results, histories=histories,
        bounds=bounds, malformed_primary_controls=corruptions, profiles=profiles, fixture_lint=lint,
        malformed_alias_controls=malformed_aliases,
        PCM_sha256=PCM_SHA, archived_code_executed=False, commands_reexecuted=0,
        SDK_reexecuted=False, QEMU_reexecuted=False, files_extracted=False,
        physical_device=False, production_selected=False, universal_codec_qualified=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if args.report:
        need(args.report.resolve().is_relative_to(ROOT/'.build') and not args.report.exists(),
             'fresh report within task-local .build required')
    result = verify()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(result))
