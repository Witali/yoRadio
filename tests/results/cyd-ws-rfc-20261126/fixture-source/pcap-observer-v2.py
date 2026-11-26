"""Private bounded IPv4/TCP counter; no sockets, guest commands or payload export.

Record alignment is NOT capture completeness. Final selected-flow proof needs
the actual slow/healthy fd+PCB role map, both SYNs, contiguous captured sequence
ranges and consistent terminal/ACK evidence. No missing bytes are inferred.
All discovered IPv4 port80/443 server flows count toward the 8 MiB envelope;
unselected boot/HTTP flows do not have to terminate before local/QEMU cleanup.

Final acceptance also relies on the CALLER proving the pinned QEMU filter was
active from connect, the capture is stopped, and final UART has no exact
'network dump write error - stopping dump'. Those explicit source/lifecycle
assumptions are necessary: PCAP has no independent dropped-record counter.
The caller must bind this receipt to its run/source/ELF/input pins before
constructing frozen Observer's wire-accounting event. This module cannot
authenticate the caller's GDB role map or no-write-error assertion.
"""
import hashlib
import ipaddress
from pathlib import Path
import re
import struct

MAX_FILE=4*1024*1024
MAX_UNIQUE_SERVER_DATA=8*1024*1024
MAX_RECORDS=32768
MAX_FLOWS=128
MASK=0xffffffff


def need(value,category):
    if not value:raise ValueError(category)


def merge(intervals):
    result=[]
    for a,z in sorted(intervals):
        if result and a<=result[-1][1]:result[-1][1]=max(result[-1][1],z)
        else:result.append([a,z])
    return result


def relative(value,isn):
    offset=(value-isn-1)&MASK
    need(offset<0x80000000,'tcp-sequence-envelope')
    return offset


def expected_map(records):
    need(isinstance(records,(list,tuple)) and len(records)==2,'exact-two-expected-flows')
    result={};roles=set();fds=set();pcbs=set()
    for entry in records:
        need(isinstance(entry,dict),'expected-flow-object')
        role=entry.get('role');fd=entry.get('guest_fd');pcb=entry.get('pcb');t=entry.get('guest_tuple')
        need(role in ('slow','healthy') and role not in roles,'expected-role')
        need(type(fd)is int and 0<=fd<=0x7fffffff and fd not in fds,'expected-fd')
        need(isinstance(pcb,str) and re.fullmatch(r'0x[0-9a-f]{1,8}',pcb),'expected-pcb')
        pcb=hex(int(pcb,16));need(pcb!='0x0' and pcb not in pcbs,'expected-pcb-identity')
        need(isinstance(t,dict) and set(t)=={'local_ip','remote_ip','local_port','remote_port'},'expected-guest-tuple')
        server=ipaddress.IPv4Address(t['local_ip']).packed;peer=ipaddress.IPv4Address(t['remote_ip']).packed
        port=t['local_port'];remote=t['remote_port']
        need(type(port)is int and port in (80,443) and type(remote)is int and 0<remote<65536,'expected-ports')
        key=(server,port,peer,remote);need(key not in result,'duplicate-expected-tuple')
        result[key]=dict(role=role,guest_fd=fd,pcb=pcb,guest_tuple=dict(t))
        roles.add(role);fds.add(fd);pcbs.add(pcb)
    need(roles=={'slow','healthy'},'both-expected-roles')
    return result


def direction():
    return dict(isn=None,intervals=[],scale=None)


def packet_flow():
    return dict(server=direction(),peer=direction(),packets=[],terminal=False,
                server_payload_packets=0,peer_zero_windows=[],fin_or_rst=0)


def terminal_proof(flow,identity):
    sides={}
    for side in ('server','peer'):
        d=flow[side];need(d['isn'] is not None,'selected-missing-syn')
        spans=merge(d['intervals'])
        need(not spans or (len(spans)==1 and spans[0][0]==0),'selected-sequence-gap')
        end=spans[0][1]if spans else 0
        need(end>0,'selected-flow-no-payload')
        fins={relative((seq+length)&MASK,d['isn']) for who,seq,ack,flags,length in flow['packets'] if who==side and flags&1}
        need(len(fins)<=1 and (not fins or next(iter(fins))==end),'selected-fin-sequence')
        sides[side]=dict(payload_bytes=end,fin_offset=next(iter(fins))if fins else None,
                         sequence_end=end+bool(fins),fin_acked=False,max_ack=0,rsts=0)
    need(any(who=='peer' and flags&2 and not flags&16 for who,seq,ack,flags,length in flow['packets']),'selected-active-peer-syn')
    need(any(who=='server' and flags&18==18 for who,seq,ack,flags,length in flow['packets']),'selected-server-synack')
    reset=False
    for side,seq,ack,flags,length in flow['packets']:
        own=sides[side];other_name='peer'if side=='server'else'server';other=sides[other_name]
        if not flags&2:
            offset=relative(seq,flow[side]['isn'])
            need(offset+length<=(own['payload_bytes']if length else own['sequence_end']),'selected-unseen-sequence')
        if flags&16:
            ack_offset=relative(ack,flow[other_name]['isn'])
            if flags&2:need(ack_offset==0,'selected-synack-ack')
            need(ack_offset<=other['sequence_end'],'selected-ack-unseen-sequence')
            own['max_ack']=max(own['max_ack'],ack_offset)
            if other['fin_offset']is not None and ack_offset==other['sequence_end']:other['fin_acked']=True
        if flags&4:
            # Active lwIP abort uses snd_nxt, which may be below a captured
            # zero-window probe. Constrain it to captured sequence space;
            # do not invent bytes or require equality with the highest byte.
            rst_offset=relative(seq,flow[side]['isn'])
            need(flags&16 and not flags&1,'selected-unsupported-reset-subtype')
            need(rst_offset<=own['sequence_end'] and length==0,'selected-rst-sequence')
            own['rsts']+=1;reset=True
    if reset:
        basis='captured-rst-with-sequence-and-ack-consistency'
    else:
        need(all(d['fin_offset']is not None and d['fin_acked']for d in sides.values()),'selected-terminal-incomplete')
        basis='both-fins-and-acknowledgments'
    return dict(**identity,terminal_basis=basis,server=sides['server'],peer=sides['peer'],
                captured_ranges_contiguous=True,missing_bytes_inferred=False)


def decode(body,*,final=False,expected_flows=None,capture_write_errors_absent=None,capture_stopped=None):
    need(len(body)<=MAX_FILE,'capture-file-bound')
    expected=expected_map(expected_flows)if expected_flows is not None else{}
    if final:
        need(len(expected)==2,'final-expected-role-map-required')
        need(capture_write_errors_absent is True,'final-no-dump-write-error-proof-required')
        need(capture_stopped is True,'final-stopped-capture-proof-required')
    result=dict(record_alignment_complete=False,final_wire_complete=False,records=0,flows=[],
                unique_server_bytes=0,unique_tcp_payload_bytes=0,selected_terminal_coverage=[],
                capture_sha256=hashlib.sha256(body).hexdigest(),pressure_or_deadline_proved=False,
                scope='All captured IPv4 port80/443 server TCP payload; ciphertext included; no payload exported',
                no_loss_assumption='Caller binds pinned filter active from connect, stopped capture and final UART absence of dump-write error; record alignment alone proves no such property')
    if len(body)<24:
        need(not final,'truncated-global-header');return result
    magic=body[:4];formats={b'\xd4\xc3\xb2\xa1':('<',1000),b'\xa1\xb2\xc3\xd4':('>',1000),b'\x4d\x3c\xb2\xa1':('<',1),b'\xa1\xb2\x3c\x4d':('>',1)}
    need(magic in formats,'unsupported-pcap-magic');endian,factor=formats[magic]
    major,minor,_,_,snaplen,link=struct.unpack_from(endian+'HHIIII',body,4)
    need((major,minor)==(2,4)and link==1 and 134<=snaplen<=65535,'pcap-header-profile')
    cursor=24;aligned=True;flows={};records=0
    while cursor<len(body):
        if len(body)-cursor<16:aligned=False;break
        sec,sub,caplen,wirelen=struct.unpack_from(endian+'IIII',body,cursor)
        need(sub<(1000000 if factor==1000 else 1000000000),'pcap-subsecond-range')
        need(14<=caplen<=snaplen and caplen<=wirelen<=65535,'pcap-record-length')
        if len(body)-cursor-16<caplen:aligned=False;break
        packet=body[cursor+16:cursor+16+caplen];cursor+=16+caplen;records+=1
        need(records<=MAX_RECORDS,'capture-record-count-bound')
        if packet[12:14]!=b'\x08\x00':continue
        ip=packet[14:];need(len(ip)>=20 and ip[0]>>4==4,'ipv4-header')
        ihl=(ip[0]&15)*4;need(20<=ihl<=60 and len(ip)>=ihl,'ipv4-header-length')
        total=struct.unpack_from('!H',ip,2)[0];need(ihl<=total<=wirelen-14,'ipv4-total-length')
        if ip[9]!=6:continue
        need(struct.unpack_from('!H',ip,6)[0]&0x3fff==0,'fragmented-tcp-not-accounted')
        tcp=ip[ihl:];need(len(tcp)>=20,'tcp-header-truncated')
        sport,dport,seq,ack=struct.unpack_from('!HHII',tcp);hlen=(tcp[12]>>4)*4;flags=tcp[13]
        need(20<=hlen<=60 and len(tcp)>=hlen and total>=ihl+hlen,'tcp-header-length')
        if sport in (80,443):key=(ip[12:16],sport,ip[16:20],dport);side='server'
        elif dport in (80,443):key=(ip[16:20],dport,ip[12:16],sport);side='peer'
        else:continue
        if key not in flows:
            need(len(flows)<MAX_FLOWS,'capture-flow-count-bound');flows[key]=packet_flow()
        flow=flows[key];d=flow[side];length=total-ihl-hlen
        need(not(flags&2 and flags&5),'tcp-syn-terminal-combination')
        if flags&2:
            need(not flow['terminal'],'tuple-reuse-after-terminal')
            need(length==0,'tcp-fast-open-not-accounted')
            need(d['isn']in(None,seq),'tuple-reuse-isn-changed');d['isn']=seq
            options=tcp[20:hlen];pos=0;scale=0
            while pos<len(options):
                kind=options[pos]
                if kind==0:break
                if kind==1:pos+=1;continue
                need(pos+2<=len(options),'tcp-option-header');size=options[pos+1]
                need(size>=2 and pos+size<=len(options),'tcp-option-length')
                if kind==3:need(size==3 and options[pos+2]<=14,'tcp-window-scale');scale=options[pos+2]
                pos+=size
            d['scale']=scale
        if length:
            need(d['isn']is not None,'missing-payload-syn')
            start=relative(seq,d['isn']);need(start+length<0x80000000,'tcp-sequence-envelope')
            d['intervals'].append((start,start+length))
            if side=='server':flow['server_payload_packets']+=1
        if key in expected:flow['packets'].append((side,seq,ack,flags,length))
        if side=='peer'and flags&16 and struct.unpack_from('!H',tcp,14)[0]==0 and len(flow['peer_zero_windows'])<64:
            flow['peer_zero_windows'].append(dict(pcap_time_ns=sec*1000000000+sub*factor,ack=ack))
        if flags&5:flow['terminal']=True;flow['fin_or_rst']+=1
    need(aligned or not final,'truncated-final-record')
    for key,flow in flows.items():
        server,port,peer,remote=key;spans=merge(flow['server']['intervals']);unique=sum(z-a for a,z in spans)
        result['flows'].append(dict(server_ip=str(ipaddress.IPv4Address(server)),server_port=port,
            peer_ip=str(ipaddress.IPv4Address(peer)),peer_port=remote,selected=key in expected,
            unique_server_bytes=unique,server_payload_packets=flow['server_payload_packets'],
            server_syn_seen=flow['server']['isn']is not None,peer_syn_seen=flow['peer']['isn']is not None,
            server_window_scale=flow['server']['scale'],peer_window_scale=flow['peer']['scale'],
            peer_zero_windows=flow['peer_zero_windows'],fin_or_rst=flow['fin_or_rst']))
        result['unique_server_bytes']+=unique
    need(result['unique_server_bytes']<=MAX_UNIQUE_SERVER_DATA,'unique-server-tcp-payload-bound')
    result.update(record_alignment_complete=aligned,records=records,unique_tcp_payload_bytes=result['unique_server_bytes'])
    if final:
        for key,identity in expected.items():
            need(key in flows,'selected-flow-missing')
            result['selected_terminal_coverage'].append(terminal_proof(flows[key],identity))
        result.update(final_wire_complete=True,caller_capture_stopped=True,caller_final_dump_write_errors_absent=True)
    return result


class CaptureGuard:
    def __init__(self,path):
        self.path=Path(path);self.last=None;self.expected=None;self.armed=True

    def expect_flows(self,records):
        need(self.expected is None,'expected-role-map-already-bound')
        validated=expected_map(records)
        self.expected=list(validated.values())
        return self

    def sample(self,*,final=False,capture_write_errors_absent=None,capture_stopped=None):
        # The limit is on the actual read, including a concurrently growing file.
        with self.path.open('rb')as stream:body=stream.read(MAX_FILE+1)
        need(len(body)<=MAX_FILE,'capture-file-bound')
        self.last=decode(body,final=final,expected_flows=self.expected,
                         capture_write_errors_absent=capture_write_errors_absent,capture_stopped=capture_stopped)
        return self.last
