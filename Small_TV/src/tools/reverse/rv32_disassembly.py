"""Give GNU explicit RV32 ISA metadata while preserving every original code byte."""
import hashlib
from pathlib import Path
import re
import struct
import subprocess
import tempfile

# Canonical attributes produced by the project's ESP32-C2 -march setting.
# Layout: RISC-V ELF psABI section 10.11, including vendor and Tag_File lengths.
ISA = 'rv32i2p1_m2p0_c2p0_zicsr2p0_zifencei2p0_zmmul1p0_zca1p0'
CANARY_PC = 0x420aeb6e
CANARY_CODE = bytes.fromhex('712b')


def compressed_jal_target(word, pc):
    """Decode RV32 C.JAL from its bits, independent of a misleading RV64 mnemonic."""
    if type(word) is not int or not 0 <= word <= 65535 or word & 0xe003 != 0x2001:
        raise ValueError('Expected an RV32 C.JAL encoding')
    immediate = (((word>>12)&1)<<11) | (((word>>11)&1)<<4) | (((word>>9)&3)<<8)
    immediate |= (((word>>8)&1)<<10) | (((word>>7)&1)<<6) | (((word>>6)&1)<<7)
    immediate |= (((word>>3)&7)<<1) | (((word>>2)&1)<<5)
    if immediate & 0x800: immediate -= 0x1000
    return (pc+immediate) & 0xffffffff


def attributes():
    """Encode a minimal standard attribute section; it is analysis metadata, not firmware."""
    values = b'\x04\x10\x05' + ISA.encode('ascii') + b'\0'
    file_attributes = b'\x01' + struct.pack('<I',5+len(values)) + values
    vendor = b'riscv\0' + file_attributes
    return b'A' + struct.pack('<I',4+len(vendor)) + vendor


def elf_view(regions):
    """Build a disposable ELF32 code view with no data segments, symbols or credentials."""
    if not 1 <= len(regions) <= 8: raise ValueError('Expected one to eight executable regions')
    names = b'\0'; seen = set(); intervals = []; headers = [(0,)*10]; data = bytearray(52)
    def put(payload):
        """Align file payloads without inserting bytes into a guest code region."""
        data.extend(bytes((-len(data))%4)); offset=len(data); data.extend(payload); return offset
    for name, address, code in regions:
        if not isinstance(name,str) or not re.fullmatch(r'\.[A-Za-z0-9_.]{1,63}',name) or name in seen:
            raise ValueError('Invalid/duplicate executable section name')
        if name in ('.riscv.attributes','.shstrtab'): raise ValueError('Reserved section name')
        if type(address) is not int or address & 1 or not isinstance(code,bytes) or not code or len(code)&1 or len(code)>8*1024*1024:
            raise ValueError('Invalid bounded RV32 code region')
        end=address+len(code)
        if not 0 <= address < end <= 0x100000000 or any(address < hi and lo < end for lo,hi in intervals):
            raise ValueError('Overlapping/overflowing RV32 code region')
        seen.add(name); intervals.append((address,end)); label=len(names); names+=name.encode('ascii')+b'\0'
        headers.append((label,1,6,address,put(code),len(code),0,0,2,0))
    label=len(names); names+=b'.riscv.attributes\0'; attr=attributes()
    headers.append((label,0x70000003,0,0,put(attr),len(attr),0,0,1,0))
    label=len(names); names+=b'.shstrtab\0'
    headers.append((label,3,0,0,put(names),len(names),0,0,1,0))
    data.extend(bytes((-len(data))%4)); section_offset=len(data)
    for header in headers:data.extend(struct.pack('<10I',*header))
    ident=b'\x7fELF\x01\x01\x01'+bytes(9)
    data[:52]=struct.pack('<16sHHIIIIIHHHHHH',ident,2,243,1,regions[0][1],0,section_offset,
                         1,52,0,0,40,len(headers),len(headers)-1)
    return bytes(data)


def tool_pins(tool):
    """Identify the selected tool and the Espressif dispatcher siblings it can launch."""
    tool=Path(tool).resolve(); files=[tool]
    if tool.name=='riscv32-esp-elf-objdump.exe':
        files += sorted(tool.parent.glob('riscv32-esp-elf-objdump-xesp*.exe'))
    return {str(file):hashlib.sha256(file.read_bytes()).hexdigest() for file in files}


class Disassembler:
    """Own one temporary ISA-qualified view and an independently checked C.JAL canary."""
    def __init__(self, tool, regions, workspace):
        """Prepare metadata and reject invalid region geometry before starting a process."""
        self.tool=Path(tool).resolve(); self.root=Path(workspace).resolve()
        self.view=elf_view(regions); self.pins=tool_pins(self.tool); self.temporary=None
        self.ranges=[(address,address+len(code)) for _,address,code in regions]
        self.metadata=dict(schema='rv32-isa-view-v1',isa=ISA,view_sha256=hashlib.sha256(self.view).hexdigest(),
                           tool_pins=self.pins,code_bytes_unchanged=True)

    def __enter__(self):
        """Create only a unique child scratch directory and validate the selected decoder."""
        self.root.mkdir(parents=True,exist_ok=True)
        self.temporary=tempfile.TemporaryDirectory(prefix='rv32-view-',dir=self.root)
        folder=Path(self.temporary.name).resolve()
        if not folder.is_relative_to(self.root): raise ValueError('Temporary view escaped its workspace')
        self.path=folder/'view.elf'; canary=folder/'canary.elf'
        try:
            self.path.write_bytes(self.view);canary.write_bytes(elf_view([('.text',CANARY_PC,CANARY_CODE)]))
            output=self._invoke(canary,['-M','no-aliases,numeric'])
            expected=compressed_jal_target(0x2b71,CANARY_PC)
            match=re.search(r'^\s*420aeb6e:\s+2b71\s+(\S+)\s+(?:0x)?([0-9a-f]+)',output,re.MULTILINE)
            if not match or match[1] not in ('c.jal','jal') or int(match[2],16)!=expected:
                raise ValueError('Selected objdump does not decode the RV32 C.JAL canary correctly')
            self.metadata['canary']=dict(pc=CANARY_PC,bytes_hex=CANARY_CODE.hex(),target=expected,
                                        stdout_sha256=hashlib.sha256(output.replace(str(canary),'canary-rv32.elf').encode()).hexdigest())
            return self
        except BaseException:
            self.__exit__(None,None,None);raise

    def _invoke(self, path, options):
        """Run only the explicit tool on this generated view, with a bounded process wait."""
        result=subprocess.run([str(self.tool),'-d','-z',*options,str(path)],stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,timeout=30,check=True)
        if result.stderr.strip(): raise ValueError('objdump reported a disassembly diagnostic: '+result.stderr.decode(errors='replace'))
        return result.stdout.decode('utf8').replace('\r\n','\n')

    def text(self, start=None, stop=None, canonical=False):
        """Disassemble the original region addresses and remove only the temporary host path."""
        if self.temporary is None: raise ValueError('Disassembler context is not open')
        if start is not None or stop is not None:
            if (type(start) is not int or type(stop) is not int or start&1 or stop&1 or
                not any(lo<=start<stop<=hi for lo,hi in self.ranges)):
                raise ValueError('Expected an aligned range within one original code region')
        options=['-M','no-aliases,numeric'] if canonical else []
        if start is not None: options.append(f'--start-address={start}')
        if stop is not None: options.append(f'--stop-address={stop}')
        return self._invoke(self.path,options).replace(str(self.path),'factory-rv32-view.elf')

    def __exit__(self, *exception):
        """Rehash decoder inputs and remove only the verified unique child scratch directory."""
        changed=tool_pins(self.tool)!=self.pins
        if self.temporary is not None:
            folder=Path(self.temporary.name).resolve()
            if not folder.is_relative_to(self.root) or not folder.name.startswith('rv32-view-'):
                raise ValueError('Refusing cleanup outside the owned view directory')
            self.temporary.cleanup();self.temporary=None
        if changed:raise ValueError('Disassembler inputs changed while exporting code')
