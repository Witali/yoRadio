"""Synthetic registry protocol controls; no codec, compiler, SDK or target launch."""
import copy
import hashlib
import unittest
from vorbis_registered_protocol import validate_log


def model():
    blocks=[256 if mode=='S' else 2048 for mode in 'SSLLLSLSSSLLSS']
    sizes=[0]+[a+b for a,b in zip(blocks,blocks[1:])]
    return dict(cases=[dict(id=f'case-{i}',expected_valid=i<8,
        expected_packet_bytes=sizes[:],offsets=[p*11 for p in range(15)]) for i in range(14)])


def protocol(target='esp32',control=None,unready=True,zero_case=None):
    core=1 if target=='esp32' else 0
    rows=[f'FLOOR1_START coordinator=0 decoder={core}',
        f'VORBIS_REGISTRY_BEGIN cases=14 packets=112 retries=312 core={core}',
        f'VORBIS_REGISTRY_INITIAL empty=1 unsupported=1 core={core}']
    for case,c in enumerate(model()['cases']):
        rows.append(f'VORBIS_REGISTRY_REGISTER case={case} result=0 ops=1 supported=1 core={core}')
        if case==0 and control=='register-open':break
        rows.append(f'VORBIS_REGISTRY_BIND_OPEN case={case} match=1 core={core}')
        if case==0 and control=='register-decode':break
        rows += [f'VORBIS_REGISTRY_BIND_DECODE case={case} match=1 core={core}',
            f'VORBIS_REGISTRY_BIND_OTHER case={case} reset=1 close=1 core={core}']
        if not c['expected_valid']:
            rows += [f'FLOOR1_OPEN case={case} result=-1 handle=0',
                f'FLOOR1_REJECT case={case} name={c["id"]} result=-1 handle=0 core={core}',
                f'VORBIS_REGISTRY_UNREGISTER case={case} empty=1 unsupported=1 core={core}']
            continue
        rows.append(f'FLOOR1_OPEN case={case} result=0 handle=1')
        for packet,size in enumerate(c['expected_packet_bytes']):
            if size:
                rows += [f'VORBIS_REGISTRY_RETRY case={case} packet={packet} attempt={attempt} result=-8 consumed=0 decoded=0 needed={size} untouched=1 canaries=1 core={core}' for attempt in range(3)]
            fields='result=-9 sample_rate=0 channel=0 bits=0' if not size and unready else 'result=0 sample_rate=48000 channel=2 bits=16'
            rows.append(f'VORBIS_REGISTRY_META case={case} packet={packet} {fields} core={core}')
            data=bytes([0 if case==zero_case else (case+packet)%254+1])*size
            rows.append(f'FLOOR1_PCM case={case} packet={packet} consumed=11 bytes={size} hex={data.hex()}')
        rows += [f'VORBIS_REGISTRY_CLOSE case={case} called=1 core={core}',
            f'VORBIS_REGISTRY_UNREGISTER case={case} empty=1 unsupported=1 core={core}',
            f'FLOOR1_ACCEPT case={case} name={c["id"]} packets=14 pcm=28160 renderer_repair=1 core={core}']
    if control:
        reason='registry_open_binding' if control=='register-open' else 'registry_decode_binding'
        rows += [f'FLOOR1_FAILURE case=0 reason={reason}',
            f'VORBIS_REGISTRY_CLEANUP case=0 closed=0 empty=1 unsupported=1 core={core}']
    else:
        rows += [f'VORBIS_REGISTRY_COMPLETE registrations=14 bindings=14 closes=8 unregistrations=14 metadata=112 retries=312 core={core}',
            f'FLOOR1_COMPLETE accepted=8 rejected=6 packets=112 pcm=225280 core={core}']
    return '\n'.join(rows+['FLOOR1_CONTROLLED_STOP'])


class RegistryProtocol(unittest.TestCase):
    def check_log(self,log=None,target='esp32',control=None,**facts):
        return validate_log(protocol(target,control) if log is None else log,model(),target,control,
            **dict(dict(returncode=0,timed_out=False,interrupted=False),**facts))

    def rejects(self,*logs,target='esp32',control=None):
        for index,log in enumerate(logs):
            with self.subTest(index=index),self.assertRaises(ValueError):
                self.check_log(log,target,control)

    def test_complete_both_cores_and_primer_readiness(self):
        for target in ('esp32','esp32c3'):
            for unready in (True,False):
                r=self.check_log(protocol(target,unready=unready),target)
                self.assertTrue(r['registered_callbacks_qualified'] and r['target_capture_completed'])
                self.assertEqual((r['registrations'],r['bindings'],r['unregistrations'],r['closes']),(14,14,14,8))
                self.assertEqual((r['pcm_packets'],r['metadata_packets'],r['retries'],r['pcm_bytes']),(112,112,312,225280))
                self.assertEqual(r['primer_info_results'],[-9 if unready else 0]*8)
                data=b''.join(bytes([(packet%254)+1])*size for packet,size in enumerate(model()['cases'][0]['expected_packet_bytes']))
                self.assertEqual(r['pcm_sha256']['0'],hashlib.sha256(data).hexdigest())
                self.assertFalse(r['independent_reference_compared'] or r['vendor_comparison_available'] or r['full_G6_qualified'])

    def test_named_binding_controls_both_cores(self):
        for target in ('esp32','esp32c3'):
            for control in ('register-open','register-decode'):
                r=self.check_log(target=target,control=control)
                self.assertTrue(r['control_effective'])
                self.assertFalse(r['registered_callbacks_qualified'] or r['target_capture_completed'])
                self.assertEqual((r['pcm_packets'],r['retries'],r['metadata_packets']),(0,0,0))

    def test_process_facts_are_required_and_strict(self):
        with self.assertRaises(TypeError):validate_log(protocol(),model(),'esp32')
        for facts in (dict(returncode=1),dict(returncode=-9),dict(returncode=False),dict(returncode=None),
                      dict(timed_out=True),dict(timed_out=None),dict(interrupted=True),dict(interrupted=None)):
            with self.subTest(facts=facts),self.assertRaises(ValueError):self.check_log(**facts)

    def test_missing_duplicate_or_reordered_events(self):
        rows=protocol().splitlines()
        for prefix in ('VORBIS_REGISTRY_REGISTER','VORBIS_REGISTRY_BIND_OPEN','VORBIS_REGISTRY_BIND_DECODE',
                       'VORBIS_REGISTRY_BIND_OTHER','VORBIS_REGISTRY_RETRY','VORBIS_REGISTRY_META',
                       'VORBIS_REGISTRY_CLOSE','VORBIS_REGISTRY_UNREGISTER','FLOOR1_PCM'):
            at=next(i for i,line in enumerate(rows) if line.startswith(prefix))
            missing=rows[:at]+rows[at+1:]
            duplicate=rows[:at]+[rows[at]]+rows[at:]
            swapped=rows[:];swapped[at],swapped[at+1]=swapped[at+1],swapped[at]
            self.rejects('\n'.join(missing),'\n'.join(duplicate),'\n'.join(swapped))

    def test_metadata_zero_wrong_format_and_primer_errors(self):
        log=protocol()
        self.rejects(log.replace('result=0 sample_rate=48000','result=0 sample_rate=0',1),
            log.replace('channel=2 bits=16','channel=1 bits=16',1),
            log.replace('channel=2 bits=16','channel=2 bits=24',1),
            log.replace('packet=1 result=0','packet=1 result=-9',1),
            log.replace('result=-9 sample_rate=0','result=0 sample_rate=0',1),
            log.replace('result=-9 sample_rate=0','result=-1 sample_rate=0',1))

    def test_retry_public_outputs_capacity_and_guards(self):
        log=protocol()
        for before,after in (('result=-8 consumed=0','result=-1 consumed=0'),
                ('consumed=0 decoded=0','consumed=1 decoded=0'),('decoded=0 needed=512','decoded=1 needed=512'),
                ('needed=512','needed=513'),('untouched=1','untouched=0'),('canaries=1','canaries=0'),
                ('attempt=2','attempt=3')):
            self.assertIn(before,log)
            self.rejects(log.replace(before,after,1))

    def test_pcm_consumption_lengths_and_nonzero_case(self):
        log=protocol()
        self.rejects(log.replace('consumed=11 bytes=0','consumed=10 bytes=0',1),
            log.replace('bytes=512 hex=','bytes=510 hex=',1),
            log.replace('bytes=512 hex=','bytes=512 hex=f',1),protocol(zero_case=0))

    def test_generic_error_is_not_header_rejection(self):
        log=protocol()
        self.rejects(log.replace('case=8 result=-1 handle=0','case=8 result=-2 handle=0',1),
            log.replace('case=8 result=-1 handle=0','case=8 result=0 handle=1',1),
            log.replace('case=8 name=case-8 result=-1','case=8 name=case-8 result=-2',1))

    def test_registry_unregistration_and_close_are_required(self):
        log=protocol()
        self.rejects(log.replace('INITIAL empty=1','INITIAL empty=0',1),
            log.replace('ops=1 supported=1','ops=1 supported=0',1),
            log.replace('reset=1 close=1','reset=0 close=1',1),
            log.replace('called=1','called=0',1),
            log.replace('UNREGISTER case=8 empty=1','UNREGISTER case=8 empty=0',1))

    def test_control_requires_precise_prerequisites_reason_and_cleanup(self):
        for control in ('register-open','register-decode'):
            log=protocol(control=control)
            self.rejects(log.replace('case=0 result=0 ops=1 supported=1','case=0 result=-2 ops=1 supported=1'),
                log.replace('case=0 reason=registry_','case=1 reason=registry_',1),
                log.replace('reason=registry_','reason=other_',1),
                log.replace('closed=0 empty=1','closed=1 empty=1'),
                log.replace('empty=1 unsupported=1 core=1\nFLOOR1_CONTROLLED_STOP','empty=0 unsupported=1 core=1\nFLOOR1_CONTROLLED_STOP'),
                log+'\nFLOOR1_OPEN case=0 result=0 handle=1',control=control)
            self.rejects(protocol(),control=control)
        self.rejects(protocol(control='register-open'),control='register-decode')
        self.rejects(protocol(control='register-decode'),control='register-open')

    def test_core_panic_extra_events_and_completion_counts(self):
        log=protocol()
        self.rejects(log.replace('core=1','core=0',1),log+'\nGuru Meditation Error',
            log+'\nVORBIS_REGISTRY_EXTRA fake=1',log+'\nFLOOR1_CONTROLLED_STOP',
            log.replace('metadata=112 retries=312','metadata=112 retries=311'),
            log.replace('packets=112 pcm=225280','packets=111 pcm=225280'))
        self.rejects(log,target='esp32c3')

    def test_matrix_cannot_shrink_or_duplicate_cases(self):
        for change in ('short','duplicate','validity','sizes','offsets'):
            value=copy.deepcopy(model())
            if change=='short':value['cases'].pop()
            if change=='duplicate':value['cases'][1]['id']=value['cases'][0]['id']
            if change=='validity':value['cases'][8]['expected_valid']=True
            if change=='sizes':value['cases'][0]['expected_packet_bytes'][1]+=1
            if change=='offsets':value['cases'][0]['offsets'][2]=value['cases'][0]['offsets'][1]
            with self.subTest(change=change),self.assertRaises(ValueError):
                validate_log(protocol(),value,'esp32',returncode=0,timed_out=False,interrupted=False)


if __name__=='__main__':unittest.main()
