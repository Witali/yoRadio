import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

root=Path('.build/c3-flac-rice-20261008')
objdump=Path('C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe')
records={}
for mode in ('control','bytewise'):
    artifact=Path('firmware/development/esp32c3-idf-6.1-r9a97-flac-rice-'+mode)
    manifest=json.loads((artifact/'manifest.json').read_text())
    build=Path(manifest['build_directory'])
    path=build/'yoradio_esp32c3_oled_native.elf'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest['elf_sha256']
    commands=json.loads((build/'compile_commands.json').read_text())
    command=[c for c in commands if c['file'].replace('\\','/').endswith('/flac_decoder/flac_decoder.cpp')]
    assert len(command)==1
    assert ('-DFLAC_BYTEWISE_RICE=1' in command[0]['command'])==(mode=='bytewise')
    (root/mode/'flac-compile.json').write_text(json.dumps(command,indent=2)+'\n')
    symbol_names=('_Z17readRiceSignedInth','_Z15decodeResidualshh')
    with path.open('rb') as stream:
        elf=ELFFile(stream)
        sections={s.name:dict(bytes=s['sh_size'],address=hex(s['sh_addr']),type=s['sh_type'])
                  for s in elf.iter_sections() if s['sh_flags']&2}
        rice={}
        for name in symbol_names:
            symbol=elf.get_section_by_name('.symtab').get_symbol_by_name(name)
            if not symbol:
                assert mode=='control' and name==symbol_names[0]
                rice[name]=dict(inlined=True)
                continue
            assert len(symbol)==1
            sym=symbol[0]
            rice[name]=dict(bytes=sym['st_size'],address=hex(sym['st_value']),section=elf.get_section(sym['st_shndx']).name)
            assert rice[name]['section']=='.flash.text'
    commands=[]
    for name in symbol_names:
        command=[str(objdump),'-d','--disassemble='+name,str(path)]
        commands.append(command)
        result=subprocess.run(command,check=True,capture_output=True)
        (root/mode/(name+'-linked.txt')).write_bytes(result.stdout)
        text=result.stdout.decode()
        if mode=='bytewise' and name==symbol_names[0]:assert '__clzsi2' in text
        if mode=='bytewise' and name==symbol_names[1]:assert symbol_names[0] in text
    records[mode]=dict(sections=sections,rice=rice,image=manifest['image'],elf_sha256=manifest['elf_sha256'],
                       sdkconfig_sha256=manifest['sdkconfig_sha256'],disassemble_commands=commands)
left,right=(records[mode]['sections'] for mode in ('control','bytewise'))
assert set(left)==set(right)
changes={key:dict(control=left[key],bytewise=right[key],byte_delta=right[key]['bytes']-left[key]['bytes'])
         for key in left if left[key]!=right[key]}
for key in left:
    if key.startswith(('.dram','.iram','.rtc')):assert left[key]==right[key],key
result=dict(passed=True,records=records,allocated_section_changes=changes,
    static_internal_ram_unchanged=True,
    note='Full linked ELF audit; project-version strings differ intentionally. No firmware performance claim.')
(root/'linked-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(changes=changes,rice={k:v['rice'] for k,v in records.items()}),indent=2))
