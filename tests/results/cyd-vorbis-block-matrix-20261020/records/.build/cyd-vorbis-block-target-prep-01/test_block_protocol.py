"""Synthetic native protocol tests only; no SDK/target/reference execution."""
import copy
import json
from pathlib import Path
import re
import unittest
from block_protocol import validate_log

HERE=Path(__file__).resolve().parent
BANKS=json.loads((HERE/'host_model.json').read_text())['banks']
HASH='a'*64
FACTS=dict(manifest_sha256=HASH,minimal_rate_rebind_qualified=True,returncode=0,timed_out=False,interrupted=False)

def synthetic(profile='cyd'):
    prefix,core=('CYD_VORBIS_BLOCK_',1) if profile=='cyd' else ('C3_VORBIS_BLOCK_',0)
    rows=[f'BEGIN banks=3 cases=108 paired_packets=5472 target_rate=192000 coordinator=0 worker={core} '
          f'minimal_source_rate=48000 minimal_rate_rebind=1 manifest={HASH}']
    pcm_total=0
    for bank in BANKS:
        name,modes,offsets=bank['name'],bank['mode_flags'],bank['offsets']; count=len(modes)
        rows += [f'BANK_BEGIN bank={name} packets={count} source_rate={bank["source_rate"]} target_rate=192000 core={core}']
        bank_total=0
        for s in range(6,14):
            for l in range(s,14):
                coord=f'bank={name} short={1<<s} long={1<<l}'
                rows += [f'CASE_BEGIN {coord} packets={count} rate=192000 vendor_open=0 checked_open=0 handles=1 core={core}']
                groups={}; case_total=0
                for i,(a,b) in enumerate(zip(offsets,offsets[1:])):
                    pcm=0 if not i else ((1<<l if modes[i-1] else 1<<s)+(1<<l if modes[i] else 1<<s))
                    kind='P' if not i else ('L' if modes[i-1] else 'S')+('L' if modes[i] else 'S')
                    rows += [f'PACKET {coord} packet={i} expected={b-a} vendor_consumed={b-a} checked_consumed={b-a} pcm={pcm} '
                         'vendor_rate=192000 checked_rate=192000 vendor_channel=2 checked_channel=2 vendor_bits=16 checked_bits=16 '
                         f'exact=1 canaries=1 transition={kind} nonzero={int(pcm>0)} core={core}']
                    if i:
                        current=groups.setdefault(kind,[0,0]); current[0]+=1; current[1]+=pcm
                    case_total+=pcm
                for kind in ('SS','SL','LS','LL'):
                    if kind in groups:
                        n,pcm=groups[kind]
                        rows += [f'TRANSITION {coord} kind={kind} packets={n} pcm={pcm} nonzero={n} core={core}']
                rows += [f'CASE_COMPLETE {coord} packets={count} pcm={case_total} handles_closed=1 core={core}']
                bank_total+=case_total
        rows += [f'BANK_COMPLETE bank={name} cases=36 paired_packets={36*count} pcm={bank_total} '
                 f'transition_groups={72 if name=="identity" else 144} core={core}']
        pcm_total+=bank_total
    rows += [f'COMPLETE banks=3 cases=108 paired_packets=5472 pcm={pcm_total} transition_groups=360 core={core}']
    return '\n'.join(prefix+line for line in rows)

class Protocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.log=synthetic(); cls.rows=cls.log.splitlines()
    def check_log(self,log,**facts): return validate_log(log,BANKS,'cyd',**(FACTS|facts))
    def rejected(self,log,**facts):
        with self.assertRaises(RuntimeError): self.check_log(log,**facts)

    def test_positive_full108_both_native_profiles(self):
        for profile in ('cyd','c3'):
            result=validate_log(synthetic(profile),BANKS,profile,**FACTS)
            self.assertEqual((result['cases'],result['paired_packets'],result['transition_groups'],result['protocol_lines']),
                             (108,5472,360,6056))

    def test_missing_duplicate_or_reordered_whole_case(self):
        begins=[i for i,line in enumerate(self.rows) if 'CASE_BEGIN ' in line]; a,b,c=begins[:3]
        for rows in (self.rows[:a]+self.rows[b:],self.rows[:b]+self.rows[a:b]+self.rows[b:],
                     self.rows[:a]+self.rows[b:c]+self.rows[a:b]+self.rows[c:]):
            self.rejected('\n'.join(rows))

    def test_missing_duplicate_reordered_packet_and_final_completion(self):
        i=next(i for i,line in enumerate(self.rows) if 'PACKET ' in line); swapped=self.rows[:]
        swapped[i+1],swapped[i+2]=swapped[i+2],swapped[i+1]
        for rows in (self.rows[:i]+self.rows[i+1:],self.rows[:i+1]+[self.rows[i]]+self.rows[i+1:],
                     swapped,self.rows[:-1]): self.rejected('\n'.join(rows))

    def test_public_metadata_checked_on_priming_and_next_packet(self):
        indices=[i for i,line in enumerate(self.rows) if 'PACKET ' in line][:2]
        for i in indices:
            for field in ('vendor_rate','checked_rate','vendor_channel','checked_channel','vendor_bits','checked_bits'):
                for value in (0,1):
                    rows=self.rows[:]; rows[i]=re.sub(r'\b'+field+r'=\d+',field+'='+str(value),rows[i])
                    with self.subTest(packet=i,field=field,value=value): self.rejected('\n'.join(rows))

    def test_consumption_pcm_guards_exactness_and_handles(self):
        for before,after in (('vendor_consumed=32','vendor_consumed=31'),('checked_consumed=32','checked_consumed=31'),
            ('pcm=128','pcm=127'),('exact=1','exact=0'),('canaries=1','canaries=0'),
            ('handles_closed=1','handles_closed=0'),('vendor_open=0','vendor_open=-1')):
            self.assertIn(before,self.log); self.rejected(self.log.replace(before,after,1))

    def test_present_transition_must_have_consistent_nonzero_pcm(self):
        coord='bank=identity short=64 long=64'
        rows=self.rows[:]
        for i,line in enumerate(rows):
            if coord in line and ('PACKET ' in line or 'TRANSITION ' in line) and 'transition=SL' in line:
                rows[i]=line.replace('nonzero=1','nonzero=0')
            if coord in line and 'TRANSITION ' in line and 'kind=SL' in line:
                rows[i]=line.replace('nonzero=1','nonzero=0')
        self.rejected('\n'.join(rows)) # LL remains nonzero: total-only nonzero checks would falsely pass.
        i=next(i for i,line in enumerate(self.rows) if 'TRANSITION ' in line)
        for wrong in ('\n'.join(self.rows[:i]+self.rows[i+1:]),self.log.replace('kind=SL','kind=SS',1),
                      self.log.replace('nonzero=1 core=1','nonzero=999999 core=1',1),
                      self.log.replace('paired_packets=5472','paired_packets=5471',1)):
            self.rejected(wrong)

    def test_prefix_core_failure_and_required_process_rebind_facts(self):
        for wrong in (self.log.replace('CYD_VORBIS_BLOCK_','C3_VORBIS_BLOCK_'),
                      self.log+'\nC3_VORBIS_BLOCK_COMPLETE fake',self.log.replace('core=1','core=0',1),
                      self.log.replace('coordinator=0','coordinator=1',1),self.log+'\nassert failed',
                      self.log+'\nCYD_VORBIS_BLOCK_FAILURE reason=arbitrary'):
            self.rejected(wrong)
        for facts in (dict(returncode=None),dict(returncode=False),dict(returncode=1),dict(timed_out=True),
                      dict(interrupted=True),dict(interrupted=None),dict(minimal_rate_rebind_qualified=False),
                      dict(manifest_sha256=''),dict(manifest_sha256='b'*64)):
            self.rejected(self.log,**facts)
        for missing in FACTS:
            facts=FACTS.copy(); facts.pop(missing)
            with self.subTest(missing=missing),self.assertRaises(TypeError): validate_log(self.log,BANKS,'cyd',**facts)

    def test_frozen_bank_contract_must_retain_all_banks_modes_and_offsets(self):
        bad=[]
        bad.append(BANKS[:-1]); swapped=copy.deepcopy(BANKS); swapped[0],swapped[1]=swapped[1],swapped[0]; bad.append(swapped)
        for field,value in (('mode_flags',[0]*14),('source_rate',192000),('offsets',[0]*15)):
            rows=copy.deepcopy(BANKS); rows[2][field]=value; bad.append(rows)
        for banks in bad:
            with self.assertRaises(RuntimeError): validate_log(self.log,banks,'cyd',**FACTS)
        with self.assertRaises(RuntimeError): validate_log(self.log,BANKS,'unknown',**FACTS)

if __name__=='__main__': unittest.main()
