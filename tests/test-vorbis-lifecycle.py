"""Negative controls for the real-library Vorbis QEMU result classifier."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('vorbis_lifecycle', ROOT/'tools/codec_benchmark/run_vorbis_lifecycle.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def row(run=1, **changes):
    values = dict(run=run, result=0, attempts=8, injected=0, live=0, requested=0,
                  actual=0, peak_requested=4096, peak_actual=4096, min_free=9000,
                  min_largest=8192, free=13000, largest=12288, integrity=1,
                  bad_owners=0, stack_free=12000, pcm=19200, samples=9600, sha256='a'*64)
    values.update(changes)
    return values


def line(kind, values):
    return 'VTEST_'+kind+' '+' '.join(f'{k}={v}' for k,v in values.items())+'\n'


def log(rows, fail=0):
    value = line('REGISTER', dict(count=2, actual=48, attempts=2, ledger_bytes=24576, pcm_workspace=16384))
    for r in rows:
        value += line('BEGIN', dict(run=r['run'], direct=0, fail_at=fail if r['run']==1 else 0,
                                    free=13000, largest=12288))
        if fail and r['run']==1:
            value += line('INJECT', dict(run=1, attempt=fail, phase=2, kind='calloc', bytes=80, caller='42001000'))
        value += line('RESULT', dict(r,injected=int(bool(fail) and r['run']==1)))
    return value+line('COMPLETE', dict(runs=len(rows)))


class Lifecycle(unittest.TestCase):
    def test_snapshot_sources_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            identities = runner.snapshot_sources(output)
            self.assertEqual(set(identities), set(runner.SOURCES))
            for name, digest in identities.items():
                self.assertEqual(runner.sha(output/'sources'/name), digest)
                self.assertEqual((output/'sources'/name).read_bytes(), (ROOT/name).read_bytes())

    def test_full_repeat_baseline(self):
        result = runner.assess(log([row(i) for i in range(1,101)]), cycles=100)
        self.assertTrue(result['decoder_gate_pass'])

    def test_baseline_rejects_memory_and_pcm_changes(self):
        for change in ({'live':1}, {'largest':6144}, {'free':12996}, {'integrity':0},
                       {'sha256':'b'*64}, {'bad_owners':1}, {'pcm':19000,'samples':9500}):
            with self.subTest(change=change):
                result = runner.assess(log([row(),row(2,**change)]), cycles=2)
                self.assertFalse(result['decoder_gate_pass'])

    def test_incomplete_or_duplicate_evidence(self):
        text = log([row()])
        for bad in (text.split('VTEST_COMPLETE')[0], text+line('RESULT',row()),
                    text.replace('VTEST_REGISTER','MISSING'), text+line('COMPLETE',dict(runs=1))):
            with self.assertRaises(ValueError):runner.assess(bad,cycles=1)

    def test_injection_must_be_reached_once(self):
        text = log([row(result=-2),row(2)], fail=3)
        for bad in (text.replace('VTEST_INJECT','MISSING'), text+line('INJECT',dict(attempt=3)),
                    text.replace('attempt=3','attempt=4')):
            with self.assertRaises(ValueError):runner.assess(bad,cycles=1,fail_at=3,reference=row())

    def test_original_crash_is_failure_not_harness_success(self):
        text = log([row()],fail=3).split('VTEST_RESULT')[0]+'Guru Meditation Error\n'
        result=runner.assess(text,cycles=1,fail_at=3,reference=row())
        self.assertEqual(result['status'],'CRASH')
        self.assertFalse(result['decoder_gate_pass'])

    def test_error_requires_cleanup_and_valid_recovery(self):
        original = row(result=-2, pcm=0,samples=0,sha256='e'*64)
        result=runner.assess(log([original,row(2)],fail=3),cycles=1,fail_at=3,reference=row())
        self.assertEqual(result['status'],'HANDLED')
        for bad in (row(2,result=-1),row(2,sha256='c'*64),row(2,live=1),row(2,free=12900)):
            self.assertFalse(runner.assess(log([original,bad],fail=3),cycles=1,
                                          fail_at=3,reference=row())['decoder_gate_pass'])
        result=runner.assess(log([row(result=-100),row(2)],fail=3),cycles=1,fail_at=3,reference=row())
        self.assertFalse(result['decoder_gate_pass'])

    def test_lossless_fallback_distinguished_from_silent_truncation(self):
        result=runner.assess(log([row(),row(2)],fail=3),cycles=1,fail_at=3,reference=row())
        self.assertEqual(result['status'],'TOLERATED')
        result=runner.assess(log([row(pcm=100,samples=50),row(2)],fail=3),cycles=1,fail_at=3,reference=row())
        self.assertEqual(result['status'],'UNSAFE_RETURN')

    def test_caller_at_function_end_uses_call_site(self):
        symbols=runner.symbol_table('42001000 00000020 T old_function\n42001020 00000010 T next_function\n')
        text=line('ALLOC',dict(run=1,attempt=1,phase=2,kind='calloc',id=3,ptr='3fc90000',old='00000000',
                              requested=80,actual=80,caller='42001020'))
        event=runner.allocation_ledger(text,symbols)[0]
        self.assertEqual(event['caller_function'],'old_function+0x20')
        text+=line('FREE',dict(run=1,id=3,ptr='3fc90000',caller='42001010'))+text
        self.assertEqual([e['event'] for e in runner.allocation_ledger(text)],['ALLOC','FREE','ALLOC'])

    def test_fixture_payload_and_headers(self):
        data=(ROOT/'tests/fixtures/esp32c3_calibration/vorbis-q10.ogg').read_bytes()
        info,setup=runner.headers(data)
        self.assertEqual(info[:5],b'\0\0\0\0\2')
        self.assertEqual(struct.unpack_from('<I',info,5)[0],48000)
        packed=runner.payload(data,info,setup,fail_at=4,cycles=100)
        self.assertEqual(struct.unpack_from('<8I',packed),(runner.MAGIC,1,0,4,100,len(data),len(info),len(setup)))
        damaged=bytearray(data);damaged[30]^=1
        with self.assertRaisesRegex(ValueError,'CRC'):runner.headers(damaged)
        with self.assertRaises(ValueError):runner.headers(data[:30])
        with self.assertRaises(ValueError):runner.payload(bytes(runner.APP1_SIZE),info,setup)


if __name__=='__main__':unittest.main()
