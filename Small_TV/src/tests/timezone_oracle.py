"""Execute real RV32 timezone code and libc against independently loaded IANA TZif.

Factory libc receives its literal recovered strings; discrepancies are retained.
Only environment, libc reentrancy/locking and existing LCD adapters are replaced.
Date conversion, TZ parsing, transition search and calendar arithmetic execute
from immutable ELF bytes. No SNTP transport or physical-board claim is made.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import struct
import sys
from zoneinfo import ZoneInfo
from machine_oracle import Machine, SCRATCH, ROOT
from control_oracle import verify_inputs

sys.path.insert(0, str(ROOT/'Small_TV/src/tools'))
from prepare_timezones import load_zones


class TimeMachine(Machine):
    """Keep actual Newlib algorithms, supplying only their platform dependencies."""
    def __init__(self, variant):
        super().__init__(variant)
        if self.is_factory:
            # Actual factory bootstrap at 0x4038046c sets this GP value.
            self.symbols['__global_pointer$'] = 0x3fcb49c0
            self.adapt(0x420ab200, 'tz-getenv-r', lambda: SCRATCH+0x1000)
            self.adapt(0x4038ab1e, 'libc-reent', lambda: SCRATCH+0x2000)
            self.adapt(self.symbols['__getreent'], 'rom-libc-reent', lambda: SCRATCH+0x2000)
            self.adapt(0x40381718, 'tz-lock', lambda: 0)
            self.adapt(0x403817e0, 'tz-unlock', lambda: 0)
        else:
            self.adapt(self.symbols['getenv'], 'tz-getenv', lambda: SCRATCH+0x1000)
            self.adapt(self.symbols['__getreent'], 'libc-reent', lambda: SCRATCH+0x2000)
            for name in ('__retarget_lock_acquire_recursive', '__retarget_lock_release_recursive'):
                self.adapt(self.symbols[name], name, lambda: 0)

    def set_zone(self, text):
        """Execute the real TZ parser with a synthetic, bounded environment string."""
        self.cpu.mem_write(SCRATCH+0x1000, text.encode('ascii')+b'\0')
        self.call(0x420aa9c8 if self.is_factory else self.symbols['tzset'])

    def local(self, epoch):
        """Execute actual libc localtime_r and return every standard struct tm field."""
        self.cpu.mem_write(SCRATCH+0x3000, struct.pack('<q', epoch))
        self.cpu.mem_write(SCRATCH+0x3100, bytes(64))
        result = self.call(0x420aa5ce if self.is_factory else self.symbols['localtime_r'],
                           SCRATCH+0x3000, SCRATCH+0x3100)
        if result != SCRATCH+0x3100:
            raise AssertionError('libc localtime_r failed')
        return list(struct.unpack('<9i', self.cpu.mem_read(SCRATCH+0x3100, 36)))

    def country_local(self, country, epoch):
        """Call the compiled firmware helper using its named RV32 64-bit argument ABI."""
        self.cpu.mem_write(SCRATCH+0x3200, country.encode('ascii')+b'\0')
        self.cpu.mem_write(SCRATCH+0x3100, bytes(64))
        result = self.call(self.symbols['timezone_local_time'], SCRATCH+0x3200,
                           epoch & 0xffffffff, (epoch >> 32) & 0xffffffff, SCRATCH+0x3100)
        if result != 1:
            raise AssertionError('Firmware local-time conversion failed')
        return list(struct.unpack('<9i', self.cpu.mem_read(SCRATCH+0x3100, 36)))


def expected_local(zone, epoch):
    """Use Python's independent ZoneInfo implementation, without firmware-generated tables."""
    utc = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)+dt.timedelta(seconds=epoch)
    local = utc.astimezone(zone)
    return [local.second, local.minute, local.hour, local.day, local.month-1,
            local.year-1900, (local.weekday()+1)%7, local.timetuple().tm_yday-1,
            int(local.dst() != dt.timedelta(0))]


def epochs_for(transitions, zone):
    """Include every source transition edge and future recurrence/calendar samples."""
    values = set()
    for at, _, _ in transitions:
        if -62135596800 < at < 253402300799:
            values.update((at-1, at, at+1))
    for year in (1900, 1969, 1970, 2000, 2024, 2025, 2026, 2038, 2040, 2070, 2100, 2400):
        for month in range(1, 13):
            values.add(int(dt.datetime(year, month, 1, tzinfo=dt.timezone.utc).timestamp()))
    values.update((int(dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc).timestamp())
                   for year in (2025, 2037, 2038, 2099)))
    # Discover future edges using independent ZoneInfo observations, not the
    # generator's parsed M rules or the firmware's calendar implementation.
    def state(epoch):
        local = (dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)+dt.timedelta(seconds=epoch)).astimezone(zone)
        return local.utcoffset(), local.dst()
    for year in (2026, 2038, 2100, 2400):
        begin = int(dt.datetime(year, 1, 1, tzinfo=dt.timezone.utc).timestamp())
        end = int(dt.datetime(year+1, 1, 1, tzinfo=dt.timezone.utc).timestamp())
        left, previous = begin, state(begin)
        while left < end:
            right = min(left+86400, end)
            current = state(right)
            if current != previous:
                low, high = left, right
                while high-low > 1:
                    middle = (low+high)//2
                    if state(middle) == previous:
                        low = middle
                    else:
                        high = middle
                values.update((high-1, high, high+1))
            left, previous = right, current
    return sorted(values)


def main():
    """Bind complete country results to the actual ELF, archived app and source data."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--legacy-only', action='store_true')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    verified_app = verify_inputs()
    manifest, data = load_zones()
    folder = ROOT/'Small_TV/src/resources/timezones'
    iana = {}
    for row in manifest['files']:
        with (folder/row['file']).open('rb') as stream:
            iana[row['zone']] = ZoneInfo.from_file(stream, row['zone'])
    native, factory = TimeMachine('native'), TimeMachine('factory')
    rows, examples = [], []
    for country in manifest['countries']:
        key, zone = country['country'], iana[country['zone']]
        if args.legacy_only:
            native.set_zone(country['legacy_tz'])
        factory.set_zone(country['legacy_tz'])
        literal_differences = 0
        mismatches = 0
        for month in range(1, 13):
            epoch = int(dt.datetime(2026, month, 15, tzinfo=dt.timezone.utc).timestamp())
            old, expected = factory.local(epoch), expected_local(zone, epoch)
            if args.legacy_only and native.local(epoch) != old:
                raise AssertionError('Factory/native libc literal algorithms differ')
            if old[:8] != expected[:8]:
                literal_differences += 1
                if len(examples) < 20:
                    examples.append({'country':key, 'utc_epoch':epoch, 'factory':old, 'iana':expected})
        epochs = epochs_for(data[country['zone']][1], zone) if not args.legacy_only else []
        for epoch in epochs:
            actual, expected = native.country_local(key, epoch), expected_local(zone, epoch)
            if actual != expected:
                mismatches += 1
                if mismatches <= 3:
                    print('MISMATCH', key, epoch, actual, expected, flush=True)
        rows.append({'country':key, 'zone':country['zone'], 'comparisons':len(epochs),
                     'mismatches':mismatches, 'factory_literal_differences':literal_differences,
                     'passed':not mismatches})
        print(key, 'comparisons=', len(epochs), 'mismatches=', mismatches, flush=True)
    fallback = []
    if not args.legacy_only:
        for key in ('', 'ZZ', 'gb'):
            for epoch in (1772931600, 1774745999, 1774746000, 1792890000):
                actual = native.country_local(key, epoch)
                expected = expected_local(iana['Europe/London'], epoch)
                fallback.append({'country':key, 'epoch':epoch, 'passed':actual==expected})
    invalid = []
    if not args.legacy_only:
        sentinel = struct.pack('<9i', *range(9))
        for country, epoch, null_output in (('CN', 0, True), ('CN', (1<<63)-1, False),
                                            ('CN', -(1<<63), False), ('GB', (1<<63)-1, False),
                                            ('GB', -(1<<63), False)):
            native.cpu.mem_write(SCRATCH+0x3200, country.encode('ascii')+b'\0')
            native.cpu.mem_write(SCRATCH+0x3100, sentinel)
            result = native.call(native.symbols['timezone_local_time'], SCRATCH+0x3200,
                                 epoch&0xffffffff, (epoch>>32)&0xffffffff,
                                 0 if null_output else SCRATCH+0x3100)
            invalid.append({'country':country, 'epoch':epoch, 'null_output':null_output,
                            'passed':result==0 and native.cpu.mem_read(SCRATCH+0x3100,36)==sentinel})
    archive = ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    built = ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.bin'
    app = (archive/'app.bin').read_bytes()
    if app != built.read_bytes():
        raise AssertionError('Archived and executing builds differ')
    report = {'passed':not args.legacy_only and all(r['passed'] for r in rows+fallback+invalid),
              'complete_country_set':not args.legacy_only and len(rows)==109,
              'legacy_only':args.legacy_only, 'countries':rows, 'fallback':fallback, 'invalid_inputs':invalid,
              'factory_difference_examples':examples,
              'comparisons':sum(r['comparisons'] for r in rows)+len(fallback)+len(invalid),
              'factory_literal_differences':sum(r['factory_literal_differences'] for r in rows),
              'iana_version':manifest['iana_version'],
              'timezone_manifest_sha256':hashlib.sha256((folder/'manifest.json').read_bytes()).hexdigest(),
              'app_sha256':verified_app,
              'source_sha256':json.loads((archive/'manifest.json').read_text(encoding='utf-8-sig'))['source_sha256'],
              'factory_elf_sha256':factory.source_sha, 'native_elf_sha256':native.source_sha,
              'adapters':{'factory':factory.executed_adapters, 'native':native.executed_adapters},
              'approved_fixes':['explicit-iana-country-offset-and-dst-rules'], 'scope':__doc__}
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    print('Timezone RV32:', report['comparisons'], 'comparisons; factory differences:',
          report['factory_literal_differences'], 'passed=', report['passed'], flush=True)
    raise SystemExit(0 if report['passed'] or args.legacy_only else 1)


if __name__ == '__main__':
    main()
