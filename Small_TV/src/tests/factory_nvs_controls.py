"""Reject actual modified NVS instructions, helper bindings and source-object identities."""
from copy import deepcopy

from audit_factory_xrefs import Image, startup_gp
from reverse.factory_nvs import PAGE, FIND, qualify
from reverse.nothrow_linkage import LinkedRuntime
from reverse.rv32_link_match import model, match


def controls(factory, obj, native, app, current_obj, qualified):
    """Send changed machine-code inputs through the real complete-body checker."""
    rejected = []; readers = {'factory': Image(factory).read, 'native': LinkedRuntime(native, app).read}
    def reject(name, operation):
        """A recorded failure counts only when the production checker actually rejects it."""
        try: operation()
        except ValueError: rejected.append(name)
        else: raise AssertionError('Invalid NVS input accepted: '+name)
    for variant, function, offset, mask, label in (
            ('factory', PAGE, 0, 16, 'factory-stack-frame'),
            ('factory', PAGE, 0x42040f02-0x42040e56, 8, 'null-result-local-branch'),
            ('factory', PAGE, 0x42040efc-0x42040e56, 1<<21, 'wrong-allocator'),
            ('factory', PAGE, 0x42040f72-0x42040e56, 1<<21, 'wrong-entry-table-helper'),
            ('factory', PAGE, 0x42040eac-0x42040e56, 1<<21, 'wrong-crc-helper'),
            ('factory', PAGE, 0x42040f42-0x42040e56, 1<<21, 'wrong-delete'),
            ('factory', PAGE, 0x42040f06-0x42040e56, 4, 'erased-page-scan-bound'),
            ('factory', PAGE, 0x42040f14-0x42040e56, 1<<20, 'wrong-partition-read-length'),
            ('factory', FIND, 0, 16, 'find-helper-instruction'),
            ('native', PAGE, 0, 16, 'current-stack-frame')):
        row = next(r for r in qualified['variants'][variant]['functions'] if r['name'] == function)
        data = bytearray(readers[variant](int(row['start'], 0), row['linked_bytes'], True))
        size = 4 if data[offset] & 3 == 3 else 2
        data[offset:offset+size] = (int.from_bytes(data[offset:offset+size], 'little') ^ mask).to_bytes(size, 'little')
        reject(label, lambda: qualify(factory, obj, native, app, current_obj, {(variant, function): bytes(data)}))
    changed = bytearray(obj); changed[-1] ^= 1
    reject('factory-object-identity', lambda: qualify(factory, bytes(changed), native, app, current_obj))
    changed = bytearray(current_obj); changed[-1] ^= 1
    reject('current-object-identity', lambda: qualify(factory, obj, native, app, bytes(changed)))
    spec = deepcopy(model(obj, PAGE))
    for offset in spec['relocs']: spec['relocs'][offset] = [r for r in spec['relocs'][offset] if r['type'] != 51]
    image = Image(factory)
    reject('missing-relax-permission', lambda: match(spec, image.read(0x42040e56, 312, True), 0x42040e56, startup_gp(image)))
    return dict(passed=True, rejected=rejected)
