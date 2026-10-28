"""Require unsafe shared-scratch variants to fail compiled runtime assertions."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

PROJECT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def sha(path):
    """Bind assertions to compiler inputs, not a planned invocation."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """A compiler error, loader failure or crash never counts as a caught mutant."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--vs-dev-cmd', type=Path, default=Path(
        'C:/Program Files/Microsoft Visual Studio/18/Community/Common7/Tools/VsDevCmd.bat'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = PROJECT / 'storage/jpeg_scratch.c'
    original = source.read_text()
    mutants = {
        'ignore_file_id': ('r->used && r->id==file->id', 'r->used'),
        'read_uninitialized': ('(!writing && bytes>r->initialized-offset)', 'false'),
        'write_gap': ('offset>r->initialized ||', '(!writing && offset>r->initialized) ||'),
        'pad_each_file': ('candidate=r->offset+r->bytes;',
                          'candidate=(r->offset+r->bytes+4095u)&~4095u;'),
        'skip_checkpoint': ('if(s->check(s->check_context))', 'if(false)'),
        'ignore_write_error': (
            'if(s->last_nor_error!=JPEG_NOR_OK){s->failed=true;return JPEG_SCRATCH_IO;}\n    if(bytes',
            'if(false){s->failed=true;return JPEG_SCRATCH_IO;}\n    if(bytes'),
        'reset_file_ids': ('s->last_nor_error=JPEG_NOR_OK;memset',
                           's->next_id=0;s->last_nor_error=JPEG_NOR_OK;memset'),
        'initialize_whole_file': ('r->initialized=offset+(uint32_t)bytes;', 'r->initialized=r->bytes;'),
        'ignore_file_bounds': ('offset>r->bytes || bytes>r->bytes-offset', 'false'),
        'ignore_buffer_alias': (
            '!disjoint(data,bytes,file->owner,sizeof(*file->owner)) || !disjoint(data,bytes,file,sizeof(*file))',
            'false'),
        'zero_write_initializes': ('if(bytes && offset+(uint32_t)bytes>r->initialized)',
                                  'if(offset+(uint32_t)bytes>r->initialized)'),
        'unpoison_job': ('!s->active || s->failed ||', '!s->active ||'),
        'forbid_failed_cleanup': ('r->used=false;file->owner->active_bytes-=r->bytes;',
                                 'if(checkpoint(file->owner)!=JPEG_SCRATCH_OK)return JPEG_SCRATCH_STOP;\n'
                                 '    r->used=false;file->owner->active_bytes-=r->bytes;'),
    }
    inputs = [source, PROJECT / 'storage/jpeg_scratch.h', PROJECT / 'storage/jpeg_nor.c',
              PROJECT / 'storage/jpeg_nor.h', HERE / 'native_test.c', HERE / 'nor_model.c',
              HERE / 'nor_model.h', Path(__file__), args.fixtures / 'scratch_fixture.h', args.vs_dev_cmd]
    report = dict(passed=False, cases=[], inputs_sha256={str(p.resolve()): sha(p) for p in inputs})
    try:
        for name, (before, after) in mutants.items():
            if original.count(before) != 1:
                raise ValueError('Mutation anchor changed: ' + name)
            folder = (args.output / name).resolve()
            folder.mkdir()
            changed, executable, batch = [folder / p for p in ('mutant.c', 'mutant.exe', 'compile.cmd')]
            changed.write_text(original.replace(before, after), encoding='utf-8', newline='\n')
            batch.write_text('@echo off\ncall "' + str(args.vs_dev_cmd.resolve()) +
                '" -arch=x64 -host_arch=x64 >nul\nif errorlevel 1 exit /b 1\ncd /d "' + str(folder) +
                '"\nwhere cl > compiler-path.txt\ncl /nologo /std:c11 /O2 /W3 /D_CRT_SECURE_NO_WARNINGS /I"' +
                str(args.fixtures.resolve()) + '" /I"' + str(PROJECT / 'storage') + '" "' +
                str(HERE / 'native_test.c') + '" "' + str(HERE / 'nor_model.c') + '" "' + str(changed) +
                '" "' + str(PROJECT / 'storage/jpeg_nor.c') + '" /Fe"' + str(executable) +
                '"\nexit /b %errorlevel%\n', encoding='utf-8', newline='\r\n')
            built = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], capture_output=True, timeout=60)
            (folder / 'compile.log').write_bytes(built.stdout + built.stderr)
            if built.returncode:
                raise RuntimeError('Mutant did not compile: ' + name)
            result = subprocess.run([str(executable)], capture_output=True, timeout=60)
            (folder / 'run.log').write_bytes(result.stdout + result.stderr)
            if result.returncode != 1 or b'FAIL ' not in result.stderr:
                raise AssertionError('Mutant escaped: ' + name)
            compiler = Path((folder / 'compiler-path.txt').read_text().splitlines()[0])
            report['cases'].append(dict(name=name, rejected=True, source_sha256=sha(changed),
                executable_sha256=sha(executable), compiler_sha256=sha(compiler), exit_code=result.returncode,
                assertion=result.stderr.decode('utf-8', errors='replace').strip()))
            print('REJECTED scratch mutant:', name, flush=True)
        report['passed'] = len(report['cases']) == len(mutants)
    finally:
        report['inputs_unchanged'] = all(sha(Path(p)) == h for p, h in report['inputs_sha256'].items())
        report['passed'] &= report['inputs_unchanged']
        (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
