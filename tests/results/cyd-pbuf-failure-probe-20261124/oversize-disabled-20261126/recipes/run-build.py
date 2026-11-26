"""Release-gated fresh legacy A/B build. Preparation never executes this recipe."""
import argparse
import os
import shutil
import subprocess
import sys
from common import BASE, ROOT, PROFILE, DEP, config_proof, guard, load, pin, write_new

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shell', default=shutil.which('pwsh') or shutil.which('powershell'))
    args = parser.parse_args()
    release = load(BASE / 'compile-release.json')
    preflight = guard(check_seed=True)
    assert release['allow_compile'] is True and release['backend'] == 'legacy'
    assert release['source_commit'] == preflight['source_commit']
    assert release['preflight'] == pin(BASE / 'preflight.json')
    build = PROFILE / 'build'
    assert not build.exists(), 'Fresh build directory required; never reuse an old cache'
    assert args.shell and not (PROFILE / 'execution-status.json').exists()
    status = dict(state='RUNNING', source_commit=preflight['source_commit'], backend='legacy', children=[])
    status_path = PROFILE / 'execution-status.json'
    def save():
        temporary = status_path.with_suffix('.tmp')
        temporary.write_text(__import__('json').dumps(status, indent=2) + '\n')
        os.replace(temporary, status_path)
    env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1', IDF_COMPONENT_MANAGER='0',
               SOURCE_DATE_EPOCH=str(preflight['metadata']['source_date_epoch']))
    def call(phase, command):
        status['phase'] = phase
        with (PROFILE / (phase + '.stdout.log')).open('xb') as out, (PROFILE / (phase + '.stderr.log')).open('xb') as err:
            child = subprocess.Popen(list(map(str, command)), cwd=ROOT, env=env, stdout=out, stderr=err)
            record = dict(phase=phase, pid=child.pid, state='RUNNING')
            status['children'].append(record); save()
            code = child.wait()
        record.update(state='TERMINAL', exit_status=code); save()
        assert code == 0, phase + ' failed; raw logs retained'
    save()
    try:
        helper = ROOT / '.build/cyd-final-campaign-20261111-01/invoke-build.ps1'
        call('gcc-reconfigure', [args.shell, '-NoLogo', '-NoProfile', '-File', helper,
                                '-Invocation', PROFILE / 'reconfigure-invocation.json'])
        write_new(PROFILE / 'reconfigure-config-proof.json', config_proof(build))
        guard()
        call('gcc-build', [args.shell, '-NoLogo', '-NoProfile', '-File', helper,
                          '-Invocation', PROFILE / 'build-invocation.json'])
        guard(); config_proof(build)
        compiled = PROFILE / 'compiled'; compiled.mkdir()
        for name in ('yoradio_cyd2usb_native.elf', 'yoradio_cyd2usb_native.map', 'yoradio_cyd2usb_native.bin',
                     'project_description.json', 'compile_commands.json', 'flasher_args.json',
                     'config/sdkconfig.json', 'config/sdkconfig.h'):
            target = compiled / name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(build / name, target)
        original = ROOT / '.build/cpbuf24/sdk/legacy/fixture'
        fixture = PROFILE / 'fixture'
        assert not fixture.exists()
        assert load(compiled / 'flasher_args.json') == load(original / 'flasher_args.json'), 'Flash layout/settings changed'
        shutil.copytree(original, fixture)
        shutil.copyfile(compiled / 'yoradio_cyd2usb_native.bin', fixture / 'yoradio_cyd2usb_native.bin')
        shutil.copyfile(compiled / 'config/sdkconfig.json', fixture / 'config/sdkconfig.json')
        unchanged = []
        for source in sorted(original.rglob('*')):
            if not source.is_file(): continue
            relative = source.relative_to(original).as_posix()
            if relative in ('yoradio_cyd2usb_native.bin', 'config/sdkconfig.json'): continue
            assert pin(source) == pin(fixture / relative)
            unchanged.append(dict(file=relative, **pin(source)))
        write_new(PROFILE / 'ab-fixture-provenance.json', dict(
            source_commit=preflight['source_commit'], scope=preflight['fixture_policy'],
            non_app_inputs=unchanged, baseline_qualification=preflight['baseline_qualification'],
            candidate_image=pin(fixture / 'yoradio_cyd2usb_native.bin'),
            candidate_config=pin(fixture / 'config/sdkconfig.json'),
            newly_built_bootloader_used=False,
            newly_built_bootloader=pin(build / 'bootloader/bootloader.bin')))
        call('foundation-check', [sys.executable, '-B', BASE / 'qualify-foundation.py'])
        guard()
        status.update(state='BUILD_PASS_QUALIFICATION_PENDING', phase='compiled-and-frozen',
                      scope='Only config/image/metadata/ABI foundation; Clang, new linked-reference proof and runtime remain required.')
    except Exception as error:
        status.update(state='TERMINAL_NONPASS', reason=str(error))
        raise
    finally:
        save()

if __name__ == '__main__':
    main()
