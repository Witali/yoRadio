"""Publish compact verified functional evidence without VM logs, private state or images."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main():
    """Require a full passing automated run and unchanged test/firmware inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('functional-validation.json'))
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding='utf-8-sig'))
    groups = {row['name']: row for row in report['groups']}
    required = ('native', 'platform', 'integrity', 'machine', 'machine_control', 'qemu')
    if not report['passed'] or report['automatic_profile'] != 'host_machine_qemu':
        raise ValueError('Only a complete passing automated run may replace the published result')
    if any(groups[name]['status'] != 'passed' for name in required):
        raise ValueError('An automated group did not pass')
    for row in report['test_inputs']:
        data = (ROOT / row['file']).read_bytes()
        if hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('Test changed after the run: ' + row['file'])
    app = ROOT / 'firmware/development/small-tv-esp32c2-reconstructed/app.bin'
    if hashlib.sha256(app.read_bytes()).hexdigest() != report['app_sha256']:
        raise ValueError('Firmware changed after the run')
    machine = groups['machine']['result']
    controls = groups['machine_control']['result']
    if any(data['app_sha256'] != report['app_sha256'] for data in (machine, controls, groups['integrity']['result'])):
        raise ValueError('Groups tested different applications')
    qemu = groups['qemu']['result']
    if not qemu['http_initial_setup']['passed']:
        raise ValueError('Real HTTP initial setup did not pass')
    if not qemu['weather_http']['passed']:
        raise ValueError('Real weather HTTP/value/LCD comparison did not pass')
    qemu_sources = [qemu['boot_reset']['reconstructed']['prepared']['sources']]
    qemu_sources.extend(row['reconstructed']['source'] for row in qemu['scenes'].values())
    qemu_sources.append(qemu['http_initial_setup']['flows']['reconstructed']['sources'])
    qemu_sources.append(qemu['weather_http']['flows']['reconstructed']['sources'])
    for sources in qemu_sources:
        app_image = next(row for row in sources['images'] if row['file'] == 'app.bin')
        if app_image['sha256'] != report['app_sha256'] or sources['source_sha256'] != report['source_sha256']:
            raise ValueError('QEMU tested a different archived application')
    summary = {key: report[key] for key in ('schema_version', 'started_utc', 'finished_utc', 'passed',
                                           'automatic_profile', 'all_functionality_verified',
                                           'source_sha256', 'app_sha256', 'test_inputs', 'notes')}
    summary['native'] = groups['native']['result']
    summary['platform'] = groups['platform']['result']
    summary['integrity'] = groups['integrity']['result']
    summary['machine'] = {'passed': machine['passed'], 'literal_factory_pixels_equal': machine['equal'],
                          'renderer_cases': len(machine['cases']),
                          'geometry_checks': len(machine['stroke_geometry_checks']),
                          'source_sha256': machine['source_sha256'],
                          'native_elf_sha256': machine['native_elf_sha256'],
                          'approved_fixes': machine['approved_fixes'],
                          'scope': machine['scope']}
    summary['machine_control'] = {key: controls[key] for key in ('passed', 'timer_traces', 'slideshow', 'scope')}
    summary['machine_control']['simple_event_frames'] = controls['simple_events']['frames']
    summary['qemu'] = {'passed': qemu['passed'], 'qemu_sha256': qemu['qemu_sha256'],
                       'profile_sha256': qemu['profile_sha256'], 'scope': qemu['scope'],
                       'helper_sha256': qemu['helper_sha256'],
                       'http_initial_setup': qemu['http_initial_setup'],
                       'weather_http': qemu['weather_http'],
                       'boot_reset': {name: {key: row[key] for key in ('passed', 'checks', 'duration_seconds', 'network')}
                                      for name, row in qemu['boot_reset'].items()},
                       'scenes': {name: {'passed': True,
                                        'variants': {variant: {key: row[variant][key] for key in ('no_panic', 'ntp_reply', 'virtual_seconds')}
                                                     for variant in ('original', 'reconstructed')},
                                        'equal_pixels_min': row['equal_pixels_min'],
                                        'equal_pixels_max': row['equal_pixels_max']}
                                  for name, row in qemu['scenes'].items()}}
    summary['not_run'] = [row for row in report['groups'] if row['status'] == 'not_run']
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Published verified functional evidence:', args.output)


if __name__ == '__main__':
    main()
