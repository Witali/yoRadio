"""Pure rate protocol/source selection checks; no SDK or metadata executable."""
import ast
import copy
from pathlib import Path
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / 'tests/run-vorbis-xiph-rate-qemu.py'
subject = types.ModuleType('rate_metadata_controller_under_test')
subject.__file__ = str(CONTROLLER)
exec(compile(CONTROLLER.read_bytes(), str(CONTROLLER), 'exec'), subject.__dict__)
BASE, PORT, FIXTURE = 'a' * 64, 'b' * 64, 'c' * 64


def log():
    return '\n'.join([
        'I (1) boot: independent metadata fixture',
        'RATE_BEGIN coordinator=0 worker=1 base=' + BASE + ' port=' + PORT + ' fixture=' + FIXTURE + ' expected=37',
        'RATE_WORKER core=1 priority=0 stack=16384',
        'RATE_ABI long_bits=32 rate_bits=32 info_bytes=32 alignment=4 rate_offset=8 unsigned=1 overlay=1',
        'RATE_PASS cases=37 live=0 bytes=0 core=1 minimum_free=200000 remaining_stack=15000',
        'RATE_STOP status=PASSED'
    ]) + '\n'


class RateProtocol(unittest.TestCase):
    def test_complete_exact_metadata_run(self):
        actual = subject.validate_log(log(), BASE, PORT, FIXTURE, 37)
        self.assertEqual(actual, dict(cases=37, live=0, bytes=0, coordinator_core=0,
            worker_core=1, priority=0, configured_stack=16384, protocol_lines=5,
            rate_source_unsigned=True, long_bits=32, rate_bits=32, info_bytes=32,
            info_alignment=4, rate_offset=8, minimum_free=200000, remaining_stack=15000))

    def test_wrong_count_identity_ownership_core_and_extra_fields_fail(self):
        original = log()
        for changed in (
            original.replace('cases=37', 'cases=38'), original.replace('live=0', 'live=1'),
            original.replace('bytes=0', 'bytes=1'), original.replace('core=1', 'core=0'),
            original.replace(BASE, 'd' * 64), original.replace(PORT, 'd' * 64),
            original.replace(FIXTURE, 'd' * 64), original.replace('status=PASSED', 'status=FAILED'),
            original.replace('live=0', 'live=0 live=0'), original.replace('stack=16384', 'stack=32768'),
            original.replace('priority=0', 'priority=3'),
            original.replace('minimum_free=200000', 'minimum_free=0'),
            original.replace('remaining_stack=15000', 'remaining_stack=16385')):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                subject.validate_log(changed, BASE, PORT, FIXTURE, 37)
        for count in (0, -1, True):
            with self.subTest(count=count), self.assertRaises(ValueError):
                subject.validate_log(original, BASE, PORT, FIXTURE, count)

    def test_wrong_source_type_abi_or_overlay_fails(self):
        original = log()
        for before, after in (('long_bits=32', 'long_bits=64'),
            ('rate_bits=32', 'rate_bits=64'), ('info_bytes=32', 'info_bytes=40'),
            ('alignment=4', 'alignment=8'), ('rate_offset=8', 'rate_offset=12'),
            ('unsigned=1', 'unsigned=0'), ('overlay=1', 'overlay=0')):
            with self.subTest(before=before), self.assertRaises(ValueError):
                subject.validate_log(original.replace(before, after), BASE, PORT, FIXTURE, 37)

    def test_missing_duplicate_reordered_and_torn_events_fail(self):
        lines = log().splitlines()
        for changed in (
            lines[:2] + lines[3:], lines + [lines[-1]],
            lines[:2] + [lines[3], lines[2]] + lines[4:],
            lines[:3] + ['I (2) ' + lines[3]] + lines[4:],
            lines + ['RATE_UNKNOWN value=1']):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                subject.validate_log('\n'.join(changed), BASE, PORT, FIXTURE, 37)

    def test_runtime_diagnostics_are_never_filtered(self):
        for message in ('Task watchdog got triggered', 'task_wdt: timeout',
            'Guru Meditation', 'Backtrace:', 'CORRUPT HEAP', 'assert failed',
            'stack overflow', 'timed out'):
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, 'native diagnostic'):
                subject.validate_log(log() + message + '\n', BASE, PORT, FIXTURE, 37)

    def test_exact_thirty_seven_compilation_rows(self):
        folder = (ROOT / '.build/rate-protocol-virtual').resolve()
        generated = folder / 'generated'
        fixtures = [('fixture', folder / 'main.c'),
            ('vorbis_xiph_alloc.c', folder / 'vorbis_xiph_alloc.c'),
            ('vorbis_xiph_rate.c', folder / 'vorbis_xiph_rate.c')]
        fixtures += [(name, folder / name) for name in subject.HEADER_PROBES]
        units = ['upstream/libvorbis/lib/' + name + '.c' for name in subject.VORBIS_UNITS]
        units += ['upstream/libogg/src/bitwise.c', 'upstream/libogg/src/framing.c']
        porting = dict(compiled_units=[dict(original=name,
            compiled=('ported/' + Path(name).name if name in subject.PORTED_UNITS else 'base/' + name))
            for name in units])
        sources = fixtures + [(row['original'], generated / row['compiled'])
            for row in porting['compiled_units']]
        database = [dict(file=str(path), command='pure-fixture-only', output=str(index) + '.o')
            for index, (_, path) in enumerate(sources)]
        selected = subject.validate_compile_sources(database, fixtures, porting, generated)
        self.assertEqual(len(selected), 37)
        self.assertEqual(set(selected), {name for name, _ in sources})
        for changed in (database[:-1], database + [database[-1]], database[1:]):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                subject.validate_compile_sources(changed, fixtures, porting, generated)
        with self.assertRaises(ValueError):
            subject.validate_compile_sources(database, fixtures[:-1], porting, generated)
        changed = copy.deepcopy(porting)
        changed['compiled_units'][0]['compiled'] = 'base/' + changed['compiled_units'][0]['original']
        with self.assertRaises(ValueError):
            subject.validate_compile_sources(database, fixtures, changed, generated)

    def test_project_scope_and_every_public_entry_order(self):
        project = ROOT / 'tests/target/vorbis_xiph_rate_qemu'
        source = (project / 'main/main.c').read_text()
        self.assertNotRegex(source,
            r'\b(?:vorbis_synthesis|vorbis_synthesis_init|vorbis_synthesis_blockin|vorbis_synthesis_trackonly|vorbis_dsp_clear|vorbis_block_init|xiph_dsp_tests|xiph_header_tests|esp_task_wdt_delete|esp_task_wdt_deinit|esp_task_wdt_reconfigure)\s*\(')
        self.assertIn('xiph_rate_tests()', source)
        self.assertIn('configUSE_TIME_SLICING != 1', source)
        self.assertIn('NULL, 0, NULL, 1', source)
        config = (project / 'sdkconfig.esp32.defaults').read_text()
        for name in ('CONFIG_ESP_TASK_WDT_EN', 'CONFIG_ESP_TASK_WDT_INIT',
            'CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0', 'CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1'):
            self.assertIn(name + '=y', config)
        orders = set()
        for name in subject.HEADER_PROBES:
            body = (project / 'main' / name).read_text()
            order = tuple(line for line in body.splitlines() if line.startswith('#include "vorbis/'))
            self.assertEqual(len(order), 3)
            self.assertIn('#include "layout_probe.h"', body)
            self.assertIn('#define OV_EXCLUDE_STATIC_CALLBACKS 1', body)
            orders.add(order)
        self.assertEqual(len(orders), 6)
        tree = ast.parse(CONTROLLER.read_text())
        self.assertTrue(any(isinstance(node, ast.FunctionDef) and node.name == 'validate_log'
            for node in tree.body))
        self.assertIn('decoder_symbols_may_be_retained', CONTROLLER.read_text())


if __name__ == '__main__':
    unittest.main()
