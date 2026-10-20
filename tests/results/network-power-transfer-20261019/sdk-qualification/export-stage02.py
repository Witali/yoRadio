import argparse,hashlib,json,shutil,struct,subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('build',type=Path)
p.add_argument('variant')
p.add_argument('backend')
p.add_argument('--evidence',default='tests/results/cyd-c3-stream-20261018/README.md')
p.add_argument('--allow-sdkconfig-change',action='store_true')
a=p.parse_args()
build=a.build.resolve()
desc=json.loads((build/'project_description.json').read_text())
image=(build/desc['app_bin']).read_bytes()
assert struct.unpack_from('<I',image,32)[0]==0xabcd5432
version=image[48:80].split(b'\0')[0].decode()
elf_hash=hashlib.sha256((build/desc['app_elf']).read_bytes()).hexdigest()
assert image[176:208].hex()==elf_hash
config=json.loads((build/'config/sdkconfig.json').read_text())
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
dirty=bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=root,text=True).strip())
assert not dirty, 'Commit source before a final firmware export'
assert commit[:8] in version and not version.endswith('-dirty'),version
out=root/'firmware/development'/a.variant
out.mkdir(parents=True,exist_ok=True)
shutil.copyfile(build/desc['app_bin'],out/'app.bin')
(out/'sdkconfig.json').write_text(json.dumps(config,indent=2,sort_keys=True)+'\n')
manifest=dict(variant=a.variant,backend=a.backend,target=desc['target'],source_commit=commit,
    idf_version=desc['git_revision'],app_version=version,app_sha256=hashlib.sha256(image).hexdigest(),
    elf_sha256=elf_hash,app_bytes=len(image),sdkconfig_sha256=hashlib.sha256((out/'sdkconfig.json').read_bytes()).hexdigest(),
    physical_tested=False,build_check='PASS',host_evidence=a.evidence,
    build_directory=build.relative_to(root).as_posix())
if desc['target']=='esp32':
    manifest['ota_slot_bytes']=0x1b0000
    assert len(image)<=manifest['ota_slot_bytes']
    if a.backend=='pdm':
        baseline=json.loads((root/'firmware/development/esp32-cyd2usb-native-pdm-baseline/sdkconfig.json').read_text())
        manifest['baseline_sdkconfig_identical']=baseline==config
        manifest['baseline_existing_sdkconfig_identical']=all(config.get(k)==v for k,v in baseline.items())
        manifest['added_configuration']={k:v for k,v in config.items() if k not in baseline}
        manifest['changed_configuration']={k:dict(baseline=v,current=config.get(k)) for k,v in baseline.items() if config.get(k)!=v}
        if not a.allow_sdkconfig_change:
            assert manifest['baseline_existing_sdkconfig_identical']
            assert all(k.startswith('YORADIO_') for k in manifest['added_configuration'])
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
