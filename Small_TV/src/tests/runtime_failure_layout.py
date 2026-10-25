"""Describe selected photo/queue metadata from the exact native ELF's DWARF."""
from pathlib import Path

from runtime_memory import RAM, size_of


def resolved(die):
    """Remove qualifiers without guessing pointer targets or missing types."""
    for _ in range(16):
        if die.tag not in ('DW_TAG_typedef', 'DW_TAG_const_type', 'DW_TAG_volatile_type', 'DW_TAG_restrict_type'):
            return die
        die = die.get_DIE_from_attribute('DW_AT_type')
    raise ValueError('Unresolved diagnostic type')


def member_path(die, path):
    """Resolve nested structure/union offsets and one scalar's declared width."""
    offset = 0
    for name in path:
        die = resolved(die)
        if die.tag not in ('DW_TAG_structure_type', 'DW_TAG_union_type'):
            raise ValueError('Expected a diagnostic aggregate')
        fields = [row for row in die.iter_children() if row.tag == 'DW_TAG_member' and
                  row.attributes.get('DW_AT_name') and row.attributes['DW_AT_name'].value.decode() == name]
        if len(fields) != 1:
            raise ValueError('Missing/ambiguous diagnostic member: ' + name)
        field = fields[0]
        location = field.attributes.get('DW_AT_data_member_location')
        if location is None and die.tag != 'DW_TAG_union_type':
            raise ValueError('Missing diagnostic member offset')
        part = location.value if location else 0
        if type(part) is not int:
            raise ValueError('Nonconstant diagnostic member offset')
        offset += part
        die = field.get_DIE_from_attribute('DW_AT_type')
    leaf = resolved(die)
    size = size_of(leaf)
    if size not in (1, 4, 8):
        raise ValueError('Unexpected diagnostic scalar size')
    encoding = leaf.attributes.get('DW_AT_encoding')
    return dict(offset=offset, size=size, signed=bool(encoding and encoding.value in (5, 6)))


def failure_layout(path):
    """Scope duplicate static names by compilation unit; never use old ELF offsets."""
    from elftools.elf.elffile import ELFFile
    worker = {'jobs', 'codec_mutex', 'ready', 'pending', 'foreground_pending', 'cancel_background', 'enabled'}
    uploads = ('active', 'preparing', 'finishing', 'slot', 'chunks', 'next', 'length', 'received',
               'cache_program_bytes', 'last_activity')
    scalars, queue, upload = {}, None, None
    with Path(path).open('rb') as stream:
        elf = ELFFile(stream)
        if elf.elfclass != 32 or not elf.little_endian or elf['e_machine'] != 'EM_RISCV':
            raise ValueError('Expected native RV32 diagnostic ELF')
        symbols = [s for s in elf.get_section_by_name('.symtab').iter_symbols()
                   if s.name == 'media_mutex' and s['st_value'] and s['st_size'] == 4]
        if len(symbols) != 1:
            raise ValueError('Missing/ambiguous media mutex')
        scalars['media_mutex'] = dict(address=symbols[0]['st_value'], size=4, signed=False)
        for cu in elf.get_dwarf_info().iter_CUs():
            top = cu.get_top_DIE(); name = top.attributes.get('DW_AT_name')
            unit = name.value.decode().replace('\\', '/') if name else ''
            for die in cu.iter_DIEs():
                name = die.attributes.get('DW_AT_name'); name = name.value.decode() if name else ''
                if die.tag == 'DW_TAG_structure_type' and name == 'QueueDefinition' and 'DW_AT_byte_size' in die.attributes and queue is None:
                    fields = {'count': ('uxMessagesWaiting',), 'length': ('uxLength',), 'item_size': ('uxItemSize',),
                              'receive_waiters': ('xTasksWaitingToReceive', 'uxNumberOfItems'),
                              'send_waiters': ('xTasksWaitingToSend', 'uxNumberOfItems'),
                              'mutex_holder_tcb': ('u', 'xSemaphore', 'xMutexHolder')}
                    queue = {key: member_path(die, parts) for key, parts in fields.items()}
                if die.tag != 'DW_TAG_variable' or 'DW_AT_location' not in die.attributes:
                    continue
                if not (unit.endswith('/photo_worker.c') and name in worker or unit.endswith('/photo_upload.c') and name == 'upload'):
                    continue
                location = die.attributes['DW_AT_location']
                if location.form != 'DW_FORM_exprloc' or len(location.value) != 5 or location.value[0] != 3:
                    raise ValueError('Unexpected diagnostic global location')
                address = int.from_bytes(bytes(location.value[1:]), 'little')
                type_die = die.get_DIE_from_attribute('DW_AT_type')
                if name == 'upload':
                    if upload is not None:
                        raise ValueError('Duplicate upload state')
                    upload = {key: dict(address=address + row['offset'], size=row['size'], signed=row['signed'])
                              for key in uploads for row in (member_path(type_die, (key,)),)}
                else:
                    if name in scalars:
                        raise ValueError('Duplicate worker diagnostic scalar')
                    scalars[name] = dict(address=address, size=size_of(type_die), signed=False)
            if set(scalars) == worker | {'media_mutex'} and queue is not None and upload is not None:
                break
        if set(scalars) != worker | {'media_mutex'} or queue is None or upload is None:
            raise ValueError('Incomplete native photo diagnostic layout')
    for row in [*scalars.values(), *upload.values()]:
        if row['size'] not in (1, 4, 8) or not any(lo <= row['address'] and row['address'] + row['size'] <= hi for lo, hi in RAM):
            raise ValueError('Diagnostic scalar outside C2 SRAM')
    return dict(worker=scalars, upload=upload, queue=queue)
