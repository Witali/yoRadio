"""Require runtime assertions to reject independently compiled broken flash guards."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

PROJECT = Path(__file__).resolve().parents[2]


def sha(path):
    """Pin actual sources, fixtures and resulting executable, not planned inputs."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """A compile/loader failure does not count as a rejected unsafe implementation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures', type=Path, required=True)
    parser.add_argument('--assets', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--vs-dev-cmd', type=Path,
                        default=Path('C:/Program Files/Microsoft Visual Studio/18/Community/Common7/Tools/VsDevCmd.bat'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source, test = PROJECT/'storage/jpeg_guard.c', Path(__file__).with_name('native_test.c')
    original = source.read_text()
    mutants = {
        'ignore_partition_identity': ('!same_partition(part, &observed[i])', 'false'),
        'ignore_resource_digest': ('memcmp(digest, resource->sha256, sizeof(digest))', 'false'),
        'ignore_read_failure': ('device->read(device->context, resource->offset + offset, buffer, bytes)',
                                '(device->read(device->context, resource->offset + offset, buffer, bytes), false)'),
        'ignore_hash_update_failure': ('hash->update(hash->context, buffer, bytes)',
                                       '(hash->update(hash->context, buffer, bytes), false)'),
        'ignore_hash_finish_failure': ('!hash->finish(hash->context, digest)',
                                       '(hash->finish(hash->context, digest), true)'),
        'leak_hash_state': ('hash->reset(hash->context);', '(void)0;'),
        'allow_boot_prefix': ('!contained(0, app_end, layout->protected_ranges, layout->protected_count)', 'false'),
        'allow_photo_reclassification': ('return contained(assets->offset, layout->resources[0].offset - assets->offset,\n'
                                         '                     layout->protected_ranges, layout->protected_count);', 'return true;'),
        'allow_settings_reclassification': (
            '!contained(assets->offset + assets->bytes, flash_bytes - (assets->offset + assets->bytes),\n'
            '                   layout->protected_ranges, layout->protected_count)', 'false'),
        'ignore_ownership_stamp': ('    uint8_t buffer[JPEG_GUARD_READ_BYTES], digest[32];',
                                  '    if (resource->bytes == 64) return JPEG_GUARD_OK;\n'
                                  '    uint8_t buffer[JPEG_GUARD_READ_BYTES], digest[32];'),
    }
    inputs = [source, PROJECT/'storage/jpeg_guard.h', PROJECT/'storage/jpeg_nor.h', test, Path(__file__),
              args.fixtures/'jpeg_layout.h', args.assets, args.vs_dev_cmd]
    report = dict(passed=False, cases=[], inputs_sha256={str(p.resolve()): sha(p) for p in inputs})
    try:
        for name, (before, after) in mutants.items():
            if original.count(before) != 1:
                raise ValueError('Mutation anchor changed: '+name)
            folder = (args.output/name).resolve(); folder.mkdir()
            changed, executable = folder/'mutant.c', folder/'mutant.exe'
            changed.write_text(original.replace(before, after), encoding='utf-8', newline='\n')
            command = folder/'compile.cmd'
            command.write_text(
                '@echo off\ncall "'+str(args.vs_dev_cmd.resolve())+'" -arch=x64 -host_arch=x64 >nul\n'
                'if errorlevel 1 exit /b 1\ncd /d "'+str(folder)+'"\nwhere cl > compiler-path.txt\n'
                'cl /nologo /std:c11 /W3 /D_CRT_SECURE_NO_WARNINGS '
                '/I"'+str(args.fixtures.resolve())+'" /I"'+str(PROJECT/'storage')+'" '
                '"'+str(test)+'" "'+str(changed)+'" /Fe"'+str(executable)+'" /link bcrypt.lib\n'
                'exit /b %errorlevel%\n', encoding='utf-8', newline='\r\n')
            compiled = subprocess.run(['cmd.exe','/d','/c',str(command)], capture_output=True, timeout=60)
            (folder/'compile.log').write_bytes(compiled.stdout+compiled.stderr)
            if compiled.returncode:
                raise RuntimeError('Mutant did not compile: '+name)
            compiler = Path((folder/'compiler-path.txt').read_text().splitlines()[0])
            outcome = subprocess.run([str(executable),str(args.assets.resolve())], capture_output=True, timeout=60)
            (folder/'run.log').write_bytes(outcome.stdout+outcome.stderr)
            if outcome.returncode != 1 or b'FAIL ' not in outcome.stderr:
                raise AssertionError('Mutant escaped runtime assertions: '+name)
            report['cases'].append(dict(name=name, rejected=True, exit_code=outcome.returncode,
                assertion=outcome.stderr.decode('utf-8',errors='replace').strip(), source_sha256=sha(changed),
                executable_sha256=sha(executable), compiler_sha256=sha(compiler)))
            print('REJECTED guard mutant:', name, flush=True)
        report['passed'] = len(report['cases']) == len(mutants)
    finally:
        report['inputs_unchanged'] = all(sha(Path(p)) == h for p,h in report['inputs_sha256'].items())
        report['passed'] &= report['inputs_unchanged']
        (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__ == '__main__':
    main()
