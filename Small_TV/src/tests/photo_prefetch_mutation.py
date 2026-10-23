"""Compile unsafe prefetch variants against the actual native policy contracts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

PROJECT = Path(__file__).resolve().parents[1]


def sha(path):
    """Bind each executed control/mutant to its actual source and compiler."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Require successful compilation and a real failing assertion for each mutant."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--vs-dev-cmd', type=Path, default=Path('C:/Program Files/Microsoft Visual Studio/18/Community/Common7/Tools/VsDevCmd.bat'))
    args = parser.parse_args();args.output.mkdir(parents=True, exist_ok=False)
    source = PROJECT/'app/display/factory_photo.c'
    contract = PROJECT/'tests/photo_prefetch.inc'
    text = source.read_text();tests = contract.read_text().split('static void test_photo_prefetch_failed_source')[0]
    wrapper = ('#include <stdio.h>\n#include <stdlib.h>\n#include "factory_photo.h"\n'
        '#define CHECK(c) do {if(!(c)){fprintf(stderr,"FAIL %s:%d: %s\\n",__FILE__,__LINE__,#c);exit(1);}} while(0)\n'+
        tests+'\nint main(void){test_photo_prefetch_policy();puts("PASS native prefetch policy control");return 0;}\n')
    mutants = {
        'ignore_fade': ('if(state->fade!=0 && state->fade!=2)return -1;', '(void)state->fade;'),
        'ignore_failed': ('enabled&configured&~failed', 'enabled&configured'),
        'ignore_configured': ('enabled&configured&~failed', 'enabled&~failed'),
        'prefer_cached_later': ('enabled&configured&~failed', 'enabled&configured&~failed&ready'),
        'wrong_round_robin': ('unsigned slot=start%5;', 'unsigned slot=(start+1)%5;'),
        'unrelated_warmup': (
            'int slot=next_photo(state->next_slot,enabled&configured&~failed);\n    return slot>=0 && !(ready&(1u<<slot)) ? slot:-1;',
            'int slot=next_photo(state->next_slot,enabled&configured&~failed&~ready);\n    return slot;')}
    inputs = [source, PROJECT/'app/include/factory_photo.h', contract, Path(__file__)]
    report = dict(passed=False, cases=[], inputs_sha256={str(p.resolve()):sha(p) for p in inputs})
    try:
        for name, mutation in [('control', None), *mutants.items()]:
            folder = args.output/name;folder.mkdir()
            body = text
            if mutation:
                before, after = mutation;assert body.count(before) == 1, name
                body = body.replace(before, after)
            unit = (folder/'policy.c').resolve();unit.write_text(body, newline='\n')
            test = (folder/'test.c').resolve();test.write_text(wrapper, newline='\n')
            executable = (folder/'policy.exe').resolve();batch = (folder/'compile.cmd').resolve()
            batch.write_text('@echo off\ncall "'+str(args.vs_dev_cmd)+'" -arch=x64 -host_arch=x64 >nul\n'
                'if errorlevel 1 exit /b 1\ncd /d "'+str(folder.resolve())+'"\nwhere cl > compiler-path.txt\n'
                'cl /nologo /O2 /std:c11 /W3 /I"'+str(PROJECT/'app/include')+'" "'+str(test)+'" "'+str(unit)+
                '" /Fe"'+str(executable)+'"\nexit /b %errorlevel%\n', newline='\r\n')
            compiled = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], capture_output=True, timeout=60)
            (folder/'compile.log').write_bytes(compiled.stdout+compiled.stderr)
            assert compiled.returncode == 0, 'Compile failure is not rejection: '+name
            ran = subprocess.run([str(executable)], capture_output=True, timeout=15)
            (folder/'run.log').write_bytes(ran.stdout+ran.stderr)
            if mutation:assert ran.returncode == 1 and b'FAIL ' in ran.stderr, 'Unsafe policy escaped: '+name
            else:assert ran.returncode == 0 and b'PASS native prefetch policy control' in ran.stdout
            compiler = Path((folder/'compiler-path.txt').read_text().splitlines()[0])
            report['cases'].append(dict(name=name, exit_code=ran.returncode, source_sha256=sha(unit),
                executable_sha256=sha(executable), compiler_sha256=sha(compiler), assertion=ran.stderr.decode(errors='replace').strip()))
            print('PASS prefetch control:' if mutation is None else 'REJECTED prefetch mutant:', name, flush=True)
        report['passed'] = True
    finally:
        report['inputs_unchanged'] = all(sha(Path(p)) == digest for p, digest in report['inputs_sha256'].items())
        report['passed'] &= report['inputs_unchanged']
        (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
