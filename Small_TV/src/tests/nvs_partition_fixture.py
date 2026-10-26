"""Private NVS partition API fixture, with byte-accurate NOR programming and injected errors."""
from runtime_call_instructions import HEAP


class Partition:
    """Retain one synthetic sector across CPU instances; this is not a second SPI device model."""
    def __init__(self, states, dirty, fail_at=0, partial=False):
        """Encode all126 bitmap entries and distinct retained payloads without user data."""
        assert len(states) == 126 and all(s in (0, 3) for s in states)
        self.base = 8192; self.bytes = bytearray(b'\xff'*4096)
        for index, state in enumerate(states):
            shift = (index % 4)*2; at = 32+index//4
            self.bytes[at] = (self.bytes[at] & ~(3 << shift)) | state << shift
            if state == 0 or index in dirty:
                self.bytes[64+32*index:96+32*index] = bytes((7+index*11+i) % 251 for i in range(32))
        self.initial = bytes(self.bytes); self.operations = []; self.fail_at = fail_at; self.partial = partial

    def operation(self, f, kind, args):
        """Validate the actual virtual partition call; errors retain any physically programmed prefix."""
        owner, address, pointer, size = args[:4]
        assert owner == HEAP+512 and address % 4 == size % 4 == 0 and size in (4, 32)
        offset = address-self.base; assert 0 <= offset < offset+size <= 4096
        fail = len(self.operations)+1 == self.fail_at
        row = dict(kind=kind, offset=offset, bytes=size, failed=fail)
        count = size//2 if fail and self.partial else 0 if fail else size
        if kind == 'read_raw':
            f.cpu.mem_write(pointer, bytes(self.bytes[offset:offset+count]))
        else:
            assert kind == 'write_raw'
            data = bytes(f.cpu.mem_read(pointer, size)); row['data'] = data.hex()
            assert all((self.bytes[offset+i] & value) == value for i, value in enumerate(data)), 'Attempted NOR0->1 program'
            for i in range(count): self.bytes[offset+i] &= data[i]
        row['transferred'] = count; self.operations.append(row)
        return 0x104 if fail else 0

    def attach(self, f):
        """Expose only read_raw/write_raw virtual slots; unexpected erase or decrypted I/O fails loudly."""
        from runtime_call_instructions import END
        f.word(HEAP+512, HEAP+768)
        f.word(HEAP+768+12, END+1024); f.word(HEAP+768+20, END+1040)
        f.boundary('read_raw', END+1024, lambda args: self.operation(f, 'read_raw', args))
        f.boundary('write_raw', END+1040, lambda args: self.operation(f, 'write_raw', args))
