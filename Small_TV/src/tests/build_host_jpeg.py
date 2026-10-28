"""Build the same offline production JPEG sources for native integration tests."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

PROJECT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT/'tools'))
from build_jpeg_library import VENDOR,verify_bundle,apply_patch,sha


def main():
    """Use real MSVC/OS SHA and production codec code, without a legacy test path."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--cmake',type=Path,required=True)
    parser.add_argument('--ninja',type=Path,required=True)
    args=parser.parse_args();upstream=verify_bundle()
    compiler=Path(shutil.which('cl.exe') or '')
    inputs={str(p.resolve()):sha(p) for p in [compiler,args.cmake,args.ninja,Path(__file__),PROJECT/'tools/build_jpeg_library.py']}
    inputs.update({str(p.relative_to(PROJECT)):sha(p) for p in VENDOR.rglob('*') if p.is_file()})
    fingerprint=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()
    # MSVC's PDB/compiler probes still have legacy path limits. A collision is
    # rejected by the complete input comparison, never accepted by this prefix.
    directory=args.output.resolve()/fingerprint[:16]
    report=directory/'build.json'
    if directory.exists():
        metadata=json.loads(report.read_text())
        assert metadata['inputs']==inputs
        for name,digest in metadata['products'].items():assert sha(directory/name)==digest,name
    else:
        directory.mkdir(parents=True);source=directory/'source';source.mkdir()
        with tarfile.open(VENDOR/'upstream.tar.gz','r:gz') as archive:archive.extractall(source,filter='data')
        for key in ('patch','flash_tables_patch','compact_pools_patch'):apply_patch(VENDOR/upstream[key],source)
        library=directory/'library'
        flags=['-DCMAKE_BUILD_TYPE=Release','-DCMAKE_TRY_COMPILE_CONFIGURATION=Release','-DENABLE_SHARED=OFF','-DENABLE_STATIC=ON','-DWITH_SIMD=OFF','-DWITH_TURBOJPEG=OFF','-DWITH_TOOLS=OFF','-DWITH_TESTS=OFF']
        subprocess.run([str(args.cmake),'-S',str(source),'-B',str(library),'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+str(args.ninja),*flags],check=True)
        subprocess.run([str(args.cmake),'--build',str(library),'--target','jpeg-static','--parallel','2'],check=True)
        files=[p for p in source.rglob('*') if p.is_file()]+list(library.glob('*.h'))+[library/'jpeg-static.lib']
        metadata=dict(upstream_commit=upstream['commit'],patch_sha256=upstream['patch_sha256'],flash_tables=True,compact_pools=True,
            flash_patch_sha256=upstream['flash_tables_patch_sha256'],pool_patch_sha256=upstream['compact_pools_patch_sha256'],
            library_sha256=sha(library/'jpeg-static.lib'),inputs=inputs,products={p.relative_to(directory).as_posix():sha(p) for p in files})
        report.write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8',newline='\n')
    (args.output/'selection.json').write_text(json.dumps(dict(build_directory=directory.as_posix()))+'\n',encoding='utf-8',newline='\n')
    print('Host JPEG dependency ready:',directory)


if __name__=='__main__':main()
