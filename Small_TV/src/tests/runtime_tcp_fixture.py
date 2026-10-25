"""Construct native TCP metadata using a real C2 ROM heap in private host RAM."""
import copy
import struct

from runtime_instruction_image import InstructionImage
from runtime_tcp_gate_test import MailboxFixture
import runtime_tcp_gate_test as gate_tests


class TcpFixture:
    """Use actual allocator instructions and actual ELF layouts, without a guest VM."""
    def __init__(self, rom, topology, layout, gate_layout):
        """Keep globals/mailbox outside this separate private ROM fixture pool."""
        gate_tests.LAYOUT = gate_layout
        self.mailbox = MailboxFixture()
        self.layout, self.topology = layout, topology
        self.image = InstructionImage(rom)
        self.base, self.size = 0x3FCC0000, 32768
        self.heap = self.image.call('multi_heap_register_impl', self.base, self.size)
        if self.heap != self.base:
            raise ValueError('Private TCP ROM heap registration failed')
        self.objects, self.calls = {}, []
        self.symbol('tcp_ticks', 100)
        self.symbol('num_tcp_pcb', 0)
        for name in ('tcp_active_pcbs', 'tcp_bound_pcbs', 'tcp_listen_pcbs', 'tcp_tw_pcbs'):
            self.symbol(name, 0)

    def read(self, address, size):
        """Serve host-only metadata; remember every attempted transport read."""
        self.calls.append((address, size))
        if self.base <= address < address + size <= self.base + self.size:
            return bytes(self.image.cpu.mem_read(address, size))
        return self.mailbox.read(address, size)

    def put(self, address, size, value):
        """Write only the private host fixture, never an emulated/physical device."""
        if self.base <= address < address + size <= self.base + self.size:
            self.image.cpu.mem_write(address, value.to_bytes(size, 'little'))
        else:
            self.mailbox.put(address, size, value)

    def symbol(self, name, value):
        """Set a synthetic scalar at its actual compiled global address."""
        row = self.layout['symbols'][name]
        self.put(row['address'], row['size'], value)

    def scalar(self, name):
        """Read a fixture global independently of the production decoder."""
        row = self.layout['symbols'][name]
        return int.from_bytes(self.read(row['address'], row['size']), 'little')

    def field(self, kind, address, key, value=None):
        """Read or populate one compiled metadata member in this host fixture."""
        row = self.layout['structures'][kind]['fields'][key]
        if value is not None:
            self.put(address + row['offset'], row['size'], value)
        else:
            return int.from_bytes(self.read(address + row['offset'], row['size']), 'little')

    def allocate(self, size):
        """Allocate through real ROM code, then initialize only its fixture payload."""
        pointer = self.image.call('multi_heap_malloc_impl', self.heap, size)
        if not pointer:
            raise ValueError('Private TCP ROM heap exhausted')
        self.image.cpu.mem_write(pointer, bytes(size))
        return pointer

    def pcb(self, role='active', state=None):
        """Register a fixture PCB in the native list and maintain its separate count."""
        from runtime_tcp_layout import LISTS
        kind = 'tcp_pcb_listen' if role == 'listen' else 'tcp_pcb'
        pointer = self.allocate(self.layout['structures'][kind]['size'])
        state = state or {'active': 'ESTABLISHED', 'bound': 'CLOSED', 'listen': 'LISTEN', 'time_wait': 'TIME_WAIT'}[role]
        self.field(kind, pointer, 'state', self.layout['states'][state])
        self.field(kind, pointer, 'next', self.scalar(LISTS[role]))
        self.symbol(LISTS[role], pointer)
        if role != 'listen':
            self.field(kind, pointer, 'tmr', self.scalar('tcp_ticks') - 2)
            self.symbol('num_tcp_pcb', self.scalar('num_tcp_pcb') + 1)
        self.objects[pointer] = kind
        return pointer

    def pbuf(self, length=24, next_pointer=0, total=None, ref=1, payload=None):
        """Create a contiguous buffer or a reference to separate RAM/ROM data."""
        size = self.layout['structures']['pbuf']['size']
        pointer = self.allocate(size + (length if payload is None else 0))
        if total is None:
            total = length + (self.field('pbuf', next_pointer, 'tot_len') if next_pointer else 0)
        for key, value in (('next', next_pointer), ('payload', pointer + size if payload is None else payload),
                           ('len', length), ('tot_len', total), ('ref', ref),
                           ('type_internal', 0x80 if payload is None else 0x01)):
            self.field('pbuf', pointer, key, value)
        self.objects[pointer] = 'pbuf'
        return pointer

    def segment(self, pcb, pbuf, queue='unacked', length=None):
        """Add an actual allocated segment without faking its pbuf reference count."""
        pointer = self.allocate(self.layout['structures']['tcp_seg']['size'])
        for key, value in (('p', pbuf), ('next', self.field('tcp_pcb', pcb, queue)),
                           ('len', self.field('pbuf', pbuf, 'tot_len') if length is None else length)):
            self.field('tcp_seg', pointer, key, value)
        self.field('tcp_pcb', pcb, queue, pointer)
        if queue in ('unsent', 'unacked'):
            count, cursor = 0, pbuf
            while cursor:
                count += 1
                cursor = self.field('pbuf', cursor, 'next')
            self.field('tcp_pcb', pcb, 'snd_queuelen', self.field('tcp_pcb', pcb, 'snd_queuelen') + count)
        self.objects[pointer] = 'tcp_seg'
        return pointer

    def frame(self, label='cycle-1', when=30):
        """Take actual ROM counters and exact linked walker output for replay."""
        header = bytes(self.image.cpu.mem_read(self.heap, 20))
        values = struct.unpack('<5I', header)
        summary = {'caps': 6158, 'free_bytes': values[1], 'minimum_free_bytes': values[2], 'pool_size': values[3]}
        inventory = self.topology.walker.inspect(
            lambda address, size: bytes(self.image.cpu.mem_read(address, size)),
            values[4], values[3], values[1], (self.base, self.base + self.size))
        return {'label': label, 'guest_seconds': when,
                'heap': {'caps': 4, 'free_bytes': values[1], 'minimum_free_bytes': values[2], 'heaps': [copy.deepcopy(summary)]},
                'heap_topology': {'elf_sha256': self.layout['elf_sha256'],
                    'rom_sha256': self.topology.walker.image.rom_sha256,
                    'dispatch_pointer': self.topology.dispatch_layout['symbols']['heap_tlsf_patch_table_ptr']['address'],
                    'dispatch_hex': self.topology.expected_dispatch.hex(),
                    'heaps': [{'heap_address': self.heap, 'header_hex': header.hex(),
                               'summary': summary, 'inventory': inventory}]}}
