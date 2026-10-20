import datetime,hashlib,json,pathlib,struct,subprocess,time
root=pathlib.Path.cwd();out=pathlib.Path(__file__).resolve().parent
assert not (out/'capture.json').exists()
component=pathlib.Path('C:/Work/yoRadio/.idf/esp-adf-libs/esp_audio_codec')
xtensa=pathlib.Path('C:/Work/yoRadio/.idf/tools-v6.0.2/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin')
riscv=pathlib.Path('C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin')
repo_files=[
 'idf/esp32c3-oled-native/main/vorbis_repair_abi.h',
 *['idf/esp32c3-oled-native/main/vorbis_repair/'+name for name in ['setup.c','simple.c','output.c','README.md','COPYING']],
 *['idf/esp32c3-oled-native/main/'+name for name in ['CMakeLists.txt','Kconfig.projbuild','qemu_vorbis_lifecycle.c','qemu_vorbis_output.inc','decoder_registration.c','decoder_registration.h','decoder_resources.h','decoder_pcm.h']],
 *['idf/esp32-cyd2usb-native/main/'+name for name in ['CMakeLists.txt','Kconfig.projbuild','audio_service.c','decoder_registration.c','decoder_registration.h','board_config.h']],
 'idf/esp32-cyd2usb-native/CMakeLists.txt','idf/esp32-cyd2usb-native/build.ps1',
 *['tools/codec_benchmark/'+name for name in ['run_vorbis_lifecycle.py','run_vorbis_output.py','vorbis_packets.py','save_vorbis_lifecycle.py','verify_vorbis_repair_build.py']],
 *['tests/'+name for name in ['test-vorbis-lifecycle.py','test-vorbis-output.py','test-vorbis-repair-evidence.py','test-vorbis-output-evidence.py']],
 *['docs/'+name for name in ['ESP32C3_VORBIS_REPAIR_PLAN.md','ESP32C3_VORBIS_REPAIR_20261004.md','ESP32C3_VORBIS_OUTPUT_20261005.md']],
 'tests/results/esp32c3-vorbis-audit-20261004/manifest.json','tests/results/esp32c3-vorbis-output-20261005/manifest.json','tests/results/esp32c3-vorbis-output-20261005/reference-error.json',
 'tests/fixtures/esp32c3_calibration/vorbis-q10.ogg']
component_files=['idf_component.yml','CMakeLists.txt','include/decoder/impl/esp_vorbis_dec.h','include/decoder/esp_audio_dec.h','include/decoder/esp_audio_dec_reg.h','include/simple_dec/esp_audio_simple_dec.h','include/simple_dec/esp_audio_simple_dec_reg.h','include/simple_dec/esp_es_parse_types.h','include/simple_dec/impl/esp_ogg_parse.h','src/simple_decoder_reg.c']
state={'status':'capturing_read_only_audit','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_sha256':{},'snapshot_map':{},'tool_hash_only':{},'commands':[],'archives':{},'members':{},'excluded_scope':'Deferred AAC private owner-view is wholly excluded. No such source/object is selected or investigated, no transitive AAC verifier executes. Generic shared public container interfaces are inspected only for Ogg/Vorbis ownership. No builds, source/test/docs/Git edits or board operations.'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def freeze(path,tool=False):
    path=path.resolve();raw=path.read_bytes();digest=sha(raw);state['input_sha256'][str(path)]=digest
    if tool:state['tool_hash_only'][str(path)]=digest
    else:
        target=out/'snapshots'/digest;target.parent.mkdir(exist_ok=True)
        if not target.exists():target.write_bytes(raw)
        state['snapshot_map'][str(path)]=str(target.relative_to(out))
    return raw
def save():(out/'capture.json').write_text(json.dumps(state,indent=2)+'\n')
for path in [*[root/name for name in repo_files],*[component/name for name in component_files],pathlib.Path(__file__).resolve()]:freeze(path)
for prefix,bin_dir in [('xtensa-esp32-elf',xtensa),('riscv32-esp-elf',riscv)]:
    for tool in ['nm','objdump']:freeze(bin_dir/(prefix+'-'+tool+'.exe'),tool=True)
for board in ['esp32','esp32c3']:
    for archive in ['libesp_audio_codec.a','libesp_audio_simple_dec.a']:
        path=component/'lib'/board/archive;raw=freeze(path)
        state['archives'][board+'/'+archive]={'path':str(path),'sha256':sha(raw),'bytes':len(raw)}
save()
def command(label,args):
    started=time.monotonic();result=subprocess.run([str(arg) for arg in args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
    target=out/'tool-output'/(label+'.txt');target.parent.mkdir(exist_ok=True);target.write_bytes(result.stdout)
    state['commands'].append({'label':label,'argv':[str(arg) for arg in args],'exit_status':result.returncode,'elapsed_seconds':time.monotonic()-started,'payload':str(target.relative_to(out)),'sha256':sha(result.stdout)})
    save();assert result.returncode==0,(label,result.stdout.decode(errors='replace'));return result.stdout
def members(raw):
    assert raw[:8]==b'!<arch>\n';offset=8;table=b'';index=0
    while offset<len(raw):
        header=raw[offset:offset+60];assert header[58:]==b'`\n'
        size=int(header[48:58]);name=header[:16].decode().strip();data=raw[offset+60:offset+60+size]
        offset+=60+size+(size%2);index+=1
        if name=='//':table=data;continue
        if name=='/':continue
        if name.startswith('/') and name[1:].isdigit():name=table[int(name[1:]):].split(b'/\n',1)[0].decode()
        else:name=name.rstrip('/')
        yield index,name,data
def sections(raw):
    assert raw[:6]==b'\x7fELF\x01\x01'
    shoff=struct.unpack_from('<I',raw,32)[0];size,count,names=struct.unpack_from('<HHH',raw,46)
    entries=[struct.unpack_from('<10I',raw,shoff+i*size) for i in range(count)]
    table=raw[entries[names][4]:entries[names][4]+entries[names][5]]
    return {table[e[0]:].split(b'\0',1)[0].decode():e[5] for e in entries}
selected={'esp_vorbis_dec.c.obj','dsp.c.obj','info.c.obj','codebook.c.obj','floor0.c.obj','floor1.c.obj','mapping0.c.obj','res012.c.obj','bitwise.c.obj','floor_lookup.c.obj',
 'audio_simple_dec_reg.c.obj','esp_audio_simple_dec.c.obj','ogg_dec.c.obj','ogg_parser.c.obj','es_parse_default.c.obj','es_parse_mem.c.obj','es_parse_reg.c.obj','esp_es_parse.c.obj','esp_es_parser_version.c.obj'}
for board,prefix,bin_dir,machine in [('esp32','xtensa-esp32-elf',xtensa,94),('esp32c3','riscv32-esp-elf',riscv,243)]:
    for tool in ['nm','objdump']:command(board+'-'+tool+'-version',[bin_dir/(prefix+'-'+tool+'.exe'),'--version'])
    for archive in ['libesp_audio_codec.a','libesp_audio_simple_dec.a']:
        original=component/'lib'/board/archive;raw=(out/state['snapshot_map'][str(original.resolve())]).read_bytes()
        for index,name,data in members(raw):
            if name not in selected:continue
            assert struct.unpack_from('<H',data,18)[0]==machine
            label=board+'-'+archive.replace('.a','')+'-'+str(index)+'-'+name
            target=out/'members'/board/(str(index)+'-'+name);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
            sec=sections(data);identity={'archive':archive,'archive_index':index,'member':name,'sha256':sha(data),'bytes':len(data),'elf_machine':machine,'sections':sec,'payload':str(target.relative_to(out)),'dwarf_present':'.debug_info' in sec}
            state['members'][label]=identity
            command(label+'-nm',[bin_dir/(prefix+'-nm.exe'),'-S','-C',target])
            command(label+'-disasm',[bin_dir/(prefix+'-objdump.exe'),'-drwC',target])
            if '.debug_info' in sec:command(label+'-dwarf',[bin_dir/(prefix+'-objdump.exe'),'--dwarf=info',target])
        print('Captured',board,archive,'Vorbis/Ogg selected members',flush=True)
state['input_unchanged_after']={name:sha(pathlib.Path(name).read_bytes())==digest for name,digest in state['input_sha256'].items()}
assert all(state['input_unchanged_after'].values());state['status']='source_and_binary_capture_complete_no_build_or_execution_of_decoder';save()
print('PASS capture',len(state['members']),'selected members;',len(state['input_sha256']),'inputs; DWARF',sum(item['dwarf_present'] for item in state['members'].values()))
