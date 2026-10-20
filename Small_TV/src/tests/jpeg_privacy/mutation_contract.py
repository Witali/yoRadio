"""Compiled unsafe privacy variants must fail behavioral assertions."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    """Retain each altered source, compiler output and concrete runtime failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--vsdevcmd', type=Path, default=Path('C:/Program Files/Microsoft Visual Studio/18/Community/Common7/Tools/VsDevCmd.bat'))
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    project = Path(__file__).resolve().parents[2]
    source = project / 'codec/jpeg_privacy.c'
    text = source.read_text()
    cases = {
        'early-sos': ('++diagnostic->scans;', '++diagnostic->scans; return JPEG_PRIVACY_OK;'),
        'allow-exif': ('uint8_t header[14];', 'uint8_t header[14];\n    if(marker==0xe1){reader->position=end;return true;}'),
        'allow-trailing': ('else if(reader.position!=source->length)fail(&reader,JPEG_PRIVACY_TRAILING);', ''),
        'allow-thumbnail': ('if(header[12] || header[13])return fail(reader,JPEG_PRIVACY_THUMBNAIL);', ''),
        'allow-adobe-flags': ('header[7] || header[8] || header[9] || header[10] || header[11]>2', 'header[11]>2'),
        'ignore-stop': ('if(!error)return true;', 'if(!error || error==-23)return true;'),
        'ignore-read-error': ('if(error) {', 'if(error && error!=-17) {'),
    }
    report = dict(passed=False, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), mutants=[])
    try:
        for name, (before, after) in cases.items():
            assert text.count(before) == 1, name
            directory = output / name
            directory.mkdir()
            mutated = directory / 'jpeg_privacy.c'
            mutated.write_text(text.replace(before, after), encoding='utf-8', newline='\n')
            executable = directory / 'privacy-mutant.exe'
            command = (f'cl /nologo /std:c11 /O2 /W4 /WX /MT /D_CRT_SECURE_NO_WARNINGS '
                       f'/I"{project / "codec"}" "{project / "tests/jpeg_privacy/native_test.c"}" '
                       f'"{mutated}" /Fe"{executable}"')
            batch = directory / 'compile.cmd'
            batch.write_text(f'@echo off\r\ncall "{args.vsdevcmd}" -arch=x64 -host_arch=x64 >nul\r\n'
                             f'if errorlevel 1 exit /b 1\r\ncd /d "{directory}"\r\n{command}\r\nexit /b %errorlevel%\r\n',
                             encoding='utf-8', newline='')
            compiled = subprocess.run(['cmd.exe', '/d', '/c', str(batch)], capture_output=True, timeout=90)
            (directory / 'compile.log').write_bytes(compiled.stdout + compiled.stderr)
            assert compiled.returncode == 0, (name, compiled.stdout, compiled.stderr)
            result = subprocess.run([str(executable)], capture_output=True, timeout=10)
            (directory / 'runtime.log').write_bytes(result.stdout + result.stderr)
            assert result.returncode == 1 and b'privacy failure at ' in result.stderr, (name, result)
            report['mutants'].append(dict(name=name, source_sha256=hashlib.sha256(mutated.read_bytes()).hexdigest(),
                                           executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest(),
                                           runtime=result.stderr.decode().strip()))
        report['passed'] = True
    finally:
        (output / 'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('PASS:', len(report['mutants']), 'compiled privacy mutants rejected at runtime')


if __name__ == '__main__':
    main()
