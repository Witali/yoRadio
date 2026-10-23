import ctypes,datetime,hashlib,importlib.machinery,importlib.util,json,os,pathlib,re,struct,subprocess,sys,time
sys.dont_write_bytecode=True
root=pathlib.Path.cwd();out=root/'.build/cyd-http-tx-target-01'
if out.exists():
    previous=(out/'report.json').read_bytes();previous_report=json.loads(previous)
    assert previous_report['commands']==[] and previous_report['passed'] is False
    assert not (out/'esp_http_client.c').exists() and not (out/'esp_http_client.c.obj').exists()
    assert not (out/'attempt-00-report.json').exists()
    (out/'attempt-00-report.json').write_bytes(previous)
else:out.mkdir(parents=True,exist_ok=False)
build=root/'idf/esp32-cyd2usb-native/build-c3-transfer';database=build/'compile_commands.json'
sdk=pathlib.Path('C:/Work/yoRadio/.idf/v6.0.2');source=sdk/'components/esp_http_client/esp_http_client.c'
patcher_path=root/'tools/patch_cyd_http_request_buffer.py'
hashes={};frozen={}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def freeze(path,group='inputs'):
    path=path.resolve();raw=path.read_bytes();digest=sha(raw);key=str(path)
    target=out/group/digest;target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists():target.write_bytes(raw)
    hashes[key]=digest;frozen[key]=str(target.relative_to(out));return raw
report={'passed':False,'scope':'Compile the patched WHOLE pinned SDK6.0.2 esp_http_client.c with the actual current CYD Xtensa compile-command row and real headers/private structs. Only ignored source/object/dependency outputs. No installed SDK, production CMake/main/header/config or Git mutation; no application link or device access. This establishes target-header/private-layout compilation, not runtime/auth/redirect/TLS/physical heap behavior.','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':[],'physical_hardware':False,'application_linked':False,'prior_attempt':{'report':'attempt-00-report.json','outcome':'Python snapshot-module import failed before executing any compiler/tool commands; retained immutable raw report and snapshots'}}
def save():
    report['input_sha256']=hashes;report['snapshot_map']=frozen
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
def execute(name,command,timeout=60):
    started=time.monotonic();env=os.environ.copy();env['GIT_OPTIONAL_LOCKS']='0';env['PYTHONUTF8']='1'
    result=subprocess.run(command,cwd=build,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
    (out/(name+'.log')).write_bytes(result.stdout)
    report['commands'].append({'name':name,'command':command,'cwd':str(build),'exit_status':result.returncode,'elapsed_seconds':time.monotonic()-started,'output_sha256':sha(result.stdout)})
    save();assert result.returncode==0,(name,result.returncode,result.stdout.decode(errors='replace'))
    return result.stdout
def windows_argv(command):
    count=ctypes.c_int();api=ctypes.windll.shell32.CommandLineToArgvW
    api.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_int)];api.restype=ctypes.POINTER(ctypes.c_wchar_p)
    pointer=api(command,ctypes.byref(count));assert pointer
    result=[pointer[i] for i in range(count.value)]
    free=ctypes.windll.kernel32.LocalFree;free.argtypes=[ctypes.c_void_p];free.restype=ctypes.c_void_p;free(pointer)
    return result
try:
    raw=freeze(database);rows=json.loads(raw);selected=[row for row in rows if pathlib.Path(row['file']).resolve()==source.resolve()]
    assert len(selected)==1;row=selected[0];assert pathlib.Path(row['directory']).resolve()==build.resolve()
    (out/'selected-compile-row.json').write_text(json.dumps(row,indent=2)+'\n',encoding='utf-8')
    original_command=row['command'];arguments=windows_argv(original_command);compiler=pathlib.Path(arguments[0])
    assert compiler.name=='xtensa-esp32-elf-gcc.exe' and 'riscv' not in original_command.lower()
    freeze(compiler,'tools');freeze(pathlib.Path(__file__).resolve(),'sources');freeze(patcher_path,'sources');sdk_bytes=freeze(source,'sources')
    for path in [build/'config/sdkconfig.h',build/'config/sdkconfig.json',build/'project_description.json',build/'toolchain/cflags',build/'specs/picolibc.specs',root/'.build/cyd-http-tx-release-01/report.json',root/'.build/cyd-memory-transfer-audit-01/report.json']:
        freeze(path)
    loader=importlib.machinery.SourceFileLoader('frozen_cyd_patch',str(out/frozen[str(patcher_path.resolve())]))
    spec=importlib.util.spec_from_loader(loader.name,loader);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    patched=module.patch(sdk_bytes);patched_source=out/'esp_http_client.c';patched_source.write_bytes(patched);freeze(patched_source,'sources')
    obj=out/'esp_http_client.c.obj'
    old_tail=' -o '+row['output']+' -c '+row['file']
    assert original_command.count(old_tail)==1
    new_tail=' -o '+obj.as_posix()+' -c '+patched_source.as_posix()
    command=original_command.replace(old_tail,new_tail,1)
    assert command.replace(new_tail,old_tail,1)==original_command
    report['compile_command_flags_identical']=True;report['changed_arguments_only']=['output object','input source replaced by exact build-local patched copy']
    (out/'original-command.txt').write_text(original_command+'\n',encoding='utf-8');(out/'target-command.txt').write_text(command+'\n',encoding='utf-8')
    dependency=out/'dependencies.d';dep_tail=' -M -MF '+dependency.as_posix()+' -MT cyd-http-tx '+patched_source.as_posix()
    dep_command=original_command.replace(old_tail,dep_tail,1)
    execute('compiler-version',[str(compiler),'--version'])
    for tool_name in ['cc1','as']:
        tool_path=pathlib.Path(execute('compiler-'+tool_name,[str(compiler),'-print-prog-name='+tool_name]).decode().strip())
        assert tool_path.is_file(),tool_path;freeze(tool_path,'tools')
    existing_object=build/row['output']
    if existing_object.is_file():freeze(existing_object,'original-build-output')
    sdk_head=execute('sdk-head',['git','-c','core.longpaths=true','-C',str(sdk),'rev-parse','HEAD']).decode().strip()
    assert sdk_head=='7101770dc6db2667b3c477cc31365dd1acd6db4e'
    assert not execute('sdk-tracked-changes',['git','-c','core.longpaths=true','-C',str(sdk),'status','--porcelain','--untracked-files=no']).strip()
    execute('dependencies',dep_command)
    dependency_text=dependency.read_text(encoding='utf-8').replace('\\\n',' ')
    assert dependency_text.startswith('cyd-http-tx:')
    tokens=re.findall(r'(?:\\.|[^\s])+',dependency_text.split(':',1)[1])
    dependencies=[]
    for token in tokens:
        token=token.replace('\\ ', ' ').replace('\\:',':').replace('\\#','#').replace('\\\\','\\')
        path=pathlib.Path(token);path=path if path.is_absolute() else build/path
        assert path.is_file(),(token,str(path));freeze(path);dependencies.append(str(path.resolve()))
    assert str((build/'config/sdkconfig.h').resolve()) in dependencies
    assert len(dependencies)>100
    report['dependency_files']=sorted(set(dependencies));report['dependency_inputs_captured_before_compile']=True
    report['sdk_commit']=sdk_head;report['whole_sdk_source_compiled']=True
    save();execute('compile',command,timeout=120)
    raw=obj.read_bytes();assert raw[:4]==b'\x7fELF' and raw[4]==1 and raw[5]==1
    elf_type,machine=struct.unpack_from('<HH',raw,16);assert elf_type==1 and machine==94
    nm=compiler.with_name('xtensa-esp32-elf-nm.exe');freeze(nm,'tools')
    execute('nm-version',[str(nm),'--version']);nm_output=execute('nm-defined',[str(nm),'--defined-only',str(obj)]).decode()
    api_rows=[line for line in nm_output.splitlines() if re.fullmatch(r'[0-9a-fA-F]+ T yoradio_http_client_release_request_buffer',line)]
    assert len(api_rows)==1,api_rows
    for name in ['esp_http_client_init','esp_http_client_cleanup','esp_http_client_request_send','esp_http_client_read']:
        assert re.search(r'^[0-9a-fA-F]+ T '+name+r'$',nm_output,re.M),name
    config=json.loads((build/'config/sdkconfig.json').read_text())
    assert config['IDF_TARGET']=='esp32' and not config['FREERTOS_UNICORE'] and not config['MBEDTLS_DYNAMIC_BUFFER']
    report['object']={'path':str(obj.relative_to(out)),'sha256':sha(raw),'bytes':len(raw),'elf_class':32,'elf_type':'ET_REL','elf_machine':machine,'target':'Xtensa ESP32, RISC-V excluded','new_api_rows':api_rows}
    report['new_api_defined_once']=True
    report['input_unchanged_after']={name:sha(pathlib.Path(name).read_bytes())==digest for name,digest in hashes.items()}
    assert all(report['input_unchanged_after'].values())
    assert execute('sdk-head-after',['git','-c','core.longpaths=true','-C',str(sdk),'rev-parse','HEAD']).decode().strip()==sdk_head
    assert not execute('sdk-tracked-changes-after',['git','-c','core.longpaths=true','-C',str(sdk),'status','--porcelain','--untracked-files=no']).strip()
    report['warnings']=re.findall(r'^.*warning:.*$',(out/'compile.log').read_text(errors='replace'),re.M)
    report['passed']=True;report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
finally:save()
print('PASS whole SDK6.0.2 Xtensa HTTP object; real private headers/flags; new API defined once; all inputs unchanged')
print('Report SHA256',sha((out/'report.json').read_bytes()))
