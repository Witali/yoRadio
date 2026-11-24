"""Bounded preparation: small snapshots only; never configure/compile/run QEMU."""
import re
import shutil
from common import *

assert not (BASE/'preflight.json').exists()
old_prep=load(ROOT/'.build/copeneth24/preflight.json')
prep=dict(source_commit=SOURCE,compiled=False,rtc_workspace=False,rtc_probe_enabled=True,
    sdk_repositories=old_prep['sdk_repositories'],protected=[],sources=[],profiles=[])
assert pin(ROOT/old_prep['generator']['path'])==dict(bytes=old_prep['generator']['bytes'],sha256=old_prep['generator']['sha256'])
assert old_prep['generated_sha256']=='e4808727b9a3a5a0e1617d57f0d39a11bdf85443b9e3556990ea4822cef60882'
prep['generated_sha256']=old_prep['generated_sha256']
prep['generator']=old_prep['generator']
qemu=ROOT/'.build/cdac-model24/fixed-self-clear/qemu-system-xtensa.exe'
assert pin(qemu)['sha256']=='28068f674d06c4322aa72989756d7dd3734bb0d06c4aa1acf21b919ccb3465f4'
prep['qemu']=dict(path=qemu.relative_to(ROOT).as_posix(),**pin(qemu))
prep['protected']+=old_prep['production']+[prep['qemu']]
for item in old_prep['support_inputs']+[old_prep['generator']]: prep['sources'].append(item)
for item in old_prep['headers']:
    if item['path'].startswith(('idf/','yoRadio/src/audioI2S/','tests/target/cyd_full_app_openeth_qemu/')):
        prep['sources'].append(item)
for backend in ('legacy','pdm','continuous'):
    previous=ROOT/'.build/copeneth24'/backend
    baseline=load(previous/'baseline.json'); cache=ROOT/baseline['cache']
    directory=BASE/backend; assert not directory.exists(); (directory/'baseline').mkdir(parents=True)
    for folder in (previous/'fixture',previous/'compiled',ROOT/baseline['old_fixture']/'fixture',ROOT/baseline['old_fixture']/'compiled'):
        for p in folder.rglob('*'):
            if p.is_file(): prep['protected'].append(dict(path=p.relative_to(ROOT).as_posix(),**pin(p)))
    for p in (previous/'sdkconfig',previous/'clang/sdkconfig',previous/'clang/config/sdkconfig.json',previous/'clang/config/sdkconfig.h',previous/'clang/compile_commands.json'):
        prep['protected'].append(dict(path=p.relative_to(ROOT).as_posix(),**pin(p)))
    assert load(cache/'config/sdkconfig.json')==load(previous/'compiled/config/sdkconfig.json')
    for name in ('yoradio_cyd2usb_native.elf','yoradio_cyd2usb_native.map','compile_commands.json'):
        assert pin(cache/name)==pin(previous/'compiled'/name)
    seed=(previous/'sdkconfig').read_text()
    seed,n=re.subn(r'(?m)^CONFIG_YORADIO_WS_STATUS_RTC_SLOW=y$','# CONFIG_YORADIO_WS_STATUS_RTC_SLOW is not set',seed)
    assert n==1
    (directory/'sdkconfig').write_text(seed,encoding='utf-8',newline='\n')
    entries=load(cache/'compile_commands.json'); objects=[]
    for entry in entries:
        p=cache/entry['output']
        objects.append(dict(source=entry['file'],path=p.relative_to(ROOT).as_posix(),identity=pin(p),allocated=alloc_signature(p)))
    shutil.copyfile(cache/'config/sdkconfig.h',directory/'baseline/sdkconfig.h')
    shutil.copyfile(cache/'compile_commands.json',directory/'baseline/compile_commands.json')
    row=dict(backend=backend,cache=baseline['cache'],rtc_on=previous.relative_to(ROOT).as_posix(),
        old_fixture=baseline['old_fixture'],project_units=baseline['project_units'],objects=objects,
        project_version=baseline['project_version'],source_date_epoch=baseline['source_date_epoch'],
        original_app_descriptor_hex=baseline['original_app_descriptor_hex'],geometry=baseline['geometry'])
    write(directory/'baseline.json',row); guard(prep,row)
    prep['profiles'].append(dict(backend=backend,baseline=(directory/'baseline.json').relative_to(ROOT).as_posix(),objects=len(objects)))
    print('PREPARED '+backend,flush=True)
prep['free_disk_gib']=round(shutil.disk_usage(ROOT).free/2**30,2)
write(BASE/'preflight.json',prep)
print('Probe is independent and remains enabled; preparation only. Free GiB',prep['free_disk_gib'])
