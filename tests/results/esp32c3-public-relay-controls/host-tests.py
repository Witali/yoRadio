import importlib.util
from pathlib import Path
import unittest

suite=unittest.TestSuite()
for path in [*sorted(Path('tests').glob('test-audio-*.py')),Path('tests/test-icy-server.py')]:
    spec=importlib.util.spec_from_file_location(path.stem.replace('-','_'),path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
with Path(__file__).with_suffix('.log').open('w') as stream:
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
print('Tests:',result.testsRun,'failures:',len(result.failures),'errors:',len(result.errors),'skipped:',len(result.skipped))
assert result.testsRun>0 and result.wasSuccessful() and not result.skipped
