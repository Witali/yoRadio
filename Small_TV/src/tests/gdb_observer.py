"""Observe completed QEMU calls through hardware breakpoints and read-only RSP.

There are no memory/register writes, software breakpoints or continue addresses.
The guest's PC is changed only by its own instruction execution.
"""
import socket
from contextlib import contextmanager
import time


class Observer:
    """Small strict localhost GDB client for immutable firmware observations."""
    def __init__(self, port):
        self.socket = socket.create_connection(('127.0.0.1',port),5)
        self.socket.settimeout(120)
        self._deadline = None
        self.breakpoints = set()
        response = self.request('qSupported')
        if 'qXfer:features:read+' not in response:
            raise AssertionError('QEMU does not advertise target register descriptions')
        self.target = self.feature('target.xml')
        if 'riscv' not in self.target:
            raise AssertionError('Expected a RISC-V QEMU target')
        self.request('?')

    def feature(self, name):
        """Read a bounded target-description XML without loading host files from it."""
        result = ''
        while len(result)<65536:
            part = self.request(f'qXfer:features:read:{name}:{len(result):x},1000')
            if not part or part[0] not in 'ml':
                raise AssertionError('Invalid target-description reply')
            result += part[1:]
            if part[0]=='l':
                return result
        raise AssertionError('Oversized register description')

    @contextmanager
    def time_limit(self, seconds):
        """Bound all RSP I/O in one diagnostic, including slow partial replies."""
        if type(seconds) not in (int, float) or not 0 < seconds <= 30:
            raise ValueError('Expected an observer deadline of at most 30 seconds')
        previous, timeout = self._deadline, self.socket.gettimeout()
        deadline = time.monotonic() + seconds
        self._deadline = min(previous, deadline) if previous is not None else deadline
        try:
            yield
        finally:
            self._deadline = previous
            self.socket.settimeout(timeout)

    def _limit_io(self):
        """Keep a total deadline from restarting on each socket byte or request."""
        if self._deadline is not None:
            remaining = self._deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('Observer diagnostic deadline expired')
            timeout = self.socket.gettimeout()
            self.socket.settimeout(min(timeout, remaining) if timeout is not None else remaining)

    def _recv(self, size):
        """Read with the remaining shared deadline while preserving normal mode."""
        self._limit_io()
        return self.socket.recv(size)

    def _send(self, data):
        """Send an existing permitted packet within the same diagnostic budget."""
        self._limit_io()
        self.socket.sendall(data)

    def receive(self):
        """Check packet checksums and decode RSP escaping/run-length encoding."""
        while True:
            first = self._recv(1)
            if not first:
                raise ConnectionError('QEMU debugger disconnected')
            if first==b'$':
                break
            if first==b'-':
                raise AssertionError('QEMU rejected the observer packet checksum')
            if first!=b'+':
                raise AssertionError('Unexpected debugger framing byte')
        payload = bytearray()
        while True:
            byte = self._recv(1)
            if not byte:
                raise ConnectionError('Truncated debugger response')
            if byte==b'#':
                break
            payload += byte
            if len(payload)>262144:
                raise AssertionError('Oversized debugger response')
        digest = bytearray()
        while len(digest)<2:
            part = self._recv(2-len(digest))
            if not part:raise ConnectionError('Missing debugger checksum')
            digest += part
        if sum(payload)%256 != int(digest,16):
            raise AssertionError('Debugger response checksum mismatch')
        self._send(b'+')
        decoded = bytearray()
        cursor = 0
        while cursor<len(payload):
            byte = payload[cursor]; cursor += 1
            if byte==ord('}'):
                if cursor==len(payload):raise AssertionError('Truncated RSP escape')
                decoded.append(payload[cursor]^0x20); cursor += 1
            elif byte==ord('*'):
                if not decoded or cursor==len(payload):raise AssertionError('Invalid RSP repetition')
                count = payload[cursor]-29; cursor += 1
                if count<0:raise AssertionError('Invalid RSP repetition count')
                decoded += bytes([decoded[-1]])*count
            else:
                decoded.append(byte)
        return decoded.decode('ascii')

    def request(self, command):
        """Send only read, hardware-breakpoint and unqualified-continue requests."""
        allowed = (command in ('?','g','c','qSupported') or
                   command.startswith(('qXfer:features:read:','m','p','Z1,','z1,')))
        if not allowed:
            raise AssertionError('State-writing debugger command is forbidden')
        data = command.encode('ascii')
        self._send(b'$'+data+b'#'+f'{sum(data)%256:02x}'.encode())
        response = self.receive()
        if response.startswith('E'):
            raise RuntimeError('Debugger request failed: '+command+' -> '+response)
        return response

    def register(self, number):
        """Read one RV32 integer register; unsupported or wider registers fail."""
        raw = bytes.fromhex(self.request(f'p{number:x}'))
        if len(raw)!=4:
            raise AssertionError('Expected a 32-bit register')
        return int.from_bytes(raw,'little')

    def memory(self, address, size):
        """Read only a small bounded code/typed-data observation."""
        if not 0<size<=4096:
            raise ValueError('Observer memory read must remain bounded')
        raw = bytes.fromhex(self.request(f'm{address:x},{size:x}'))
        if len(raw)!=size:
            raise AssertionError('Short debugger memory read')
        return raw

    def breakpoint(self, address, insert=True):
        """Change QEMU's hardware breakpoint list, leaving guest code bytes intact."""
        reply = self.request(f'{"Z" if insert else "z"}1,{address:x},2')
        if reply!='OK':
            raise AssertionError('QEMU rejected a hardware breakpoint')
        if insert:self.breakpoints.add(address)
        else:self.breakpoints.remove(address)

    def continue_to(self, address):
        """Run normally until the requested instruction; never assign a guest PC."""
        reply = self.request('c')
        if not reply.startswith(('T05','S05')) or self.register(32)!=address:
            raise AssertionError('Unexpected QEMU stop: '+reply)

    def resume(self):
        """Resume without a target address; QMP may observe elapsed virtual time."""
        self._send(b'$c#63')

    def interrupt(self):
        """Pause normally running QEMU without changing a register or instruction."""
        self._send(b'\x03')
        reply=self.receive()
        if not reply.startswith(('T02','S02')):
            raise AssertionError('Unexpected debugger interrupt response: '+reply)

    def close(self):
        """Release this debugger connection; the VM owner handles shutdown."""
        self.socket.close()
