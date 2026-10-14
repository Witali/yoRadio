"""Check IANA releases or reproduce a pinned TZif snapshot without installing code.

Network access is explicit and belongs to this maintenance command, never to the
firmware build. New releases require all three version/digest pins; discovering a
new version does not change the committed manifest or the firmware's country map.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit
from urllib.request import urlopen
import zipfile

from prepare_timezones import load_zones, parse_footer, parse_tzif

IANA_VERSION_URL = 'https://data.iana.org/time-zones/tzdb/version'
WHEEL_LIMIT = 8 * 1024 * 1024


def validate_pin(iana, package, digest):
    """Reject incomplete or ambiguous pins before constructing any download URL."""
    if (not re.fullmatch(r'[0-9]{4}[a-z]+', iana)
            or not re.fullmatch(r'[0-9]{4}\.[0-9]+(?:\.[0-9]+)?', package)
            or not re.fullmatch(r'[0-9a-f]{64}', digest)):
        raise ValueError('Expected an IANA release, tzdata version and lowercase SHA-256')
    return {'iana_version': iana, 'package_version': package, 'wheel_sha256': digest}


def fetch(url, limit, host):
    """Read a bounded HTTPS response and reject redirects away from its publisher."""
    def allowed(address):
        """Keep requests and their final destinations on the expected HTTPS origin."""
        parsed = urlsplit(address)
        return (parsed.scheme == 'https' and parsed.hostname == host
                and parsed.port in (None, 443) and not parsed.username and not parsed.password)
    if not allowed(url):
        raise ValueError('Unexpected timezone download URL')
    with urlopen(url, timeout=30) as response:
        if not allowed(response.geturl()):
            raise ValueError('Timezone download redirected to a different publisher')
        data = response.read(limit+1)
    if len(data) > limit:
        raise ValueError('Timezone download exceeded its size limit')
    return data


def wheel_record(metadata, version, expected_sha=None):
    """Select one published, non-yanked data wheel and verify an optional digest pin."""
    if metadata['info']['version'] != version:
        raise ValueError('Package metadata version mismatch')
    rows = [row for row in metadata['urls']
            if row['filename'] == f'tzdata-{version}-py2.py3-none-any.whl']
    if len(rows) != 1 or rows[0].get('yanked') or rows[0]['packagetype'] != 'bdist_wheel':
        raise ValueError('Expected exactly one non-yanked timezone wheel')
    row = rows[0]
    if expected_sha is not None and row['digests']['sha256'] != expected_sha:
        raise ValueError('Published wheel does not match the pinned SHA-256')
    return row


def check_latest(pinned):
    """Report IANA's current release and a transport candidate without updating pins."""
    current = fetch(IANA_VERSION_URL, 128, 'data.iana.org').decode('ascii').strip()
    if not re.fullmatch(r'[0-9]{4}[a-z]+', current):
        raise ValueError('Invalid IANA release response')
    metadata = json.loads(fetch('https://pypi.org/pypi/tzdata/json', 1024*1024, 'pypi.org'))
    version = metadata['info']['version']
    row = wheel_record(metadata, version)
    return {'pinned_iana_version': pinned['iana_version'], 'latest_iana_version': current,
            'iana_update_available': current != pinned['iana_version'],
            'iana_source': IANA_VERSION_URL, 'candidate_package_version': version,
            'candidate_wheel_sha256': row['digests']['sha256'],
            'note': 'Candidate data must still declare the selected IANA version and pass all tests.'}


def download_wheel(pin):
    """Fetch only the exact pinned data archive; never install or import its code."""
    version = pin['package_version']
    metadata = json.loads(fetch(f'https://pypi.org/pypi/tzdata/{version}/json',
                                1024*1024, 'pypi.org'))
    row = wheel_record(metadata, version, pin['wheel_sha256'])
    return fetch(row['url'], WHEEL_LIMIT, 'files.pythonhosted.org')


def snapshot(wheel, reference, pin):
    """Validate the complete archive and all selected rules before producing output."""
    if len(wheel) > WHEEL_LIMIT or hashlib.sha256(wheel).hexdigest() != pin['wheel_sha256']:
        raise ValueError('Timezone wheel digest or size mismatch')
    manifest = copy.deepcopy(reference)
    manifest.update(pin)
    manifest['package_source'] = f"https://pypi.org/project/tzdata/{pin['package_version']}/"
    manifest['iana_source'] = f"https://data.iana.org/time-zones/tzdb-{pin['iana_version']}/"
    files, contents = [], {}
    with zipfile.ZipFile(io.BytesIO(wheel)) as archive:
        def read_member(name, limit):
            """Read exactly one bounded allowlisted member without extracting paths."""
            # Read specific members instead of extracting paths supplied by the archive.
            matches = [item for item in archive.infolist() if item.filename == name]
            if len(matches) != 1 or matches[0].file_size > limit:
                raise ValueError('Missing, duplicate or oversized timezone member: '+name)
            return archive.read(matches[0])

        init = read_member('tzdata/__init__.py', 4096).decode('utf-8')
        for name, value in [('__version__', pin['package_version']), ('IANA_VERSION', pin['iana_version'])]:
            matches = re.findall(r'^'+name+r'\s*=\s*[\"\']([^\"\']+)[\"\']\s*$', init, re.M)
            if matches != [value]:
                raise ValueError('Archive declares a different '+name)
        for zone in sorted({row['zone'] for row in reference['countries']}):
            if not re.fullmatch(r'[A-Za-z0-9_+\-]+(?:/[A-Za-z0-9_+\-]+)+', zone):
                raise ValueError('Invalid IANA zone name: '+zone)
            data = read_member('tzdata/zoneinfo/'+zone, 1024*1024)
            _, _, footer = parse_tzif(data)
            parse_footer(footer)  # Future rules must be representable by the firmware.
            filename = zone.replace('/', '__')+'.tzif'
            if filename in contents:
                raise ValueError('Colliding timezone filenames')
            contents[filename] = data
            files.append({'zone': zone, 'file': filename, 'sha256': hashlib.sha256(data).hexdigest()})
    manifest['files'] = files
    contents['manifest.json'] = (json.dumps(manifest, indent=2)+'\n').encode('utf-8')
    return manifest, contents


def write_snapshot(output, contents):
    """Stage validated files before replacing them; preserve README and unrelated files."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.timezone-', dir=output.parent) as temporary:
        staged = Path(temporary)
        for name, data in contents.items():
            (staged/name).write_bytes(data)
        # Manifest goes last so an interrupted update cannot silently pass hash checks.
        for name in contents:
            (staged/name).replace(output/name)


def main():
    """Run release discovery or an explicit, optionally offline snapshot update."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-latest', action='store_true')
    parser.add_argument('--output', type=Path, help='Candidate or resource directory to write')
    parser.add_argument('--wheel', type=Path, help='Use a local wheel without network access')
    parser.add_argument('--iana-version')
    parser.add_argument('--package-version')
    parser.add_argument('--wheel-sha256')
    args = parser.parse_args()
    explicit = (args.iana_version, args.package_version, args.wheel_sha256)
    if args.check_latest and (args.output or args.wheel or any(explicit)):
        parser.error('--check-latest only reports releases; do not combine it with update arguments')
    if not args.check_latest and (not args.output or (any(explicit) and not all(explicit))):
        parser.error('Supply --output and either all three version/digest pins or none')
    reference, _ = load_zones()  # Retain the validated factory country/default mapping.
    if args.check_latest:
        print(json.dumps(check_latest(reference), indent=2))
        return
    pin = validate_pin(*explicit) if all(explicit) else validate_pin(
        reference['iana_version'], reference['package_version'], reference['wheel_sha256'])
    if args.wheel and args.wheel.stat().st_size > WHEEL_LIMIT:
        raise ValueError('Local timezone archive exceeded its size limit')
    wheel = args.wheel.read_bytes() if args.wheel else download_wheel(pin)
    manifest, contents = snapshot(wheel, reference, pin)
    write_snapshot(args.output, contents)
    print(f"Saved IANA {manifest['iana_version']}: {len(manifest['files'])} zones, "
          f"{len(manifest['countries'])} country keys to {args.output}")


if __name__ == '__main__':
    main()
