import argparse
import hashlib
import json
from pathlib import Path
import shutil

p=argparse.ArgumentParser()
p.add_argument('--label', required=True)
a=p.parse_args()
project=Path('idf/esp32c3-oled-native')
root=Path('.build/idf-upgrade')
dest=root/('buildlogs-'+a.label)
for build in project.glob('build-idf-'+a.label+'-*'):
    if a.label=='6.1' and ('compact' in build.name or 'native-control' in build.name):continue
    if a.label=='6.1-compact' and 'compact-ram' in build.name:continue
    if not (build/'project_description.json').exists():continue
    output=dest/build.name
    output.mkdir(parents=True, exist_ok=True)
    for log in (build/'log').glob('idf_py_*'):
        shutil.copyfile(log, output/(log.name+'.log'))
    shutil.copyfile(build/'sdkconfig', output/'sdkconfig')
    for name in ('audit.json','late-sbr-audit.json'):
        file=build/'esp-idf/main/compact5'/name
        if file.exists():shutil.copyfile(file, output/name)

if a.label=='6.1-compact':
    flags=('COMPACT_SBR','HIGH_HISTORY','HIGH_HISTORY_PC19',
           'SMOOTHING_HISTORY','LOW_WORKSPACE','ASYMMETRIC_OWNER','LATE_SBR')
    def read_config(path):
        rows=path.read_text().splitlines()
        return {flag:('CONFIG_YORADIO_AAC_'+flag+'=y') in rows
                for flag in ('PLUS',*flags)}
    control=project/'build-idf-6.1-native-control-config/sdkconfig'
    rows=[('production',project/'build-idf-6.1-compact-production/sdkconfig'),
          ('control',control)]
    result={name:dict(features=read_config(file), sdkconfig_sha256=hashlib.sha256(file.read_bytes()).hexdigest())
            for name,file in rows}
    assert all(result['production']['features'].values())
    assert result['control']['features']['PLUS']
    assert not any(result['control']['features'][key] for key in flags)
    result['passed']=True
    (root/'default-config-6.1-compact.json').write_text(json.dumps(result,indent=2)+'\n')
    out=dest/'native-control-config'
    out.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(control,out/'sdkconfig')
print('Captured', a.label)
