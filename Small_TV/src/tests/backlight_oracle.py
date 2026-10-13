"""Compare executed factory/native LEDC initialization and brightness call traces."""
import argparse
import hashlib
import json
import struct

from machine_oracle import Machine, ROOT, SCRATCH, ELFFile


def native_layouts():
    """Read actual compiled field offsets, rather than assuming the native SDK ABI."""
    wanted = {'tv_settings_t', 'ledc_timer_config_t', 'ledc_channel_config_t'}
    layouts = {}
    with (ROOT / '.build/small-tv-esp32c2/small_tv_reconstructed.elf').open('rb') as stream:
        elf = ELFFile(stream)
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                name = die.attributes.get('DW_AT_name')
                if die.tag != 'DW_TAG_typedef' or not name or name.value.decode() not in wanted:
                    continue
                structure = die.get_DIE_from_attribute('DW_AT_type')
                layouts[name.value.decode()] = {
                    member.attributes['DW_AT_name'].value.decode():
                    member.attributes['DW_AT_data_member_location'].value
                    for member in structure.iter_children() if member.tag == 'DW_TAG_member'}
    if set(layouts) != wanted:
        raise AssertionError('Missing compiled backlight ABI')
    return layouts


class BacklightMachine(Machine):
    """Capture only LEDC calls; all decisions and duty arithmetic execute in RV32."""
    def __init__(self, variant, layouts):
        super().__init__(variant)
        self.events, self.duty, self.layouts = [], None, layouts
        addresses = (0x42014c2e, 0x42015104, 0x4201550c, 0x42014e68) if self.is_factory else (
            self.symbols['ledc_timer_config'], self.symbols['ledc_channel_config'],
            self.symbols['ledc_set_duty'], self.symbols['ledc_update_duty'])
        for address, name, callback in zip(addresses, ('timer-config', 'channel-config', 'set-duty', 'update-duty'),
                                            (self.timer, self.channel, self.set_duty, self.update_duty)):
            self.adapt(address, name, callback)

    def configuration(self, kind, names):
        """Decode factory offsets verified in 0x42008d62, or native DWARF offsets."""
        offsets = dict(zip(names, range(0, len(names) * 4, 4))) if self.is_factory else self.layouts[kind]
        return [struct.unpack('<I', self.cpu.mem_read(self.reg(10) + offsets[name], 4))[0] for name in names]

    def timer(self):
        """Record the timer's resolution, frequency, source and channel selection."""
        self.events.append(['timer', *self.configuration('ledc_timer_config_t',
            ('speed_mode', 'duty_resolution', 'timer_num', 'freq_hz', 'clk_cfg'))])
        return 0

    def channel(self):
        """Record initial duty and the active-low GPIO's complete channel fields."""
        values = self.configuration('ledc_channel_config_t',
            ('gpio_num', 'speed_mode', 'channel', 'intr_type', 'timer_sel', 'duty', 'hpoint', 'sleep_mode', 'flags'))
        self.events.append(['channel', *values])
        self.duty = values[5]
        return 0

    def set_duty(self):
        """Record a hardware duty write, including its exact integer result."""
        self.events.append(['set', self.reg(10), self.reg(11), self.reg(12)])
        self.duty = self.reg(12)
        return 0

    def update_duty(self):
        """Record the separate hardware latch operation."""
        self.events.append(['update', self.reg(10), self.reg(11)])
        return 0

    def initialize(self):
        """Execute the whole successful backlight initialization sequence."""
        self.events.clear()
        return self.call(0x42008d62 if self.is_factory else self.symbols['backlight_init'])

    def level(self, value):
        """Execute a forced duty write used by both the factory and native fade."""
        self.events.clear()
        self.call(0x42008bd2 if self.is_factory else self.symbols['backlight_set_level'], value)

    def schedule(self, minute, start=22, stop=9, day=100, night=800, enabled=1, valid=True):
        """Seed the semantic settings/time fields and execute the schedule decision."""
        self.events.clear()
        if self.is_factory:
            for offset, value in ((384, day), (400, enabled), (404, start), (408, stop), (412, night)):
                self.cpu.mem_write(0x3fcb7b9c + offset, struct.pack('<I', value))
            self.cpu.mem_write(0x3fcbffce, bytes([minute // 60, minute % 60]))
            self.call(0x42008c4c)
        else:
            fields = self.layouts['tv_settings_t']
            for name, value in (('day_level', day), ('night_level', night)):
                self.cpu.mem_write(SCRATCH + fields[name], struct.pack('<H', value))
            for name, value in (('night_start', start), ('night_stop', stop), ('night_mode', enabled)):
                self.cpu.mem_write(SCRATCH + fields[name], bytes([value]))
            self.call(self.symbols['backlight_update'], SCRATCH, minute // 60, minute % 60, int(valid))


def run_checks():
    """Check traces, not only final duty, including silent unchanged-brightness calls."""
    layouts = native_layouts()
    factory, native = BacklightMachine('factory', layouts), BacklightMachine('native', layouts)
    factory.initialize()
    result = native.initialize()
    initialization = {'factory': factory.events[:], 'native': native.events[:],
                      'passed': result == 0 and factory.events == native.events and factory.duty == native.duty}
    failures, comparisons = [], 0

    def compare(case):
        nonlocal comparisons
        comparisons += 1
        if factory.events != native.events or factory.duty != native.duty:
            if len(failures) < 8:
                failures.append({'case': case, 'factory': factory.events[:], 'native': native.events[:],
                                 'factory_duty': factory.duty, 'native_duty': native.duty})
            return False
        return True

    direct_passed = True
    for level in range(1001):
        for repeat in range(2):
            factory.level(level)
            native.level(level)
            direct_passed = compare({'level': level, 'repeat': repeat}) and direct_passed
    factory.initialize()
    native.initialize()
    schedule_passed, schedules = True, []
    for start in range(18, 24):
        for stop in range(5, 13):
            passed = True
            for minute in range(1440):
                for valid in (True, False):
                    factory.schedule(minute, start, stop, valid=valid)
                    native.schedule(minute, start, stop, valid=valid)
                    passed = compare({'start': start, 'stop': stop, 'minute': minute, 'valid': valid}) and passed
            schedules.append({'start': start, 'stop': stop, 'calls': 2880, 'passed': passed})
            schedule_passed = passed and schedule_passed
    parameter_passed = True
    for level in range(1001):
        for enabled in (0, 1):
            for repeat in range(2):
                factory.schedule(12 * 60 + 1, day=level, night=level, enabled=enabled)
                native.schedule(12 * 60 + 1, day=level, night=level, enabled=enabled)
                parameter_passed = compare({'configured_level': level, 'enabled': enabled, 'repeat': repeat}) and parameter_passed
    guards = []
    for value in (1001, 2000, 0xffffffff):
        native.level(value)
        guards.append({'input': value, 'passed': native.events == [['set', 0, 0, 8191], ['update', 0, 0]]})
    # The original caches the scheduled level, not the actual level after fade.
    # Record that literal difference, then require configured duty to be restored.
    photo = []
    for level in (0, 1, 100, 500, 1000):
        factory.initialize()
        native.initialize()
        factory.schedule(720, day=level, enabled=0)
        native.schedule(720, day=level, enabled=0)
        factory.level(0)
        native.level(0)
        factory.schedule(720, day=level, enabled=0)
        native.schedule(720, day=level, enabled=0)
        photo.append({'configured_level': level, 'literal_factory_duty': factory.duty,
                      'native_duty': native.duty, 'factory': factory.events[:], 'native': native.events[:],
                      'passed': native.duty == level * 8191 // 1000 and
                                native.events == ([] if level == 0 else [['set', 0, 0, level * 8191 // 1000], ['update', 0, 0]])})
    return {'passed': initialization['passed'] and direct_passed and schedule_passed and parameter_passed and
                      all(row['passed'] for row in guards + photo),
            'initialization': initialization, 'direct_levels': 1001, 'comparisons': comparisons,
            'schedules': schedules, 'guards': guards, 'photo_restore': photo, 'first_failures': failures,
            'factory_elf_sha256': factory.source_sha, 'native_elf_sha256': native.source_sha,
            'approved_fix': 'photo fade must restore configured duty even when the original schedule cache did not change',
            'scope': 'Executed LEDC initialization, duty arithmetic and conditional schedule call traces; successful driver boundaries are captured. RF, electrical PWM and SDK locking are outside scope.'}


def main():
    """Save the exact executable identities and fail on unexpected trace differences."""
    from control_oracle import verify_inputs
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    app_sha = verify_inputs()
    report = run_checks()
    report['app_sha256'] = app_sha
    report['source_sha256'] = json.loads((ROOT / 'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text())['source_sha256']
    from pathlib import Path
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Backlight RV32:', report['comparisons'], 'comparisons; passed=', report['passed'])
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
