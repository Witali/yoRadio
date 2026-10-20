"""Synthetic host protocol tests; no SDK/compiler/QEMU/codec execution."""
import hashlib
from pathlib import Path
import re
import unittest
from c3_vorbis_format_protocol import fixture_accounting, validate_log as validate_protocol

HERE = Path(__file__).resolve().parent
HEADER = (HERE/'fixture.h').read_text()

def validate_log(log,scope,control,header,**facts):
    # All logs here are synthetic; supply explicit synthetic process facts.
    return validate_protocol(log,scope,control,header,returncode=facts.get('returncode',0),timed_out=facts.get('timed_out',False))

def protocol(scope='acceptance', control=None):
    sizes,pcm = fixture_accounting(HEADER)
    rows = [f'BEGIN expected_rejection={int(scope == "baseline")} coordinator=0',
            'VENDOR_OPEN rate=192000 long=8192 result=0 handle=1']
    rows += [f'VENDOR_PACKET packet={i} consumed={n} pcm={pcm(8192)[i]} sample_rate=192000 channel=2 bits=16 canaries=1 core=0' for i,n in enumerate(sizes)]
    rows += ['VENDOR_COMPLETE packets=68 pcm=1089792 nonzero=1080420 full8192=66']
    pairs = [(48000,2048),(192000,8192),(64000,8192)]
    if scope == 'acceptance' and not control: pairs += [(63999,8192),(48000,8192)]
    for rate,long in pairs:
        ref = 192000 if long == 8192 else rate
        rows += [f'PAIR_PACKET rate={rate} long={long} packet={i} consumed={n} pcm={pcm(long)[i]} '
                 f'vendor_expected_rate={ref} vendor_rate={ref} checked_expected_rate={rate} checked_rate={rate} '
                 'expected_channel=2 vendor_channel=2 checked_channel=2 expected_bits=16 vendor_bits=16 checked_bits=16 exact=1 canaries=1 core=0'
                 for i,n in enumerate(sizes)]
        rows += [f'EXACT rate={rate} long={long} packets=68 pcm={sum(pcm(long))} full8192={pcm(long).count(16384)}']
    if control: rows += ['FAILURE legal_candidate_open_required']
    else:
        if scope == 'baseline': rows += [f'LEGAL_REJECT rate={rate} long=8192 result=-1 header_error=1' for rate in (63999,48000)]
        rows += [f'INVALID_REJECT case={name} result=-1 header_error=1' for name in ('zero_rate','short32','long16384','short_exceeds_long')]
        rows += [('BASELINE low_rejected=2' if scope == 'baseline' else 'COMPLETE low_exact=2')+' high_exact=2 normal_exact=1 invalid_rejected=4 core=0']
    return '\n'.join('C3_VORBIS_FORMAT_'+row for row in rows)

class Protocol(unittest.TestCase):
    def test_real_api_requires_both_process_facts(self):
        for facts in ({},dict(returncode=0),dict(timed_out=False)):
            with self.subTest(facts=facts),self.assertRaises(TypeError): validate_protocol(protocol(),'acceptance',None,HEADER,**facts)

    def test_exact_fixture_and_positive_scopes(self):
        self.assertEqual(hashlib.sha256((HERE/'fixture.h').read_bytes()).hexdigest(),'839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378')
        for scope,control,lines,pairs in (('baseline',None,285,3),('acceptance',None,421,5),('acceptance','old-guard',279,3)):
            with self.subTest(scope=scope,control=control):
                result = validate_log(protocol(scope,control),scope,control,HEADER,returncode=0)
                self.assertEqual((result['protocol_lines'],result['exact_pair_packets']),(lines,pairs*68))
                self.assertEqual(result['vendor_packets'],68)

    def test_wrong_or_mixed_prefix_and_wrong_core(self):
        log = protocol()
        for wrong in (log.replace('C3_VORBIS_FORMAT_','CYD_VORBIS_FORMAT_'),
                      log+'\nCYD_VORBIS_FORMAT_BEGIN expected_rejection=0 coordinator=0',
                      log.replace('C3_VORBIS_FORMAT_','prefix C3_VORBIS_FORMAT_',1),
                      log.replace('core=0','core=1',1),log.replace('coordinator=0','coordinator=1',1)):
            with self.subTest(log=wrong[:70]),self.assertRaises(RuntimeError): validate_log(wrong,'acceptance',None,HEADER)

    def test_missing_duplicate_reordered_or_inexact_packet(self):
        log = protocol(); rows = log.splitlines(); changed = rows[:]
        changed[3],changed[4] = changed[4],changed[3]
        for wrong in ('\n'.join(rows[:3]+rows[4:]),log+'\n'+rows[2],'\n'.join(changed),
                      log.replace('consumed=32','consumed=31',1),log.replace('canaries=1','canaries=0',1),
                      log.replace('exact=1','exact=0',1),log.replace('pcm=1089792','pcm=1089791',1)):
            with self.assertRaises(RuntimeError): validate_log(wrong,'acceptance',None,HEADER)

    def test_zero_and_mismatched_metadata_including_priming(self):
        rows = protocol().splitlines()
        for index,line in enumerate(rows):
            if 'PACKET ' not in line or not (' packet=0 ' in line or ' packet=1 ' in line): continue
            fields = ('sample_rate','channel','bits') if 'VENDOR_PACKET' in line else (
                'vendor_rate','checked_rate','vendor_channel','checked_channel','vendor_bits','checked_bits')
            for field in fields:
                for value in (0,1):
                    bad = rows[:]; bad[index] = re.sub(r'\b'+field+r'=\d+',field+'='+str(value),line,count=1)
                    with self.subTest(line=index,field=field,value=value),self.assertRaises(RuntimeError): validate_log('\n'.join(bad),'acceptance',None,HEADER)

    def test_generic_error_is_not_header_rejection(self):
        for scope in ('baseline','acceptance'):
            log = protocol(scope)
            for bad in (log.replace('header_error=1','header_error=0',1),log.replace(' header_error=1','',1),
                        log.replace('result=-1 header_error=1','result=0 header_error=1',1)):
                with self.assertRaises(RuntimeError): validate_log(bad,scope,None,HEADER)

    def test_control_needs_exact_failure_after_all_prerequisites(self):
        log = protocol('acceptance','old-guard')
        early = '\n'.join(log.splitlines()[:2]+['C3_VORBIS_FORMAT_FAILURE legal_candidate_open_required'])
        for bad in (early,log.replace('legal_candidate_open_required','vendor_high8192_metadata'),
                    log.replace('VENDOR_COMPLETE','VENDOR_INCOMPLETE'),log+'\nassert failed'):
            with self.assertRaises(RuntimeError): validate_log(bad,'acceptance','old-guard',HEADER)

    def test_process_timeout_panic_and_scope_failures(self):
        log = protocol()
        for facts in (dict(returncode=None),dict(returncode=False),dict(returncode=1),dict(returncode=-15),dict(timed_out=True),dict(timed_out=None)):
            with self.subTest(facts=facts),self.assertRaises(RuntimeError): validate_log(log,'acceptance',None,HEADER,**facts)
        for marker in ('Guru Meditation Error','abort()','Backtrace:','assert failed','CORRUPT HEAP','timed out','TimeoutExpired'):
            with self.subTest(marker=marker),self.assertRaises(RuntimeError): validate_log(log+'\n'+marker,'acceptance',None,HEADER)
        for scope,control in (('unknown',None),('baseline','old-guard'),('acceptance','wrong-control')):
            with self.assertRaises(RuntimeError): validate_log(log,scope,control,HEADER)
        with self.assertRaises(RuntimeError): validate_log(protocol('baseline'),'acceptance',None,HEADER)

if __name__ == '__main__': unittest.main()
