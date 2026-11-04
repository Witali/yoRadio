"""Data-only authentication of an isolated recorded SDK/QEMU memory probe."""
import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile

sys.dont_write_bytecode = True
from parse_measurements import parse

FOLDER = Path(__file__).resolve().parent
ROOT = FOLDER.parents[2]
SDK = '7101770dc6db2667b3c477cc31365dd1acd6db4e'
CURRENT_REPORT = 'c6c3747da732c8573512d024a27758ab62f7760ae44bbedca9b05751655ff7db'
QEMU = '4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d'
HELPER = '8b3c80edffd3298e2ccd1816fe20aa1cf6cbf30c367aad7035448f35ce868b6b'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def relative(name):
    path = PurePosixPath(name)
    need(not path.is_absolute() and '..' not in path.parts and path.parts and
         name == path.as_posix(), 'contained logical record')
    return path


def parser_functions(body):
    tree = ast.parse(body)
    return {node.name:ast.dump(node, include_attributes=False)
        for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in ('fields','parse')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-current', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((FOLDER/'manifest.json').read_bytes())
    need(manifest['scope'] == dict(actual_isolated_SDK_QEMU=True,
        public_word_allocation_and_integer_access=True, allocated_code_executed=False,
        decoder_qualified=False, full_application_fit_qualified=False,
        physical_hardware_qualified=False, RF_qualified=False, extra_RAM_from_aliases=False), 'bounded memory-only scope')
    need({path.name for path in FOLDER.iterdir()} ==
         {'README.md','verify.py','parse_measurements.py','manifest.json','captures.zip'}, 'complete package census')
    pin = manifest['archive']
    archive = FOLDER/pin['path']
    need(archive.name == 'captures.zip' and archive.stat().st_size == pin['bytes'] and
         sha(archive.read_bytes()) == pin['sha256'], 'exact inspected text archive')
    blobs = {}
    with zipfile.ZipFile(archive) as container:
        need(len(container.infolist()) == pin['physical_blobs'], 'physical text census')
        for member in container.infolist():
            body = container.read(member)
            need(member.filename == 'blobs/'+sha(body) and member.filename not in blobs and
                 b'\0' not in body and not body.startswith((b'MZ',b'\x7fELF',b'!<arch>\n')),
                 'unique text-only physical payload')
            body.decode('utf-8')
            blobs[member.filename] = body
    rows = manifest['files']
    need(len(rows) == len({row['path'] for row in rows}) and
         {row['blob'] for row in rows} == set(blobs), 'all logical records accounted for')
    data = {}
    origins = {}
    for row in rows:
        name = row['path']
        path = relative(name)
        body = blobs[row['blob']]
        need(path.suffix.lower() not in {'.a','.bin','.elf','.exe','.o','.obj','.pcm','.pyc','.zip'} and
             len(body) == row['bytes'] and sha(body) == row['sha256'], 'exact retained logical record')
        need(row['original_path'] not in origins, 'unique original provenance')
        data[name] = body
        origins[row['original_path']] = row
    omissions = manifest['omitted_local_files']
    omitted = {row['original_path']:row for row in omissions}
    need(len(omitted) == len(omissions) and not set(omitted) & set(origins), 'unique whole-file omissions')
    need(all(row['original_retained_locally'] and row['byte_payload_published'] is False and
             row['bytes'] >= 0 and len(row['sha256']) == 64 for row in omissions), 'whole originals retained locally')

    def take(name):
        need(name in data, 'required published data '+name)
        return data[name]

    def locator(name):
        name = name.replace('\\','/')
        prefix = manifest['original_execution_root']+'/'
        return name[len(prefix):] if name.startswith(prefix) else name

    def identity(original, digest, size=None):
        name = locator(original)
        need(name in origins or name in omitted, 'original identity accounted for')
        row = origins.get(name, omitted.get(name))
        need(row['sha256'] == digest and (size is None or row['bytes'] == size), 'recorded original identity')
        return row

    captures = {row['label']:row for row in manifest['captures']}
    need(set(captures) == {'current','original01'}, 'current and original native outcomes retained')
    reports = {}
    bundles = {}
    source_maps = {}
    for label, capture in captures.items():
        report = json.loads(take(capture['report']))
        bundle = json.loads(take(label+'/execution-bundle.json'))
        sources = json.loads(take(label+'/source-manifest.json'))
        reports[label] = report
        bundles[label] = bundle
        source_maps[label] = sources
        need(bundle['sdk_commit'] == SDK and bundle['sources'] == sources and
             len(sources) == capture['source_count'] and len(bundle['runtime']) == capture['runtime_count'],
             'exact frozen source/runtime graph')
        need(('PASS' if report['passed'] else 'NONPASS') == capture['status'] and
             report['target_executed'] and not report['physical_device'] and not report['external_network'] and
             not report['private_heap_state'] and not report['decoder'] and not report['production_firmware'] and
             not report['application_memory_qualified'] and not report['extra_RAM_inferred'], 'honest original target scope')
        need(report['all_bound_inputs_current'] and not report['bound_input_failures'], 'terminal frozen input-integrity result')
        for original, row in sources.items():
            identity(capture['original_root']+'/'+row['snapshot'], row['sha256'], row['bytes'])
        for original, digest in bundle['runtime'].items():
            identity(original, digest)
        for name, digest in bundle['artifacts'].items():
            identity(capture['original_root']+'/'+name, digest)
        for command in report['commands']:
            need(command['state'] == 'complete' and command['pid'] > 0 and command['exit_status'] == 0 and
                 not command.get('timed_out'), 'actual authoritative terminal SDK/QEMU/tool commands')
            for stream in ('stdout','stderr'):
                identity(capture['original_root']+'/'+command['name']+'.'+stream+'.log', command[stream+'_sha256'])
        commands = {row['name']:row for row in report['commands']}
        need(commands['build']['timeout_seconds'] == 1200 and commands['qemu']['timeout_seconds'] == 120,
             'unchanged diagnostic deadlines')
        child = json.loads(take(label+'/sdk-child.json').decode('utf-8-sig'))
        need(child['pid'] > 0 and child['exit_status'] == 0, 'actual SDK child terminal status')
        need(take(label+'/sdk-head.stdout.log').decode().strip() == SDK and
             not take(label+'/sdk-clean.stdout.log'), 'pinned clean actual SDK before execution')
        qemu = commands['qemu']['argv']
        need(qemu[qemu.index('-smp')+1] == '2' and qemu[qemu.index('-nic')+1] == 'none' and
             '-no-reboot' in qemu and '-snapshot' in qemu and
             qemu[qemu.index('-drive')+1].replace('\\','/').endswith('/qemu-flash.bin,if=mtd,format=raw'),
             'actual isolated dual-core image invocation')
        runtime_qemu = [(name,digest) for name,digest in bundle['runtime'].items() if name.endswith('qemu-system-xtensa.exe')]
        need(len(runtime_qemu) == 1 and runtime_qemu[0][1] == QEMU, 'exact actual QEMU executable identity')
        flash = identity(capture['original_root']+'/qemu-flash.bin', bundle['artifacts']['qemu-flash.bin'], 4194304)
        need(flash['original_path'] in omitted, 'whole diagnostic flash bytes omitted')
        for original in bundle['runtime']:
            if original.lower().endswith(('.exe','.bin')) or original.startswith('runtime-path-redacted:'):
                need(locator(original) in omitted, 'whole runtime executable/ROM bytes omitted')

    current = reports['current']
    need(sha(take('current/report.json')) == CURRENT_REPORT and current['passed'] and current['completed'],
         'exact authoritative passing native report')
    need(take('current/sdk-head-after.stdout.log').decode().strip() == SDK and
         not take('current/sdk-clean-after.stdout.log'), 'actual SDK still pinned and clean after execution')
    recorded = parse(take('current/qemu.stdout.log').decode()+'\n'+take('current/qemu.stderr.log').decode(errors='replace'))
    need(recorded == current['measurements'], 'all actual UART measurements recomputed using recorded semantics')
    need([row['case']['kind'] for row in recorded['cases']] == ['WORDS32','EXEC32'] and
         all(row['case']['allocated'] == row['case']['attempted'] == 8 and row['case']['refused'] == 0 and
             row['pure_iram_requested_bytes'] == 80640 and row['diram_alias_requested_bytes'] == 11520
             for row in recorded['cases']), 'complete recorded allocation cases; aliases counted once')
    need(recorded['probe_initial_pure_IRAM_extent'] == current['probe_map']['pure_iram_initial_extent'],
         'own probe boot and map extents agree')
    mapping = take('current/build/cyd_word_plane_caps_qemu.map').decode()
    end = re.search(r'^\s*(0x[0-9a-f]+)\s+_iram_end\s*=', mapping, re.M)
    need(end is not None and int(end[1],16) == current['probe_map']['iram_end'] and
         max(0,0x400a0000-max(0x40080000,int(end[1],16))) == recorded['probe_initial_pure_IRAM_extent'],
         'actual probe map matches independently parsed boot geometry')
    history = current['historical_native06']
    need(history['pure_iram_initial_extent'] == 80740 and history['initial_allocator_region_not_current_free'] and
         history['does_not_describe_minimal_probe_capacity'], 'older full-task extent remains a different historical image')
    for name in ('whole_console','whole_map'):
        row = history[name]
        identity(row['path'], row['sha256'], row['bytes'])
    need(locator(history['whole_console']['path']) in omitted, 'whole PCM-bearing historical console omitted')

    config = json.loads(take('current/build/config/sdkconfig.json'))
    raw_config = take('current/sdkconfig').decode()
    true_flags = ('HEAP_POISONING_LIGHT','FREERTOS_CHECK_STACKOVERFLOW_CANARY',
        'COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE','ESP_TASK_WDT_EN','ESP_TASK_WDT_INIT','ESP_TASK_WDT_PANIC',
        'ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0','ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1')
    need(config['IDF_TARGET'] == 'esp32' and config['ESP_DEFAULT_CPU_FREQ_MHZ'] == 240 and config['FREERTOS_HZ'] == 1000 and
         config['ESP_TASK_WDT_TIMEOUT_S'] == 20 and all(config.get(key) is True for key in true_flags) and
         not any(config.get(key,False) for key in ('FREERTOS_UNICORE','SPIRAM','ESP32_IRAM_AS_8BIT_ACCESSIBLE_MEMORY',
              'ESP_SYSTEM_ALLOW_RTC_FAST_MEM_AS_HEAP')), 'actual public-capability diagnostic safeguards')
    need(all('CONFIG_'+key+'=y' in raw_config for key in true_flags) and
         'CONFIG_ESP_TASK_WDT_TIMEOUT_S=20' in raw_config, 'bound raw sdkconfig agrees with generated JSON')
    config_sources = [row for path,row in source_maps['current'].items()
        if path.replace('\\','/').endswith('/build/config/sdkconfig.h')]
    need(len(config_sources) == 1, 'actual compiler consumed generated configuration')
    config_header = take('current/'+config_sources[0]['snapshot']).decode()
    need(all('#define CONFIG_'+key+' 1' in config_header for key in true_flags) and
         '#define CONFIG_ESP_TASK_WDT_TIMEOUT_S 20' in config_header, 'consumed configuration header agrees with raw config')
    closure = json.loads(take('current/actual-compiler-closure.json'))
    need(closure['translation_unit']['file'].replace('\\','/').endswith('/sources/harness/project/main/main.c') and
         any(path.replace('\\','/').endswith('/pcm_word_plane.h') for path in closure['actual_dependencies']),
         'actual main translation unit and helper dependency witness')
    assembly = take('current/word-object-disassembly.stdout.log').decode().replace('\r\n','\n')
    need(current['word_helper_assembly']['byte_halfword_FP_access'] is False, 'recorded helper access-width inspection')
    for name, body in current['word_helper_assembly']['functions'].items():
        found = re.search(r'^[0-9a-f]+ <'+name+r'>:\n(.*?)(?=^[0-9a-f]+ <|\Z)', assembly, re.M|re.S)
        need(found is not None and found[1] == body.replace('\r\n','\n') and
             not re.search(r'\b(?:l8ui|l16ui|l16si|s8i|s16i|lsi|ssi|l32f|s32f|float\.s|ufloat\.s)\b', found[1]),
             'actual recorded helper-object integer word operations')

    own_parser = parser_functions((FOLDER/'parse_measurements.py').read_bytes())
    need(set(own_parser) == {'fields','parse'} and
         own_parser == parser_functions(take('current/sources/controller.py')) and
         own_parser == parser_functions(take('reader/reader.py')) and
         sha(take('reader/reader.py')) == sha(take('current/sources/controller.py')),
         'exact frozen pure parser semantics; no captured import')
    reader = json.loads(take(manifest['reader_report']))
    need(reader['passed'] and reader['synthetic_parser_vectors'] and reader['honest_refusal_vector_preserved'] and
         reader['high_DIRAM_query_vector_preserved'] and not reader['SDK_started'] and not reader['QEMU_started'] and
         not reader['native_word_access_qualified'] and reader['rejected_controls'] == len(reader['rejected']) == 26 and
         sha(take('reader/reader.py')) == reader['reader_sha256'], 'unchanged reader26 receipt; synthetic scope only')
    original = reports['original01']
    need(not original['passed'] and not original['completed'] and
         original['failure'] == 'no real access/resource/runtime assertion failure' and
         b'CYD_WORD_FAILURE actual_executable_capability' in take('original01/qemu.stdout.log'), 'original native NONPASS stays NONPASS')
    paused = json.loads(take('original01/paused-state.json'))
    need(paused['controller_exit'] == 1 and paused['native_status'] == 'NONPASS' and
         paused['actual_failure'] == 'actual_executable_capability', 'authoritative original controller failure receipt')

    target = manifest['optional_current_target_helper']
    expected = {'tests/target/cyd_word_plane_caps_qemu/'+name for name in (
        'README.md','sdk-build.ps1','project/CMakeLists.txt','project/partitions.csv',
        'project/sdkconfig.defaults','project/main/CMakeLists.txt','project/main/main.c')}
    expected.add('idf/components/native_stream/include/pcm_word_plane.h')
    need(len(target) == 8 and {row['repository_path'] for row in target} == expected, 'explicit eight target/helper currentness inputs')
    for row in target:
        body = take(row['payload'])
        need(sha(body) == row['sha256'] and len(body) == row['bytes'], 'frozen target/helper input binding')
        if args.require_current:
            path = ROOT/relative(row['repository_path'])
            need(path.resolve().is_relative_to(ROOT) and sha(path.read_bytes()) == row['sha256'], 'current target/helper input')
        if row['repository_path'].endswith('pcm_word_plane.h'):
            need(row['sha256'] == HELPER, 'separately qualified exact helper')
    support = manifest['historical_support_controllers']
    need(len(support) == 2 and {row['repository_path'] for row in support} ==
         {'tests/run-cyd-word-plane-caps-qemu.py','tests/run-cyd-family1-playback-task-qemu.py'} and
         all(row['currentness_claimed'] is False and sha(take(row['payload'])) == row['sha256'] and
             len(take(row['payload'])) == row['bytes'] for row in support), 'complete exact support snapshots remain historical only')
    print(json.dumps(dict(checkpoint_verified=True, optional_target_helper_currentness_required=args.require_current,
        optional_current_inputs=8, support_controller_currentness_claimed=False,
        native_cases=2, allocated_planes_per_case=[8,8], pure_IRAM_requested_bytes_per_case=[80640,80640],
        shared_DIRAM_requested_bytes_per_case=[11520,11520], aliases_counted_once=True,
        exact_public_cleanup=True, synthetic_reader_controls=26, original_native01_status='NONPASS',
        allocated_code_executed=False, full_application_fit_qualified=False,
        physical_hardware_qualified=False, RF_qualified=False, omitted_original_bytes_read=False)))


if __name__ == '__main__':
    main()
