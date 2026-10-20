"""Negative controls for omission detection; no VMs or factory data are read."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audit_correspondence', ROOT/'tools/audit_correspondence.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class CorrespondenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Use the current reviewed snapshot, without regenerating its hashes."""
        cls.manifest = json.loads((ROOT/'reference/correspondence.json').read_text(encoding='utf-8'))

    def reject(self, mutate, message):
        """Each invalid mapping must fail for its own reason."""
        changed = deepcopy(self.manifest)
        mutate(changed)
        with self.assertRaisesRegex(ValueError, message):
            audit.audit(ROOT, changed)

    def test_current(self):
        result = audit.audit(ROOT, self.manifest)
        self.assertTrue(result['passed'])
        self.assertFalse(result['semantic_equivalence_proved'])
        self.assertEqual(result['factory_export_functions'], 176)
        # Multi-scan privacy adds two bounded source/check adapters to upload.
        self.assertEqual(result['native_app_functions'], 172)
        self.assertEqual(len(result['assembly_only']), 11)

    def test_missing_factory(self):
        self.reject(lambda m: m['factory'].pop(), 'Factory inventory differs')

    def test_duplicate_factory(self):
        self.reject(lambda m: m['factory'].append(m['factory'][0]), 'Duplicate correspondence')

    def test_wrong_native(self):
        row = next(i for i, r in enumerate(self.manifest['factory']) if r['native'])
        self.reject(lambda m: m['factory'][row]['native'].append('app/app_main.c#misspelled'), 'Unknown native target')

    def test_empty_application_target(self):
        row = next(i for i, r in enumerate(self.manifest['factory']) if r['status'] == 'source_reviewed')
        self.reject(lambda m: m['factory'][row].update(native=[]), 'no native target')

    def test_missing_reverse_row(self):
        name = next(iter(self.manifest['native_support']))
        self.reject(lambda m: m['native_support'].pop(name), 'Unaccounted native function')

    def test_stale_source(self):
        self.reject(lambda m: m['inputs'].update({'src/app/app_main.c': '0'*64}), 'Review inputs changed')

    def test_missing_jpeg_support(self):
        """The newly compiled extension must remain visible in reverse review."""
        self.reject(lambda m: m['native_support'].pop('codec/jpeg_decoder.c#jpeg_decoder_decode'),
                    'Unaccounted native function')

    def test_stale_jpeg_adapter(self):
        """Changing an adapter cannot retain an old factory/native inventory pin."""
        self.reject(lambda m: m['inputs'].update({'src/storage/jpeg_cache.c': '0'*64}),
                    'Review inputs changed')

    def test_wrong_reference(self):
        self.reject(lambda m: m['factory'][0].update(reference='reference/application.c'), 'Wrong reference')

    def test_wrong_assembly_target(self):
        self.reject(lambda m: m['assembly_only']['0x42011040'].update(native=['missing']), 'Unknown assembly-only')

    def test_parser(self):
        """Ignore fake definitions in comments/strings; handle macros and pointers."""
        with tempfile.TemporaryDirectory(dir=ROOT.parents[1]/'.build') as folder:
            path = Path(folder)/'fixture.c'
            path.write_text('/* void phantom(void) {} */\n'
                            'static void *allocate( /* pool */ int size) { return 0; }\n'
                            'CJSON_PUBLIC(int) api(void) { const char *s="void fake() {}"; return 1; }\n'
                            'static bool IRAM_ATTR timer(int x)\n{ if (x) { return true; } return false; }\n'
                            'unsigned\nsplit_return_type(void) { return 0; }\n', encoding='utf-8')
            names = [r['symbol'] for r in audit.functions(path, path.parent)]
            self.assertEqual(names, ['fixture.c#allocate', 'fixture.c#api', 'fixture.c#timer',
                                     'fixture.c#split_return_type'])


if __name__ == '__main__':
    unittest.main()
