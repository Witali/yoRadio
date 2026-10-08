import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('evidence_tests', 'tests/test-flac-rice-physical-evidence.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.DATA=Path('.build/c3-flac-rice-20261008')
names=['test_missing_cpu_samples_cannot_be_complete',
       'test_malformed_cpu_and_interruption_cannot_be_complete',
       'test_missing_dma_and_zero_audio','test_canonical_runtime_faults_are_preserved']
suite=unittest.TestSuite(module.RicePhysicalEvidence(name) for name in names)
raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
