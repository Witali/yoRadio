"""Reject missing record algorithms, altered helper instructions and corrupted actual CRC tables."""
from copy import deepcopy

from audit_factory_xrefs import Image, sha
from reverse.nothrow_linkage import LinkedRuntime
from reverse.nvs_record_linkage import qualify
from nvs_records_cpu import HEADER_CHECK
from nvs_rom_crc import vectors

HASH_FIND = '_ZN3nvs8HashList4findEjRKNS_4ItemE'


def controls(factory, parts, native, app, current_parts, linkage, crc):
    """Mutations must fail the real static/CPU checker, not just change a report flag."""
    rejected = []; readers = {'factory': Image(factory).read, 'native': LinkedRuntime(native, app).read}
    def reject(name, operation):
        """Require explicit rejection of the changed input."""
        try: operation()
        except (ValueError, AssertionError): rejected.append(name)
        else: raise AssertionError('Invalid record input accepted: '+name)
    missing = {k: v for k, v in parts.items() if k != 'nvs_types.cpp'}
    reject('missing-factory-item', lambda: qualify(factory, missing, native, app, current_parts))
    missing_current = {k: v for k, v in current_parts.items() if k != 'nvs_item_hash_list.cpp'}
    reject('missing-native-hash-algorithm', lambda: qualify(factory, parts, native, app, missing_current))
    for variant, name, call, label in (('factory', HEADER_CHECK, False, 'factory-header-frame'),
                                     ('native', HEADER_CHECK, False, 'native-header-frame'),
                                     ('factory', HASH_FIND, True, 'factory-hash-callee'),
                                     ('native', HASH_FIND, True, 'native-hash-callee')):
        row = next(r for r in linkage['variants'][variant]['functions'] if r['name'] == name)
        code = bytearray(readers[variant](int(row['start'], 0), row['linked_bytes'], True))
        if call:
            edge = next(t for t in row['transformations'] if 'call' in t['kind'])
            offset = int(edge['pc'], 0)-int(row['start'], 0); size = len(bytes.fromhex(edge['linked_bytes']))
            if size == 8: offset += 4; size = 4
            mask = 1 << 21 if size == 4 else 8
        else: offset = 0; size = 4 if code[0] & 3 == 3 else 2; mask = 16
        code[offset:offset+size] = (int.from_bytes(code[offset:offset+size], 'little') ^ mask).to_bytes(size, 'little')
        reject(label, lambda: qualify(factory, parts, native, app, current_parts, {(variant, name): bytes(code)}))
    changed = deepcopy(crc); table = bytearray.fromhex(changed['table']['bytes']); table[32] ^= 1
    changed['table']['bytes'] = table.hex(); changed['table']['sha256'] = sha(table)
    reject('rom-crc-table-arithmetic', lambda: vectors(changed))
    return dict(passed=True, rejected=rejected)
