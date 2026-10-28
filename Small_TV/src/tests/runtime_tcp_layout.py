"""Resolve selected TCP metadata fields and state values from the tested ELF."""
import hashlib
from pathlib import Path

from runtime_memory import RAM, size_of
from runtime_tcp_gate import QUALIFIED_ELF


FIELDS = {
    'tcp_pcb': {'next': 4, 'state': 4, 'tmr': 4, 'snd_queuelen': 2,
                'unsent': 4, 'unacked': 4, 'ooseq': 4, 'refused_data': 4},
    'tcp_pcb_listen': {'next': 4, 'state': 4},
    'tcp_seg': {'next': 4, 'p': 4, 'len': 2},
    'pbuf': {'next': 4, 'payload': 4, 'tot_len': 2, 'len': 2, 'ref': 1, 'type_internal': 1},
}
LISTS = {'bound': 'tcp_bound_pcbs', 'listen': 'tcp_listen_pcbs',
         'active': 'tcp_active_pcbs', 'time_wait': 'tcp_tw_pcbs'}
STATES = ('CLOSED', 'LISTEN', 'SYN_SENT', 'SYN_RCVD', 'ESTABLISHED', 'FIN_WAIT_1',
          'FIN_WAIT_2', 'CLOSE_WAIT', 'CLOSING', 'LAST_ACK', 'TIME_WAIT')


def tcp_layout(app):
    """Qualify native ABI and the already checked zero-prefix malloc policy."""
    from elftools.elf.elffile import ELFFile
    app = Path(app)
    digest = hashlib.sha256(app.read_bytes()).hexdigest()
    if digest != QUALIFIED_ELF:
        raise ValueError('TCP allocation policy is not qualified for this ELF')
    with app.open('rb') as stream:
        elf = ELFFile(stream)
        if elf.elfclass != 32 or not elf.little_endian or elf['e_machine'] != 'EM_RISCV':
            raise ValueError('Expected little-endian RV32 TCP metadata')
        wanted = set(LISTS.values()) | {'tcp_ticks', 'num_tcp_pcb'}
        symbols = {s.name: {'address': s['st_value'], 'size': s['st_size']}
                   for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name in wanted}
        structures, states = {}, None
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                name = die.attributes.get('DW_AT_name')
                name = name.value.decode('ascii', errors='replace') if name else ''
                if name == 'tcp_state' and die.tag == 'DW_TAG_enumeration_type' and states is None:
                    states = {m.attributes['DW_AT_name'].value.decode('ascii'): m.attributes['DW_AT_const_value'].value
                              for m in die.iter_children() if m.tag == 'DW_TAG_enumerator'}
                if (name not in FIELDS or name in structures or die.tag != 'DW_TAG_structure_type' or
                        'DW_AT_byte_size' not in die.attributes):
                    continue
                fields = {}
                for member in die.iter_children():
                    if member.tag != 'DW_TAG_member':
                        continue
                    key = member.attributes['DW_AT_name'].value.decode('ascii')
                    if key in FIELDS[name]:
                        fields[key] = {'offset': member.attributes['DW_AT_data_member_location'].value,
                                       'size': size_of(member.get_DIE_from_attribute('DW_AT_type'))}
                structures[name] = {'size': size_of(die), 'fields': fields}
            if len(structures) == len(FIELDS) and states is not None:
                break
    layout = {'elf_sha256': digest, 'symbols': symbols, 'structures': structures, 'states': states,
              'metadata_allocation_offset': 0, 'pbuf_contiguous_flag': 0x80}
    validate_layout(layout)
    return layout


def validate_layout(layout):
    """Reject incomplete, overlapping or differently compiled pointer/scalar fields."""
    if (layout['elf_sha256'] != QUALIFIED_ELF or layout['metadata_allocation_offset'] != 0 or
            layout['pbuf_contiguous_flag'] != 0x80 or set(layout['states']) != set(STATES) or
            len(set(layout['states'].values())) != len(STATES) or
            any(type(value) is not int or not 0 <= value <= 255 for value in layout['states'].values())):
        raise ValueError('Unqualified TCP ABI or allocation policy')
    if set(layout['symbols']) != set(LISTS.values()) | {'tcp_ticks', 'num_tcp_pcb'}:
        raise ValueError('Missing TCP globals')
    for row in layout['symbols'].values():
        if (row['size'] != 4 or type(row['address']) is not int or row['address'] % 4 or
                not any(lo <= row['address'] < row['address'] + 4 <= hi for lo, hi in RAM)):
            raise ValueError('TCP global outside bounded SRAM')
    for name, expected in FIELDS.items():
        structure = layout['structures'][name]
        if not 0 < structure['size'] <= 1024 or set(structure['fields']) != set(expected):
            raise ValueError('Missing or oversized TCP metadata structure')
        spans = []
        for key, field in structure['fields'].items():
            offset, size = field['offset'], field['size']
            if (type(offset) is not int or size != expected[key] or
                    not 0 <= offset < offset + size <= structure['size'] or
                    offset % min(size, 4) or any(offset < end and start < offset + size for start, end in spans)):
                raise ValueError('Invalid or overlapping TCP metadata field')
            spans.append((offset, offset + size))
