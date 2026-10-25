"""Qualify an idle lwIP mailbox before inspecting mutable TCP lists."""
import hashlib
from pathlib import Path

from runtime_memory import RAM, MemorySnapshot, size_of


# This policy was checked against the linked sys_thread_tcpip implementation and
# its build configuration. A new ELF must qualify its synchronization separately.
QUALIFIED_ELF = '76b5ce3700d299b607774467a57bc95e07d3cd39f6385bc3a1befd0504c2dad8'
FIELDS = {'sys_mbox_s': ('os_mbox',),
          'QueueDefinition': ('xTasksWaitingToReceive', 'uxMessagesWaiting'),
          'tskTaskControlBlock': ('xEventListItem',),
          'xLIST': ('uxNumberOfItems', 'xListEnd'),
          'xLIST_ITEM': ('pxNext', 'pxPrevious', 'pvOwner', 'pxContainer')}


def tcp_gate_layout(app):
    """Read selected native DWARF fields, ignoring unrelated flexible arrays."""
    from elftools.elf.elffile import ELFFile
    app = Path(app)
    digest = hashlib.sha256(app.read_bytes()).hexdigest()
    if digest != QUALIFIED_ELF:
        raise ValueError('TCP synchronization is not qualified for this ELF')
    with app.open('rb') as stream:
        elf = ELFFile(stream)
        if elf.elfclass != 32 or not elf.little_endian or elf['e_machine'] != 'EM_RISCV':
            raise ValueError('Expected little-endian RV32 TCP state')
        wanted = {'tcpip_mbox', 'pxCurrentTCBs'}
        symbols = {s.name: {'address': s['st_value'], 'size': s['st_size']}
                   for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name in wanted}
        structures, holders = {}, {}
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                name = die.attributes.get('DW_AT_name')
                name = name.value.decode('ascii', errors='replace') if name else ''
                if die.tag == 'DW_TAG_variable' and name == 'lwip_task' and 'DW_AT_location' in die.attributes:
                    location = die.attributes['DW_AT_location']
                    if location.form != 'DW_FORM_exprloc' or len(location.value) != 5 or location.value[0] != 3:
                        raise ValueError('Unexpected native lwIP task pointer location')
                    address = int.from_bytes(bytes(location.value[1:]), 'little')
                    holders[address] = size_of(die.get_DIE_from_attribute('DW_AT_type'))
                if (name not in FIELDS or name in structures or die.tag != 'DW_TAG_structure_type' or
                        'DW_AT_byte_size' not in die.attributes):
                    continue
                fields = {}
                for member in die.iter_children():
                    if member.tag != 'DW_TAG_member':
                        continue
                    key = member.attributes['DW_AT_name'].value.decode('ascii')
                    if key not in FIELDS[name]:
                        continue
                    offset = member.attributes['DW_AT_data_member_location'].value
                    fields[key] = {'offset': offset, 'size': size_of(member.get_DIE_from_attribute('DW_AT_type'))}
                if set(fields) != set(FIELDS[name]):
                    raise ValueError('Missing native mailbox field in ' + name)
                structures[name] = {'size': size_of(die), 'fields': fields}
            if len(structures) == len(FIELDS) and holders:
                break
    if set(symbols) != wanted or len(holders) != 1 or next(iter(holders.values())) != 4:
        raise ValueError('Missing or ambiguous lwIP mailbox ownership symbols')
    symbols['lwip_task'] = {'address': next(iter(holders)), 'size': 4}
    layout = {'elf_sha256': digest, 'synchronization': 'exclusive-tcpip-task-no-core-locking',
              'symbols': symbols, 'structures': structures}
    TcpMailboxGate(layout)
    return layout


class TcpMailboxGate:
    """Observe only a verified task blocked on the actual TCP/IP receive queue."""
    def __init__(self, layout):
        """Qualify every pointer, selected field and the exact synchronization policy."""
        self.layout = layout
        if layout['elf_sha256'] != QUALIFIED_ELF or layout['synchronization'] != 'exclusive-tcpip-task-no-core-locking':
            raise ValueError('Unqualified TCP mailbox synchronization policy')
        for row in layout['symbols'].values():
            self.extent(row['address'], row['size'])
            if row['size'] != 4 or row['address'] % 4:
                raise ValueError('Unexpected mailbox pointer ABI')
        if set(layout['symbols']) != {'tcpip_mbox', 'pxCurrentTCBs', 'lwip_task'}:
            raise ValueError('Missing mailbox identity symbols')
        for name, keys in FIELDS.items():
            structure = layout['structures'][name]
            if not 0 < structure['size'] <= 1024 or set(structure['fields']) != set(keys):
                raise ValueError('Invalid mailbox structure ABI')
            spans = []
            for field in structure['fields'].values():
                start, size = field['offset'], field['size']
                if (type(start) is not int or type(size) is not int or not 0 <= start < start + size <= structure['size'] or
                        any(start < end and begin < start + size for begin, end in spans)):
                    raise ValueError('Overlapping or out-of-bounds mailbox field')
                spans.append((start, start + size))
        queue = layout['structures']['QueueDefinition']
        mailbox = layout['structures']['sys_mbox_s']['fields']['os_mbox']
        if mailbox['size'] != queue['size'] or mailbox['offset'] % 4:
            raise ValueError('lwIP mailbox does not contain the compiled queue')
        list_size = layout['structures']['xLIST']['size']
        item_size = layout['structures']['xLIST_ITEM']['size']
        if (queue['fields']['xTasksWaitingToReceive']['size'] != list_size or
                layout['structures']['tskTaskControlBlock']['fields']['xEventListItem']['size'] != item_size):
            raise ValueError('Queue/TCB list ABI differs')
        for structure, keys in (('QueueDefinition', ('uxMessagesWaiting',)),
                                ('xLIST', ('uxNumberOfItems',)), ('xLIST_ITEM', FIELDS['xLIST_ITEM'])):
            if any(layout['structures'][structure]['fields'][key]['size'] != 4 for key in keys):
                raise ValueError('Unexpected mailbox list scalar width')

    @staticmethod
    def extent(address, size):
        """Reject invalid pointers before exposing them to the guest transport."""
        if (type(address) is not int or type(size) is not int or not 0 < size <= 1024 or
                not any(lo <= address < address + size <= hi for lo, hi in RAM)):
            raise ValueError('Mailbox observation outside bounded C2 SRAM')

    def sample(self, read):
        """Busy is an observation, never permission to force or fake a quiet state."""
        words = []

        def memory(address, size):
            """Record only bounded scalar/list metadata reads for independent replay."""
            self.extent(address, size)
            data = read(address, size)
            if len(data) != size:
                raise ValueError('Short mailbox metadata read')
            words.append([address, size, data.hex()])
            return data

        def symbol(name):
            """Read one actual linked pointer, without compiler-name suffix guesses."""
            row = self.layout['symbols'][name]
            return int.from_bytes(memory(row['address'], row['size']), 'little')

        def field(name, address, key):
            """Read exactly one selected metadata member, not the whole object."""
            row = self.layout['structures'][name]['fields'][key]
            return int.from_bytes(memory(address + row['offset'], row['size']), 'little')

        def finish(quiet, reason):
            """Keep busy observations explicit alongside their exact read transcript."""
            return {'elf_sha256': self.layout['elf_sha256'], 'quiet': quiet, 'reason': reason,
                    'task_address': task, 'mailbox_address': mailbox, 'reads': words}

        task, mailbox, current = symbol('lwip_task'), symbol('tcpip_mbox'), symbol('pxCurrentTCBs')
        if not task or not mailbox:
            return finish(False, 'not-initialized')
        for address, name in ((task, 'tskTaskControlBlock'), (mailbox, 'sys_mbox_s')):
            self.extent(address, self.layout['structures'][name]['size'])
            if address % 4:
                raise ValueError('Unaligned TCP/IP task or mailbox')
        if current == task:
            return finish(False, 'tcpip-running')
        queue = mailbox + self.layout['structures']['sys_mbox_s']['fields']['os_mbox']['offset']
        waiting = queue + self.layout['structures']['QueueDefinition']['fields']['xTasksWaitingToReceive']['offset']
        event = task + self.layout['structures']['tskTaskControlBlock']['fields']['xEventListItem']['offset']
        if field('xLIST_ITEM', event, 'pxContainer') != waiting:
            return finish(False, 'tcpip-not-waiting-on-mailbox')
        if field('QueueDefinition', queue, 'uxMessagesWaiting'):
            return finish(False, 'mailbox-has-work')
        # An event container alone can be stale/corrupt. Verify the actual list,
        # both link directions, unique owner and the identity of the TCB's item.
        reader = MemorySnapshot(memory, self.layout)
        if reader.task_list(waiting) != [task]:
            raise ValueError('TCP/IP mailbox waiting list has a different owner')
        data = reader.structure('xLIST', waiting)
        end = self.layout['structures']['xLIST']['fields']['xListEnd']['offset']
        nxt = self.layout['structures']['xLIST_ITEM']['fields']['pxNext']['offset']
        if int.from_bytes(data[end + nxt:end + nxt + 4], 'little') != event:
            raise ValueError('TCP/IP mailbox uses a different event item')
        return finish(True, 'tcpip-blocked-on-empty-mailbox')

    def replay(self, row):
        """Replay the exact read order and reject omitted or unused metadata."""
        reads, cursor = row['reads'], 0
        if type(reads) is not list or len(reads) > 140:
            raise ValueError('Unbounded mailbox metadata transcript')

        def read(address, size):
            """Serve only the next exact archived metadata request."""
            nonlocal cursor
            if cursor >= len(reads) or reads[cursor][:2] != [address, size]:
                raise ValueError('Missing or reordered mailbox metadata')
            data = bytes.fromhex(reads[cursor][2])
            cursor += 1
            return data

        result = self.sample(read)
        if cursor != len(reads) or result != row:
            raise ValueError('Noncanonical or unused mailbox metadata')
        return result
