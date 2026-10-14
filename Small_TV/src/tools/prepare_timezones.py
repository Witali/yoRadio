"""Generate immutable clock offset tables from pinned, hash-checked IANA TZif data.

Only UTC offset and DST flags are needed by the firmware. Abbreviations and city
selection remain outside its factory country-based interface. Parsing is strict:
unsupported source formats fail the build instead of silently using US DST rules.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[1]


def parse_tzif(data):
    """Read the complete 64-bit TZif block and its mandatory recurrence footer."""
    def block(position, width):
        if data[position:position+4] != b'TZif' or data[position+4:position+5] not in (b'2', b'3', b'4'):
            raise ValueError('Expected TZif version 2 or later')
        ut, std, leap, count, types, chars = struct.unpack_from('>6I', data, position+20)
        if leap or not 1 <= types <= 256:
            raise ValueError('Unexpected leap-second or type table')
        begin = position+44
        end = begin+count*(width+1)+types*6+chars+ut+std
        if end > len(data):
            raise ValueError('Truncated TZif data')
        return begin, end, count, types

    _, end, _, _ = block(0, 4)
    begin, end, count, types = block(end, 8)
    times = struct.unpack_from('>'+str(count)+'q', data, begin)
    indices = data[begin+count*8:begin+count*9]
    info = [struct.unpack_from('>iBB', data, begin+count*9+i*6) for i in range(types)]
    if any(a >= b for a, b in zip(times, times[1:])) or any(i >= types for i in indices):
        raise ValueError('Invalid TZif transition table')
    if any(dst not in (0, 1) or not -89999 <= offset <= 93599 for offset, dst, _ in info):
        raise ValueError('Invalid UTC offset or DST flag')
    footer = data[end:]
    if not footer.startswith(b'\n') or not footer.endswith(b'\n') or b'\n' in footer[1:-1]:
        raise ValueError('Missing TZif recurrence footer')
    transitions = tuple((at, *info[index][:2]) for at, index in zip(times, indices))
    return info[0][:2], transitions, footer[1:-1].decode('ascii')


def parse_footer(text):
    """Convert explicit POSIX month/week/weekday rules, including signed hours."""
    name = r'(?:[A-Za-z]{3,}|<[A-Za-z0-9+\-]{3,}>)'
    hour = r'[+\-]?\d+(?::\d{1,2}(?::\d{1,2})?)?'
    match = re.fullmatch('('+name+')('+hour+')(?:(('+name+'))('+hour+')?,([^,]+),([^,]+))?', text)
    if not match:
        raise ValueError('Unsupported or implicit POSIX recurrence: '+text)

    def seconds(value, limit):
        sign = -1 if value.startswith('-') else 1
        values = [int(v) for v in value.lstrip('+-').split(':')]
        if values[0] > limit or any(v > 59 for v in values[1:]):
            raise ValueError('Invalid POSIX time: '+value)
        return sign*sum(v*factor for v, factor in zip(values, (3600, 60, 1)))

    def rule(value):
        found = re.fullmatch(r'M(\d+)\.(\d+)\.(\d+)(?:/('+hour+'))?', value)
        if not found:
            raise ValueError('Unsupported transition rule: '+value)
        month, week, weekday = map(int, found.group(1, 2, 3))
        if not 1 <= month <= 12 or not 1 <= week <= 5 or not 0 <= weekday <= 6:
            raise ValueError('Invalid transition date')
        return month, week, weekday, seconds(found[4] or '2', 167)

    standard = -seconds(match[2], 24)
    if not match[3]:
        return standard, standard, 0, (0, 0, 0, 0), (0, 0, 0, 0)
    daylight = -seconds(match[5], 24) if match[5] else standard+3600
    return standard, daylight, 1, rule(match[6]), rule(match[7])


def load_zones():
    """Validate every retained factory country key and every pinned source hash."""
    folder = ROOT/'resources/timezones'
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    legacy = re.findall(r'\{"([^"]+)","([^"]+)"\}',
                        (ROOT/'app/services/country_timezones.h').read_text(encoding='utf-8'))
    if [(r['country'], r['legacy_tz']) for r in manifest['countries']] != legacy:
        raise ValueError('Country defaults differ from the recovered factory table')
    zones = {}
    for row in manifest['files']:
        if Path(row['file']).name != row['file']:
            raise ValueError('Timezone filename must stay within its resource folder')
        data = (folder/row['file']).read_bytes()
        if hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('Timezone hash mismatch: '+row['zone'])
        initial, transitions, footer = parse_tzif(data)
        zones[row['zone']] = initial, transitions, parse_footer(footer)
    if len(zones) != len(manifest['files']) or {r['zone'] for r in manifest['countries']} != set(zones):
        raise ValueError('Duplicate or unreferenced timezone source')
    return manifest, zones


def generate_timezones(output):
    """Deduplicate identical clock rules and write a deterministic C header."""
    manifest, zones = load_zones()
    unique = list(dict.fromkeys(zones.values()))
    text = ('/* Generated from IANA '+manifest['iana_version']+'; public-domain timezone data. */\n'
            '#pragma once\n')
    for index, (_, transitions, _) in enumerate(unique):
        if transitions:
            text += f'static const timezone_transition_t timezone_transitions_{index}[] = {{\n'
            text += ''.join('{INT64_C(%d),%d,%d},\n'%row for row in transitions)+'};\n'
    text += 'static const timezone_data_t timezone_zones[] = {\n'
    for index, (initial, transitions, footer) in enumerate(unique):
        standard, daylight, has_dst, start, end = footer
        pointer = f'timezone_transitions_{index}' if transitions else 'NULL'
        text += ('{%s,%d,%d,%d,%d,%d,%d,{%s},{%s}},\n' %
                 (pointer, len(transitions), *initial, standard, daylight, has_dst,
                  ','.join(map(str, start)), ','.join(map(str, end))))
    text += '};\nstatic const struct {const char *country; unsigned zone;} timezone_countries[] = {\n'
    for row in manifest['countries']:
        text += '{"%s",%d},\n'%(row['country'], unique.index(zones[row['zone']]))
    default = next(row for row in manifest['countries'] if row['country']==manifest['default_country'])
    text += '};\n#define TIMEZONE_DEFAULT_INDEX %d\n'%unique.index(zones[default['zone']])
    (output/'timezone_data.h').write_text(text, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    generate_timezones(args.output)
