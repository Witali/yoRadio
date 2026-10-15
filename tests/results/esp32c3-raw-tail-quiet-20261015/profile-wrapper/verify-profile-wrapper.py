"""Run after applying the reviewed profile; neither build nor flash an app."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
base=Path('.build/c3-raw-tail-quiet-20261015');out=base/'profile-wrapper'
project=Path('idf/esp32c3-oled-native')
source=project/'sdkconfig.radio-tested.defaults'
prepared=base/'promotion-candidates'/source
assert source.read_bytes()==prepared.read_bytes(),'Profile has not been promoted'
assert not out.exists(),'Preserve existing evidence'
for mode in ('fresh','cached'):
    assert not (project/f'build-profile-wrapper-{mode}-20261015').exists(),'Use a new build directory'
out.mkdir()
records=[]
for mode in ('fresh','cached'):
    directory=project/f'build-profile-wrapper-{mode}-20261015';config=directory/'sdkconfig'
    if mode=='cached':
        directory.mkdir()
        shutil.copyfile('firmware/development/esp32c3-idf61-production-20261013/sdkconfig',config)
        shutil.copyfile(config,out/'cached-before.sdkconfig')
    with (out/f'{mode}.log').open('x',encoding='utf-8') as log:
        code=subprocess.call(['pwsh','-NoProfile','-File',str(base/'check-profile-wrapper.ps1'),'-Mode',mode],stdout=log,stderr=subprocess.STDOUT)
    assert code==0,(mode,code)
    comparison=out/f'{mode}-comparison.json'
    code=subprocess.call([sys.executable,str(base/'compare-profile.py'),str(config),str(comparison)])
    shutil.copyfile(config,out/f'{mode}.sdkconfig')
    records.append(dict(mode=mode,result='PASS' if code==0 else 'FAIL',comparison=comparison.as_posix()))
    (out/'summary.json').write_text(json.dumps(records,indent=2)+'\n')
    assert code==0,'Configuration differs; preserve evidence and investigate'
print('Fresh and cached production wrapper match all candidate configuration keys')
