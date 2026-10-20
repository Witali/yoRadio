"""Finalize only ignored Vorbis/Ogg audit evidence, without a build or decoder run."""
import datetime
import hashlib
import json
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parent
ROOT = OUT.parent.parent
CAP = json.loads((OUT / 'capture.json').read_text())
CHECKS = json.loads((OUT / 'analysis-checks.json').read_text())
EXCERPTS = json.loads((OUT / 'excerpt-map.json').read_text())
INVENTORY = json.loads((OUT / 'symbol-inventory.json').read_text())
assert not (OUT / 'report.json').exists()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source(relative, token):
    path = ROOT / relative
    raw = path.read_bytes()
    digest = CHECKS['all_input_sha256'][str(path)]
    assert sha(raw) == digest
    matches = [i for i, line in enumerate(raw.decode().splitlines(), 1) if token in line]
    assert matches, (relative, token)
    return {'path': str(path), 'line': matches[0], 'sha256': digest,
            'link': '[' + relative + '](' + str(path).replace('\\', '/') + ':' + str(matches[0]) + ')'}


def binary(basename, function, offsets):
    label, item = next((label, item) for label, item in CAP['members'].items()
                       if label.startswith('esp32-') and item['member'] == basename)
    archive = CAP['archives']['esp32/' + item['archive']]
    excerpt = EXCERPTS.get('esp32:' + function)
    raw_path = OUT / 'tool-output' / (label + '-disasm.txt')
    lines = raw_path.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line == 'Disassembly of section .text.' + function + ':')
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith('Disassembly of section ')), len(lines))
    instructions = []
    for offset in offsets:
        match = next(((i, line) for i, line in enumerate(lines[start:end], start + 1)
                      if re.match(r'^\s*' + offset.removeprefix('0x') + r':\s+\w+\s+', line)), None)
        assert match, (basename, function, offset)
        number, line = match
        instructions.append({'section_offset': offset, 'line': number, 'instruction': line.strip(),
                             'link': '[' + function + '+' + offset + '](' + str(raw_path).replace('\\', '/') + ':' + str(number) + ')'})
    return {'architecture': 'Xtensa ESP32', 'elf_machine': 94,
            'archive_path': archive['path'], 'archive_sha256': archive['sha256'],
            'member': basename, 'archive_index': item['archive_index'], 'member_sha256': item['sha256'],
            'symbol_or_section': function, 'address_kind': 'section-relative byte offsets, never absolute runtime addresses',
            'disassembly': str(raw_path), 'disassembly_sha256': sha(raw_path.read_bytes()),
            'excerpt': excerpt, 'instructions': instructions}


donor = 'idf/esp32c3-oled-native/main/'
cyd = 'idf/esp32-cyd2usb-native/main/'
findings = [
    {'id': 'V1', 'priority': 'high', 'classification': 'confirmed_binary_control_flow_defect',
     'title': 'Failed Vorbis open reads and frees an already freed wrapper',
     'scenario': 'After wrapper/info allocation succeeds, an invalid or allocation-failed setup header takes the cleanup path. The wrapper pointer remains in a3 after media_lib_free; execution falls through to read a3+0 and later calls media_lib_free on a3 again.',
     'observed': 'esp_vorbis_dec_open +0xf7 clears info, +0xff frees info, +0x109 frees wrapper; +0x10c loads wrapper->dsp from the freed wrapper; +0x12f frees the wrapper again. Symbolic allocator relocations and instructions establish the defect without donor layout assumptions.',
     'evidence': [binary('esp_vorbis_dec.c.obj', 'esp_vorbis_dec_open', ['0xf7', '0xff', '0x109', '0x10c', '0x12f'])],
     'candidate': source(donor + 'vorbis_repair/setup.c', 'esp_audio_err_t __wrap_esp_vorbis_dec_open'),
     'gate': 'Xtensa whole actual archive malformed-header and fail-every-allocation runs: handle stays NULL, exactly one owner frees each allocation, no leaked bytes, later valid open/decode/close works.'},
    {'id': 'V2', 'priority': 'high', 'classification': 'confirmed_binary_control_flow_defect',
     'title': 'Vorbis DSP and setup constructors dereference unchecked allocation results',
     'scenario': 'The first 80-byte DSP allocation fails. The returned NULL is used as the store base immediately. Additional pointer tables/channel buffers and floor constructors also have unchecked paths.',
     'observed': 'vorbis_dsp_create +0xd calls calloc; +0x17 stores the info pointer through its result without a conditional branch. floor0_info_unpack allocates 40 bytes and later stores via its result; floor1_info_unpack allocates 36 and stores partitions at +0x20 without a NULL check.',
     'evidence': [binary('dsp.c.obj', 'vorbis_dsp_create', ['0xd', '0x17', '0x36', '0x52']),
                  binary('floor0.c.obj', 'floor0_info_unpack', ['0xf', '0x1e']),
                  binary('floor1.c.obj', 'floor1_info_unpack', ['0xf', '0x20'])],
     'candidate': source(donor + 'vorbis_repair/setup.c', 'static vorbis_dsp_state *repair_dsp_create'),
     'gate': 'Fresh target OOM sweep must discover the actual Xtensa allocation order including all channels, tables, floors, mappings, books, parser caches, and cleanup after partial construction; donor allocation counts are not target evidence.'},
    {'id': 'V3', 'priority': 'high', 'classification': 'confirmed_binary_control_flow_defect',
     'title': 'Ogg simple open writes through a failed initial calloc',
     'scenario': 'The 48-byte simple state allocation fails during Ogg open.',
     'observed': 'esp_audio_simple_dec_open +0x3d calls calloc, +0x42 copies the result to a3, +0x47 writes the container at a3+44 without any NULL test.',
     'evidence': [binary('esp_audio_simple_dec.c.obj', 'esp_audio_simple_dec_open', ['0x38', '0x3d', '0x42', '0x47'])],
     'candidate': source(donor + 'vorbis_repair/simple.c', 'esp_audio_err_t __wrap_esp_audio_simple_dec_open'),
     'gate': 'Checked Ogg-only initializer with NULL publication until ready; prove original close/reset accepts the extended allocation and parser-open/config/decoder failures release exactly their owned resources. Other simple types must forward unchanged.'},
    {'id': 'V4', 'priority': 'high', 'classification': 'confirmed_binary_call_order_with_runtime_effect_to_qualify',
     'title': 'PCM capacity is checked after Vorbis synthesis mutates history',
     'scenario': 'A valid audio packet is offered with a too-small PCM buffer and the caller resizes then retries the same packet, as current CYD audio_service does.',
     'observed': 'esp_vorbis_dec_decode calls vorbis_dsp_synthesis at +0xab, then computes output bytes from dsp out_begin/out_end/channels and checks output capacity at +0xe9. The insufficient-buffer branch sets needed_size and returns -8. The history mutation follows from the called target synthesis implementation; exact audible corruption is not measured here.',
     'evidence': [binary('esp_vorbis_dec.c.obj', 'esp_vorbis_dec_decode', ['0xab', '0xd9', '0xdd', '0xdf', '0xe9']),
                  binary('dsp.c.obj', 'vorbis_dsp_synthesis', ['0x0'])],
     'candidate': source(donor + 'vorbis_repair/output.c', 'esp_audio_err_t __wrap_esp_vorbis_dec_decode'),
     'current_cyd_entry': source(cyd + 'audio_service.c', 'if (result == ESP_AUDIO_ERR_BUFF_NOT_ENOUGH)'),
     'gate': 'Actual Xtensa raw-packet ample-buffer oracle vs repeated needed_size-1 and then exact-size retries; first priming block, short/long changes, byte-two window flags, EOS trimming. Require consumed=decoded=0 and unchanged history on every rejected retry.'},
    {'id': 'V5', 'priority': 'medium', 'classification': 'confirmed_binary_control_flow_defect',
     'title': 'A second undersized retry drops the retained Ogg packet',
     'scenario': 'The Ogg simple decoder already holds pending_data/pending_bytes after BUFF_NOT_ENOUGH. A retry still returns BUFF_NOT_ENOUGH.',
     'observed': 'esp_audio_simple_dec_process +0xc0 reads pending_bytes, +0xd9 calls decode. Every nonzero result branches +0xde to +0x100; +0x102 stores zero pending_bytes and +0x104 reports the prior pending_consumed. The initial parser-fed -8 branch at +0x21c instead retains these fields. No error-specific exception exists on the retry path.',
     'evidence': [binary('esp_audio_simple_dec.c.obj', 'esp_audio_simple_dec_process', ['0xc0', '0xd9', '0xde', '0x100', '0x102', '0x104', '0x21c', '0x226'])],
     'candidate': source(donor + 'vorbis_repair/simple.c', 'if (result == ESP_AUDIO_ERR_BUFF_NOT_ENOUGH && pending_bytes)'),
     'gate': 'Actual container decode must reject the same pending packet repeatedly, preserve data/bytes/consumed ownership, then produce the exact same PCM as ample buffers without duplicate or missing frames.'},
    {'id': 'V6', 'priority': 'medium', 'classification': 'confirmed_binary_error_propagation_defect',
     'title': 'Ogg allocation failure can be reported as ordinary progress/success',
     'scenario': 'Vorbis identification/setup header realloc fails, or the elementary parser returns ESP_ES_PARSE_ERR_NO_MEM (-3) during Ogg processing.',
     'observed': 'parse_vorbis_header failed realloc at +0x8a/+0xba branches to +0x21 (return boolean 0, the same non-match path). Separately simple process receives parser result at +0x146; only -6/-9 take the explicit unsupported path, while -3 stores consumed and follows +0x162/+0x166 to the ordinary +0x262 return-0 path when no PCM/padding exists. The scope wrapper can preserve both signals.',
     'evidence': [binary('ogg_parser.c.obj', 'parse_vorbis_header', ['0x21', '0x8a', '0x8f', '0xba', '0xbf']),
                  binary('esp_audio_simple_dec.c.obj', 'esp_audio_simple_dec_process', ['0x146', '0x149', '0x153', '0x15a', '0x162', '0x166', '0x262'])],
     'candidate': source(donor + 'vorbis_repair/simple.c', 'typedef struct { bool allocation_failed; } failure_scope;'),
     'gate': 'Actual Xtensa task-local nested failure scopes; inject each packet/header realloc and parser cache allocation, return MEM_LACK with decoded_size=0, close failed handle in CYD. Verify two task/core scopes cannot contaminate one another and zero-size realloc/non-Ogg forwarding remains unchanged.'},
]

layout = [
    {'type': 'wrapper', 'donor': '48 bytes; dsp0, packet8, sent_info40',
     'target_observed': 'calloc48 in open; decode passes wrapper+8 to synthesis and uses byte40; close loads dsp0.',
     'evidence': [binary('esp_vorbis_dec.c.obj', 'esp_vorbis_dec_open', ['0x48']),
                  binary('esp_vorbis_dec.c.obj', 'esp_vorbis_dec_decode', ['0x9e', '0x118', '0x133'])]},
    {'type': 'vorbis_info / codec_setup', 'donor': 'info32 setup pointer28; setup52 with blocks0/4, counts8/12/16/20/24 and arrays28/32/36/40/44/48',
     'target_observed': 'info memset32, setup calloc52 at info+28; target cleanup uses the asserted array offsets and count offsets with mapping20/residue28/book64 strides.',
     'evidence': [binary('info.c.obj', 'vorbis_info_init', ['0x3', '0x13', '0x1d']),
                  binary('info.c.obj', 'vorbis_info_clear', ['0x5', '0xa', '0x15', '0x3b', '0x46', '0x7e', '0xa6', '0xb1'])]},
    {'type': 'dsp', 'donor': '80 bytes; info0, work28/mdctright32, output36/40, lW44/W48, 64-bit counters56/64/72',
     'target_observed': 'Constructor allocation and stores corroborate these offsets; decode reads output36/40 and PCM preflight must independently match target synthesis use of W48.',
     'evidence': [binary('dsp.c.obj', 'vorbis_dsp_create', ['0x6', '0x17', '0x36', '0x52']),
                  binary('esp_vorbis_dec.c.obj', 'esp_vorbis_dec_decode', ['0xd9', '0xdd'])]},
    {'type': 'codebook', 'donor': '64 bytes; dec_table16, q_val60, other typed fields0..56',
     'target_observed': 'Target clear frees q_val60 and dec_table16 and zeros64; setup cleanup strides64. Decode-map reads typed vector fields. Not a complete field-by-field mathematical type proof.',
     'evidence': [binary('codebook.c.obj', 'vorbis_book_clear', ['0x3', '0xe', '0x18']),
                  binary('codebook.c.obj', 'decode_map', ['0x1c', '0x35', '0x6a'])]},
    {'type': 'floors/residue/mapping', 'donor': 'floor0=40; floor1=36 with six owned pointers0..20; class stride11; residue28; mapping20',
     'target_observed': 'Allocation/clear sizes and nested owned-pointer cleanup match. floor1 class allocation uses addx4(i,i), then addx2(5i,i), thus 11i. Full subclass book interpretation and signed-char behavior still require target fixtures.',
     'evidence': [binary('floor0.c.obj', 'floor0_info_unpack', ['0x6']),
                  binary('floor1.c.obj', 'floor1_free_info', ['0x6', '0x10', '0x1a', '0x42']),
                  binary('floor1.c.obj', 'floor1_info_unpack', ['0x7f', '0x82']),
                  binary('mapping0.c.obj', 'mapping_clear_info', ['0x5', '0x10', '0x1a', '0x24']),
                  binary('res012.c.obj', 'res_clear_info', ['0x5', '0x10', '0x1a'])]},
    {'type': 'bitreader and stack packet construction', 'donor': 'ogg_buffer16/ref16/pack24; packet32 has two int64 values and wrapper starts packet at8',
     'target_observed': 'readinit zeros24 and reads ref buffer0/begin4/length8 and buffer.data0; writes pack head12/tail16/headptr4/headend8/count20. This corroborates the fields used by repair_header, not every ownership field or alignment.',
     'evidence': [binary('bitwise.c.obj', 'tremor_oggpack_readinit', ['0x3', '0x10', '0x12', '0x14', '0x16', '0x1c', '0x1e', '0x20', '0x22', '0x24'])]},
    {'type': 'simple registration/state', 'donor': 'registration32 parser_type20; state48 parser4/decoder8/pending12/16/20/padding24/28/32/ready36/errors38/limit40/align42/container44',
     'target_observed': 'Target open reads registration decoder16/parser20; process/reset/close use the asserted state offsets. Allocation is48. The extension remains our allocation and target close calls media_lib_free on base state.',
     'evidence': [binary('esp_audio_simple_dec.c.obj', 'esp_audio_simple_dec_open', ['0x38', '0x114', '0x116']),
                  binary('esp_audio_simple_dec.c.obj', 'esp_audio_simple_dec_process', ['0xc0', '0x109', '0x198', '0x19a']),
                  binary('esp_audio_simple_dec.c.obj', 'esp_audio_simple_dec_close', ['0x0'])]},
]

authorities = [
    {'title': 'Xiph.Org Vorbis I specification', 'url': 'https://www.xiph.org/vorbis/doc/Vorbis_I_spec.html',
     'verified': '2026-10-20 with web tool, sections1.1.5/1.1.6,2.1.8,3.2.1,4.2.2,4.3.8,AppendixA.2',
     'summary': 'Legal block sizes include8192. Sparse unused entries have no Huffman nodes. First audio block primes overlap; later output depends on both block sizes. Audio packet truncation has defined semantics. Ogg Vorbis may cross pages; final granule can trim PCM. Hardware exceptions require explicit support in the specification.'},
    {'title': 'RFC3533 Ogg encapsulation version0', 'url': 'https://www.rfc-editor.org/rfc/rfc3533',
     'verified': '2026-10-20 with web tool, sections5/6',
     'summary': 'Page continuation, zero lacing terminators, checksum, stream serials, BOS/EOS and page sequence are container test authorities. Their coverage is not established by one repaired decoder fixture.'},
    {'title': 'Pinned Xiph Tremor source provenance',
     'url': 'https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/',
     'verified': '2026-10-20 with web tool; immutable referenced tree exists',
     'summary': 'Provenance for donor setup adaptation only. It is not proof that vendor machine code was built from this exact tree.'},
]

report = {
    'status': 'read_only_source_and_binary_audit_complete_implementation_and_target_qualification_not_run',
    'stage': 14,
    'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': {'included': 'C3 checked Vorbis setup/output/Ogg wrappers; current CYD Vorbis registration and decoder retry/EOF ownership; actual installed codec2.6.2 ESP32/C3 archive selected members and public interfaces; read-only nm/objdump.',
              'excluded': CAP['excluded_scope'],
              'mutations': 'Only new ignored audit outputs in this folder. No tracked source/test/docs/Git/SDK mutations, builds, decoder execution or device operations.'},
    'conclusions': [
        'Proceed with a separately qualified Xtensa-specific port: six concrete target binary defects/call-order problems justify the checked setup, checked Ogg open/error propagation, PCM preflight and pending-packet preservation.',
        'No conflicting offset was found in the independently examined target consumers/cleanup paths; this is partial corroboration, not proof that RV32 private ABI is portable in full. All sizes, alignment, signed fields and consumers must be qualified with actual Xtensa builds and decodes before production enablement.',
        'Most existing CYD registration rollback, PCM owner release, resize retry, EOS drain loop and failed-handle close already exist; reuse them and test the actual service. Do not copy task core affinity, stack sizes, pool/TLS/IRAM tuning or donor performance numbers.',
        'No standard conformance pass, target PCM/OOM result, heap reduction or speedup is claimed by this audit. Stage14 remains open.',
    ],
    'installed_identity': {'component_version': '2.6.2 from idf_component.yml',
                           'public_headers': 'Shared installed headers are architecture-neutral API declarations; private layouts are absent.',
                           'component_selection': 'Installed CMake chooses lib/${CONFIG_IDF_TARGET}. Frozen existing CYD project_description identifies target=esp32, SDKv6.0.2 and the same codec component path.',
                           'parser_embedded_version': 'v1.0.1 in esp_es_parser_version.c.obj on both targets; a parser subcomponent version, not a replacement for package2.6.2.',
                           'archives': CAP['archives'],
                           'member_count': 38, 'machine_ids': {'esp32': 94, 'esp32c3': 243}, 'selected_debug_info_count': 0,
                           'compiler_comment': 'Both selected public Vorbis wrappers record GCC15.2.0 crosstool-NG esp-15.2.0_20251204. This does not imply ABI equivalence.',
                           'wrapper_symbol_availability': INVENTORY['selected_wrapper_entrypoints'],
                           'allocator_resolution_limit': 'media_lib_module_calloc/media_lib_module_realloc/media_lib_free are external dependencies of selected members; existing target linking resolves them elsewhere. The new target gate must verify the real allocator definition and --wrap relocation/callback routes in its actual linked ELF, not infer from an undefined symbol.'},
    'confirmed_binary_flow_findings': findings,
    'private_layout_observations_not_full_abi_proof': {
        'status': 'Partial positive corroboration; no observed conflicting field among examined consumers; do not relabel donor ABI as Xtensa proven.',
        'observations': layout,
        'not_proven': ['No DWARF types in any of the38 selected members. Pointers/long/size_t/int64 alignment must be compiler-asserted for actual Xtensa configuration.',
                       'Every codebook decode table representation, quantization signedness, floor subclass/mode mapping and all DSP consumers have not been proven equivalent by this audit.',
                       'The actual linker can resolve function pointers differently from direct wraps; target registration open/decode callback identities and parser dispatch must be verified from the final ELF plus execution.',
                       '64-bit host natural layout is different and cannot execute these private structures against vendor Xtensa objects. Host fixtures need explicit ILP32/layout seams and cannot qualify target ABI.']},
    'additional_bounded_candidates_and_caveats': [
        {'candidate': 'Carry checked codebook capacities and temporary ownership with setup repair',
         'evidence': [binary('codebook.c.obj', '_make_decode_table', ['0x5', '0xc', '0x21', '0x28', '0x39', '0x44', '0x46', '0x76']),
                      binary('codebook.c.obj', '_make_words', ['0x65', '0x70', '0x72', '0xa2', '0x1ca'])],
         'interpretation': 'Target table workspace already uses used-entry sizing, so it is not a demonstrated new heap optimization. Target _make_words receives entry count and has no output-capacity parameter; donor adds checks before each node write and checked allocation arithmetic. A legal/malformed sparse-tree corpus is required to establish behavior, not an invented savings number.',
         'source': source(donor + 'vorbis_repair/setup.c', 'size_t table_words=(size_t)s->used_entries*2+1;')},
        {'candidate': 'Keep a real final byte for empty separate EOF',
         'evidence': [binary('esp_es_parse.c.obj', 'esp_es_parse_frame', ['0x2c', '0x30', '0x6a', '0x460', '0x462', '0x43a'])],
         'interpretation': 'Target parser requires a non-NULL buffer and bypasses parsing when input length is zero, even with buffered state and EOS. CYD already drains on EOS but cannot force this branch through an empty packet. The donor genuine-byte tail staging is justified as a candidate; missing final PCM count and granule trimming remain to be reproduced on target. Do not fabricate zero padding.',
         'source': source(donor + 'vorbis_repair/simple.c', 'if (state->has_tail)')},
        {'candidate': 'Review inherited block-size profile before claiming standards support',
         'evidence': [binary('info.c.obj', '_vorbis_unpack_info', ['0x7c', '0x81', '0x8c', '0x8f', '0xb1', '0xb6'])],
         'interpretation': 'Both donor setup and target original reject longblock>4096 for rate<64000; target literals are63999/4096/8192. The shared public README advertises8-48kHz mono/stereo16-bit. The official spec allows8192; this audit established no explicit hardware exception authorizing this particular gate. Do not silently broaden binary DSP support or call the inherited restriction full conformance. Add a legal48k/8192 target fixture and separate supported-profile decision.',
         'source': source(donor + 'vorbis_repair/setup.c', '#ifdef LIMIT_TO_64kHz')},
        {'candidate': 'Retain original DSP arithmetic while measuring its remaining stack demand',
         'interpretation': 'Selected target res_inverse and vorbis_book_decode*v* still use input-derived movsp stack allocation. Donor setup/output repair does not replace those synthesis functions. Their retained existence is a limit on any claim that the whole decoder has bounded stack or complete malformed-input hardening; no safe stack-size reduction is justified.',
         'evidence': [binary('res012.c.obj', 'res_inverse', ['0x93', '0xb4', '0x330']),
                      binary('codebook.c.obj', 'vorbis_book_decodev_add', ['0x1b', '0x1e'])]},
    ],
    'current_cyd_already_present': [
        {'item': 'Transactional registration and rollback', 'entry': source(cyd + 'decoder_registration.c', 'esp_audio_err_t decoder_register_codecs(void)')},
        {'item': 'Independent decoder/PCM release, including failed opens', 'entry': source(cyd + 'audio_service.c', 'static void decoder_release(')},
        {'item': 'Output resize/retry', 'entry': source(cyd + 'audio_service.c', 'if (result == ESP_AUDIO_ERR_BUFF_NOT_ENOUGH)')},
        {'item': 'EOS drain loop', 'entry': source(cyd + 'audio_service.c', '// Ogg may retain several packets: EOS drains until no PCM remains.')},
    ],
    'implementation_plan_unimplemented': [
        {'step': 1, 'work': 'Separate target ABI bridge and guard preflight; no production default enabled yet',
         'details': 'New CYD-local typed bridge retains Tremor license/provenance. Assert every shared size/offset plus sizeof(long/pointer/size_t), alignof(int64), signed-char assumptions with actual Xtensa compiler/config. Guard target==esp32, exact selected component path/version, both ESP32 archive hashes, required symbol definitions and wrapper routes. Reject wrong/missing hash/target, including supplying donor C3 archives. Do not point the C3 helper at esp32 or weaken its guard.',
         'entry': source(donor + 'CMakeLists.txt', 'function(yoradio_vorbis_repair)')},
        {'step': 2, 'work': 'Bounded checked setup/open and Ogg ownership port',
         'details': 'Port setup/simple scope ownership only after target ABI audit. Publish handle only after success, clear every partial child once, preserve used-entry table bounds. Ogg-only checked state preserves public APIs and original close/reset. Preserve thread-local previous scope restoration for nesting and cross-core isolation; global allocator wrapper transparent outside scope. Do not replace native_health failed-allocation hook, numeric reservations, or retained DSP arithmetic.',
         'entries': [source(donor + 'vorbis_repair/setup.c', 'esp_audio_err_t __wrap_esp_vorbis_dec_open'), source(donor + 'vorbis_repair/simple.c', 'static esp_audio_err_t process_checked')]},
        {'step': 3, 'work': 'Target output preflight, repeated pending retry and real-byte EOF staging',
         'details': 'Port as separate logical change once raw ample target oracle is frozen. Reject too-small PCM before synthesis, preserve pending packet on every repeated rejection, retain genuine byte for separate empty EOF, clear extension on reset. Validate first-packet, transition, truncation and final granule contracts. Keep current CYD generation/EOF/PCM owners and task core affinity.'},
        {'step': 4, 'work': 'Qualify and then integrate with actual radio service',
         'details': 'New standalone Xtensa verifier must not import C3 verifier because that imports an unrelated deferred audit and recognizes RV32 jump patterns. Parse Xtensa callx/literal relocations and actual linked callback tables. Enable production only after gates below; capture source/tool/SDK/archive/config/golden/ELF before/after hashes, finite terminal markers, no omitted cases. Apply full lint once source is frozen and all3 output variants compile.'},
    ],
    'required_gates_all_unrun_here': [
        {'gate': 'G1 actual Xtensa compile/link/ABI', 'checks': 'Compile whole repair TUs against SDK6.0.2 real headers/config. Assert all bridge fields, ELF machine94, two CPU target with assertions, all nine wrappers and real targets linked once, operation table selects repaired open/decode; no direct original route or accidental C3 object. Exact negative guards for wrong archive/target/missing wrapper. Host private-layout tests are supplementary.'},
        {'gate': 'G2 actual archive PCM oracle', 'checks': 'Freeze original ESP32 raw-packet ample-buffer output with packet boundaries and trim metadata. Compare repaired raw output exact byte/sample/hash equality; independent pinned libvorbis/ffmpeg golden for container/granule and documented fixed-point tolerance. C3 fixture/golden may seed corpus but its PCM counts, hashes and error bounds are not ESP32 results.'},
        {'gate': 'G3 output retry/EOS', 'checks': 'Actual Ogg and raw at tiny, needed_size-1, repeated tiny, exact needed_size and ample capacity; alternating short/long blocks, first priming frame,64modes/two-byte header, last page multiple packets, final-byte split, empty separate EOF, repeated EOF, reset/reopen, empty/truncated streams. Named checks for no consumed or PCM/history change on rejected retry, no missing/duplicate PCM and final trim.'},
        {'gate': 'G4 OOM/lifetime', 'checks': 'Discover successful target allocation sequence first, then fail every actual alloc/realloc on open/setup/DSP/Ogg header/cache/packet and PCM resize. Guard regions and owner ledger detect UAF/double free/leaks; each failure returns a defined error and no PCM, NULL publication when open fails, repeated owner release safe, then valid play works. Include persistent registration failures and rollback. Fault instrumentation must not replace native_health hook or confuse allocator fault injection with physical heap measurement.'},
        {'gate': 'G5 task isolation and actual service', 'checks': 'Real FreeRTOS tasks on both cores with barriers: independent Ogg handles, nested process scopes, out-of-scope and zero-size realloc, non-Ogg passthrough, reset only after per-handle process quiescence. Actual decoder_task generation changes, Stop→Play, output resize-failure, network EOF/no-EOS/error, stale data and queue leases. This does not authorize concurrent reset/close on one handle, excluded by public API.'},
        {'gate': 'G6 standards corpus and explicit profile', 'checks': 'Legal sparse codebooks including unused entries and0/1-used cases; map types0/1/2, ordered/unordered, floor0/1, residue0/1/2, channel coupling/submaps, mono/stereo advertised rates,8192-block profile decision. Distinguish legal audio packet truncation from malformed setup. Ogg lacing255/0, cross-page packets, CRC/version/sequence errors, BOS/EOS, serial changes/chained logical streams and granule trim against authoritative expected behavior. This bounded audit and one golden are not conformance certification.'},
        {'gate': 'G7 meaningful exact controls', 'checks': 'Undo each fix separately: reintroduce early free, omit one NULL check, wrong bridge offset, synthesize before capacity check, clear pending on second -8, swallow allocation failure, use process-global instead of task-local scope, drop final real byte. Each expected named semantic check must fail; unexpected panic/timeouts are not successful controls except an explicitly retained historical crash reproduction.'},
        {'gate': 'G8 target measurements and production integration', 'checks': 'Measure actual allocated and largest free blocks, peak live heap, stack high-water per decoder path and task/core CPU/cycles on ESP32; retain original ample baseline. No C3 or ESP32-S3 performance table numbers. Build/lint all3 CYD output backends and current option combinations; preserve existing affinity. Actual radio playback/network/resource validation and release artifact export remain separate board gates.'},
    ],
    'authorities': authorities,
    'evidence': {'capture': {'path': 'capture.json', 'sha256': sha((OUT / 'capture.json').read_bytes())},
                 'analysis_checks': {'path': 'analysis-checks.json', 'sha256': sha((OUT / 'analysis-checks.json').read_bytes())},
                 'symbol_inventory': {'path': 'symbol-inventory.json', 'sha256': sha((OUT / 'symbol-inventory.json').read_bytes())},
                 'static_call_references': {'path': 'xtensa-call-references.json', 'sha256': sha((OUT / 'xtensa-call-references.json').read_bytes())},
                 'excerpt_map': {'path': 'excerpt-map.json', 'sha256': sha((OUT / 'excerpt-map.json').read_bytes())},
                 'all_input_sha256': CHECKS['all_input_sha256'],
                 'tool_hash_only': CAP['tool_hash_only'], 'source_snapshots': 'Content-addressed snapshots/map in capture.json and supplement.json. Four archives and38 selected ELF members preserved; tools hash-only.',
                 'finalizer_sha256': sha(pathlib.Path(__file__).read_bytes())},
    'failed_attempts': [{'step': 'Initial ignored analyze.py metadata capture', 'exit_status': 1,
                         'reason': 'Assumed SDK version.txt did not exist. Replaced metadata input with existing tools/cmake/version.cmake before successful analysis. No decoder or compilation executed in either attempt.',
                         'missing_path': 'C:/Work/yoRadio/.idf/v6.0.2/version.txt'}],
}

assert len(report['confirmed_binary_flow_findings']) == 6
report['evidence']['input_unchanged_final'] = {
    name: sha(pathlib.Path(name).read_bytes()) == digest for name, digest in CHECKS['all_input_sha256'].items()}
assert all(report['evidence']['input_unchanged_final'].values())
report['evidence']['payloads_sha256'] = {
    str(path.relative_to(OUT)): sha(path.read_bytes()) for path in sorted(OUT.rglob('*'))
    if path.is_file() and path.name != 'report.json'}
report['evidence']['payload_count'] = len(report['evidence']['payloads_sha256'])
path = OUT / 'report.json'
path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps({'report': str(path), 'sha256': sha(path.read_bytes()),
                  'source_inputs_current': len(report['evidence']['input_unchanged_final']),
                  'payload_count': report['evidence']['payload_count'],
                  'finding_count': len(findings), 'builds_or_decoder_runs': 0}, indent=2))
