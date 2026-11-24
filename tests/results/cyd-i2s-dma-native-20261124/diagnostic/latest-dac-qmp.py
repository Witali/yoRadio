"""Read only validated DAC control metadata from a disposable, paused QEMU."""
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import time

BASE = Path(__file__).resolve().parent
LAYOUT = json.loads((BASE / 'layout.json').read_bytes())
OUTPUT = Path(os.environ['CYD_DAC_SNAPSHOT'])
PORT = int(os.environ['CYD_DAC_QMP_PORT'])
MODE = os.environ.get('CYD_DAC_CAPTURE_MODE','timeout')

class QMP:
    def __init__(self):
        self.socket = socket.create_connection(('127.0.0.1',PORT),timeout=2)
        self.stream = self.socket.makefile('rwb',buffering=0)
        self.greeting = json.loads(self.stream.readline())
        self.sequence = 0
        self.events = []
        self.call('qmp_capabilities')

    def call(self, command, arguments=None):
        self.sequence += 1
        packet = dict(execute=command,id=self.sequence)
        if arguments is not None: packet['arguments'] = arguments
        self.stream.write(json.dumps(packet).encode()+b'\n')
        while True:
            response = json.loads(self.stream.readline())
            if 'event' in response:
                self.events.append(response['event'])
            elif response.get('id') == self.sequence:
                if 'error' in response: raise RuntimeError('QMP command rejected')
                return response['return']

    def words(self, address, count=1):
        assert address % 4 == 0 and 0 < count <= 6
        assert (0x3ffae000 <= address < address+count*4 <= 0x40000000 or
                0x3ff4f000 <= address < address+count*4 <= 0x3ff4f100)
        value = self.call('human-monitor-command',{'command-line':f'xp /{count}wx 0x{address:x}'})
        words = []
        for line in value.splitlines():
            if ':' in line:
                words += [int(item,16) for item in re.findall(r'0x([0-9a-fA-F]{8})(?=\s|$)',line.split(':',1)[1])]
        assert len(words) == count, 'Unexpected physical-memory response'
        return words

    def word(self,address): return self.words(address)[0]
    def close(self): self.stream.close(); self.socket.close()

def capture_on_health(health):
    driver = health['output_driver']
    destination = OUTPUT
    if OUTPUT.exists():
        if MODE != 'reference' or not driver['timeouts']: return
        destination = OUTPUT.with_name('dma-timeout-after-reference.json')
        if destination.exists(): return
    if MODE == 'timeout' and not driver['timeouts']: return
    if MODE == 'reference' and not driver['writes']: return
    record = dict(state='SNAPSHOT_STARTING',mode=MODE,physical_tested=False,
        scope='Paused VM DAC registers and validated driver control metadata only; no audio/TLS buffers.',
        health=health,elf=LAYOUT['elf'],layout_sha256=hashlib.sha256((BASE/'layout.json').read_bytes()).hexdigest())
    client = None
    paused = False
    started = time.monotonic()
    try:
        client = QMP()
        client.call('stop'); paused = True
        record['program_counters'] = {}
        for cpu in (0,1):
            try:
                text = client.call('human-monitor-command',{'command-line':'p /x $pc','cpu-index':cpu})
                values = re.findall(r'0x([0-9a-fA-F]+)',text)
                record['program_counters'][str(cpu)] = int(values[-1],16) if values else None
            except Exception:
                record['program_counters'][str(cpu)] = None
        record['registers'] = {name:client.word(0x3ff4f000+offset) for name,offset in
            dict(conf=0x08,raw=0x0c,status=0x10,enabled=0x14,out_link=0x30,eof_descriptor=0x38,link_config=0x60).items()}
        handle = client.word(LAYOUT['s_dac_address'])
        assert handle and handle % 4 == 0
        cfg = {key:client.word(handle+offset) for key,offset in LAYOUT['cfg'].items()}
        assert cfg == dict(desc_num=6,buf_size=1024,freq_hz=48000), 'Unexpected DAC object shape'
        assert client.word(handle+LAYOUT['handle']['chan_cnt']) == 1
        flags = client.word(handle+LAYOUT['handle']['is_enabled'])
        booleans = {key:(flags>>(8*(LAYOUT['handle'][key]-LAYOUT['handle']['is_enabled'])))&255
                    for key in ('is_enabled','is_cyclic','is_running','is_async')}
        assert all(value in (0,1) for value in booleans.values())
        pool = client.word(handle+LAYOUT['handle']['desc_pool'])
        queue = {key:client.word(pool+offset) for key,offset in LAYOUT['queue'].items()}
        assert queue['uxLength'] == 6 and queue['uxItemSize'] == 4 and queue['uxMessagesWaiting'] <= 6
        array = client.word(handle+LAYOUT['handle']['desc'])
        addresses = client.words(array,6)
        assert len(set(addresses)) == 6 and all(0x3ffae000<=address<0x40000000 and address%4==0 for address in addresses)
        descriptors = []
        for address in addresses:
            control,buffer,next_address = client.words(address,3)
            descriptors.append(dict(address=address,control=control,capacity=control&4095,
                length=(control>>12)&4095,owner=bool(control&(1<<31)),eof=bool(control&(1<<30)),
                buffer_address=buffer,next_address=next_address))
        record.update(state='SNAPSHOT_COMPLETE',handle_address=handle,cfg=cfg,flags=booleans,
            queue=queue,head={key:client.word(handle+offset) for key,offset in LAYOUT['head'].items()},
            descriptors=descriptors)
    except Exception as error:
        record.update(state='SNAPSHOT_FAILED',category=type(error).__name__)
    finally:
        if client is not None:
            try:
                if paused: client.call('cont')
                record['events'] = client.events
            except Exception as error:
                record['resume_error_category'] = type(error).__name__
            client.close()
        record['observation_wall_seconds'] = round(time.monotonic()-started,6)
        destination.write_text(json.dumps(record,indent=2)+'\n')
