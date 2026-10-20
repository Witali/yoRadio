"""Check that reversible-but-erase-heavy encodings also fail coefficient contracts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]


def sha(path):
    """Pin input/product bytes for each actually compiled mutation."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """A compile failure/crash is never a successful negative control."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--vs-dev-cmd', type=Path, default=Path('C:/Program Files/Microsoft Visual Studio/18/Community/Common7/Tools/VsDevCmd.bat'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = PROJECT / 'codec/jpeg_coefficients.c'
    original = source.read_text()
    mutants = {
        'raw_twos_complement_ac': [('if(phase && value<0)', 'if(false)')],
        'magnitude_dc_bijective': [('if(phase && value<0)', 'if(value<0)'), ('if(!phase)value-=65536;', 'if(false)value-=65536;')],
        'omit_complement_bijective': [('word=(uint16_t)~word;', 'word=(uint16_t)word;'),
                                     ('(uint16_t)~((uint16_t)in[i]|((uint16_t)in[i+1]<<8))', '(uint16_t)((uint16_t)in[i]|((uint16_t)in[i+1]<<8))')],
        'lose_int16_min': [(' : INT16_MIN;', ' : 0;')],
        'ignore_block_phase': [('unsigned phase=offset%128u;', 'unsigned phase=0;')],
        'odd_byte_write': [('(bytes|offset)&1u', 'offset&1u')],
        'allow_partial_overlap': [('return out==in || (out>in ? out-in>=bytes : in-out>=bytes);', 'return true;')],
    }
    inputs = [source, PROJECT / 'codec/jpeg_coefficients.h', HERE / 'native_test.c', Path(__file__), args.vs_dev_cmd]
    report = dict(passed=False, cases=[], inputs_sha256={str(p.resolve()): sha(p) for p in inputs})
    try:
        for name, replacements in mutants.items():
            text = original
            for before, after in replacements:
                assert text.count(before) == 1, (name, before)
                text = text.replace(before, after)
            folder = (args.output / name).resolve()
            folder.mkdir()
            changed, executable, batch = [folder / n for n in ('mutant.c', 'mutant.exe', 'compile.cmd')]
            changed.write_text(text, encoding='utf-8', newline='\n')
            batch.write_text('@echo off\ncall "' + str(args.vs_dev_cmd.resolve()) +
                '" -arch=x64 -host_arch=x64 >nul\nif errorlevel 1 exit /b 1\ncd /d "' + str(folder) +
                '"\nwhere cl > compiler-path.txt\ncl /nologo /std:c11 /O2 /W3 /I"' + str(PROJECT / 'codec') +
                '" "' + str(HERE / 'native_test.c') + '" "' + str(changed) + '" /Fe"' + str(executable) +
                '"\nexit /b %errorlevel%\n', encoding='utf-8', newline='\r\n')
            built = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], capture_output=True, timeout=60)
            (folder / 'compile.log').write_bytes(built.stdout + built.stderr)
            assert built.returncode == 0, name
            result = subprocess.run([str(executable)], capture_output=True, timeout=30)
            (folder / 'run.log').write_bytes(result.stdout + result.stderr)
            assert result.returncode == 1 and b'FAIL ' in result.stderr, (name, result.returncode, result.stdout, result.stderr)
            compiler = Path((folder / 'compiler-path.txt').read_text().splitlines()[0])
            report['cases'].append(dict(name=name, source_sha256=sha(changed), executable_sha256=sha(executable),
                compiler_sha256=sha(compiler), assertion=result.stderr.decode(errors='replace').strip(), rejected=True))
            print('REJECTED coefficient mutant:', name, flush=True)
        report['passed'] = True
    finally:
        report['inputs_unchanged'] = all(sha(Path(p)) == h for p, h in report['inputs_sha256'].items())
        report['passed'] &= report['inputs_unchanged']
        (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
