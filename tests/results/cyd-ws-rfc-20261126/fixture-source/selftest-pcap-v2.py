"""Pure v2 packet controls; no files written, socket, process or guest used."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import unittest
from unittest import mock

P=Path(__file__).with_name('pcap-observer-v2.py')
spec=importlib.util.spec_from_file_location('private_pcap_v2',P)
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)


def packet(server,port,seq,ack,*,flags=16,payload=b'',window=2000,options=b''):
    assert len(options)%4==0
    src,dst=(b'\x0a\x00\x02\x0f',b'\x0a\x00\x02\x02')if server else(b'\x0a\x00\x02\x02',b'\x0a\x00\x02\x0f')
    sport,dport=(443,port)if server else(port,443)
    tcp=struct.pack('!HHIIBBHHH',sport,dport,seq&p.MASK,ack&p.MASK,(20+len(options))//4<<4,flags,window,0,0)+options+payload
    ip=struct.pack('!BBHHHBBH4s4s',0x45,0,20+len(tcp),1,0x4000,64,6,0,src,dst)
    return b'\0'*12+b'\x08\x00'+ip+tcp


def capture(packets):
    data=struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,160,1)
    for n,row in enumerate(packets):data+=struct.pack('<IIII',1,n,min(160,len(row)),len(row))+row[:160]
    return data


def flow(port=50000,sisn=100,pisn=500,body=b'ciphertext-placeholder',reset=False):
    n=len(body)
    rows=[packet(False,port,pisn,0,flags=2,options=b'\x03\x03\x03\x01'),
          packet(True,port,sisn,pisn+1,flags=18),packet(False,port,pisn+1,sisn+1),
          packet(False,port,pisn+1,sisn+1,payload=b'command'),
          packet(True,port,sisn+1,pisn+8,payload=body)]
    if reset:rows.append(packet(True,port,sisn+max(1,n),pisn+8,flags=20))
    else:rows += [packet(True,port,sisn+1+n,pisn+8,flags=17),
                  packet(False,port,pisn+8,sisn+2+n),
                  packet(False,port,pisn+8,sisn+2+n,flags=17),
                  packet(True,port,sisn+2+n,pisn+9)]
    return rows


ROLES=[dict(role=role,guest_fd=54+i,pcb=hex(0x123400+i),guest_tuple=dict(local_ip='10.0.2.15',remote_ip='10.0.2.2',local_port=443,remote_port=50000+i))for i,role in enumerate(('slow','healthy'))]


def final(rows,**kwargs):
    args=dict(final=True,expected_flows=ROLES,capture_write_errors_absent=True,capture_stopped=True);args.update(kwargs)
    return p.decode(capture(rows),**args)


class Tests(unittest.TestCase):
    def test_live_alignment_is_not_final(self):
        r=p.decode(capture([]));self.assertTrue(r['record_alignment_complete']);self.assertFalse(r['final_wire_complete'])
        with self.assertRaises(ValueError):final([])
        r=p.decode(capture(flow())[:-2]);self.assertFalse(r['record_alignment_complete'])

    def test_two_bound_flows_encrypted_payload_and_fin_ack(self):
        r=final(flow()+flow(50001))
        self.assertTrue(r['final_wire_complete']);self.assertEqual(len(r['selected_terminal_coverage']),2)
        self.assertEqual(r['unique_tcp_payload_bytes'],2*len(b'ciphertext-placeholder'))
        self.assertNotIn('ciphertext-placeholder',json.dumps(r))
        self.assertTrue(all(x['terminal_basis']=='both-fins-and-acknowledgments'for x in r['selected_terminal_coverage']))

    def test_wrap_retransmission_and_overlapping_ranges_once(self):
        s=0xfffffff0;rows=flow(sisn=s,body=b'x'*40,reset=True)
        rows.insert(5,packet(True,50000,s+1,508,payload=b'x'*40))
        rows.insert(6,packet(True,50000,s+21,508,payload=b'x'*20))
        r=final(rows+flow(50001));self.assertEqual(r['unique_tcp_payload_bytes'],40+len(b'ciphertext-placeholder'))

    def test_snap_truncation_counts_verified_ip_payload(self):
        r=final(flow(body=b'x'*1000)+flow(50001));self.assertEqual(r['unique_tcp_payload_bytes'],1000+len(b'ciphertext-placeholder'))

    def test_aligned_whole_record_gap_not_inferred(self):
        rows=flow(body=b'x'*30)
        rows[4:5]=[packet(True,50000,101,508,payload=b'x'*10),packet(True,50000,121,508,payload=b'x'*10)]
        with self.assertRaisesRegex(ValueError,'sequence-gap'):final(rows+flow(50001))

    def test_same_isn_reuse_after_fin_or_reset_rejected(self):
        for reset in (False,True):
            with self.assertRaisesRegex(ValueError,'reuse-after-terminal'):final(flow(reset=reset)+flow()+flow(50001))

    def test_changed_isn_reuse_and_missing_syn_rejected(self):
        with self.assertRaises(ValueError):final(flow()[:5]+[packet(True,50000,999,508,flags=18)]+flow(50001))
        rows=flow();del rows[1]
        with self.assertRaises(ValueError):final(rows+flow(50001))

    def test_missing_exact_flow_or_role_identity_rejected(self):
        with self.assertRaises(ValueError):final(flow())
        wrong=[dict(x,guest_tuple=dict(x['guest_tuple'],remote_port=51000+i))for i,x in enumerate(ROLES)]
        with self.assertRaises(ValueError):final(flow()+flow(50001),expected_flows=wrong)
        with self.assertRaises(ValueError):p.expected_map([ROLES[0],dict(ROLES[1],guest_fd=54)])

    def test_caller_no_loss_and_stopped_prerequisites(self):
        rows=flow()+flow(50001)
        for kwargs in (dict(expected_flows=None),dict(capture_write_errors_absent=False),dict(capture_write_errors_absent=None),dict(capture_stopped=False)):
            with self.assertRaises(ValueError):final(rows,**kwargs)

    def test_ack_cannot_cover_unseen_bytes(self):
        rows=flow();rows[-1]=packet(True,50000,123,9999)
        with self.assertRaisesRegex(ValueError,'ack-unseen'):final(rows+flow(50001))

    def test_synack_must_ack_exact_peer_syn(self):
        rows=flow();rows[1]=packet(True,50000,100,508,flags=18)
        with self.assertRaisesRegex(ValueError,'synack-ack'):final(rows+flow(50001))

    def test_fin_must_follow_captured_payload_and_be_acknowledged(self):
        rows=flow();rows[5]=packet(True,50000,150,508,flags=17)
        with self.assertRaisesRegex(ValueError,'fin-sequence'):final(rows+flow(50001))
        with self.assertRaisesRegex(ValueError,'terminal-incomplete'):final(flow()[:-1]+flow(50001))

    def test_rst_within_captured_space_and_ack_bound(self):
        r=final(flow(reset=True)+flow(50001))
        self.assertTrue(r['final_wire_complete'])
        self.assertIn('rst',r['selected_terminal_coverage'][0]['terminal_basis'])
        rows=flow(reset=True);rows[-1]=packet(True,50000,999,508,flags=20)
        with self.assertRaises(ValueError):final(rows+flow(50001))
        rows=flow(reset=True);rows[-1]=packet(True,50000,110,0,flags=4)
        with self.assertRaisesRegex(ValueError,'unsupported-reset'):final(rows+flow(50001))

    def test_nonselected_health_counts_without_terminal_requirement(self):
        health=flow(50002,body=b'h'*35)[:5]
        r=final(flow()+flow(50001)+health)
        self.assertEqual(r['unique_tcp_payload_bytes'],2*len(b'ciphertext-placeholder')+35)
        self.assertEqual(len(r['selected_terminal_coverage']),2)

    def test_record_truncation_rejects_final(self):
        with self.assertRaises(ValueError):p.decode(capture(flow()+flow(50001))[:-1],final=True,expected_flows=ROLES,capture_write_errors_absent=True,capture_stopped=True)
        with self.assertRaises(ValueError):p.decode(b'x'*(p.MAX_FILE+1))

    def test_capture_guard_reads_only_max_plus_one(self):
        class Tracked(io.BytesIO):
            def read(self,n=-1):
                self.request=n;self.actual=super().read(n);return self.actual
            def close(self):pass
        stream=Tracked(b'x'*(p.MAX_FILE+4096));guard=p.CaptureGuard('not-opened.pcap')
        with mock.patch.object(Path,'open',return_value=stream):
            with self.assertRaises(ValueError):guard.sample()
        self.assertEqual(stream.request,p.MAX_FILE+1);self.assertEqual(len(stream.actual),p.MAX_FILE+1)

    def test_guard_exact_mapping_and_final_flags(self):
        guard=p.CaptureGuard('not-opened.pcap').expect_flows(ROLES)
        with self.assertRaises(ValueError):guard.expect_flows(ROLES)
        with mock.patch.object(Path,'open',return_value=io.BytesIO(capture(flow()+flow(50001)))):
            self.assertTrue(guard.sample(final=True,capture_stopped=True,capture_write_errors_absent=True)['final_wire_complete'])

    def test_all_discovered_flows_apply_envelope(self):
        with mock.patch.object(p,'MAX_UNIQUE_SERVER_DATA',100):
            with self.assertRaisesRegex(ValueError,'payload-bound'):final(flow()+flow(50001)+flow(50002,body=b'x'*60))


if __name__=='__main__':unittest.main()
