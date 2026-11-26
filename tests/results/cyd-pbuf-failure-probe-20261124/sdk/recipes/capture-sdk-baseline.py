"""Capture original compiled evidence only; no candidate source freeze/build."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import zipfile

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
OUTPUT=BASE/'sdk-baseline'

def identity(data): return dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
def pin(path): return identity(Path(path).read_bytes())
def load(path): return json.loads(Path(path).read_bytes())
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream: stream.write((json.dumps(value,indent=2)+'\n').encode())
def relative(path): return Path(path).resolve().relative_to(ROOT).as_posix()
def section(path,name):
    data=Path(path).read_bytes(); assert data[:6]==b'\x7fELF\x01\x01'
    header=struct.unpack_from('<16sHHIIIIIHHHHHH',data)
    sections=[struct.unpack_from('<IIIIIIIIII',data,header[6]+i*header[11])for i in range(header[12])]
    strings=sections[header[13]]; names=data[strings[4]:strings[4]+strings[5]]
    found=[s for s in sections if names[s[0]:].split(b'\0',1)[0].decode()==name]
    assert len(found)==1; s=found[0]; return data[s[4]:s[4]+s[5]]
def zip_bytes(zip_file,name,data):
    assert not Path(name).is_absolute() and '..'not in Path(name).parts
    entry=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0)); entry.compress_type=zipfile.ZIP_DEFLATED
    zip_file.writestr(entry,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
def archive_member(archive,wanted):
    data=Path(archive).read_bytes(); assert data.startswith(b'!<arch>\n'); offset=8; names=b''; result=[]
    while offset<len(data):
        header=data[offset:offset+60]; assert len(header)==60 and header[58:60]==b'`\n'
        name=header[:16].decode().strip(); size=int(header[48:58]); body=data[offset+60:offset+60+size]
        if name=='//': names=body
        elif name.startswith('/') and name[1:].isdigit(): name=names[int(name[1:]):].split(b'/\n',1)[0].decode()
        else: name=name.removesuffix('/')
        if name==wanted: result.append(body)
        offset+=60+size+(size&1)
    assert len(result)==1; return result[0]

assert not OUTPUT.exists(),'Use a fresh baseline directory; never overwrite evidence'
assert shutil.disk_usage(ROOT).free>2*1024**3
OUTPUT.mkdir(parents=True)
old=ROOT/'.build/cnortc24'; prior=load(old/'preflight.json'); results=load(old/'results.json')
index=dict(purpose='Original compiled-byte preservation only; not a candidate source/head freeze.',
    candidate_commit=None,candidate_source_pending=True,compiled=False,configured=False,qemu_run=False,
    old_fixture_source_commit=results['source_commit'],old_project_reference=results['project_source_reference'],
    old_static_results=dict(path=relative(old/'results.json'),**pin(old/'results.json')),
    qemu=prior['qemu'],generator=prior['generator'],sdk_repositories=prior['sdk_repositories'],profiles=[],protected=[])
protected={item['path']:dict(item)for item in prior['protected']}
for backend in ('legacy','pdm','continuous'):
    directory=OUTPUT/backend; directory.mkdir()
    frozen=old/backend; row=load(frozen/'baseline.json'); qualified=load(frozen/'qualification.json')
    cache=(ROOT/row['cache']).resolve(); assert cache.is_relative_to(ROOT/'.build')
    assert pin(cache/'yoradio_cyd2usb_native.elf')==qualified['elf']
    assert pin(cache/'yoradio_cyd2usb_native.bin')==qualified['image']
    assert load(cache/'config/sdkconfig.json')==load(frozen/'compiled/config/sdkconfig.json')
    entries=load(frozen/'compiled/compile_commands.json')
    assert entries==load(cache/'compile_commands.json')
    changed={item['path']:item['after']for item in load(frozen/'object-comparison.json')['changed_raw']}
    expected={item['path']:changed.get(item['path'],item['identity'])for item in row['objects']}
    objects=[]; copies={}; zip_path=directory/'objects.zip'
    with zipfile.ZipFile(zip_path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for entry in entries:
            path=(cache/entry['output']).resolve(); assert path.is_relative_to(cache) and '.git'not in path.parts
            body=path.read_bytes(); found=identity(body); assert found==expected[relative(path)]
            name=path.relative_to(cache).as_posix(); zip_bytes(archive,name,body)
            objects.append(dict(source=entry['file'],path=relative(path),zip_member=name,**found))
            if Path(entry['file']).name in ('pcm.c','pbuf.c','tcp_out.c','esp_bootloader_desc.c','esp_app_desc.c'):
                copies[Path(entry['file']).name+'.obj']=(path,body)
    with zipfile.ZipFile(zip_path) as archive:
        assert len(archive.namelist())==len(objects)
        for item in objects: assert identity(archive.read(item['zip_member']))==dict(bytes=item['bytes'],sha256=item['sha256'])
    for name,(path,body) in copies.items():
        with (directory/name).open('xb') as stream: stream.write(body)
        assert pin(directory/name)==pin(path)
    assert 'pcm.c.obj'in copies and 'esp_bootloader_desc.c.obj'in copies
    descriptor=section(copies['esp_bootloader_desc.c.obj'][0],'.rodata.esp_bootloader_desc'); assert len(descriptor)==80
    with (directory/'bootloader-descriptor-section.bin').open('xb') as stream: stream.write(descriptor)
    main=cache/'esp-idf/main/libmain.a'; assert archive_member(main,'pcm.c.obj')==copies['pcm.c.obj'][1]
    shutil.copyfile(main,directory/'libmain.a'); assert pin(main)==pin(directory/'libmain.a')
    originals=[('sdkconfig',frozen/'sdkconfig'),('sdkconfig.json',cache/'config/sdkconfig.json'),
        ('sdkconfig.h',cache/'config/sdkconfig.h'),('compile_commands.json',cache/'compile_commands.json'),
        ('project_description.json',cache/'project_description.json'),('flasher_args.json',cache/'flasher_args.json'),
        ('original-qualification.json',frozen/'qualification.json'),('original-object-comparison.json',frozen/'object-comparison.json')]
    copied=[]
    for name,path in originals:
        shutil.copyfile(path,directory/name); assert pin(path)==pin(directory/name)
        copied.append(dict(original=relative(path),copy=name,**pin(path)))
    build_inputs=[]
    with zipfile.ZipFile(directory/'build-inputs.zip','x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for name in ('build.ninja','CMakeCache.txt','CMakeFiles/rules.ninja','config/sdkconfig.cmake','toolchain/cflags','toolchain/cxxflags'):
            path=cache/name
            if path.is_file():
                data=path.read_bytes(); zip_bytes(archive,name,data); build_inputs.append(dict(path=relative(path),zip_member=name,**identity(data)))
    for folder in (frozen/'fixture',frozen/'compiled'):
        for path in folder.rglob('*'):
            if path.is_file(): protected[relative(path)]=dict(path=relative(path),**pin(path))
    for item in objects: assert pin(ROOT/item['path'])==dict(bytes=item['bytes'],sha256=item['sha256'])
    write(directory/'objects.json',objects)
    record=dict(backend=backend,cache=relative(cache),objects=len(objects),logical_object_bytes=sum(x['bytes']for x in objects),
        object_zip=dict(file='objects.zip',**pin(zip_path)),object_catalog=dict(file='objects.json',**pin(directory/'objects.json')),
        raw_object_copies={name:pin(directory/name)for name in copies},main_archive=pin(directory/'libmain.a'),
        archive_pcm_member_matches=True,bootloader_descriptor_section=identity(descriptor),
        copied_inputs=copied,build_inputs=build_inputs,project_units=row['project_units'],
        project_version=row['project_version'],source_date_epoch=row['source_date_epoch'])
    write(directory/'snapshot.json',record); index['profiles'].append(record)
    print(json.dumps(dict(backend=backend,objects=len(objects),logical_bytes=record['logical_object_bytes'],zip_bytes=record['object_zip']['bytes'],raw_pcm_and_main_preserved=True)),flush=True)
for name,item in sorted(protected.items()):
    assert '.git'not in Path(name).parts
    assert pin(ROOT/name)==dict(bytes=item['bytes'],sha256=item['sha256']); index['protected'].append(item)
public=ROOT/'tests/results/cyd-openeth-no-rtc-20261124/sdk'
manifest=load(public/'artifact-manifest.json')
for item in manifest: assert pin(public/item['file'])==dict(bytes=item['bytes'],sha256=item['sha256'])
index['public_sdk_manifest']=dict(path=relative(public/'artifact-manifest.json'),**pin(public/'artifact-manifest.json'),verified_files=len(manifest))
index['objects_preserved']=sum(x['objects']for x in index['profiles'])
index['logical_object_bytes']=sum(x['logical_object_bytes']for x in index['profiles'])
index['total_snapshot_bytes']=sum(p.stat().st_size for p in OUTPUT.rglob('*')if p.is_file())
index['free_disk_gib']=round(shutil.disk_usage(ROOT).free/2**30,2)
write(OUTPUT/'baseline-index.json',index)
print(json.dumps(dict(completed=True,objects=index['objects_preserved'],logical_bytes=index['logical_object_bytes'],snapshot_bytes=index['total_snapshot_bytes'],protected_files=len(index['protected']),candidate_commit=None,free_disk_gib=index['free_disk_gib'])))
