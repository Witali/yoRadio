"""Require the NOR contract to reject independently compiled broken implementations."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

PROJECT = Path(__file__).resolve().parents[2]


def sha(path):
    """Identify the exact source, fixtures, compiler and executable bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Keep mutants outside source directories and require runtime assertion failures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--vs-dev-cmd', type=Path,
                        default=Path('C:/Program Files/Microsoft Visual Studio/18/Community/Common7/Tools/VsDevCmd.bat'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = PROJECT/'storage/jpeg_nor.c'
    original = source.read_text()
    mutants = {
        'skip_erase': ('if (erase) {', 'if (false) {'),
        'lose_unchanged_pages': ('uint32_t selected = erase ? nonempty : changed;',
                                 'uint32_t selected = changed;'),
        'allow_protected_flash': ('return remaining == 0;', 'return true;'),
        'ignore_program_verification': ('if (memcmp(previous, wanted + offset, page_bytes)) {',
                                         'if (0 && memcmp(previous, wanted + offset, page_bytes)) {'),
        'ignore_erased_sector_verification': ('if (previous[i] != 0xff) {', 'if (false) {'),
        'read_stale_flash': ('if (store->cached && store->cached_sector == address - inside)',
                            'if (false)'),
    }
    report = dict(passed=False, scope=__doc__, cases=[],
        inputs_sha256={str(path.resolve()): sha(path) for path in (
            source, PROJECT/'storage/jpeg_nor.h', Path(__file__), Path(__file__).with_name('native_test.c'),
            args.fixtures/'plan_fixture.h', args.vs_dev_cmd)})
    try:
        for name, (before, after) in mutants.items():
            if original.count(before) != 1:
                raise ValueError('Mutation anchor changed: '+name)
            folder = (args.output/name).resolve()
            folder.mkdir()
            changed = folder/'mutant.c'
            changed.write_text(original.replace(before, after), encoding='utf-8', newline='\n')
            executable = folder/'mutant.exe'
            command = folder/'compile.cmd'
            command.write_text(
                '@echo off\ncall "'+str(args.vs_dev_cmd.resolve())+'" -arch=x64 -host_arch=x64 >nul\n'
                'if errorlevel 1 exit /b 1\ncd /d "'+str(folder)+'"\n'
                'where cl > compiler-path.txt\ncl /nologo /std:c11 /W3 /D_CRT_SECURE_NO_WARNINGS '
                '/I"'+str(args.fixtures.resolve())+'" /I"'+str(PROJECT/'storage')+'" '
                '"'+str(Path(__file__).with_name('native_test.c'))+'" "'+str(changed)+'" '
                '/Fe"'+str(executable)+'"\nexit /b %errorlevel%\n', encoding='utf-8', newline='\r\n')
            compiled = subprocess.run(['cmd.exe', '/d', '/c', str(command)], capture_output=True)
            (folder/'compile.log').write_bytes(compiled.stdout+compiled.stderr)
            if compiled.returncode:
                raise RuntimeError('Mutant must compile before rejection can count: '+name)
            compiler = Path((folder/'compiler-path.txt').read_text().splitlines()[0])
            outcome = subprocess.run([str(executable)], capture_output=True)
            (folder/'run.log').write_bytes(outcome.stdout+outcome.stderr)
            if outcome.returncode != 1 or b'FAIL ' not in outcome.stderr:
                raise AssertionError('Broken storage did not fail a runtime assertion: '+name)
            report['cases'].append(dict(name=name, rejected=True, exit_code=outcome.returncode,
                source_sha256=sha(changed), executable_sha256=sha(executable), compiler_sha256=sha(compiler),
                assertion=outcome.stderr.decode('utf-8', errors='replace').strip()))
            print('REJECTED NOR mutant:', name, flush=True)
        report['passed'] = len(report['cases']) == len(mutants)
    finally:
        report['inputs_unchanged'] = all(sha(Path(path)) == digest for path, digest in report['inputs_sha256'].items())
        report['passed'] &= report['inputs_unchanged']
        (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
