"""Focused synthetic-log controls only; no codec, SDK, QEMU or target faults."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'tests/fixtures/flac_ordinary_task/observer.py'
spec = importlib.util.spec_from_file_location('ordinary_flac_reader_control', SOURCE)
observer = importlib.util.module_from_spec(spec); spec.loader.exec_module(observer)
refusals = []


def event(tag, **values):
    return tag + ' ' + ' '.join(key + '=' + str(value) for key, value in values.items())


def model():
    fixtures = [dict(name='unused-model-' + str(index), pcm_bytes=4096, pcm_sha256='a'*64) for index in range(127)]
    fixtures += [dict(name=name, pcm_bytes=33316 if index == 2 else 4096, pcm_sha256='a'*64)
                 for index, name in enumerate(observer.FIXTURES)]
    lines = [event('CYD_FLAC_TASK_BOOT', actual_audio_service_tu=1, sdk='v6.0.2',
                   core0_stream=1, core1_decode_output=1, hardware=0), event('CYD_FLAC_ORDINARY_CONFIG', **observer.CONFIG)]
    for index, flag in enumerate(('ordered_eof', 'stop_reopen', 'maintenance_resume')):
        lines.append(event('CYD_FLAC_TASK_CASE', id='T'+str(index), **{flag: 1}, byte_compare=1,
                           pcm_bytes=33316 if index == 2 else 4096))
    lines.append(event('CYD_FLAC_ORDINARY_POSITIVE_BEGIN', minimum_us=15000000, deadline_us=90000000, started_us=1000000))
    for index in range(2):
        lines.append(event('CYD_FLAC_ORDINARY_ITERATION', index=index, elapsed_us=(index+1)*8000000,
            pcm_bytes=33316, sha256='a'*64, created=index+6, destroyed=index+6, http_cleanup=index+6,
            writes=(index+1)*16, layouts=(index+1)*16, gains=(index+1)*16, feed_calls=(index+1)*48,
            decode_calls=(index+1)*32, max_decode_call_us=9000, heap_free=64000, heap_min=60000,
            heap_largest=32000, internal_free=64000, internal_largest=32000, dma_free=32000,
            dma_largest=16000, stream_stack_free=2048, decode_stack_free=3072, output_stack_free=1024,
            idle0_status=0, idle1_status=0, workspace=0, live_decoders=0, live_clients=0,
            allocation_failures=0, decoder_failures=0, stream_failures=0, output_failures=0))
    lines.append(event('CYD_FLAC_ORDINARY_POSITIVE_END', iterations=2, elapsed_us=16000100, last_completion_us=16000000,
                       minimum_us=15000000, deadline_us=90000000))
    lines.append(event('CYD_FLAC_ORDINARY_COMPLETE', original_cases=3, positive_iterations=2,
        actual_audio_service_tu=1, created=7, destroyed=7, real_http_cleanup=7, writes=32, layouts=32,
        gains=32, core_bindings=1, hardware=0, real_output_driver=0, oom_injection=0,
        deliberate_backpressure=0, semantic_fault_controls=0))
    return lines, fixtures


class Controls(unittest.TestCase):
    def reject(self, label, lines, fixtures=None):
        if fixtures is None:
            fixtures = model()[1]
        with self.subTest(label=label), self.assertRaises(ValueError):
            observer.parse('\n'.join(lines), fixtures)
        refusals.append(label)

    def test_complete_model_and_colored_sdk_lines(self):
        lines, fixtures = model()
        result = observer.parse('\n'.join(['\x1b[0;32mI (1) heap_init: startup\x1b[0m', *lines]), fixtures)
        self.assertEqual(len(result['positive_iterations']), 2)
        self.assertFalse(result['physical_hardware'])
        self.assertFalse(result['actual_output_driver'])

    def test_production_policy(self):
        for key, value in observer.CONFIG.items():
            lines, _ = model(); lines[1] = lines[1].replace(key+'='+str(value), key+'='+str(value+1), 1)
            self.reject('policy-'+key, lines)

    def test_original_lifecycle_presence_and_pcm(self):
        for index in (2, 3, 4):
            lines, _ = model(); del lines[index]; self.reject('missing-T'+str(index-2), lines)
        lines, _ = model(); lines[2] = lines[2].replace('pcm_bytes=4096', 'pcm_bytes=4095'); self.reject('partial-original-PCM', lines)
        lines, _ = model(); lines[2], lines[3] = lines[3], lines[2]; self.reject('reordered-original', lines)

    def test_positive_length_hash_time_and_owners(self):
        changes = dict(index=3, elapsed_us=0, pcm_bytes=33315, created=5, destroyed=5,
                       http_cleanup=5, layouts=15, gains=15, feed_calls=0, decode_calls=0,
                       max_decode_call_us=0, heap_free=0, heap_min=65000, heap_largest=65000,
                       internal_largest=65000, dma_largest=33000, stream_stack_free=6145,
                       decode_stack_free=16385, output_stack_free=4097, idle0_status=1,
                       idle1_status=1, workspace=1, live_decoders=1, live_clients=1,
                       allocation_failures=1, decoder_failures=1, stream_failures=1, output_failures=1)
        for key, value in changes.items():
            lines, _ = model(); row=observer.fields(lines[6], 'CYD_FLAC_ORDINARY_ITERATION'); row[key]=value
            lines[6]=event('CYD_FLAC_ORDINARY_ITERATION', **row); self.reject('iteration-'+key, lines)
        lines, _ = model(); lines[6] = lines[6].replace('sha256='+'a'*64, 'sha256='+'b'*64); self.reject('different-PCM-hash', lines)
        lines, _ = model(); lines[7] = lines[7].replace('elapsed_us=16000000', 'elapsed_us=90000000'); self.reject('whole-phase-deadline', lines)
        lines, _ = model(); lines[6] = lines[6].replace('elapsed_us=8000000', 'elapsed_us=15000000'); self.reject('extra-file-after-minimum', lines)

    def test_watchdog_warning_without_reset(self):
        for warning in ('E (17000) task_wdt: Task watchdog got triggered.',
                        '\x1b[0;33mW (17000) task_wdt: stalled idle owner\x1b[0m',
                        'Interrupt wdt timeout on CPU1', 'watchdog timeout on CPU0'):
            lines, _ = model(); lines.insert(7, warning); self.reject('actual-warning-'+warning, lines)

    def test_missing_or_extra_terminals(self):
        lines, _ = model(); self.reject('missing-final', lines[:-1])
        lines, _ = model(); self.reject('missing-positive-end', lines[:-2]+lines[-1:])
        lines, _ = model(); self.reject('duplicate-final', lines+[lines[-1]])
        lines, _ = model(); lines[-1] = lines[-1].replace('real_output_driver=0', 'real_output_driver=1'); self.reject('invented-driver-claim', lines)
        lines, _ = model(); lines[-2] = lines[-2].replace('iterations=2', 'iterations=1'); self.reject('wrong-terminal-count', lines)

    def test_duplicate_unknown_and_bad_numeric_fields(self):
        lines, _ = model(); lines[6] += ' writes=16'; self.reject('duplicate-field', lines)
        lines, _ = model(); lines[6] += ' repaired_status=0'; self.reject('unknown-field', lines)
        lines, _ = model(); lines[6] = lines[6].replace('writes=16', 'writes=-16'); self.reject('negative-count', lines)
        lines, fixtures = model(); self.reject('missing-fixture', lines, fixtures[:-1])


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    pins={}
    for source in (SOURCE, Path(__file__).resolve()):
        data=source.read_bytes(); relative=source.relative_to(ROOT); target=args.output/'sources'/relative
        target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
        pins[relative.as_posix()]=hashlib.sha256(data).hexdigest()
    output = io.StringIO(); result = unittest.TextTestRunner(stream=output, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
    (args.output/'controls.log').write_text(output.getvalue(), encoding='utf-8')
    current=all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest for name,digest in pins.items())
    report=dict(passed=result.wasSuccessful() and current, synthetic_log_models_only=True, native_execution=False,
                target_fault_controls=False, groups=result.testsRun, modeled_refusals=refusals, source_sha256=pins,
                sources_unchanged=current, command=[sys.executable,*sys.argv], python_version=sys.version,
                python_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest())
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k in ('passed','synthetic_log_models_only','native_execution','target_fault_controls','groups','sources_unchanged')},indent=2))
    print('modeled_refusals='+str(len(refusals)))
    if not report['passed']:
        print(output.getvalue()); raise SystemExit(1)


if __name__ == '__main__':
    main()
