"""Continue only the preserved header-guard failure; do not retry reconfigure."""
import argparse
import json
import os
import shutil
import subprocess
import sys
from common import BASE, ROOT, PROFILE, guard, load, pin, write_new
from common_reviewed import config_proof

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shell', default=shutil.which('pwsh') or shutil.which('powershell'))
    args = parser.parse_args()
    release = load(BASE / 'compile-release.json'); preflight = guard()
    assert release['allow_compile'] is True and release['backend'] == 'legacy'
    assert release['source_commit'] == preflight['source_commit'] and release['preflight'] == pin(BASE / 'preflight.json')
    original = load(PROFILE / 'execution-status.json')
    assert original['state'] == 'TERMINAL_NONPASS' and original['phase'] == 'gcc-reconfigure'
    assert original['reason'] == 'Generated header delta widened'
    assert original['children'] == [dict(phase='gcc-reconfigure', pid=21820, state='TERMINAL', exit_status=0)]
    review = load(BASE / 'header-guard-review.json')
    assert pin(PROFILE / 'sdkconfig') == review['generated_sdkconfig']
    for name, expected in review['continuation_helpers'].items():
        assert pin(BASE / name) == expected
    build = PROFILE / 'build'; assert build.resolve().is_relative_to(PROFILE.resolve())
    config_proof(build)
    assert not (PROFILE / 'compiled').exists() and not (PROFILE / 'fixture').exists()
    status_path = PROFILE / 'continuation-status.json'; assert not status_path.exists()
    status = dict(state='RUNNING', source_commit=preflight['source_commit'], children=[],
                  original_reconfigure_failure=pin(PROFILE / 'execution-status.json'), review=pin(BASE / 'header-guard-review.json'))
    def save():
        temporary = status_path.with_suffix('.tmp'); temporary.write_text(json.dumps(status, indent=2) + '\n'); os.replace(temporary, status_path)
    env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1', IDF_COMPONENT_MANAGER='0',
               SOURCE_DATE_EPOCH=str(preflight['metadata']['source_date_epoch']))
    def call(phase, command):
        status['phase'] = phase
        with (PROFILE / (phase + '.stdout.log')).open('xb') as out, (PROFILE / (phase + '.stderr.log')).open('xb') as err:
            child = subprocess.Popen(list(map(str, command)), cwd=ROOT, env=env, stdout=out, stderr=err)
            item = dict(phase=phase, pid=child.pid, state='RUNNING'); status['children'].append(item); save(); code = child.wait()
        item.update(state='TERMINAL', exit_status=code); save(); assert code == 0, phase + ' failed; original logs retained'
    save()
    try:
        write_new(PROFILE / 'reconfigure-config-proof-reviewed.json', config_proof(build))
        call('gcc-build', [args.shell, '-NoLogo', '-NoProfile', '-File',
                          ROOT / '.build/cyd-final-campaign-20261111-01/invoke-build.ps1',
                          '-Invocation', PROFILE / 'build-invocation.json'])
        guard(); config_proof(build)
        compiled = PROFILE / 'compiled'; compiled.mkdir()
        for name in ('yoradio_cyd2usb_native.elf', 'yoradio_cyd2usb_native.map', 'yoradio_cyd2usb_native.bin',
                     'project_description.json', 'compile_commands.json', 'flasher_args.json',
                     'config/sdkconfig.json', 'config/sdkconfig.h'):
            destination = compiled / name; destination.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(build / name, destination)
        original_fixture = ROOT / '.build/cpbuf24/sdk/legacy/fixture'; fixture = PROFILE / 'fixture'
        assert load(compiled / 'flasher_args.json') == load(original_fixture / 'flasher_args.json')
        shutil.copytree(original_fixture, fixture)
        shutil.copyfile(compiled / 'yoradio_cyd2usb_native.bin', fixture / 'yoradio_cyd2usb_native.bin')
        shutil.copyfile(compiled / 'config/sdkconfig.json', fixture / 'config/sdkconfig.json')
        unchanged = []
        for source in sorted(original_fixture.rglob('*')):
            if not source.is_file(): continue
            relative = source.relative_to(original_fixture).as_posix()
            if relative in ('yoradio_cyd2usb_native.bin', 'config/sdkconfig.json'): continue
            assert pin(source) == pin(fixture / relative); unchanged.append(dict(file=relative, **pin(source)))
        write_new(PROFILE / 'ab-fixture-provenance.json', dict(source_commit=preflight['source_commit'],
            scope=preflight['fixture_policy'], non_app_inputs=unchanged, baseline_qualification=preflight['baseline_qualification'],
            candidate_image=pin(fixture / 'yoradio_cyd2usb_native.bin'), candidate_config=pin(fixture / 'config/sdkconfig.json'),
            newly_built_bootloader_used=False, newly_built_bootloader=pin(build / 'bootloader/bootloader.bin')))
        call('foundation-check', [sys.executable, '-B', BASE / 'qualify-foundation-reviewed.py'])
        guard(); status.update(state='BUILD_PASS_QUALIFICATION_PENDING', phase='compiled-and-frozen')
    except Exception as error:
        status.update(state='TERMINAL_NONPASS', reason=str(error)); raise
    finally:
        save()

if __name__ == '__main__':
    main()
