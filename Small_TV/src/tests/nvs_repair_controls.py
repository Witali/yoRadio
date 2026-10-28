"""Reject modified repair helpers and forbidden private partition fixture requests."""
from audit_factory_xrefs import Image
from reverse.nothrow_linkage import LinkedRuntime
from reverse.nvs_repair_linkage import ALTER, SET, PURGE, RANGE, qualify
from nvs_partition_fixture import Partition
from runtime_call_instructions import HEAP


def controls(factory, obj, native, app, current_obj, nvs, linkage):
    """Exercise complete-body matching and callback constraints using changed actual inputs."""
    rejected = []; readers = {'factory': Image(factory).read, 'native': LinkedRuntime(native, app).read}
    for variant, name, label, call in (('factory', ALTER, 'factory-alter-frame', False),
                                     ('factory', ALTER, 'factory-set-target', True),
                                     ('factory', SET, 'factory-set-instruction', False),
                                     ('native', ALTER, 'native-alter-frame', False),
                                     ('native', PURGE, 'native-purge-target', True),
                                     ('native', RANGE, 'native-memset-target', True)):
        row = next(r for r in linkage['variants'][variant]['functions'] if r['name'] == name)
        code = bytearray(readers[variant](int(row['start'], 0), row['linked_bytes'], True))
        if call:
            transform = next(t for t in row['transformations'] if 'call' in t['kind'])
            offset = int(transform['pc'], 0)-int(row['start'], 0)
            size = len(bytes.fromhex(transform['linked_bytes']))
            # JALR clears immediate bit0; change bit1 to select a different target.
            if size == 8: offset += 4; size = 4; mask = 1 << 21
            else: mask = 1 << 21 if size == 4 else 8
        else: offset = 0; size = 4 if code[0] & 3 == 3 else 2; mask = 16
        code[offset:offset+size] = (int.from_bytes(code[offset:offset+size], 'little') ^ mask).to_bytes(size, 'little')
        try: qualify(factory, obj, native, app, current_obj, nvs, {(variant, name): bytes(code)})
        except ValueError: rejected.append(label)
        else: raise AssertionError('Altered repair helper accepted: '+label)
    class Data:
        """Supply only deterministic source bytes for invalid writer requests."""
        def mem_read(self, address, size):
            """Return ones so programming an already cleared bitmap attempts forbidden0->1."""
            return b'\xff'*size
    class Cpu:
        cpu = Data()
    for label, kind, offset, length in (('nor-zero-to-one', 'write_raw', 32, 4),
                                      ('outside-sector', 'write_raw', 4096, 4),
                                      ('unaligned-fixture-call', 'write_raw', 33, 4),
                                      ('unexpected-fixture-size', 'write_raw', 32, 8),
                                      ('unexpected-erase', 'erase', 32, 4)):
        partition = Partition([0]*126, set())
        try: partition.operation(Cpu(), kind, (HEAP+512, 8192+offset, HEAP+1536, length))
        except AssertionError: rejected.append(label)
        else: raise AssertionError('Invalid partition fixture request accepted: '+label)
    return dict(passed=True, rejected=rejected)
