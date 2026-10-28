"""Observe TCP lists and buffer metadata without reading packet contents."""
from collections import Counter
import hashlib
import json

from runtime_tcp_allocations import AllocationIndex
from runtime_tcp_gate import TcpMailboxGate, tcp_gate_layout
from runtime_tcp_layout import FIELDS, LISTS, tcp_layout, validate_layout


def canonical(data):
    """Preserve JSON types as well as values when pairing and replaying metadata."""
    return json.dumps(data, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


class TcpSnapshot:
    """Require a quiet TCP/IP actor and independently replayed live allocations."""
    def __init__(self, app, layout=None, gate_layout=None):
        """Bind both the synchronization and allocation policies to the same ELF."""
        self.layout = layout or tcp_layout(app)
        validate_layout(self.layout)
        self.gate = TcpMailboxGate(gate_layout or tcp_gate_layout(app))
        if self.layout['elf_sha256'] != self.gate.layout['elf_sha256']:
            raise ValueError('TCP gate and metadata ELF differ')

    def sample(self, read, snapshot, topology):
        """Read selected fields only; busy samples explicitly omit the TCP inventory."""
        result = {'elf_sha256': self.layout['elf_sha256'], 'label': snapshot['label'],
                  'guest_seconds': snapshot['guest_seconds'],
                  'heap_inventory_sha256': hashlib.sha256(canonical(snapshot['heap_topology'])).hexdigest(),
                  'gate': self.gate.sample(read), 'observed': False, 'reads': []}
        if not result['gate']['quiet']:
            return result
        index = AllocationIndex(topology, snapshot)
        reads = result['reads']

        def number(address, size):
            """Copy one already bounded scalar field, never a packet or HTTP buffer."""
            TcpMailboxGate.extent(address, size)
            data = read(address, size)
            if len(data) != size:
                raise ValueError('Short TCP metadata read')
            reads.append([address, size, data.hex()])
            return int.from_bytes(data, 'little')

        def symbol(name):
            """Resolve every global pointer/count from the linked native symbols."""
            row = self.layout['symbols'][name]
            return number(row['address'], row['size'])

        def fields(kind, address):
            """Validate the complete metadata object before the first selected read."""
            if address % 4:
                raise ValueError('Unaligned TCP metadata object')
            structure = self.layout['structures'][kind]
            index.claim(kind, address, structure['size'])
            return {key: number(address + structure['fields'][key]['offset'], structure['fields'][key]['size'])
                    for key in FIELDS[kind]}

        ticks, allocated_pcbs = symbol('tcp_ticks'), symbol('num_tcp_pcb')
        heads = {name: symbol(symbol_name) for name, symbol_name in LISTS.items()}
        pcbs, segments, pbufs, pbuf_edges = [], {}, {}, set()

        def pbuf_chain(head, owner_kind, owner):
            """Accept shared references, but reject cycles inside any individual chain."""
            chain, seen, pointer = [], set(), head
            if pointer:
                pbuf_edges.add((owner_kind, owner, pointer))
            while pointer:
                if pointer in seen or len(chain) >= 4096:
                    raise ValueError('Cyclic or oversized pbuf chain')
                seen.add(pointer)
                if pointer not in pbufs:
                    if len(pbufs) >= 4096:
                        raise ValueError('Oversized TCP pbuf inventory')
                    data = fields('pbuf', pointer)
                    if not data['ref'] or data['tot_len'] < data['len']:
                        raise ValueError('Invalid pbuf reference count or lengths')
                    payload_allocation = None
                    if data['len']:
                        payload_allocation = index.claim('pbuf-data', data['payload'], data['len'],
                                                         owner=pointer, metadata=False, optional=True)
                        if data['type_internal'] & self.layout['pbuf_contiguous_flag']:
                            if payload_allocation != pointer:
                                raise ValueError('Contiguous pbuf payload is outside its allocation')
                    pbufs[pointer] = {'address': pointer, 'fields': data, 'payload_allocation': payload_allocation}
                data = pbufs[pointer]['fields']
                chain.append(pointer)
                if data['next']:
                    pbuf_edges.add(('next', pointer, data['next']))
                pointer = data['next']
            for offset, pointer in enumerate(chain):
                data = pbufs[pointer]['fields']
                following = pbufs[chain[offset + 1]]['fields']['tot_len'] if offset + 1 < len(chain) else 0
                # tot_len == len marks a packet boundary even if next starts a
                # different packet. A non-boundary node must balance its chain.
                if offset == len(chain) - 1 and data['tot_len'] != data['len']:
                    raise ValueError('Truncated pbuf chain')
                if data['tot_len'] != data['len'] and data['tot_len'] != data['len'] + following:
                    raise ValueError('Inconsistent pbuf packet/chain total length')
            return chain

        def segment_chain(head, pcb, queue):
            """Account for each queue node once while retaining shared pbuf ownership."""
            chain, pointer = [], head
            while pointer:
                if pointer in segments or len(segments) >= 2048:
                    raise ValueError('Cyclic, multiply owned or oversized TCP segment list')
                data = fields('tcp_seg', pointer)
                if not data['p']:
                    raise ValueError('TCP segment has no pbuf')
                buffers = pbuf_chain(data['p'], 'segment', pointer)
                if data['len'] > pbufs[buffers[0]]['fields']['tot_len']:
                    raise ValueError('TCP segment exceeds its packet length')
                segments[pointer] = {'address': pointer, 'pcb': pcb, 'queue': queue,
                                     'fields': data, 'pbuf_chain': buffers}
                chain.append(pointer)
                pointer = data['next']
            return chain

        seen_pcbs, states = set(), self.layout['states']
        allowed = {'bound': {states['CLOSED']}, 'listen': {states['LISTEN']},
                   'time_wait': {states['TIME_WAIT']},
                   'active': set(states.values()) - {states['CLOSED'], states['LISTEN'], states['TIME_WAIT']}}
        state_names = {value: name for name, value in states.items()}
        for name, pointer in heads.items():
            kind = 'tcp_pcb_listen' if name == 'listen' else 'tcp_pcb'
            while pointer:
                if pointer in seen_pcbs or len(seen_pcbs) >= 256:
                    raise ValueError('Cyclic, multiply owned or oversized TCP PCB list')
                seen_pcbs.add(pointer)
                data = fields(kind, pointer)
                if data['state'] not in allowed[name]:
                    raise ValueError('TCP PCB state does not match its list')
                row = {'address': pointer, 'list': name, 'state': state_names[data['state']], 'fields': data}
                if kind == 'tcp_pcb':
                    age = (ticks - data['tmr']) & 0xFFFFFFFF
                    if age >= 2**31:
                        raise ValueError('TCP PCB timer is ahead of the observed ticks')
                    row['age_ticks'] = age
                    row['queues'] = {queue: segment_chain(data[queue], pointer, queue)
                                     for queue in ('unsent', 'unacked', 'ooseq')}
                    row['refused_pbuf_chain'] = pbuf_chain(data['refused_data'], 'refused', pointer)
                    queued = sum(len(segments[segment]['pbuf_chain']) for queue in ('unsent', 'unacked')
                                 for segment in row['queues'][queue])
                    if data['snd_queuelen'] != queued:
                        raise ValueError('TCP send queue length differs from its actual pbuf chains')
                pcbs.append(row)
                pointer = data['next']
        incoming = Counter(edge[2] for edge in pbuf_edges)
        for pointer, row in pbufs.items():
            row['references_observed'] = incoming[pointer]
            if row['fields']['ref'] < incoming[pointer]:
                raise ValueError('Pbuf refcount is smaller than its observed distinct owners')
        registered = sum(row['list'] != 'listen' for row in pcbs)
        if not registered <= allocated_pcbs <= 256:
            raise ValueError('TCP PCB allocation counter is inconsistent')
        result.update(observed=True, tcp_ticks=ticks, num_tcp_pcb=allocated_pcbs,
                      registered_nonlisten_pcbs=registered, unregistered_pcbs=allocated_pcbs - registered,
                      list_counts={name: sum(row['list'] == name for row in pcbs) for name in LISTS},
                      state_counts=dict(sorted(Counter(row['state'] for row in pcbs).items())),
                      pcbs=pcbs, segments=[segments[key] for key in sorted(segments)],
                      pbufs=[pbufs[key] for key in sorted(pbufs)], attribution=index.summary())
        return result

    def validate(self, snapshot, topology):
        """Recompute the complete TCP observation from exact archived metadata reads."""
        data = snapshot['tcp_topology']
        reads = data['gate']['reads'] + data['reads']
        if not isinstance(reads, list) or len(reads) > 50000:
            raise ValueError('Unbounded TCP metadata transcript')
        cursor = 0

        def read(address, size):
            """Reject reordered, missing, incorrectly typed or oversized read requests."""
            nonlocal cursor
            if cursor >= len(reads):
                raise ValueError('Missing TCP metadata read')
            row = reads[cursor]
            if (len(row) != 3 or type(row[0]) is not int or type(row[1]) is not int or
                    row[:2] != [address, size] or type(row[2]) is not str or len(row[2]) != size * 2):
                raise ValueError('Changed or noncanonical TCP metadata read')
            cursor += 1
            return bytes.fromhex(row[2])

        replay = self.sample(read, snapshot, topology)
        if cursor != len(reads) or canonical(replay) != canonical(data):
            raise ValueError('TCP inventory differs from typed metadata replay')
