"""Pure synthetic protocol regressions; never invokes a codec, SDK or target."""
import hashlib
from pathlib import Path
import re
import unittest
import rate_protocol as protocol

HERE=Path(__file__).resolve().parent
FIXTURE=HERE.parents[1]/'tests/target/cyd_vorbis_format_qemu/main/fixture.h'
RATES=(48000,44100,32000,24000,22050,16000,12000,11025,8000,1,63999,64000,
       192000,2147483647,2147483648,4294967295)
FACTS=dict(returncode=0,timed_out=False,interrupted=False)

def fixture():
    raw=FIXTURE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=protocol.FIXTURE_SHA256: raise RuntimeError('Canonical fixture changed')
    def array(name):
        text=re.search(r'\b'+name+r'\[\]\s*=\s*\{([^}]+)\}',raw.decode()).group(1)
        return [int(v) for v in text.split(',') if v.strip()]
    offsets,modes=array('fixture_offsets'),array('fixture_long_mode')
    sizes=[b-a for a,b in zip(offsets,offsets[1:])]
    blocks=[2048 if m else 256 for m in modes]
    pcm=[0]+[a+b for a,b in zip(blocks,blocks[1:])]
    return sizes,pcm

def synthetic(mode='acceptance',control=None):
    sizes,pcms=fixture()
    rows=[f'BEGIN expected_unsigned_rejection={int(mode=="baseline")} limited_policy={int(mode=="limited")} '
          'cases=16 short=256 long=2048 golden_rate=192000 coordinator=0','WORKER core=1',
          'ZERO_REJECT rate=0 result=-1 handle=0 handles_closed=1 core=1']
    accepted=rejected=paired=total=0
    for index,rate in enumerate(RATES):
        coord=f'index={index} rate={rate}'
        reject=(mode=='baseline' and rate>2147483647) or (mode=='limited' and rate>=64000)
        effective=control is not None and rate==2147483648
        bad_open=reject if not effective else control=='signed-validity'
        result=-1 if bad_open else 0
        rows += [f'CASE_OPEN {coord} golden_rate=192000 vendor_open=0 checked_open={result} vendor_handle=1 checked_handle={int(not bad_open)} header_error={int(bad_open)} core=1']
        if effective:
            rows += ['FAILURE '+('legal_unsigned_rate_open_required' if control=='signed-validity' else 'limited_rate_rejection_required')]
            break
        if reject:
            rows += [f'CASE_REJECT {coord} result=-1 header_error=1 handles_closed=1 core=1']; rejected+=1
            continue
        for packet,(size,pcm) in enumerate(zip(sizes,pcms)):
            rows += [f'PACKET {coord} packet={packet} expected={size} vendor_consumed={size} checked_consumed={size} pcm={pcm} '
                f'vendor_rate=192000 checked_rate={rate} vendor_channel=2 checked_channel=2 vendor_bits=16 checked_bits=16 '
                f'exact=1 canaries=1 nonzero={int(pcm>0)} core=1']
        rows += [f'CASE_COMPLETE {coord} packets=68 pcm={sum(pcms)} nonzero=67 handles_closed=1 core=1']
        accepted+=1; paired+=68; total+=sum(pcms)
    if not control: rows += [f'COMPLETE cases=16 accepted={accepted} rejected={rejected} paired_packets={paired} pcm={total} zero_rejected=1 core=1']
    return '\n'.join(protocol.PREFIX+row for row in rows)+'\n'


class RateProtocol(unittest.TestCase):
    def validate(self,text,mode='acceptance',control=None,**facts):
        return protocol.validate_log(text,mode,control,**(FACTS|facts))
    def rejects(self,text,mode='acceptance',control=None,**facts):
        with self.assertRaises(RuntimeError): self.validate(text,mode,control,**facts)
    def test_actual_fixture_and_all_sixteen_rates(self):
        sizes,pcm=fixture()
        self.assertEqual(tuple(sizes),protocol.PACKET_SIZES); self.assertEqual(tuple(pcm),protocol.PCM_SIZES)
        self.assertEqual(sum(pcm),272640); self.assertEqual(len(sizes),68); self.assertEqual(protocol.RATES,RATES)
    def test_three_complete_modes(self):
        expected={'acceptance':(16,0,1088,4362240,1124),'baseline':(14,2,952,3816960,988),'limited':(11,5,748,2999040,784)}
        for mode,counts in expected.items():
            with self.subTest(mode=mode):
                r=self.validate(synthetic(mode),mode)
                self.assertEqual(tuple(r[k] for k in ('accepted','rejected','paired_packets','pcm_bytes','protocol_lines')),counts)
                self.assertIsNone(r['exact_failure']); self.assertEqual(r['zero_rejected'],1)
    def test_named_controls_only_at_unsigned_boundary(self):
        for mode,control,accepted,rejected,lines,reason in (
            ('acceptance','signed-validity',14,0,985,'legal_unsigned_rate_open_required'),
            ('limited','signed-policy',11,3,781,'limited_rate_rejection_required')):
            with self.subTest(control=control):
                text=synthetic(mode,control); r=self.validate(text,mode,control)
                self.assertEqual((r['accepted'],r['rejected'],r['protocol_lines']),(accepted,rejected,lines))
                self.assertEqual(r['exact_failure'],reason)
                self.rejects(text,mode)
                self.rejects(synthetic(mode),mode,control)
    def test_unknown_or_incompatible_mode_and_controls(self):
        text=synthetic()
        for mode,control in (('unknown',None),('baseline','signed-validity'),('acceptance','signed-policy'),('limited','signed-validity'),('acceptance','skip')):
            with self.subTest(mode=mode,control=control): self.rejects(text,mode,control)
    def test_control_requires_exact_public_header_error_witness(self):
        text=synthetic('acceptance','signed-validity')
        self.rejects(text.replace('checked_open=-1 vendor_handle=1 checked_handle=0 header_error=1',
                                 'checked_open=-4 vendor_handle=1 checked_handle=0 header_error=0',1),'acceptance','signed-validity')
        self.rejects(text.replace('header_error=1 core=1','header_error=0 core=1',1),'acceptance','signed-validity')
        self.rejects(text.replace(' header_error=1 core=1',' core=1',1),'acceptance','signed-validity')
    def test_real_process_facts_required(self):
        text=synthetic()
        for facts in ({'returncode':1},{'returncode':-1},{'returncode':3199971767},{'returncode':None},{'returncode':False},
                      {'timed_out':True},{'timed_out':None},{'interrupted':True},{'interrupted':None}):
            with self.subTest(facts=facts): self.rejects(text,**facts)
        with self.assertRaises(TypeError): protocol.validate_log(text,'acceptance')
    def test_native_prefix_and_actual_cores(self):
        text=synthetic()
        for before,after in (('coordinator=0','coordinator=1'),('WORKER core=1','WORKER core=0'),('core=1','core=0'),
                             ('CYD_VORBIS_RATE_','C3_VORBIS_RATE_'),('CYD_VORBIS_RATE_PACKET','noise CYD_VORBIS_RATE_PACKET')):
            with self.subTest(after=after): self.rejects(text.replace(before,after,1))
    def test_missing_duplicate_reordered_and_trailing_lines(self):
        lines=synthetic().splitlines()
        for text in ('\n'.join(lines[:8]+lines[9:]),'\n'.join(lines[:8]+[lines[8]]+lines[8:]),
                     '\n'.join(lines[:8]+[lines[9],lines[8]]+lines[10:]),'\n'.join(lines[:-1]),
                     '\n'.join(lines+[lines[-1]])):
            self.rejects(text)
    def test_every_packet_metadata_including_priming_and_last(self):
        lines=synthetic().splitlines()
        for packet in (0,1,67):
            at=next(i for i,s in enumerate(lines) if '_PACKET index=0 ' in s and f' packet={packet} ' in s)
            for old,new in (('vendor_rate=192000','vendor_rate=48000'),('checked_rate=48000','checked_rate=0'),
                            ('vendor_channel=2','vendor_channel=1'),('checked_channel=2','checked_channel=3'),
                            ('vendor_bits=16','vendor_bits=0'),('checked_bits=16','checked_bits=32')):
                with self.subTest(packet=packet,new=new):
                    changed=lines.copy(); changed[at]=changed[at].replace(old,new,1); self.rejects('\n'.join(changed))
    def test_consumption_exact_pcm_bounds_and_canaries(self):
        text=synthetic()
        for old,new in (('expected=32','expected=31'),('vendor_consumed=32','vendor_consumed=0'),
                        ('checked_consumed=32','checked_consumed=31'),('pcm=0 vendor_rate','pcm=2 vendor_rate'),
                        ('exact=1','exact=0'),('canaries=1','canaries=0')):
            with self.subTest(new=new): self.rejects(text.replace(old,new,1))
    def test_nonzero_byte_attestations_and_sum(self):
        text=synthetic()
        self.rejects(text.replace('nonzero=0 core=1','nonzero=1 core=1',1))
        self.rejects(text.replace('nonzero=1 core=1','nonzero=99999 core=1',1))
        self.rejects(text.replace('pcm=272640 nonzero=67','pcm=272640 nonzero=66',1))
        self.rejects(text.replace('nonzero=1 core=1','nonzero=0 core=1'))
    def test_handles_and_totals(self):
        text=synthetic()
        for old,new in (('handles_closed=1','handles_closed=0'),('vendor_handle=1','vendor_handle=0'),
                        ('checked_handle=1','checked_handle=0'),('accepted=16','accepted=15'),('pcm=4362240','pcm=0'),
                        ('zero_rejected=1','zero_rejected=0')):
            with self.subTest(new=new): self.rejects(text.replace(old,new,1))
    def test_unsigned_rate_printing_and_high_boundary_metadata(self):
        text=synthetic()
        for rate,negative in ((2147483648,-2147483648),(4294967295,-1)):
            for field in ('rate','checked_rate'):
                with self.subTest(rate=rate,field=field): self.rejects(text.replace(f'{field}={rate}',f'{field}={negative}',1))
    def test_zero_rejection_is_first_and_mandatory(self):
        text=synthetic()
        self.rejects(text.replace('ZERO_REJECT rate=0 result=-1','ZERO_REJECT rate=0 result=0',1))
        self.rejects(text.replace('ZERO_REJECT rate=0','ZERO_REJECT rate=1',1))
        lines=text.splitlines(); self.rejects('\n'.join(lines[:2]+lines[3:]))
    def test_rejected_status_and_handle_must_agree(self):
        text=synthetic('baseline')
        self.rejects(text.replace('checked_open=-1','checked_open=0',1),'baseline')
        self.rejects(text.replace('CASE_REJECT index=14 rate=2147483648 result=-1','CASE_REJECT index=14 rate=2147483648 result=-2',1),'baseline')
        self.rejects(text.replace('checked_open=-1 vendor_handle=1 checked_handle=0','checked_open=-1 vendor_handle=1 checked_handle=1',1),'baseline')
    def test_limited_policy_covers_all_five_high_rates(self):
        text=synthetic('limited')
        for index in range(11,16):
            rate=RATES[index]; line=next(s for s in text.splitlines() if f'_CASE_REJECT index={index} rate={rate} ' in s)
            self.rejects(text.replace(line+'\n',''),'limited')
    def test_unexpected_failure_or_named_failure_wrong_position(self):
        text=synthetic()
        for reason in ('legal_unsigned_rate_open_required','limited_rate_rejection_required','any_other_failure'):
            self.rejects(text+'CYD_VORBIS_RATE_FAILURE '+reason+'\n')
        control=synthetic('acceptance','signed-validity')
        self.rejects(control.replace('FAILURE legal_unsigned_rate_open_required','FAILURE any_other_failure'),'acceptance','signed-validity')
        self.rejects(control.replace('index=14 rate=2147483648','index=13 rate=2147483647'),'acceptance','signed-validity')
    def test_target_panics_timeouts_and_foreign_markers(self):
        text=synthetic()
        for extra in ('Guru Meditation','assert failed','CORRUPT HEAP','TimeoutExpired','timed out','Backtrace:',
                      'C3_VORBIS_RATE_COMPLETE','noise CYD_VORBIS_RATE_COMPLETE'):
            with self.subTest(extra=extra): self.rejects(text+extra+'\n')
    def test_benign_boot_noise_is_not_protocol(self):
        result=self.validate('boot: starting\n'+synthetic()+'QEMU shutdown\n')
        self.assertEqual(result['protocol_lines'],1124)


if __name__=='__main__': unittest.main()
