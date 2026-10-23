import datetime,hashlib,importlib.machinery,importlib.util,json,os,pathlib,re,struct,subprocess,sys,time
sys.dont_write_bytecode=True
root=pathlib.Path.cwd();out=root/'.build/cyd-http-tx-target-01';report_path=out/'report.json'
def sha(raw):return hashlib.sha256(raw).hexdigest()
original_report=report_path.read_bytes();report=json.loads(original_report)
assert report['passed'] is False
prior=out/'attempt-01-completed-compile-report.json'
if prior.exists():assert prior.read_bytes()==original_report
else:prior.write_bytes(original_report)
report['completion_validation']={'validator':str(pathlib.Path(__file__).resolve()),'prior_report':prior.name,'prior_report_sha256':sha(original_report),'reason':'Whole target compile and nm commands succeeded. Initial postcompile validator used a multiline regex that did not accept Windows CRLF; final validator uses splitlines. No compiler, source, flags or object changes.'}
for command in report['commands']:
    assert command['exit_status']==0
    assert sha((out/(command['name']+'.log')).read_bytes())==command['output_sha256']
compile_commands=[item for item in report['commands'] if item['name']=='compile'];assert len(compile_commands)==1
row=json.loads((out/'selected-compile-row.json').read_bytes());build=pathlib.Path(row['directory'])
assert build.resolve()==(root/'idf/esp32-cyd2usb-native/build-c3-transfer').resolve()
original_command=row['command'];old_tail=' -o '+row['output']+' -c '+row['file']
obj=out/'esp_http_client.c.obj';patched_source=out/'esp_http_client.c'
new_tail=' -o '+obj.as_posix()+' -c '+patched_source.as_posix()
assert original_command.count(old_tail)==1
assert compile_commands[0]['command']==original_command.replace(old_tail,new_tail,1)
assert compile_commands[0]['cwd']==str(build)
assert (out/'original-command.txt').read_text().rstrip('\n')==original_command
assert (out/'target-command.txt').read_text().rstrip('\n')==compile_commands[0]['command']
database=json.loads((build/'compile_commands.json').read_bytes())
assert [entry for entry in database if entry['file']==row['file']]==[row]
patcher_path=root/'tools/patch_cyd_http_request_buffer.py';source=pathlib.Path(row['file'])
loader=importlib.machinery.SourceFileLoader('frozen_patch_final_check',str(out/report['snapshot_map'][str(patcher_path.resolve())]))
spec=importlib.util.spec_from_loader(loader.name,loader);patcher=importlib.util.module_from_spec(spec);loader.exec_module(patcher)
assert patched_source.read_bytes()==patcher.patch(source.read_bytes())
raw=obj.read_bytes();assert raw[:6]==b'\x7fELF\x01\x01'
elf_type,machine=struct.unpack_from('<HH',raw,16);assert (elf_type,machine)==(1,94)
nm_lines=(out/'nm-defined.log').read_text().splitlines()
api_rows=[line for line in nm_lines if re.fullmatch(r'[0-9a-fA-F]+ T yoradio_http_client_release_request_buffer',line)]
assert len(api_rows)==1
expected=['esp_http_client_init','esp_http_client_cleanup','esp_http_client_request_send','esp_http_client_read']
for name in expected:assert len([line for line in nm_lines if re.fullmatch(r'[0-9a-fA-F]+ T '+name,line)])==1,name
config=json.loads((build/'config/sdkconfig.json').read_bytes())
assert config['IDF_TARGET']=='esp32' and not config['FREERTOS_UNICORE'] and not config['MBEDTLS_DYNAMIC_BUFFER']
assert len(report['dependency_files'])>100 and str((build/'config/sdkconfig.h').resolve()) in report['dependency_files']
assert report['dependency_inputs_captured_before_compile'] is True
validator=pathlib.Path(__file__).resolve();digest=sha(validator.read_bytes());snapshot=out/'sources'/digest
snapshot.write_bytes(validator.read_bytes());report['input_sha256'][str(validator)]=digest;report['snapshot_map'][str(validator)]=str(snapshot.relative_to(out))
report['completion_validation']['validator_captured_after_compile']=True
report['input_unchanged_after']={name:sha(pathlib.Path(name).read_bytes())==digest for name,digest in report['input_sha256'].items()}
report['snapshot_unchanged_after']={name:sha((out/report['snapshot_map'][name]).read_bytes())==digest for name,digest in report['input_sha256'].items()}
assert all(report['input_unchanged_after'].values()) and all(report['snapshot_unchanged_after'].values())
sdk=pathlib.Path('C:/Work/yoRadio/.idf/v6.0.2');env=os.environ.copy();env['GIT_OPTIONAL_LOCKS']='0'
for name,tail in [('sdk-head-after',['rev-parse','HEAD']),('sdk-tracked-changes-after',['status','--porcelain','--untracked-files=no'])]:
    command=['git','-c','core.longpaths=true','-C',str(sdk),*tail];started=time.monotonic()
    result=subprocess.run(command,cwd=build,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
    (out/(name+'.log')).write_bytes(result.stdout)
    assert result.returncode==0
    if name=='sdk-head-after':assert result.stdout.decode().strip()==report['sdk_commit']=='7101770dc6db2667b3c477cc31365dd1acd6db4e'
    else:assert not result.stdout.strip()
    report['commands'].append({'name':name,'command':command,'cwd':str(build),'exit_status':result.returncode,'elapsed_seconds':time.monotonic()-started,'output_sha256':sha(result.stdout)})
report['object']={'path':obj.name,'sha256':sha(raw),'bytes':len(raw),'elf_class':32,'elf_endian':'little','elf_type':'ET_REL','elf_machine':machine,'target':'Xtensa ESP32; EM_RISCV243 excluded','new_api_rows':api_rows,'existing_public_symbols_checked':expected}
report['configuration']={'target':config['IDF_TARGET'],'freertos_unicore':config['FREERTOS_UNICORE'],'mbedtls_dynamic_buffer':config['MBEDTLS_DYNAMIC_BUFFER'],'actual_allocator_usable_bytes_measured':False,'heap_savings_quantified':False,'request_tx_capacity_note':'The prior audit identifies a 4096-byte application-configured request buffer. It is a requested capacity, not a measured usable allocation size or a guaranteed heap gain. This object-only compile performs no allocation measurement.'}
report['new_api_defined_once']=True
report['warnings']=re.findall(r'^.*warning:.*$',(out/'compile.log').read_text(errors='replace'),re.M)
report['output_sha256']={path.name:sha(path.read_bytes()) for path in out.iterdir() if path.is_file() and path.name!='report.json'}
assert sha((root/'.build/cyd-http-tx-release-01/report.json').read_bytes())=='08c2a41a11ac8156b147f44142998f355f5aed5648051ee9209a2c49fc3fe32b'
assert sha((root/'.build/cyd-memory-transfer-audit-01/report.json').read_bytes())=='2a9eab5d44b055dd5350b200397a5e4c7c7f7e8157c92e8baeb7f0b5119c1ec9'
report['passed']=True;report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':report['passed'],'report_sha256':sha(report_path.read_bytes()),'inputs':len(report['input_sha256']),'dependencies':len(report['dependency_files']),'object':report['object'],'warnings':len(report['warnings'])},indent=2))
