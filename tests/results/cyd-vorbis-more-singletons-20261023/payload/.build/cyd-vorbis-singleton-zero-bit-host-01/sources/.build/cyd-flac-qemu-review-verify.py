import datetime,hashlib,json,pathlib,re,struct
root=pathlib.Path.cwd();out=root/'.build/cyd-flac-qemu-independent-review-01';evidence=root/'.build/cyd-custom-flac-qemu-tracked-01'
review=json.loads((out/'review.json').read_text(encoding='utf-8'));report=json.loads((evidence/'report.json').read_text(encoding='utf-8'));bundle=json.loads((evidence/'execution-bundle.json').read_text(encoding='utf-8'))
assert report['passed'] and not report['physical_hardware'] and not report['actual_cyd_decoder_task'] and not report['oom_injection']
counts={}
for group in ['frozen_sources_sha256','fixture_sha256','artifact_sha256']:
    for name,digest in bundle[group].items():assert hashlib.sha256((evidence/name).read_bytes()).hexdigest()==digest,(group,name)
    counts[group]=len(bundle[group])
for name,digest in bundle['runtime_sha256'].items():assert hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest()==digest,name
counts['runtime_sha256']=len(bundle['runtime_sha256'])
current_binding={name:hashlib.sha256((root/name).read_bytes()).hexdigest()==digest for name,digest in review['source_sha256'].items()}
assert {name for name,match in current_binding.items() if not match}=={'tests/run-cyd-flac-qemu.py'}
for name in report['source_sha256']:
    source=pathlib.Path(name);relative=source.relative_to(root)
    if relative.parts[:3]==('tests','target','cyd_flac_qemu'):frozen=evidence/'sources/harness'/pathlib.Path(*relative.parts[3:])
    elif relative.as_posix()=='tests/run-cyd-flac-qemu.py':frozen=evidence/'sources/runner'/source.name
    else:frozen=evidence/'sources/repository'/relative
    assert (out/'sources'/relative).read_bytes()==frozen.read_bytes(),name
commands=json.loads((evidence/'build/compile_commands.json').read_text(encoding='utf-8'))
selected={}
for name in ['idf/components/custom_flac/custom_flac_adapter.cpp','yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp','yoRadio/src/audioI2S/CodecMemoryArena.cpp']:
    matches=[row for row in commands if pathlib.Path(row['file']).resolve()==(evidence/'sources/repository'/name).resolve()]
    assert len(matches)==1 and '-O3' in matches[0]['command'],name
    if not name.endswith('CodecMemoryArena.cpp'):assert '-DFLAC_OUTPUT_FRAMES=512' in matches[0]['command'] and '-DFLAC_SEGMENTED_WORKSPACE=1' in matches[0]['command']
    selected[name]=matches[0]['command']
config=json.loads((evidence/'build/config/sdkconfig.json').read_text(encoding='utf-8'))
assert config['IDF_TARGET']=='esp32' and not config['FREERTOS_UNICORE'] and config['COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE'] and config['HEAP_POISONING_LIGHT'] and config['FREERTOS_CHECK_STACKOVERFLOW_CANARY']
log=(evidence/'qemu.log').read_text(encoding='utf-8')
rows=[json.loads(line.split('CYD_FLAC_QEMU_CASE ',1)[1]) for line in log.splitlines() if line.startswith('CYD_FLAC_QEMU_CASE ')]
assert len(rows)==520 and len({(r['id'],r['schedule']) for r in rows})==520
assert {(r['id'],r['schedule']) for r in rows}=={(i,s) for i in range(130) for s in [0,1,127,2048]}
assert len(re.findall(r'CYD_FLAC_QEMU_BOOT target=esp32 sdk=v6\.0\.2\b.*owner_core=1 coordinator_core=0 output_frames=512',log))==1
terminal='CYD_FLAC_QEMU_COMPLETE fixtures=130 cases=520 guards=48 byte_compare=1 heap_integrity=1 owner_core=1 coordinator_core=0 actual_cyd_task=0 oom_injection=0 hardware=0'
assert log.count(terminal)==1 and log.strip().endswith(terminal)
assert not re.search(r'Guru Meditation|assert failed|panic.ed|watchdog.*triggered|stack smashing|CORRUPT HEAP',log,re.I)
assert report['sdk_commit']==bundle['sdk_commit']=='7101770dc6db2667b3c477cc31365dd1acd6db4e'
assert report['execution_bundle_sha256']==review['execution_bundle_sha256']
assert [row for row in report['commands'] if row['name']=='qemu'][0]['exit_status']==0
fixtures=json.loads((evidence/'fixture-manifest.json').read_text(encoding='utf-8'))
blob=(evidence/'fixtures.bin').read_bytes();magic,version,count,size=struct.unpack_from('<4I',blob)
assert (magic,version,count,size)==(0x514c4643,1,130,96)
for row in fixtures:
    encoded=pathlib.Path(row['encoded_path']).read_bytes();pcm=pathlib.Path(row['expected_pcm_path']).read_bytes()
    assert hashlib.sha256(encoded).hexdigest()==row['sha256'] and hashlib.sha256(pcm).hexdigest()==row['pcm_sha256']
    assert len(encoded)==row['bytes'] and len(pcm)==row['pcm_bytes'] and row['ffmpeg_byte_oracle']
    assert blob[row['encoded_offset']:row['encoded_offset']+len(encoded)]==encoded
    assert blob[row['pcm_offset']:row['pcm_offset']+len(pcm)]==pcm
    command=next(item for item in report['commands'] if item['name']=='ffmpeg-'+str(row['id']))
    assert command['exit_status']==0 and command['output_sha256']==row['pcm_sha256']
for row in rows:assert row['pcm_bytes']==fixtures[row['id']]['pcm_bytes'] and row['callbacks']>0 and row['feeds']>0 and row['stack_free']>0
# Pure path-predicate reproduction; never mkdir or execute the runner here.
pwsh=next(pathlib.Path(name) for name in bundle['runtime_sha256'] if pathlib.Path(name).name.lower()=='pwsh.exe')
candidate=(pwsh.parent/'codex-flac-output-review-example').resolve()
sdk=pathlib.Path('C:/Work/yoRadio/.idf/v6.0.2');idf_tools=pathlib.Path('C:/Work/yoRadio/.idf/tools-v6.0.2')
qemu=next(pathlib.Path(name) for name in bundle['runtime_sha256'] if pathlib.Path(name).name.lower()=='qemu-system-xtensa.exe')
rom=next(pathlib.Path(name).parent for name in bundle['runtime_sha256'] if pathlib.Path(name).name=='esp32-v3-rom.bin')
ffmpeg=next(pathlib.Path(name) for name in bundle['runtime_sha256'] if pathlib.Path(name).name.lower()=='ffmpeg.exe')
blocked=candidate==root or candidate in root.parents or (candidate.is_relative_to(root) and not candidate.is_relative_to(root/'.build'))
blocked=blocked or any(candidate==p or candidate.is_relative_to(p) for p in [sdk,idf_tools,qemu.parent,rom,ffmpeg.parent])
enclosing=next((p for p in candidate.parents if (p/'.git').exists()),None)
blocked=blocked or bool(enclosing and not candidate.is_relative_to(enclosing/'.build'))
assert not blocked and candidate.is_relative_to(pwsh.parent)
review['verified_evidence']={'hash_counts':counts,'source_hashes_current_after':current_binding,'all_initial_frozen_copies_equal_reviewed_sources':True,'report_passed':True,'fixture_count':130,'unique_cases':520,'guards_count_arithmetic':'42 truncated STREAMINFO +3 malformed declarations/signature +1 callback abort +1 separate EOF +1 reopen =48','all_ffmpeg_oracle_record_hashes_and_blob_offsets_verified':True,'actual_component_compile_commands':selected,'sdk_commit':report['sdk_commit'],'dual_core_assertion_heap_stack_config_verified':True,'qemu_exit_status':0,'one_boot_one_terminal_and_no_panic_patterns':True,'reviewer_reran_sdk_qemu_or_ffmpeg':False}
review['findings']=[{'id':'QEMU-RUNNER-01','priority':'P3','file':'tests/run-cyd-flac-qemu.py','line':55,'end_line':56,'title':'Include PowerShell and overridden Python installation parents in output guards','scenario':'A fresh output child inside a portable PowerShell installation, or an overridden SDK Python installation outside protected SDK/repository roots, is allowed because the installed-directory guard omits powershell.parent and idf_python.parent. The runner then creates its SDK project/build/fixture tree inside that tool installation despite its explicit installed-tool output protection contract. Fresh-output checking prevents overwriting existing files, and the completed default-path run is valid.','evidence':{'pure_path_predicate_example':str(candidate),'power_shell_installation_parent':str(pwsh.parent),'existing_output_guards_reject':False,'filesystem_mutation_for_reproduction':False},'requested_change':'Add powershell.parent and idf_python.parent to the protected installation parents and cover accepted/rejected output paths without starting SDK/QEMU.','impact_on_completed_checkpoint':'None: its .build output is outside all tool installations and all artifact/input hashes verified.'}]
review['checked_contracts']=[
 'Independent FFmpeg PCM16 output is hash-compared against generated fixture expectation, then those actual FFmpeg bytes are bundled and checked at every emitted target callback; total emitted PCM must exactly match.',
 'Every callback runs on core1, validates source/PCM depth, channel/rate metadata, pointer alignment, nonempty and512frame/channel bound, frame alignment, remaining oracle bounds and memcmp before advancing.',
 'Actual frozen custom_flac and custom_codec_support components compile through production CMake paths with their real adapter/core/arena; no decoder or allocator replacements are injected.',
 'SDK exact commit and tracked-clean checks run before/after; actual Xtensa ELF/chip image, ESP32 target, two cores, enabled assertions, heap poisoning and stack canaries are verified in config and target assertions.',
 'Target and host independently reject duplicate/missing ID/schedule combinations; coordinator requires520complete cases and all130masks==15, then actual48guard notification before one terminal marker.',
 '48guards are actual target code assertions over42prefixes, signature/metadata/frame-window malformed cases, byte-verified callback abort, zero-byte EOF and reopen. Heap integrity/core allocation counter are checked after destruction.',
 'Flash partition/image/fixture blobs are bounded/nonoverlapping and4MiB, actualmerge slices match sourcefiles. Execution bundle exists before QEMU and bound source/fixture/artifact/runtime inputs are rehashed after execution.',
 'QEMU child must exit0 and complete within timeout; panic/watchdog/heap/stack patterns or incomplete/duplicate terminal output fail. Current captured log ends with its sole terminal marker.',
 'Output path resolves links and requires a fresh directory; source/repository/SDK/QEMU/ROM/FFmpeg protection is present, with the narrow PowerShell/customPython parent omission recorded separately.'
]
review['limitations']=[
 'This adapter/core checkpoint does not execute actual CYD decoder_task, queue/maintenance lifecycle, inject OOM, or qualify deliberate semantic mutants on target; these remain explicitly open.',
 'QEMU heap/stack and scheduler checks are limited to the16384-byte synthetic owner task/debug profile; they do not prove full firmware margins, I2S/DMA, RF, physical timing, power or hardware behavior.',
 'Only six source depths and selected valid/malformed fixtures are covered; complete FLAC CRC/MD5/malformed-stream conformance or all21possible source depths are not established.',
 'Runtime input hashes cover the explicitly listed executables/ROMs/tools metadata; this is not an exhaustive byte snapshot of every SDK/toolchain dependency binary/header or a claim every tool binary is immutable.'
]
review['final_binding_pending']=True
review['findings'][0]['status']='Accepted; runner-only preflight fix in progress. Fresh tracked-02 run pending; immutable tracked-01 evidence remains valid for its initial frozen source.'
review['reviewed_utc_final']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(out/'review.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
print('Review: completed checkpoint evidence verified;1low-impact output-path guard finding')
print('Review SHA256',hashlib.sha256((out/'review.json').read_bytes()).hexdigest())
