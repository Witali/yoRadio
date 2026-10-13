"""Differentially execute factory and rebuilt RV32 rendering functions.

Algorithms run from their actual executable bytes. Only the LCD byte transport
and C text formatting are adapters for the literal programs. A separate corrected
reference redirects two declared erroneous stroke calls; this is not a full-board timing test.
Input ELF files and the private dump are read-only. Results contain synthetic
preferences and framebuffer hashes, never firmware strings or owner settings.
"""
import argparse
from array import array
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import zlib

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'.build/small-tv-parity/oracle-deps'))
from elftools.elf.elffile import ELFFile
from unicorn import __version__ as UNICORN_VERSION
from unicorn import Uc, UcError, UC_ARCH_RISCV, UC_MODE_RISCV32, UC_HOOK_MEM_INVALID, UC_HOOK_CODE
from unicorn import riscv_const as rv

DUMP_SHA='5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4'
REGS=[getattr(rv,f'UC_RISCV_REG_X{index}') for index in range(32)]
STACK=0x2007f000
RETURN=0x2007e000
SCRATCH=0x20000000


class Panel:
    """Apply ST7789 address-window commands and big-endian RGB565 pixel bytes."""
    def __init__(self):
        self.pixels=array('H',[0])*57600
        self.command=0
        self.x0=self.y0=0
        self.x1=self.y1=239
        self.x=self.y=0
        self.pending=b''
        self.transfers=0

    def transfer(self,data,is_data):
        """Consume one complete SPI payload without imposing a renderer algorithm."""
        self.transfers+=1
        if not is_data:
            if len(data)!=1:
                raise AssertionError('Unexpected multi-byte LCD command')
            self.command=data[0]; self.pending=b''
            if self.command==0x2c:
                self.x,self.y=self.x0,self.y0
            return
        if self.command in (0x2a,0x2b):
            self.pending+=data
            if len(self.pending)==4:
                start,end=struct.unpack('>HH',self.pending)
                if self.command==0x2a:
                    self.x0,self.x1=start,end
                else:
                    self.y0,self.y1=start,end
                self.pending=b''
            return
        if self.command!=0x2c:
            return
        if len(data)%2:
            raise AssertionError('Odd RGB565 payload')
        for offset in range(0,len(data),2):
            if 0<=self.x<240 and 0<=self.y<240:
                self.pixels[self.y*240+self.x]=(data[offset]<<8)|data[offset+1]
            self.x+=1
            if self.x>self.x1:
                self.x=self.x0; self.y+=1
                if self.y>self.y1:
                    self.y=self.y0

    def png(self,path):
        """Write an RGB PNG with no identifying metadata, for difference review."""
        rows=[]
        for y in range(240):
            row=bytearray([0])
            for color in self.pixels[y*240:(y+1)*240]:
                r=(color>>11)&31; g=(color>>5)&63; b=color&31
                row.extend(((r<<3)|(r>>2),(g<<2)|(g>>4),(b<<3)|(b>>2)))
            rows.append(bytes(row))
        def chunk(kind,payload):
            return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload))
        encoded=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',240,240,8,2,0,0,0))
        path.write_bytes(encoded+chunk(b'IDAT',zlib.compress(b''.join(rows)))+chunk(b'IEND',b''))


class Machine:
    """Load immutable RV32 programs and call them with explicit ABI inputs."""
    def __init__(self,variant):
        self.variant=variant
        self.is_factory=variant.startswith('factory')
        self.cpu=Uc(UC_ARCH_RISCV,UC_MODE_RISCV32)
        for address,size in [(SCRATCH,0x80000),(0x3c000000,0x200000),
                (0x3fca0000,0x40000),(0x3ff40000,0x10000),(0x40000000,0x90000),
                (0x40380000,0x40000),(0x42000000,0x200000)]:
            self.cpu.mem_map(address,size)
        self.symbols={}
        self.panel=Panel()
        self.adapters={}
        self.executed_adapters={}
        self.fault=None
        rom=ROOT/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'
        self.load(rom)
        path=(ROOT/'.build/small-tv-reverse/factory-analysis.elf' if self.is_factory
              else ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf')
        self.load(path)
        self.source_sha=hashlib.sha256(path.read_bytes()).hexdigest()
        self.cpu.hook_add(UC_HOOK_MEM_INVALID,self.invalid_memory)
        self.cpu.hook_add(UC_HOOK_CODE,self.stop_at_return,begin=RETURN,end=RETURN)
        if self.is_factory:
            self.adapt(0x420091e4,'lcd-command',self.lcd_command)
            self.adapt(0x4200925a,'lcd-data',self.lcd_data)
            self.adapt(0x400006a8,'sprintf',self.format_text)
            if variant=='factory-corrected':
                # This separate expected reference changes only the two
                # confirmed erroneous stroke calls. Literal factory runs
                # remain intact and their pixel differences are reported.
                self.redirect_call(0x420097fa,0x420a73e0,'correct-line-x-cos')
                self.redirect_call(0x4200982c,0x420a7464,'correct-line-y-sin')
        else:
            transfer=next(value for name,value in self.symbols.items() if name.startswith('lcd_transfer'))
            self.adapt(transfer,'lcd-transfer',self.lcd_transfer)
            self.adapt(self.symbols['snprintf'],'snprintf',self.format_text)

    def load(self,path):
        """Map original ELF load segments and retain exact symbol addresses."""
        with path.open('rb') as stream:
            elf=ELFFile(stream)
            for segment in elf.iter_segments():
                if segment['p_type']=='PT_LOAD' and segment['p_filesz']:
                    self.cpu.mem_write(segment['p_vaddr'],segment.data())
                    if segment['p_paddr']!=segment['p_vaddr'] and 0x40000000<=segment['p_paddr']<0x40090000:
                        self.cpu.mem_write(segment['p_paddr'],segment.data())
            table=elf.get_section_by_name('.symtab')
            if table:
                self.symbols.update({symbol.name:symbol['st_value'] for symbol in table.iter_symbols()
                                     if symbol['st_value']})

    def invalid_memory(self,cpu,access,address,size,value,context):
        """Report missing hardware/ABI state rather than inventing memory values."""
        self.fault={'pc':hex(cpu.reg_read(rv.UC_RISCV_REG_PC)),
                    'address':hex(address),'access':access,'bytes':size}
        return False

    def stop_at_return(self,cpu,address,size,context):
        """End a function invocation at its synthetic caller return address."""
        cpu.emu_stop()

    def reg(self,index):
        """Read one unsigned integer argument/register."""
        return self.cpu.reg_read(REGS[index])&0xffffffff

    def string(self,address):
        """Read a bounded C string only for synthetic test formatting."""
        data=bytearray()
        for index in range(512):
            value=self.cpu.mem_read(address+index,1)[0]
            if not value:
                return bytes(data)
            data.append(value)
        raise AssertionError('Unterminated oracle string')

    def adapt(self,address,name,callback):
        """Replace only a documented boundary, recording every adapter used."""
        self.adapters[address]=name
        def hook(cpu,pc,size,context):
            self.executed_adapters[name]=self.executed_adapters.get(name,0)+1
            result=callback()
            cpu.reg_write(REGS[10],0 if result is None else result&0xffffffff)
            cpu.reg_write(rv.UC_RISCV_REG_PC,cpu.reg_read(REGS[1]))
        self.cpu.hook_add(UC_HOOK_CODE,hook,begin=address,end=address)

    def lcd_command(self):
        """Send the factory's one-byte command to the common panel model."""
        self.panel.transfer(bytes([self.reg(10)&255]),False)

    def redirect_call(self,address,target,name):
        """Correct a declared reference call without editing executable bytes."""
        self.adapters[address]=name
        def hook(cpu,pc,size,context):
            if size!=4:
                raise AssertionError('Expected a 32-bit factory JAL instruction')
            self.executed_adapters[name]=self.executed_adapters.get(name,0)+1
            cpu.reg_write(REGS[1],pc+4)
            cpu.reg_write(rv.UC_RISCV_REG_PC,target)
        self.cpu.hook_add(UC_HOOK_CODE,hook,begin=address,end=address)

    def lcd_data(self):
        """Send factory SPI data without replacing its glyph/window calculations."""
        self.panel.transfer(bytes(self.cpu.mem_read(self.reg(10),self.reg(11))),True)

    def lcd_transfer(self):
        """Send the compiled C driver's command/data payload to the same model."""
        self.panel.transfer(bytes(self.cpu.mem_read(self.reg(10),self.reg(11))),bool(self.reg(12)))

    def format_text(self):
        """Model bounded integer/string C formatting; other conversions fail explicitly."""
        bounded=not self.is_factory
        destination=self.reg(10)
        capacity=self.reg(11) if bounded else 512
        fmt=self.string(self.reg(12 if bounded else 11)).decode('latin1')
        argument=13 if bounded else 12
        def replace(match):
            nonlocal argument
            spec=match[1]
            if spec=='%':
                return '%'
            if argument>17:
                raise AssertionError('Formatter stack arguments are not supported')
            value=self.reg(argument); argument+=1
            if spec.endswith('s'):
                return self.string(value).decode('latin1')
            if spec.endswith('d') and value&0x80000000:
                value-=0x100000000
            if spec[-1] not in ('d','u','x','X'):
                raise AssertionError('Unsupported formatter conversion')
            return ('%'+spec)%value
        pieces=[]
        offset=0
        while offset<len(fmt):
            start=fmt.find('%',offset)
            if start<0:
                pieces.append(fmt[offset:]); break
            pieces.append(fmt[offset:start])
            match=re.match(r'%([0-9.]*[duxXs]|%)',fmt[start:])
            if not match:
                raise AssertionError('Unsupported formatter conversion')
            pieces.append(replace(match))
            offset=start+len(match[0])
        result=''.join(pieces).encode('latin1')
        if capacity:
            self.cpu.mem_write(destination,result[:capacity-1]+b'\0')
        return len(result)

    def call(self,address,*arguments):
        """Invoke one machine function, failing on faults or an instruction deadline."""
        for index in range(1,32):
            self.cpu.reg_write(REGS[index],0)
        self.cpu.reg_write(REGS[2],STACK)
        self.cpu.reg_write(REGS[1],RETURN)
        self.cpu.reg_write(REGS[3],self.symbols.get('__global_pointer$',0))
        for index,value in enumerate(arguments):
            self.cpu.reg_write(REGS[10+index],value&0xffffffff)
        try:
            self.cpu.emu_start(address,RETURN,count=20000000)
        except UcError as error:
            raise RuntimeError(f'{self.variant} PC {self.cpu.reg_read(rv.UC_RISCV_REG_PC):#x}: {error}; fault={self.fault}') from error
        if self.cpu.reg_read(rv.UC_RISCV_REG_PC)!=RETURN:
            raise RuntimeError('Oracle instruction deadline expired')
        return self.reg(10)

    def seed(self,hour,minute,second,weekday=2,date_format=2,hour12=0):
        """Write identical explicit preferences/time into the two different ABIs."""
        address=b'10.0.2.15\0'
        if self.is_factory:
            raw=bytearray(444)
            struct.pack_into('<I',raw,0x170,hour12)
            struct.pack_into('<I',raw,0x17c,date_format)
            self.cpu.mem_write(0x3fcb7b9c,bytes(raw))
            self.cpu.mem_write(0x3fcb7b84,address)
            self.cpu.mem_write(0x3fcbffc8,struct.pack('<I6B',2026,10,13,hour,minute,second,weekday))
        else:
            settings=bytearray(344)
            struct.pack_into('<I',settings,0,1)
            settings[312]=date_format; settings[317]=hour12
            self.cpu.mem_write(SCRATCH,bytes(settings))
            self.cpu.mem_write(SCRATCH+0x200,struct.pack('<9i',second,minute,hour,13,9,126,weekday,285,0)+bytes(8))
            self.cpu.mem_write(SCRATCH+0x300,address)

    def simple(self,reset=True,minute_update=True,second_update=True):
        """Run the corresponding factory entry points or actual compiled C function."""
        if self.is_factory:
            if reset:
                self.call(0x4200bd26)
            self.cpu.mem_write(0x3fcc39f5,bytes([int(minute_update),int(second_update)]))
            self.call(0x4200bd8c)
        else:
            self.call(self.symbols['factory_draw_simple'],SCRATCH,SCRATCH+0x200,SCRATCH+0x300,
                      int(reset),int(second_update),int(minute_update))

    def dial(self,reset=True):
        """Execute original analog geometry/math and the compiled C counterpart."""
        if self.is_factory:
            if reset:
                self.call(0x4200a156)
            else:
                self.cpu.mem_write(0x3fcc39f6,b'\x01')
                self.call(0x4200a5b0)
        else:
            self.call(self.symbols['factory_draw_dial'],SCRATCH+0x200,SCRATCH+0x300,int(reset))


def main():
    """Compare controlled rendering cases and keep explicit differences as failures."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'.build/small-tv-parity/oracle')
    parser.add_argument('--themes',nargs='+',choices=['simple','dial'],default=['simple','dial'])
    parser.add_argument('--extended',action='store_true',help='Exercise every weekday/date mode and cardinal-angle cases')
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    dump=(ROOT/'Small_TV/full-flash.bin').read_bytes()
    if hashlib.sha256(dump).hexdigest()!=DUMP_SHA:
        raise ValueError('Input is not the verified factory dump; obtain it with git lfs pull')
    if UNICORN_VERSION!='2.1.4':
        raise ValueError('Install the pinned oracle-requirements.txt dependencies')
    # Verify the executable oracle's five load segments against the immutable
    # ESP image payloads, rather than trusting a generated ELF filename/hash.
    offset=0x10000+24; segments={}
    for _ in range(dump[0x10001]):
        address,length=struct.unpack_from('<II',dump,offset); offset+=8
        segments[address]=dump[offset:offset+length]; offset+=length
    with (ROOT/'.build/small-tv-reverse/factory-analysis.elf').open('rb') as stream:
        oracle_segments={segment['p_vaddr']:segment.data() for segment in ELFFile(stream).iter_segments()
                         if segment['p_type']=='PT_LOAD' and segment['p_filesz']}
    if oracle_segments!=segments:
        raise ValueError('Factory ELF payload differs from original instructions/data')
    original=Machine('factory'); native=Machine('native')
    corrected=Machine('factory-corrected')
    cases=[(7,14,0,2,2,0),(7,14,1,2,2,0),(0,0,0,0,0,1),
           (12,59,1,1,1,1),(13,0,0,6,2,1),(23,59,0,7,2,1)]
    if args.extended:
        cases+= [(hour,minute,second,day,mode,hour12) for day in range(8)
                 for mode in range(3) for hour12 in range(2)
                 for hour,minute,second in [(0,0,0),(12,30,30),(23,59,59)]]
    results=[]
    for theme in args.themes:
        for index,values in enumerate(cases):
            for machine in (original,native):
                machine.panel=Panel(); machine.seed(*values); getattr(machine,theme)()
            mismatches=[pixel for pixel,(left,right) in enumerate(zip(original.panel.pixels,native.panel.pixels)) if left!=right]
            case={'theme':theme,'inputs':list(values),'different_pixels':len(mismatches),
                'first_differences':[[i%240,i//240,original.panel.pixels[i],native.panel.pixels[i]] for i in mismatches[:20]]}
            if theme=='simple' and values[3]==0:
                # The user explicitly requires correcting obvious vendor bugs.
                # Keep the literal factory-0 comparison above, then separately
                # execute its supported Sunday-7 path as the expected label.
                original.panel=Panel()
                sunday=list(values); sunday[3]=7
                original.seed(*sunday); original.simple()
                case['approved_fix']='simple-sunday-standard-tm-wday'
                case['corrected_reference_inputs']=sunday
                case['corrected_reference_different_pixels']=sum(
                    left!=right for left,right in zip(original.panel.pixels,native.panel.pixels))
            elif theme=='dial':
                corrected.panel=Panel(); corrected.seed(*values); corrected.dial()
                case['approved_fix']='analog-perpendicular-stroke-offsets'
                case['corrected_reference_different_pixels']=sum(
                    left!=right for left,right in zip(corrected.panel.pixels,native.panel.pixels))
            case['passed']=case.get('corrected_reference_different_pixels',len(mismatches))==0
            results.append(case)
            if not case['passed']:
                for machine in (original,native,corrected) if theme=='dial' else (original,native):
                    machine.panel.png(args.output/(f'{theme}-{index}-'+machine.variant+'.png'))
            if mismatches or index%24==0:
                print(theme,index,'different pixels:',len(mismatches),flush=True)
        # Keep real framebuffer history across updates: erasing hands and
        # preserving labels are different paths from a clean initial drawing.
        sequence=[(7,14,0,2,2,0),(7,14,1,2,2,0),(7,14,15,2,2,0),
                  (7,14,30,2,2,0),(7,14,59,2,2,0),(7,15,0,2,2,0),
                  (7,15,1,2,2,0),(8,0,0,2,2,0)]
        for machine in (original,native,corrected):
            machine.panel=Panel()
        previous=None
        for index,values in enumerate(sequence):
            minute_update=previous is None or values[0:2]!=previous[0:2]
            for machine in (original,native):
                machine.seed(*values)
                if theme=='simple':
                    machine.simple(reset=index==0,minute_update=minute_update)
                else:
                    machine.dial(reset=index==0)
            differences=sum(left!=right for left,right in zip(original.panel.pixels,native.panel.pixels))
            case={'theme':theme,'path':'sequential-update','inputs':list(values),
                  'different_pixels':differences}
            if theme=='dial':
                corrected.seed(*values); corrected.dial(reset=index==0)
                case['approved_fix']='analog-perpendicular-stroke-offsets'
                case['corrected_reference_different_pixels']=sum(
                    left!=right for left,right in zip(corrected.panel.pixels,native.panel.pixels))
            case['passed']=case.get('corrected_reference_different_pixels',differences)==0
            results.append(case)
            if not case['passed']:
                for machine in (original,native,corrected) if theme=='dial' else (original,native):
                    machine.panel.png(args.output/(f'{theme}-update-{index}-'+machine.variant+'.png'))
                print(theme,'update',index,'different pixels:',differences,flush=True)
            previous=values
    # Independent geometric properties supplement the corrected reference:
    # width-five axis-aligned strokes must cover exactly five parallel rows
    # or columns, including when the endpoints are reversed.
    geometry=[]
    for x0,y0,x1,y1 in [(20,80,140,80),(140,80,20,80),(80,20,80,140),(80,140,80,20)]:
        native.panel=Panel()
        native.call(native.symbols['thick_line'],x0,y0,x1,y1,5,0xffff)
        if y0==y1:
            expected={(x,y) for x in range(min(x0,x1),max(x0,x1)+1) for y in range(y0-2,y0+3)}
        else:
            expected={(x,y) for x in range(x0-2,x0+3) for y in range(min(y0,y1),max(y0,y1)+1)}
        drawn={(i%240,i//240) for i,color in enumerate(native.panel.pixels) if color==0xffff}
        passed=drawn==expected and all(color in (0,0xffff) for color in native.panel.pixels)
        geometry.append({'endpoints':[x0,y0,x1,y1],'width':5,'passed':passed})
    manifest=json.loads((ROOT/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text())
    archived=ROOT/'firmware/development/small-tv-esp32c2-reconstructed/app.bin'
    compiled=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.bin'
    if archived.read_bytes()!=compiled.read_bytes():
        raise ValueError('Archived firmware differs from the tested build')
    if compiled.read_bytes()[176:208]!=bytes.fromhex(native.source_sha):
        raise ValueError('Tested ELF differs from the firmware descriptor ELF digest')
    app_sha=hashlib.sha256(compiled.read_bytes()).hexdigest()
    if app_sha!=next(item['sha256'] for item in manifest['images'] if item['file']=='app.bin'):
        raise ValueError('Archived manifest has a stale application hash')
    report={'factory_elf_sha256':original.source_sha,'native_elf_sha256':native.source_sha,
            'app_sha256':app_sha,
            'source_sha256':manifest['source_sha256'],
            'unicorn_version':'2.1.4','equal':not any(case['different_pixels'] for case in results),'cases':results,
            'passed':all(case['passed'] for case in results) and all(case['passed'] for case in geometry),
            'stroke_geometry_checks':geometry,
            'approved_fixes':{'simple-sunday-standard-tm-wday':
                'Display Sun for standard tm_wday 0; factory 0 repeats the date, while factory 7 draws Sun',
                'analog-perpendicular-stroke-offsets':
                'Use cos/sin for x/y after atan2+pi/2; the original sin/cos collapses axis-aligned thick strokes'},
            'adapters':{machine.variant:machine.executed_adapters for machine in (original,native,corrected)},
            'scope':'Controlled renderer execution; literal LCD/format adapters and separately declared corrected reference; no board/timing claim'}
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Factory pixels equal:',report['equal'],'; verification passed:',report['passed'])
    raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':
    main()
