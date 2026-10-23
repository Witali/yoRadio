import datetime,hashlib,json,pathlib,re
root=pathlib.Path.cwd();out=root/'.build/cyd-flac-qemu-independent-review-01';evidence=root/'.build/cyd-custom-flac-qemu-tracked-02'
path=out/'review.json';review=json.loads(path.read_text(encoding='utf-8'))
raw=(evidence/'report.json').read_bytes();bundle_raw=(evidence/'execution-bundle.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='3d6f11d493d92c33586919aefd96de10982a97598cb558b157083e1ad46a006d'
assert hashlib.sha256(bundle_raw).hexdigest()=='e24f8aae8f79f41331bb40f35b9b6cd7d4a2776a3117b97b1cfcbc987854435b'
report=json.loads(raw);bundle=json.loads(bundle_raw)
assert report['passed'] and not report['physical_hardware'] and not report['actual_cyd_decoder_task'] and not report['oom_injection']
old_runner=(out/'sources/tests/run-cyd-flac-qemu.py').read_bytes();runner=(root/'tests/run-cyd-flac-qemu.py').read_bytes()
before=b'(sdk,idf_tools,qemu.parent,rom_directory,ffmpeg.parent)'
after=b'(sdk,idf_tools,idf_python.parent,qemu.parent,rom_directory,ffmpeg.parent,powershell.parent)'
assert old_runner.count(before)==1 and runner==old_runner.replace(before,after)
current={}
for absolute,digest in report['source_sha256'].items():
    source=pathlib.Path(absolute);relative=source.relative_to(root);name=relative.as_posix();data=source.read_bytes()
    assert hashlib.sha256(data).hexdigest()==digest,name;current[name]=digest
    if name!='tests/run-cyd-flac-qemu.py':assert digest==review['source_sha256'][name],name
    target=out/'final-sources'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    if relative.parts[:3]==('tests','target','cyd_flac_qemu'):frozen=evidence/'sources/harness'/pathlib.Path(*relative.parts[3:])
    elif name=='tests/run-cyd-flac-qemu.py':frozen=evidence/'sources/runner'/source.name
    else:frozen=evidence/'sources/repository'/relative
    assert data==frozen.read_bytes(),name
assert len(current)==18
counts={}
for group in ['frozen_sources_sha256','fixture_sha256','artifact_sha256']:
    for name,digest in bundle[group].items():assert hashlib.sha256((evidence/name).read_bytes()).hexdigest()==digest,(group,name)
    counts[group]=len(bundle[group])
for name,digest in bundle['runtime_sha256'].items():assert hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest()==digest,name
counts['runtime_sha256']=len(bundle['runtime_sha256'])
log=(evidence/'qemu.log').read_text(encoding='utf-8')
rows=[json.loads(line.split('CYD_FLAC_QEMU_CASE ',1)[1]) for line in log.splitlines() if line.startswith('CYD_FLAC_QEMU_CASE ')]
assert len(rows)==520 and len({(r['id'],r['schedule']) for r in rows})==520
assert {(r['id'],r['schedule']) for r in rows}=={(i,s) for i in range(130) for s in [0,1,127,2048]}
assert rows==report['exact_pcm_cases']
assert len(re.findall(r'CYD_FLAC_QEMU_BOOT target=esp32 sdk=v6\.0\.2\b.*owner_core=1 coordinator_core=0 output_frames=512',log))==1
terminal='CYD_FLAC_QEMU_COMPLETE fixtures=130 cases=520 guards=48 byte_compare=1 heap_integrity=1 owner_core=1 coordinator_core=0 actual_cyd_task=0 oom_injection=0 hardware=0'
assert log.count(terminal)==1 and log.strip().endswith(terminal)
assert not re.search(r'Guru Meditation|assert failed|panic.ed|watchdog.*triggered|stack smashing|CORRUPT HEAP',log,re.I)
assert report['sdk_commit']==bundle['sdk_commit']=='7101770dc6db2667b3c477cc31365dd1acd6db4e'
assert report['execution_bundle_sha256']==hashlib.sha256(bundle_raw).hexdigest()
assert next(row for row in report['commands'] if row['name']=='qemu')['exit_status']==0
fixtures=json.loads((evidence/'fixture-manifest.json').read_text(encoding='utf-8'));blob=(evidence/'fixtures.bin').read_bytes()
for fixture in fixtures:
    encoded=pathlib.Path(fixture['encoded_path']).read_bytes();pcm=pathlib.Path(fixture['expected_pcm_path']).read_bytes()
    assert hashlib.sha256(encoded).hexdigest()==fixture['sha256'] and hashlib.sha256(pcm).hexdigest()==fixture['pcm_sha256']
    assert len(encoded)==fixture['bytes'] and len(pcm)==fixture['pcm_bytes'] and fixture['ffmpeg_byte_oracle']
    assert blob[fixture['encoded_offset']:fixture['encoded_offset']+len(encoded)]==encoded
    assert blob[fixture['pcm_offset']:fixture['pcm_offset']+len(pcm)]==pcm
    command=next(item for item in report['commands'] if item['name']=='ffmpeg-'+str(fixture['id']))
    assert command['exit_status']==0 and command['output_sha256']==fixture['pcm_sha256']
for row in rows:assert row['pcm_bytes']==fixtures[row['id']]['pcm_bytes'] and row['callbacks']>0 and row['feeds']>0 and row['stack_free']>0
config=json.loads((evidence/'build/config/sdkconfig.json').read_text(encoding='utf-8'))
assert config['IDF_TARGET']=='esp32' and not config['FREERTOS_UNICORE'] and config['COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE'] and config['HEAP_POISONING_LIGHT'] and config['FREERTOS_CHECK_STACKOVERFLOW_CANARY']
commands=json.loads((evidence/'build/compile_commands.json').read_text(encoding='utf-8'))
for name in ['idf/components/custom_flac/custom_flac_adapter.cpp','yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp','yoRadio/src/audioI2S/CodecMemoryArena.cpp']:
    selected=[row for row in commands if pathlib.Path(row['file']).resolve()==(evidence/'sources/repository'/name).resolve()]
    assert len(selected)==1 and '-O3' in selected[0]['command']
    if not name.endswith('CodecMemoryArena.cpp'):assert '-DFLAC_OUTPUT_FRAMES=512' in selected[0]['command'] and '-DFLAC_SEGMENTED_WORKSPACE=1' in selected[0]['command']
preflight=root/'.build/cyd-custom-flac-qemu-preflight-02';preflight_raw=(preflight/'report.json').read_bytes();dry=json.loads(preflight_raw)
assert dry['passed'] and dry['previous_reports_unchanged'] and dry['runner_sha256']==hashlib.sha256(runner).hexdigest()
assert {c['case'] for c in dry['checks']}=={'portable-pwsh','portable-python'}
for case in dry['checks']:
    assert case['status']==2 and case['created'] is False and 'Output must not overlap installed SDK/tool/ROM directories' in case['diagnostic']
    command=case['command'];candidate=pathlib.Path(command[command.index('--output')+1])
    assert not (candidate if candidate.is_absolute() else root/candidate).exists()
destination=out/'evidence/tracked-02';destination.mkdir(parents=True,exist_ok=True)
(destination/'report.json').write_bytes(raw);(destination/'execution-bundle.json').write_bytes(bundle_raw);(destination/'preflight-report.json').write_bytes(preflight_raw)
(destination/'runner.diff').write_bytes((preflight/'runner.diff').read_bytes())
review['historical_findings']=review['findings']
review['historical_findings'][0]['status']='Resolved by the exact two-parent guard extension, both dry preflight rejection cases, and fresh current-source tracked-02 full matrix.'
review['findings']=[];review['final_open_findings']=[];review['final_binding_pending']=False
review['final_source_sha256']=current
review['final_verified_evidence']={'report':'.build/cyd-custom-flac-qemu-tracked-02/report.json','report_sha256':hashlib.sha256(raw).hexdigest(),'execution_bundle_sha256':hashlib.sha256(bundle_raw).hexdigest(),'preflight_report_sha256':hashlib.sha256(preflight_raw).hexdigest(),'all18_sources_current_and_frozen_copies_identical':True,'other17_sources_unchanged_from_initial_review':True,'runner_diff_only_two_protected_parent_entries':True,'both_dry_guard_cases_reject_before_output_creation':True,'bound_payload_hash_counts':counts,'unique_cases':520,'actual_guard_completion_count':48,'one_boot_one_terminal_and_no_panic_patterns':True,'qemu_exit_status':0,'all_ffmpeg_oracle_records_and_blobs_match':True,'actual_component_commands_and_dual_core_assert_debug_config_verified':True,'reviewer_reran_sdk_qemu_or_ffmpeg':False}
review['reviewed_utc_final']=datetime.datetime.now(datetime.timezone.utc).isoformat()
review['result']='Initial output-parent guard finding resolved. Final current-source checkpoint fully bound to tracked-02 evidence; no open findings in reviewed adapter/core scope.'
path.write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
print('Final tracked-02 binding verified;P3 resolved;no open findings')
print('Review SHA256',hashlib.sha256(path.read_bytes()).hexdigest())
