"""Compile embedded JavaScript and verify local JPEG/crop algorithms using Node."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
SITE = ROOT / 'Small_TV/local_site'


def main():
    """Record content identities and reject pages that differ from the exporter."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', default=shutil.which('node') or r'C:\Program Files\nodejs\node.exe')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = subprocess.run([args.node, str(SITE / 'check_scripts.mjs'), '--json'],
                            check=True, capture_output=True, text=True)
    report = json.loads(result.stdout)
    upload_source = (SITE / 'photo_upload.js').read_text(encoding='utf-8').rstrip()
    if (SITE / 'pages/photo.html').read_text(encoding='utf-8').count(upload_source) != 1:
        raise ValueError('Regenerate photo.html after changing the upload module')
    transfer_test = Path(__file__).with_name('photo_transfer_test.mjs')
    transfer_run = subprocess.run([args.node, str(transfer_test), str(SITE / 'pages/photo.html')],
                                  check=True, capture_output=True, text=True)
    transfer = json.loads(transfer_run.stdout)
    if not transfer['passed']:
        raise ValueError('Photo transfer sequencing/retry checks failed')
    report['photo_transfer'] = transfer
    wifi_source = (SITE / 'wifi_network.js').read_text(encoding='utf-8').rstrip()
    for page in ('setup', 'settings'):
        if (SITE / ('pages/' + page + '.html')).read_text(encoding='utf-8').count(wifi_source) != 1:
            raise ValueError('Regenerate Wi-Fi page after changing its formatter: ' + page)
    wifi_test = Path(__file__).with_name('wifi_scan_test.mjs')
    wifi_run = subprocess.run([args.node, str(wifi_test), str(SITE / 'pages')],
                              check=True, capture_output=True, text=True)
    wifi = json.loads(wifi_run.stdout)
    if not wifi['passed']:
        raise ValueError('Signed Wi-Fi scan labels failed')
    report['wifi_scan'] = wifi
    manifest = json.loads((SITE / 'pages-manifest.json').read_text(encoding='utf-8'))
    for page in report['pages']:
        recorded = next(row for row in manifest['pages'] if row['name'] == page['page'])
        if recorded['local_page_sha256'] != page['sha256']:
            raise ValueError('Page changed without regeneration: ' + page['page'])
    paths = ['check_scripts.mjs', 'jpeg_metadata.js', 'photo_crop.js', 'photo_crop.html', 'photo_upload.js',
             'wifi_network.js', 'extract_pages.py', 'pages-manifest.json']
    paths += ['pages/' + page['page'] + '.html' for page in report['pages']]
    report['inputs'] = [{'file': (SITE / name).relative_to(ROOT).as_posix(),
                        'sha256': hashlib.sha256((SITE / name).read_bytes()).hexdigest()}
                       for name in paths]
    report['inputs'].append({'file': transfer_test.relative_to(ROOT).as_posix(),
                             'sha256': hashlib.sha256(transfer_test.read_bytes()).hexdigest()})
    report['inputs'].append({'file': wifi_test.relative_to(ROOT).as_posix(),
                            'sha256': hashlib.sha256(wifi_test.read_bytes()).hexdigest()})
    report['scope'] = ('JavaScript syntax, signed Wi-Fi labels, crop/metadata and controlled HTTP transfer checks; '
                       'real browser Canvas and guest upload are recorded separately.')
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f"PASS frontend: {report['scripts']} scripts, {report['metadata_checks']} JPEG checks, "
          f"{report['crop_checks']} crop, {report['resize_checks']} resize, "
          f"{len(transfer['checks'])} photo transfer, {len(wifi['checks'])} Wi-Fi label checks")


if __name__ == '__main__':
    main()
