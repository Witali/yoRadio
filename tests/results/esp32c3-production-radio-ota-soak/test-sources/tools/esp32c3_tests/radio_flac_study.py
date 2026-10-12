"""Run matched real-radio LPC32/LPC12 files on an existing awake C3 image.

Reuses the original load gates, records partial logs after every case, and
alternates pair order across stations. Does not flash firmware.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from common import Board, require, sha
from diagnostic import DiagnosticCapture
from ota import image_info
import run


def paired_order(specs):
    groups = {}
    for spec in specs:
        groups.setdefault(spec['station'], {})[spec['max_lpc_order']] = spec
    names = []
    for i, pair in enumerate(groups.values()):
        require(set(pair) == {12,32}, 'Each station needs exactly LPC12 and LPC32')
        require(all(pair[12][key] == pair[32][key] for key in
                    ('pcm24_sha256','pcm24_bytes','pcm_sha256','rate','channels','bits','seconds')),
                'Pair does not encode identical PCM')
        names.extend(pair[order]['name'] for order in ((32,12) if i%2 == 0 else (12,32)))
    return names


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board', required=True)
    p.add_argument('--host', required=True)
    p.add_argument('--serial-port', required=True)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--fixtures', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--seconds', type=int, default=115)
    args = p.parse_args()
    require(not args.output.exists(), 'Use a new result directory')
    manifest = json.loads(args.fixtures.read_text())
    names = paired_order(manifest['fixtures'])
    config = args.firmware.with_name('sdkconfig').read_text()
    require('CONFIG_YORADIO_QEMU=y' not in config and 'CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y' not in config,
            'An awake physical image is required')
    image = image_info(args.firmware.read_bytes())
    require(Board(args.board).info()['app_elf_sha256'] == image['app_elf_sha256'], 'Wrong installed image')
    args.output.mkdir(parents=True)
    metadata = dict(firmware=image, firmware_sha256=sha(args.firmware.read_bytes()),
        sdkconfig_sha256=sha(args.firmware.with_name('sdkconfig').read_bytes()),
        fixture_manifest_sha256=sha(args.fixtures.read_bytes()),
        runner_sha256=sha(Path(__file__).read_bytes()), names=names, seconds=args.seconds,
        full_cpu_threshold_percent=99.9, warmup_seconds=10,
        transport='HTTP, unpaced socket writes / normal TCP backpressure',
        polling='0.1 s delay between WebUI requests',
        note='Total CPU, decoder task share and LPC bitstream order are distinct measurements')
    (args.output/'experiment.json').write_text(json.dumps(metadata,indent=2)+'\n')
    original = run.Suite.sustained
    def sustained(self, *positional, **keywords):
        try:
            return original(self, *positional, **keywords)
        finally:
            (self.output/'performance.json').write_text(json.dumps(self.capture.rows,indent=2)+'\n')
    run.Suite.sustained = sustained
    run.Capture = DiagnosticCapture
    sys.argv = ['run.py','--board',args.board,'--host',args.host,'--serial-port',args.serial_port,
        '--fixture-manifest',str(args.fixtures),'--sdkconfig',str(args.firmware.with_name('sdkconfig')),
        '--suite','load','--load-seconds',str(args.seconds),'--unpaced-files','--delivery-stats',
        '--output',str(args.output)]
    for name in names:
        sys.argv.extend(['--case',name])
    return run.main()


if __name__ == '__main__':
    raise SystemExit(main())
