"""Prove published boot, network and display verdicts remain independent."""
import copy
import io
import unittest
from boot_state_contract import validate_reset_boot, validate_reset_display, validate_reset_network


def fixture():
    """Build a small report containing separate positive subsystem observations."""
    sample = dict(host_seconds=.2, guest_seconds=.1, nonzero_bytes=12000, frame_sha256='a' * 64)
    return {'reset_display_observation': dict(method='bounded_post_reset_framebuffer', passed=True,
                **sample, polls=1, host_timeout=30, guest_timeout=5, samples=[copy.deepcopy(sample)]),
            'checks_by_subsystem': {
                'display': {'passed': True, 'checks': {'display_ready_after_reset': True}},
                'network': {'passed': True, 'checks': {'network_recovered_after_reset': True}}},
            'boot_observation': {'rom_boots_before_reset': 1, 'rom_boots_after_reset': 2}}


class IndependentConsumerTests(unittest.TestCase):
    def test_display_accepts_no_network_or_rom_evidence(self):
        row = fixture()
        row['checks_by_subsystem']['network'] = {'passed': False, 'checks': {}}
        row.pop('boot_observation')
        self.assertTrue(validate_reset_display(row))

    def test_network_accepts_no_display_or_rom_evidence(self):
        row = fixture()
        row.pop('reset_display_observation')
        row.pop('boot_observation')
        row['checks_by_subsystem']['display'] = {'passed': False, 'checks': {}}
        self.assertTrue(validate_reset_network(row))

    def test_rom_accepts_no_network_or_display_evidence(self):
        self.assertTrue(validate_reset_boot({'boot_observation': fixture()['boot_observation']}))

    def test_blank_or_late_display_rejected(self):
        for key, value in (('nonzero_bytes', 0), ('guest_seconds', 5), ('host_seconds', 30)):
            row = fixture()
            row['reset_display_observation'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_reset_display(row)

    def test_frame_identity_and_final_sample_required(self):
        for key, value in (('frame_sha256', 'bad'), ('nonzero_bytes', 13000), ('polls', 2)):
            row = fixture()
            row['reset_display_observation'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_reset_display(row)

    def test_network_cannot_use_display_as_evidence(self):
        row = fixture()
        row['checks_by_subsystem']['network']['checks']['display_ready_after_reset'] = True
        with self.assertRaises(ValueError):
            validate_reset_network(row)

    def test_display_cannot_use_network_as_evidence(self):
        row = fixture()
        row['checks_by_subsystem']['display']['checks']['station_dhcp'] = True
        with self.assertRaises(ValueError):
            validate_reset_display(row)

    def test_old_rom_counter_rejected(self):
        row = fixture()
        row['boot_observation']['rom_boots_after_reset'] = 1
        with self.assertRaises(ValueError):
            validate_reset_boot(row)


def run_tests():
    """Return real unittest results for the mandatory VM suite."""
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(IndependentConsumerTests))
    report = {'passed': result.wasSuccessful(), 'tests': result.testsRun, 'output': stream.getvalue()}
    if not report['passed']:
        raise AssertionError(report['output'])
    return report


if __name__ == '__main__':
    print(run_tests())
