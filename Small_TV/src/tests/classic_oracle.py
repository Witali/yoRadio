"""Execute classic fields and animation selection from factory and compiled RV32.

LCD glyph/window/clock/weather algorithms are literal executable code. JPEG/BMP
outputs are recorded media boundaries, not decoded pixels; independent decoder
and QEMU tests cover those. Only synthetic preferences/weather enter the CPUs.
"""
import argparse
from dataclasses import dataclass, replace
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import struct

from machine_oracle import Machine, Panel, ROOT, SCRATCH, ELFFile, UC_HOOK_CODE, REGS, rv
from control_oracle import verify_inputs

FLASH_READ = 0x40392326  # AUIPC/JALR at 0x4200b632/0x4200b636, not the ROM namesake.
FRAME_CURSOR = 0x3fcc3a24
CURSOR = SCRATCH + 0x800
WEATHER = SCRATCH + 0x400


def layout(name):
    """Read the compiled structure size/member offsets from this ELF's DWARF."""
    path = ROOT / '.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    with path.open('rb') as stream:
        elf = ELFFile(stream)
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                attr = die.attributes.get('DW_AT_name')
                if die.tag == 'DW_TAG_typedef' and attr and attr.value == name.encode():
                    structure = die.get_DIE_from_attribute('DW_AT_type')
                    return structure.attributes['DW_AT_byte_size'].value, {
                        child.attributes['DW_AT_name'].value.decode():
                        child.attributes['DW_AT_data_member_location'].value
                        for child in structure.iter_children() if child.tag == 'DW_TAG_member'}
    raise AssertionError('Missing compiled structure: ' + name)


@dataclass(frozen=True)
class Inputs:
    """Keep each controlled state independent of the programs' memory layouts."""
    hour: int = 7
    minute: int = 14
    second: int = 0
    weekday: int = 2
    date_format: int = 2
    hour12: int = 0
    fahrenheit: int = 0
    miles: int = 0
    year: int = 2026
    month: int = 10
    day: int = 13
    city: str = 'Fixture'
    valid: bool = True
    temperature: int = 26
    minimum: float = 21.5
    maximum: float = 29.5
    wind: float = 3.75
    humidity: int = 67
    main: str = 'Clouds'
    description: str = 'scattered cloud'
    direction: str = '-East-north-east'
    step: int = 0
    animation: int = 0


class ClassicMachine(Machine):
    """Execute the composite renderer with declared flash/network/media boundaries."""
    def __init__(self, variant, dump, assets):
        super().__init__(variant)
        self.dump, self.assets, self.media_calls = dump, assets, []
        self.frames = {int(row['flash_offset'], 16): ['animation', animation['index'], row['index']]
                       for animation in assets['animations'] for row in animation['frames']}
        if self.is_factory:
            self.adapt(FLASH_READ, 'asset-header-read', self.flash_read)
            self.adapt(0x4200c518, 'jpeg-output-recorded', self.jpeg)
            self.adapt(0x42010eca, 'bmp-output-recorded', self.weather)
            if variant == 'factory-classic-corrected':
                self.cpu.hook_add(UC_HOOK_CODE,self.clip_partial_glyph,begin=0x4200950e,end=0x4200950e)
        else:
            self.settings_size, self.settings_fields = layout('tv_settings_t')
            self.weather_size, self.weather_fields = layout('weather_snapshot_t')
            if self.settings_size != 344:
                raise AssertionError('Unexpected settings ABI')
            self.adapt(self.symbols['network_address'], 'synthetic-address', self.address)
            self.adapt(self.symbols['media_draw_jpeg'], 'jpeg-output-recorded', self.jpeg)
            self.adapt(self.symbols['media_draw_weather'], 'bmp-output-recorded', self.weather)
            self.adapt(self.symbols['media_animation_frames'], 'asset-frame-count', self.frame_count)
            self.adapt(self.symbols['media_draw_animation'], 'animation-output-recorded', self.animation)

    def clip_partial_glyph(self, cpu, address, size, context):
        """Correct only the factory blitter's rejection of a partially visible glyph.

        Original glyph pixels/coordinates are already computed by its own code.
        Fully visible rectangles still execute the original blitter unchanged.
        """
        x0,y0,x1,y1 = (self.reg(index) for index in range(10,14))
        if x0 >= 240 or y0 >= 240 or (x1 < 240 and y1 < 240):
            return
        width,height = x1-x0+1,y1-y0+1
        if width <= 0 or height <= 0 or width*height*2 > 0x2800:
            raise AssertionError('Unexpected corrected glyph rectangle')
        data = bytes(cpu.mem_read(self.reg(14),width*height*2))
        visible_x,visible_y = min(x1,239),min(y1,239)
        for command,window in [(0x2a,(x0,visible_x)),(0x2b,(y0,visible_y))]:
            self.panel.transfer(bytes([command]),False)
            self.panel.transfer(struct.pack('>HH',*window),True)
        self.panel.transfer(b'\x2c',False)
        for row in range(visible_y-y0+1):
            self.panel.transfer(data[row*width*2:(row*width+visible_x-x0+1)*2],True)
        key = 'correct-partial-glyph-blit'
        self.executed_adapters[key] = self.executed_adapters.get(key,0)+1
        cpu.reg_write(REGS[10],0)
        cpu.reg_write(rv.UC_RISCV_REG_PC,cpu.reg_read(REGS[1]))

    def format_text(self):
        """Adapt printf text with RV32 vararg alignment; arithmetic remains machine code."""
        bounded = not self.is_factory
        destination = self.reg(10)
        capacity = self.reg(11) if bounded else 512
        fmt = self.string(self.reg(12 if bounded else 11)).decode('latin1')
        argument = 13 if bounded else 12

        def convert(match):
            nonlocal argument
            spec = match[1]
            if spec == '%':
                return '%'
            if spec.endswith('f'):
                argument += argument & 1  # doubles begin at an even a-register pair
                if argument > 16:
                    raise AssertionError('Unsupported formatter stack double')
                value = struct.unpack('<d', struct.pack('<II', self.reg(argument),
                                                       self.reg(argument + 1)))[0]
                argument += 2
            else:
                if argument > 17:
                    raise AssertionError('Unsupported formatter stack argument')
                value = self.reg(argument)
                argument += 1
                if spec.endswith('s'):
                    value = self.string(value).decode('latin1')
                elif spec.endswith('d') and value & 0x80000000:
                    value -= 0x100000000
            return ('%' + spec) % value

        pieces, position = [], 0
        while position < len(fmt):
            start = fmt.find('%', position)
            if start < 0:
                pieces.append(fmt[position:])
                break
            pieces.append(fmt[position:start])
            match = re.match(r'%([0-9.]*[duxXsf]|%)', fmt[start:])
            if not match:
                raise AssertionError('Unsupported classic printf conversion')
            pieces.append(convert(match))
            position = start + len(match[0])
        result = ''.join(pieces).encode('latin1')
        if capacity:
            self.cpu.mem_write(destination, result[:capacity - 1] + b'\0')
        return len(result)

    def flash_read(self):
        """Supply only the actual public 1-KiB animation header requested by the SDK."""
        destination, offset, size = self.reg(11), self.reg(12), self.reg(13)
        if offset not in [int(a['flash_offset'], 16) for a in self.assets['animations']] or size != 1024:
            raise AssertionError('Unexpected classic flash read')
        self.cpu.mem_write(destination, self.dump[offset:offset + size])
        return 0

    def address(self):
        """Supply the same synthetic station address as the original global."""
        data = b'10.0.2.15\0'
        if self.reg(11) < len(data):
            raise AssertionError('Network address buffer too short')
        self.cpu.mem_write(self.reg(10), data)

    def frame_count(self):
        """Return the verified fixture's count; this boundary is not a decoder test."""
        return self.assets['animations'][self.reg(10)]['frame_count']

    def jpeg(self):
        """Record selected asset identity and coordinates without drawing substitute pixels."""
        if self.is_factory:
            x, y, offset = self.reg(10), self.reg(11), self.reg(12)
        else:
            offset, x, y = self.reg(10), self.reg(12), self.reg(13)
        self.media_calls.append([self.frames.get(offset, ['jpeg', offset]), x, y])
        return 0

    def weather(self):
        """Require the actual selected icon/coordinates, then record the BMP boundary."""
        if self.is_factory:
            x, y = self.reg(10), self.reg(11)
            offset = int.from_bytes(self.cpu.mem_read(0x3fcc3aa8, 4), 'little')
            if offset != 0x377000:
                raise AssertionError('Wrong synthetic weather icon')
        else:
            x, y = self.reg(11), self.reg(12)
            if self.string(self.reg(10)) != b'01d':
                raise AssertionError('Wrong synthetic weather icon')
        self.media_calls.append([['weather', '01d'], x, y])
        return 0

    def animation(self):
        """Record the compiled renderer's selected animation/frame and LCD position."""
        self.media_calls.append([['animation', self.reg(10), self.reg(11)], self.reg(12), self.reg(13)])
        return 0

    def render(self, inputs, reset=True, cursor=0):
        """Seed explicit ABI fields, then execute both composite renderer entry points."""
        self.seed(inputs.hour, inputs.minute, inputs.second, inputs.weekday,
                  inputs.date_format, inputs.hour12)
        self.media_calls.clear()
        if cursor is not None:
            self.cpu.mem_write(FRAME_CURSOR if self.is_factory else CURSOR, bytes([cursor]))
        if self.is_factory:
            raw = 0x3fcb7b9c
            for offset, value in [(0x164, inputs.animation), (0x16c, inputs.fahrenheit),
                                  (0x174, inputs.miles), (0x184, 0xf800),
                                  (0x188, 0xffe0), (0x18c, 0xffff)]:
                self.cpu.mem_write(raw + offset, struct.pack('<I', value))
            self.cpu.mem_write(0x3fcb7c77, inputs.city.encode() + b'\0')
            self.cpu.mem_write(0x3fcbffc8, struct.pack('<I6B', inputs.year, inputs.month, inputs.day,
                                inputs.hour, inputs.minute, inputs.second, inputs.weekday))
            self.cpu.mem_write(0x3fcc39d7, bytes([inputs.valid]))
            self.cpu.mem_write(0x3fcc3a30, struct.pack('<3d2i', inputs.minimum, inputs.maximum,
                                                    inputs.wind, inputs.humidity, inputs.temperature))
            for address, text in [(0x3fcbff6c, inputs.main), (0x3fcbff80, inputs.description),
                                  (0x3fcbff94, inputs.direction)]:
                if len(text) > 19:
                    raise AssertionError('Synthetic weather text exceeds the factory buffer')
                self.cpu.mem_write(address, text.encode() + b'\0')
            self.cpu.mem_write(0x3fcc3aa8, struct.pack('<I', 0x377000 if inputs.valid else 0))
            if reset:
                self.call(0x4200aebe)
            self.cpu.mem_write(0x3fcc3a25, bytes([inputs.step]))
            self.cpu.mem_write(0x3fcc39f7, b'\x01')  # the declared description timer event
            self.call(0x4200b738)
        else:
            fields = self.settings_fields
            self.cpu.mem_write(SCRATCH + fields['city'], inputs.city.encode() + b'\0')
            self.cpu.mem_write(SCRATCH + fields['colors'], struct.pack('<3H', 0xf800, 0xffe0, 0xffff))
            for key, value in [('fahrenheit', inputs.fahrenheit), ('miles', inputs.miles),
                               ('animation', inputs.animation)]:
                self.cpu.mem_write(SCRATCH + fields[key], bytes([value]))
            yday = dt.date(inputs.year, inputs.month, inputs.day).timetuple().tm_yday - 1
            self.cpu.mem_write(SCRATCH + 0x200, struct.pack('<9i', inputs.second, inputs.minute,
                inputs.hour, inputs.day, inputs.month - 1, inputs.year - 1900, inputs.weekday, yday, 0) + bytes(8))
            weather, fields = bytearray(self.weather_size), self.weather_fields
            weather[fields['valid']] = inputs.valid
            for key, value in [('temperature_c', inputs.temperature), ('temperature_min_c', inputs.minimum),
                               ('temperature_max_c', inputs.maximum), ('wind_mps', inputs.wind)]:
                struct.pack_into('<d', weather, fields[key], value)
            struct.pack_into('<i', weather, fields['humidity'], inputs.humidity)
            for key, text in [('icon', '01d'), ('main', inputs.main), ('description', inputs.description),
                              ('wind_direction', inputs.direction)]:
                value = text.encode()
                weather[fields[key]:fields[key] + len(value)] = value
            self.cpu.mem_write(WEATHER, bytes(weather))
            frame = self.call(self.symbols['factory_animation_next'], CURSOR,
                              self.assets['animations'][inputs.animation]['frame_count'])
            self.call(self.symbols['factory_draw_classic'], SCRATCH, SCRATCH + 0x200, WEATHER,
                      inputs.step, frame, int(reset), int(reset))


def renderer_checks(factory, native, corrected, output):
    """Compare all field pixels and media requests, including real framebuffer history."""
    cases = []
    inputs = [replace(Inputs(), fahrenheit=f, miles=m, step=step, valid=valid,
                      temperature=t, minimum=t-4.5, maximum=t+3.5)
              for f in range(2) for m in range(2) for step in range(10)
              for valid, t in [(True,26), (True,-5), (False,0)]]
    inputs += [replace(Inputs(), hour=h, minute=minute, second=second, weekday=day,
                       date_format=date, hour12=hour12)
               for day in range(7) for date in range(3) for hour12 in range(2)
               for h,minute,second in [(0,0,0),(12,30,30),(23,59,59)]]
    inputs += [replace(Inputs(), city=city, main=main, description=description)
               for city,main,description in [('A','Clear','clear'),('Fixture City','Rain','light rain'),
                   ('FifteenLetters!','Thunderstorm','scattered cloud'),('','','')]]
    inputs += [replace(Inputs(), year=y, month=m, day=d, weekday=(dt.date(y,m,d).weekday()+1)%7)
               for y,m,d in [(2024,2,29),(2025,12,31),(2026,1,1)]]
    def compare(row, index):
        differences = [i for i,(a,b) in enumerate(zip(factory.panel.pixels,native.panel.pixels)) if a!=b]
        row.update(different_pixels=len(differences), media_equal=factory.media_calls==native.media_calls,
                   factory_media=factory.media_calls[:], native_media=native.media_calls[:])
        row['passed'] = not differences and row['media_equal']
        if differences:
            corrected_difference = sum(a!=b for a,b in zip(corrected.panel.pixels,native.panel.pixels))
            if (corrected_difference==0 and corrected.media_calls==native.media_calls and
                    corrected.executed_adapters.get('correct-partial-glyph-blit',0)):
                row['approved_fix'] = 'clip-partially-visible-glyph'
                row['corrected_reference_different_pixels'] = 0
                row['passed'] = True
        cases.append(row)
        if not row['passed']:
            row['first_differences'] = [[i%240,i//240] for i in differences[:20]]
            for machine in (factory,native):
                machine.panel.png(output/f'classic-{index}-{machine.variant}.png')
    for index, data in enumerate(inputs):
        for machine in (factory,native):
            machine.panel = Panel()
            machine.render(data)
        if factory.panel.pixels != native.panel.pixels:
            corrected.panel = Panel()
            corrected.render(data)
        compare({'kind':'initial','inputs':data.__dict__}, index)
    for machine in (factory,native,corrected):
        machine.panel = Panel()
    timeline = [(7,14,0),(7,14,1),(7,14,15),(7,14,30),(7,14,59),(7,15,0),(7,15,1),(8,0,0)]
    for index,(hour,minute,second) in enumerate(timeline):
        data = replace(Inputs(), hour=hour, minute=minute, second=second, step=index)
        for machine in (factory,native,corrected):
            machine.render(data, reset=index==0, cursor=0 if index==0 else None)
        compare({'kind':'sequential','inputs':data.__dict__}, len(inputs)+index)
    return cases


def animation_checks(factory, native):
    """Compare every retained cursor across all five containers and their terminators."""
    cases = []
    for old in factory.assets['animations']:
        for new in factory.assets['animations']:
            for cursor in range(old['frame_count'] + 1):
                factory.cpu.mem_write(FRAME_CURSOR, bytes([cursor]))
                native.cpu.mem_write(CURSOR, bytes([cursor]))
                for step in range(3):
                    factory.media_calls.clear()
                    factory.cpu.mem_write(0x3fcb7d00, struct.pack('<I', new['index']))
                    factory.call(0x4200b5cc)
                    frame = native.call(native.symbols['factory_animation_next'], CURSOR, new['frame_count'])
                    actual = factory.media_calls
                    expected = [[['animation',new['index'],frame],160,160]]
                    a = factory.cpu.mem_read(FRAME_CURSOR,1)[0]
                    b = native.cpu.mem_read(CURSOR,1)[0]
                    cases.append({'from':old['index'],'to':new['index'],'initial_cursor':cursor,
                                  'step':step,'frame':frame,'next_cursor':b,
                                  'passed':actual==expected and a==b})
    guards = []
    for count in (0,127,0xffffffff):
        native.cpu.mem_write(CURSOR,b'\x07')
        result = native.call(native.symbols['factory_animation_next'],CURSOR,count)
        guards.append({'frames':count,'passed':result==0xffffffff and native.cpu.mem_read(CURSOR,1)==b'\x07'})
    return {'cases':cases,'guards':guards,'passed':all(r['passed'] for r in cases+guards)}


def glyph_geometry_checks(factory, native):
    """Require every visible bit of the original 'r' bitmap at panel boundaries."""
    # Original 24-pixel font: ASCII 32 onward, 2 padded bytes per row.
    glyph = bytes(factory.cpu.mem_read(0x3c0ec3e4 + (ord('r')-32)*48,48))
    checks = []
    native.cpu.mem_write(SCRATCH+0x900,b'r\0')
    for x,y in [(236,83),(228,228),(0,235),(235,235)]:
        native.panel = Panel()
        native.call(native.symbols['display_factory_text'],x,y,SCRATCH+0x900,24,0xffe0,0,0)
        expected = {(x+column,y+row) for row in range(24) for column in range(12)
                    if x+column<240 and y+row<240 and glyph[row*2+column//8]&(1<<(column%8))}
        actual = {(index%240,index//240) for index,color in enumerate(native.panel.pixels) if color==0xffe0}
        checks.append({'x':x,'y':y,'visible_ink_pixels':len(expected),
                       'passed':actual==expected and all(color in (0,0xffe0) for color in native.panel.pixels)})
    return checks


def main():
    """Require exact field/selection equality and save identities of both tested programs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    failures = args.output.parent / 'classic-failures'
    failures.mkdir(exist_ok=True)
    app_sha = verify_inputs()
    dump = (ROOT/'Small_TV/full-flash.bin').read_bytes()
    assets = json.loads((ROOT/'Small_TV/assets/manifest.json').read_text())
    factory, native = ClassicMachine('factory',dump,assets), ClassicMachine('native',dump,assets)
    corrected = ClassicMachine('factory-classic-corrected',dump,assets)
    cases = renderer_checks(factory,native,corrected,failures)
    animation = animation_checks(factory,native)
    glyphs = glyph_geometry_checks(factory,native)
    manifest = json.loads((ROOT/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text())
    report = {'passed':all(row['passed'] for row in cases+glyphs) and animation['passed'],
              'app_sha256':app_sha,'source_sha256':manifest['source_sha256'],
              'factory_elf_sha256':factory.source_sha,'native_elf_sha256':native.source_sha,
              'renderer_cases':cases,'animation':animation,
              'glyph_geometry_checks':glyphs,
              'literal_equal':not any(row['different_pixels'] for row in cases),
              'approved_fixes':{'clip-partially-visible-glyph':
                  'Factory 0x4200950e rejects an entire glyph if its rectangle crosses 239; retain its computed bitmap and clip only the visible columns/rows.'},
              'adapters':{'factory':factory.executed_adapters,'native':native.executed_adapters,
                          'factory-classic-corrected':corrected.executed_adapters},
              'scope':'Exact executed classic text/window pixels and media-request identities; media output is recorded, not decoded. Executed animation cursor/header selection; task scheduling and physical timing remain outside scope.'}
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f"Classic RV32: {len(cases)} field/media cases; {len(animation['cases'])} animation transitions; passed={report['passed']}")
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
