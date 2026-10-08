from pathlib import Path
import json,subprocess
root=Path('.build/c3-idf-head-20261008');sdk=Path('C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6')
meta={'idf_revision':subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD'],text=True).strip(),'status':subprocess.check_output(['git','-C',str(sdk),'status','--porcelain'],text=True),'submodules':subprocess.check_output(['git','-C',str(sdk),'submodule','status','--recursive'],text=True).splitlines(),'series':(sdk/'tools/cmake/version.cmake').read_text(),'notes':['Shallow pinned SDK reports 9a97f6c5 in the image IDF string; full commit is recorded separately.','Existing tools-v6.1 directory reused; setup upgraded esptool 5.4.0 to 5.5.0 and installed SDK-required OpenOCD and ROM ELF versions.','Initial submodule inventory in sandbox failed with MSYS NtCreateDirectoryObject access denied; retry used normal process access.']}
assert not meta['status']
assert all(x.startswith(' ') for x in meta['submodules'])
(root/'sdk-environment.json').write_text(json.dumps(meta,indent=2)+'\n')
print('SDK source clean;',len(meta['submodules']),'submodules pinned')
