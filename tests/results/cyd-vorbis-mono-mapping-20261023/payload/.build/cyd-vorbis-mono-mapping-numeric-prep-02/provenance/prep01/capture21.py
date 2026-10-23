"""Validate actual complete21 capture/terminal and recover every unmodified raw-channel byte."""
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re

from pcm_metrics import need
from policy21 import CASE_IDS, CHANNELS, CASE_RATES, FRAMES

COMMANDS = ('sdk-head', 'sdk-clean', 'build', 'setup-macros', 'symbols', 'merge', 'qemu', 'sdk-head-after', 'sdk-clean-after')
COUNTS = dict(cases=21, packets=294, expected_pcm_bytes=464640, protocol_events=654,
              case_mask=2097151, arrays=105, full_raw_arrays=63)


def sha(data): return hashlib.sha256(data).hexdigest()


def relative(value):
    path = PurePosixPath(str(value).replace('\\', '/'))
    need(str(value) and not path.is_absolute() and '..' not in path.parts and ':' not in str(path), 'Safe relative path required')
    return path.as_posix()


class Inputs:
    def __init__(self): self.rows = {}

    def read(self, role, path, expected=None, size=None):
        path = Path(path).resolve()
        raw = path.read_bytes()
        row = dict(path=str(path), bytes=len(raw), sha256=sha(raw))
        need(expected is None or row['sha256'] == expected, 'Input SHA mismatch: ' + role)
        need(size is None or row['bytes'] == size, 'Input size mismatch: ' + role)
        need(role not in self.rows or self.rows[role] == row, 'Input role changed: ' + role)
        self.rows[role] = row
        return raw

    def current(self):
        for role, row in self.rows.items():
            raw = Path(row['path']).read_bytes()
            need(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'Input changed: ' + role)


def capture(inputs, args, pins):
    root, repo, runtime = args.target.resolve(), args.repository.resolve(), args.runtime.resolve()
    need(root.parent == runtime.parent == repo / '.build' and root != runtime,
         'Separate direct-child build capture/runtime required')
    actual = pins['actual_capture']
    for role, path, digest in (('target_report', root / 'report.json', args.target_report_sha256),
                               ('target_terminal', args.target_terminal.resolve(), args.target_terminal_sha256),
                               ('runtime_preparation', runtime / 'preparation.json', args.runtime_preparation_sha256)):
        need(path == repo / actual[role]['path'] and digest == actual[role]['sha256'],
             'Reviewed actual CLI path/SHA required:' + role)
    raw_report = inputs.read('target/report', root / 'report.json', args.target_report_sha256)
    report = json.loads(raw_report)
    need(report.get('result') == 'CHECKED_CORPUS_PCM_CAPTURED' and
         all(report.get(k) is True for k in ('completed', 'target_capture_completed', 'checked_decode_completed')) and
         all(report.get(k) is False for k in ('passed', 'vendor_comparison_available', 'vendor_checked_pcm_equal',
             'independent_reference_compared', 'numeric_reference_qualified', 'format_corpus_qualified',
             'full_G6_qualified', 'physical_device', 'production_radio_integration')),
         'Complete actual target capture required; no partial or NONPASS acceptance')
    terminal = json.loads(inputs.read('target/terminal', args.target_terminal, args.target_terminal_sha256))
    need(terminal.get('schema') == 'direct-exec-tool-terminal-v1' and type(terminal.get('exit_code')) is int and
         terminal['exit_code'] == 0 and terminal['report_sha256'] == sha(raw_report) and
         type(terminal.get('session_id')) is int and terminal['session_id'] > 0 and
         type(terminal.get('terminal_chunk_id')) is str and terminal['terminal_chunk_id'] and
         re.fullmatch('[0-9a-f]{64}', terminal['entrypoint_sha256']), 'Actual direct-tool terminal0/report/controller required')
    # No PCM/protocol-log access precedes the actual complete report+terminal gate.
    preparation = json.loads(inputs.read('runtime/preparation', runtime / 'preparation.json', args.runtime_preparation_sha256))
    need(preparation['schema'] == 'mono21-root-materialization-v1' and preparation['completed'] is True and
         preparation['counts'] == COUNTS and preparation['actual_qualification_terminal0_verified'] is True and
         preparation['all_twenty_one_original_bytes_unchanged'] is True and
         all(preparation[k] is False for k in ('target_executed', 'numeric_qualified', 'full_G6_qualified')) and
         preparation['qualification']['sha256'] == pins['reference']['qualification']['sha256'],
         'Actual reviewed complete21 materialization required')
    artifacts = {}
    for name, expected in (('controller', runtime / 'run-cyd-vorbis-mono21-qemu.py'),
                           ('contract', runtime / 'contract.json'), ('header', runtime / 'materialized01/data.h')):
        row = preparation[name]
        need(Path(row['path']).resolve() == expected, 'Runtime artifact path binding:' + name)
        artifacts[name] = inputs.read('runtime/' + name, expected, row['sha256'], row['bytes'])
    need(terminal['entrypoint_sha256'] == preparation['controller']['sha256'], 'Actual terminal entrypoint must equal reviewed runtime controller')
    runtime_pins = json.loads(inputs.read('runtime/source-pins', runtime / 'source-pins.json'))
    need(runtime_pins['reference'] == pins['reference'] and tuple(runtime_pins['expected_case_ids']) == CASE_IDS and
         runtime_pins['qualified_reviewed_report_sha256'] == pins['reference']['qualification']['sha256'] and
         runtime_pins['prior_unrelated_NONPASS_unchanged'] is True, 'Exact existing mono21 reference scope required')
    binding_raw = inputs.read('runtime/binding', runtime / 'reference-binding21.json')
    mapping_raw = inputs.read('runtime/source-map', runtime / 'source-map.json')
    saved = json.loads(artifacts['contract'])
    matrix = runtime / 'inputs/all21/matrix.json'
    matrix_raw = inputs.read('runtime/matrix', matrix, pins['reference']['comparison']['sha256'])
    need(matrix_raw == (repo / pins['reference']['comparison']['path']).read_bytes(), 'Runtime full21 matrix bytes unchanged')
    replacements = {'__FIRST_MATRIX_PATH__': matrix.relative_to(repo).as_posix(), '__FIRST_MATRIX_SHA__': sha(matrix_raw),
        '__REFERENCE_PROOFS__': repr({row['path']: row['sha256'] for row in pins['reference'].values()}),
        '__CONTRACT_ID__': saved['contract_sha256'], '__CONTRACT_FILE_SHA__': sha(artifacts['contract']),
        '__DATA_HEADER_SHA__': sha(artifacts['header']), '__SOURCE_MAP_SHA__': sha(mapping_raw),
        '__REFERENCE_BINDING_SHA__': sha(binding_raw), '__REFERENCE_HELPER_SHA__': pins['runtime_helpers']['reference_binding.py'],
        '__RECORDED_HELPER_SHA__': pins['runtime_helpers']['recorded_qualification.py'],
        '__CARRIER_HELPER_SHA__': pins['runtime_helpers']['carrier.py'],
        '__SOURCE_PINS_SHA__': sha((runtime / 'source-pins.json').read_bytes()),
        '__QUALIFICATION_ROOT__': Path(pins['reference']['qualification']['path']).parent.as_posix(),
        '__CASE_COUNT__': '21', '__TOTAL_PACKETS__': '294', '__TOTAL_PCM__': '464640', '__CASE_MASK__': '2097151', '__PROTOCOL_EVENTS__': '654'}
    template = inputs.read('runtime/reviewed-controller-template', repo / pins['controller_template']['path'],
                           pins['controller_template']['sha256']).decode()
    for marker, value in replacements.items():
        need(marker in template, 'Required controller marker:' + marker)
        template = template.replace(marker, value)
    need(template.encode() == artifacts['controller'], 'Actual controller must exactly equal reviewed source sealed with actual runtime facts')
    for name, digest in pins['runtime_helpers'].items():
        inputs.read('runtime/helper/' + name, runtime / name, digest)
    need(tuple(row['name'] for row in report['commands']) == COMMANDS, 'All nine actual target commands required')
    for row in report['commands']:
        need(row['state'] == 'complete' and type(row['exit_status']) is int and row['exit_status'] == 0 and
             row['timed_out'] is row['interrupted'] is False and type(row['pid']) is int and row['pid'] > 0 and row['argv'] and row['cwd'],
             'Actual target child terminal0/non-timeout facts required')
        for stream in ('stdout', 'stderr'):
            inputs.read('target/log/' + row['name'] + '/' + stream, root / (row['name'] + '.' + stream + '.log'), row[stream + '_sha256'])
    for origin, row in report['inputs'].items():
        inputs.read('target/input/' + relative(row['snapshot']), root / relative(row['snapshot']), row['sha256'], row.get('bytes'))
    for name, path, data in (('controller', 'sources/helpers/run.py', artifacts['controller']),
                             ('contract', 'sources/corpus/contract.json', artifacts['contract']),
                             ('header', 'sources/project/main/data.h', artifacts['header']),
                             ('binding', 'sources/reference/reference-binding21.json', binding_raw),
                             ('source-map', 'sources/corpus/source-map.json', mapping_raw)):
        need(inputs.read('target/frozen-' + name, root / path) == data, 'Actual capture/runtime artifact mismatch:' + name)
    protocol_path = root / 'sources/helpers/protocol.py'
    inputs.read('target/protocol', protocol_path, pins['runtime_helpers']['protocol.py'])
    inputs.read('target/caller', root / 'sources/project/main/main.c', pins['caller_sha256'])
    for role, path in (('candidate-setup', 'sources/candidate/vorbis_repair/setup.c'), ('variant-setup', 'variant/vorbis_repair/setup.c')):
        inputs.read('target/' + role, root / path, pins['setup_sha256'])
    need(report['variant_sources']['variant/vorbis_repair/setup.c'] == pins['setup_sha256'], 'Actual variant setup identity')
    macros = (root / 'setup-macros.stdout.log').read_bytes().decode().replace('\r\n', '\n')
    for pattern in (r'^#define CONFIG_IDF_TARGET_ESP32 1$', r'^#define CONFIG_YORADIO_VORBIS_REPAIR 1$',
                    r'^#define CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ 240$'):
        need(re.search(pattern, macros, re.M), 'Actual ESP32 setup compile context')
    need(not re.search(r'^#define (?:CONFIG_FREERTOS_UNICORE|LIMIT_TO_64kHz)\b', macros, re.M), 'Actual unrestricted two-core profile required')
    relocated = []
    need(len(saved['manifest_inputs']) == 1, 'One complete21 matrix required')
    for item in saved['manifest_inputs']:
        need(Path(item['path']).resolve() == matrix and item['sha256'] == sha(matrix_raw), 'Exact runtime matrix identity')
        row = report['inputs'][str(Path(item['path']).resolve())]
        need(row['sha256'] == item['sha256'], 'Frozen target matrix identity')
        relocated.append(dict(path=str((root / relative(row['snapshot'])).resolve()), sha256=item['sha256']))
    spec = importlib.util.spec_from_file_location('pinned_mono21_numeric_protocol', protocol_path)
    protocol = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(protocol)  # Normal pinned definitions, no target or guarded main.
    contract = protocol.load_contract(relocated)
    model = contract['model']
    for row in contract['source_facts']:
        inputs.read('target/relocated-source/' + row['path'], row['path'], row['sha256'], row['bytes'])
    need(saved['model'] == model and saved['contract_sha256'] == contract['contract_sha256'] and
         tuple(c['id'] for c in model['cases']) == CASE_IDS and tuple(c['channels'] for c in model['cases']) == CHANNELS and
         tuple(c['rate'] for c in model['cases']) == CASE_RATES and all(tuple(c['frames']) == FRAMES for c in model['cases']) and
         (len(model['cases']), model['total_packets'], model['total_pcm'], model['case_mask']) == (21, 294, 464640, 2097151),
         'Exact complete21 channel/rate/frame contract required')
    corpus = report['corpus']
    need(corpus['contract_sha256'] == saved['contract_sha256'] and corpus['contract_file_sha256'] == sha(artifacts['contract']) and
         corpus['data_header_sha256'] == sha(artifacts['header']) and corpus['reference_binding_sha256'] == sha(binding_raw) and
         (corpus['cases'], corpus['packets'], corpus['expected_pcm']) == (21, 294, 464640) and
         corpus['dual_reference_passed'] is True and corpus['dual_reference_scope'] == 'only-existing-mono21-campaign' and
         corpus['previous_unrelated_dual_NONPASS_reinterpreted'] is False, 'Actual report full21 accounting/reference scope')
    qemu = report['commands'][6]
    log = inputs.read('target/qemu-stdout', root / 'qemu.stdout.log', qemu['stdout_sha256']).decode(errors='replace') + '\n' + \
          inputs.read('target/qemu-stderr', root / 'qemu.stderr.log', qemu['stderr_sha256']).decode(errors='replace')
    observed = protocol.validate_log(log, contract, returncode=qemu['exit_status'], timed_out=qemu['timed_out'],
        interrupted=qemu['interrupted'], manifest_hashes=model['manifest_sha256'])
    captured = observed.pop('case_pcm')
    need(observed == report['observed'] and observed['protocol_lines'] == 654 and
         len(captured) == len(report['observed_pcm']) == 21, 'All654 protocol events and21 full PCM streams required')
    paths = set()
    for index, (case, item, row) in enumerate(zip(model['cases'], captured, report['observed_pcm'])):
        name = f"observed-pcm/{index:02d}-{case['id']}.s16le"
        offsets = [0]
        for count in case['pcm']: offsets.append(offsets[-1] + count)
        need(relative(row['path']) == name and row['case'] == item['case'] == index and row['id'] == item['id'] == case['id'] and
             row['sha256'] == item['sha256'] and row['packet_offsets'] == item['packet_offsets'] == offsets and
             row['reference_id'] == '0-' + case['id'] and row['reference_scope'] == 'mono21' and
             row['reference_qualification_sha256'] == pins['reference']['qualification']['sha256'], 'Persisted21 PCM metadata/offset/reference binding')
        value = inputs.read('target/PCM/' + name, root / name, row['sha256'], row['bytes'])
        need(value == item['pcm'] and len(value) == case['total_pcm'] == 7040 * case['channels'] * 2,
             'Every actual raw-channel byte required; no padding/duplication/truncation')
        paths.add(root / name)
    need(set((root / 'observed-pcm').iterdir()) == paths and sum(len(x['pcm']) for x in captured) == 464640,
         'Exact complete21 PCM file set and total')
    return report, contract, captured, json.loads(binding_raw), json.loads(mapping_raw)
