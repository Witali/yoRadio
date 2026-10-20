"""Reject pixel corruption or repeated sector erases in compiled backing-store mutants."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
PROBE = HERE.parent / 'jpeg_library_probe'


def sha(path):
    """Bind compiled code and fixture bytes to the independent checks."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Crashes/compile errors do not count; check both reuse cycles against exact pixels."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--traffic', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--vs-dev-cmd', type=Path, default=Path('C:/Program Files/Microsoft Visual Studio/18/Community/Common7/Tools/VsDevCmd.bat'))
    args = parser.parse_args()
    build = json.loads((args.build / 'build.json').read_text())
    for name, h in build['probe_inputs'].items():
        assert sha(PROBE / name) == h, name
    traffic = json.loads((args.traffic / 'report.json').read_text())
    row = next(c for c in traffic['cases'] if c['name'] == 'rich-cmyk-progressive-12')
    image = (args.traffic / 'fixtures/rich-cmyk-progressive-12.jpg').resolve()
    assert sha(image) == row['fixture_sha256']
    source = HERE.parent / 'jpeg_scratch/probe_backing_nor.c'
    original = source.read_text()
    mutations = {
        'omit_first_initialization': ('result=prepare_fresh(slot,offset,block,encoded);', 'result=JPEG_SCRATCH_OK;'),
        'forget_prepared_flag': ('fresh_sectors[sector/8u]|=(uint8_t)mask;', '(void)mask;'),
        'retain_bitmap_after_abort': ('memset(fresh_sectors,0,sizeof(fresh_sectors));', '(void)fresh_sectors;'),
        'wrong_file_base': ('uint32_t start=scratch.files[files[slot].file.slot].offset+offset;', 'uint32_t start=offset;'),
    }
    args.output.mkdir(parents=True, exist_ok=False)
    env = {k: v for k, v in os.environ.items() if not k.startswith('SMALL_TV_NOR_')}
    env['SMALL_TV_COEFF_PACKING'] = '1'
    fixture_header = next(Path(p).parent for p in build['backing_fixture_inputs'] if p.endswith('scratch_fixture.h'))
    sources = [PROBE / n for n in ('probe.c','probe_memory.c','probe_faults.c','probe_reuse.c','table_dump.c')]
    sources += [HERE.parent / 'jpeg_scratch/nor_model.c', PROJECT / 'storage/jpeg_scratch.c',
                PROJECT / 'storage/jpeg_nor.c', PROJECT / 'codec/jpeg_coefficients.c']
    include = [PROBE, HERE.parent / 'jpeg_scratch', PROJECT / 'storage', PROJECT / 'codec',
               fixture_header, args.build / 'source/src', args.build / 'library']
    library = (args.build / 'library/jpeg-static.lib').resolve()
    report = dict(passed=False,cases=[],runner_sha256=sha(Path(__file__)),build=build,
                  fixture_sha256=sha(image),expected_sha256=row['expected_sha256'])
    for name, (before, after) in mutations.items():
        assert original.count(before) == 1, name
        folder = (args.output / name).resolve()
        folder.mkdir()
        changed, exe, batch = [folder / n for n in ('backing.c','mutant.exe','compile.cmd')]
        changed.write_text(original.replace(before,after),encoding='utf-8',newline='\n')
        command = ['cl','/nologo','/std:c11','/O2','/W3','/MT','/DJPEG_STATIC','/D_CRT_SECURE_NO_WARNINGS']
        command += ['/I"'+str(p.resolve())+'"' for p in include]
        command += ['"'+str(p.resolve())+'"' for p in [*sources,changed]]
        command += ['/Fe"'+str(exe)+'"','/link','"'+str(library)+'"']
        batch.write_text('@echo off\ncall "'+str(args.vs_dev_cmd.resolve())+'" -arch=x64 -host_arch=x64 >nul\n'
            'if errorlevel 1 exit /b 1\ncd /d "'+str(folder)+'"\n'+' '.join(command)+'\nexit /b %errorlevel%\n',
            encoding='utf-8',newline='\r\n')
        compiled = subprocess.run(['cmd.exe','/d','/c',str(batch)],capture_output=True,timeout=60)
        (folder/'compile.log').write_bytes(compiled.stdout+compiled.stderr)
        assert compiled.returncode == 0, (name,compiled.stdout,compiled.stderr)
        first, second = folder/'first.raw',folder/'second.raw'
        result = subprocess.run([str(exe),'reuse',str(image),str(first),str(second),'65536','1','none','0','0'],
                                env=env,capture_output=True,timeout=30)
        (folder/'run.log').write_bytes(result.stdout+result.stderr)
        assert result.returncode in (0,1), (name,result.returncode,result.stderr)
        record = json.loads(result.stdout)
        reasons = []
        if not record['first']['passed'] or not record['recovery']['passed']:
            reasons.append('valid JPEG decode failed')
        if sha(first)!=row['expected_sha256'] or sha(second)!=row['expected_sha256']:
            reasons.append('exact pixel mismatch')
        # At most one initial erase per used sector in each valid packed job.
        sectors = (record['first']['scratch_peak_bytes']+4095)//4096
        if record['first']['nor_erases']>sectors:
            reasons.append('first job repeats sector erase')
        if record['recovery']['nor_erases']-record['first']['nor_erases']>sectors:
            reasons.append('reused job repeats sector erase')
        assert reasons, (name,record)
        report['cases'].append(dict(name=name,rejected=True,reasons=reasons,result=record,
            source_sha256=sha(changed),executable_sha256=sha(exe)))
        print('REJECTED integration mutant:',name,','.join(reasons),flush=True)
    report['inputs_unchanged'] = all(sha(PROBE/n)==h for n,h in build['probe_inputs'].items())
    report['passed'] = report['inputs_unchanged'] and len(report['cases'])==len(mutations)
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__ == '__main__':
    main()
