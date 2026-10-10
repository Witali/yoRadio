"""Compile only affected application objects with the probe disabled."""
import hashlib,json,re,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parent
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-pipeline-probe').resolve()
baseline=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-growth-tls')
out=root/'disabled-objects';out.mkdir(exist_ok=True)
wrapper=out/'disable.h'
wrapper.write_text('#include "'+(build/'config/sdkconfig.h').as_posix()+'"\n#undef CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC\n')
commands=json.loads((build/'compile_commands.json').read_text())
result={}
def sections(path):
    with path.open('rb') as f:
        return {s.name:s.data()
                for s in ELFFile(f).iter_sections()
                if s['sh_size'] and s.name.startswith(('.text','.rodata','.srodata','.data','.bss'))}
for name in ('audio_service.c','native_audio_output.c','web_service.c'):
    entry=next(c for c in commands if Path(c['file']).name==name)
    output=out/(name+'.obj')
    command,count=re.subn(r' -o \S+', ' -o '+output.as_posix(),entry['command'])
    assert count==1 and ' -MF ' not in command
    command+=' -include '+wrapper.as_posix()
    if not output.exists():
        with (out/(name+'.log')).open('xb') as log:
            subprocess.run(command,cwd=entry['directory'],shell=False,stdout=log,stderr=subprocess.STDOUT,check=True)
    previous=list(baseline.rglob(name+'.obj'));assert len(previous)==1
    before,after=sections(previous[0]),sections(output)
    differences=[key for key in before.keys()|after.keys() if before.get(key)!=after.get(key)]
    permitted={}
    if name=='native_audio_output.c':
        # ESP_ERROR_CHECK includes its source line and __FILE__. A direct
        # Windows compiler invocation also preserves backslashes in __FILE__.
        # Verify these exact changes instead of ignoring an entire function.
        old_source=subprocess.check_output(['git','show','897d39a9:idf/esp32c3-oled-native/main/'+name],text=True)
        new_source=Path(entry['file']).read_text()
        marker='ESP_ERROR_CHECK(i2s_del_channel(s_pdm));'
        lines=[next(i for i,line in enumerate(text.splitlines(),1) if marker in line)
               for text in (old_source,new_source)]
        def line_instruction(line):
            assert 0<=line<2048
            return ((line<<20)|(12<<7)|0x13).to_bytes(4,'little') # addi a2,zero,line
        section='.text.native_audio_output_suspend'
        assert after[section].count(line_instruction(lines[1]))==1
        assert after[section].replace(line_instruction(lines[1]),line_instruction(lines[0]))==before[section]
        section_name='.rodata.native_audio_output_suspend.str1.4'
        assert after[section_name].replace(b'\\',b'/')==before[section_name]
        permitted={section:dict(error_check_lines=lines),section_name:dict(file_separator_only=True)}
        assert set(differences)==set(permitted),differences
    else:
        assert not differences,(name,differences)
    result[name]=dict(result='PASS',source_diagnostic_differences=permitted,
        sections={key:dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest()) for key,data in after.items()})
(root/'disabled-object-audit.json').write_text(json.dumps(dict(result='PASS',objects=result,
    scope='Disabled probe: identical sections except verified ESP_ERROR_CHECK source line/file spelling; no code/data size increase'),indent=2)+'\n')
print('PASS: disabled probe has no code/data size increase; only verified source-location diagnostics differ')
