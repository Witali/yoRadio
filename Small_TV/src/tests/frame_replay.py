"""Execute complete classic scenes with real JPEG/BMP decoders and LCD transport.

No media output is replaced with a prerecorded picture. Only SDK flash,
allocation, mutex and address boundaries are adapted, as in the decoder gates.
"""
from dataclasses import replace
import struct
import zlib

from classic_oracle import Inputs
from jpeg_oracle import assets_list
from machine_oracle import Machine, Panel, ROOT, SCRATCH, UC_HOOK_CODE
from weather_render_oracle import WeatherMachine


class SceneMachine(WeatherMachine):
    """Run the actual composite renderer and every selected media decoder."""
    def adapt(self, address, name, callback):
        """Observe media identities without skipping their executable bodies."""
        if name in ('jpeg-output-recorded','animation-output-recorded'):
            self.cpu.hook_add(UC_HOOK_CODE,lambda cpu,pc,size,context:callback(),begin=address,end=address)
        elif name != 'asset-frame-count':
            super().adapt(address,name,callback)

    def __init__(self, variant, dump, assets):
        self.jpeg_assets = assets_list(assets)
        factory=variant.startswith('factory')
        # Validate public bytes once in assets_list, then retain immutable bounds.
        # Reopening every earlier JPEG for each 512-byte read obscures test runtime.
        self.jpeg_ranges=[(int(item['flash_offset'],16) if factory else item['native_offset'],
                           item['source_length']+512 if factory else
                           0x3c00 if item['file'].startswith('status/') else
                           (ROOT/'Small_TV/assets'/item['file']).stat().st_size)
                          for item in self.jpeg_assets]
        self.header_ranges = [(int(item['flash_offset'],16),1024) for item in assets['animations']]
        super().__init__(variant,dump,assets)
        if not self.is_factory:
            self.adapt(self.symbols['malloc'],'scene-workspace-malloc',self.allocate)
            self.adapt(self.symbols['free'],'scene-workspace-free',self.release)
        self.jpeg_decomp_calls=0
        entry=0x42011fd8 if self.is_factory else self.symbols['jd_decomp']
        self.cpu.hook_add(UC_HOOK_CODE,self.observe_jpeg,begin=entry,end=entry)

    def observe_jpeg(self,cpu,pc,size,context):
        """Count entry into the genuine decompressor without replacing any instructions."""
        self.jpeg_decomp_calls+=1

    def allocate(self):
        """Provide owned bounded BMP rows or the real JPEG workspace."""
        size = self.reg(10)
        if size not in (120,180,8192):
            raise AssertionError('Unexpected scene allocation: '+str(size))
        pointer = self.heap_next
        self.heap_next += (size+15)&~15
        if self.heap_next >= SCRATCH+0x70000:
            raise AssertionError('Scene allocation fixture exhausted')
        self.allocations.add(pointer)
        return pointer

    def permitted_read(self, offset, size):
        """Restrict flash access to immutable public media and GIF directory headers."""
        if any(start<=offset and offset+size<=start+length for start,length in self.header_ranges):
            return
        for start,length in self.jpeg_ranges:
            if start<=offset and offset+size<=start+length:
                return
        try:
            super().permitted_read(offset,size)
        except AssertionError as error:
            raise AssertionError(f'Scene flash access outside public assets: {offset:#x}+{size}') from error

    def flash_read(self):
        """Serve the original flash ABI for GIF, JPEG and BMP algorithms."""
        destination,offset,size = self.reg(11),self.reg(12),self.reg(13)
        self.permitted_read(offset,size)
        self.cpu.mem_write(destination,self.dump[offset:offset+size])
        return 0

    def render(self, inputs, reset=True, cursor=0, force_status=False):
        """Run one whole scene and require all temporary decoder storage to be freed."""
        self.heap_next = SCRATCH+0x4000
        self.jpeg_decomp_calls=0
        super().render(inputs,reset,cursor,force_status)
        if self.allocations:
            raise AssertionError('Scene leaked media allocations')


def panel_rgb(panel,brightness=1000):
    """Match the QEMU surface's integer RGB565 expansion for byte-exact comparisons."""
    table = {}
    for color in set(panel.pixels):
        r,g,b = color>>11,(color>>5)&63,color&31
        table[color] = bytes(value*brightness//1000 for value in (r*255//31,g*255//63,b*255//31))
    return b''.join(table[color] for color in panel.pixels)


def write_rgb_png(path,pixels):
    """Save exact expected surface bytes with no metadata or alternate color expansion."""
    if len(pixels)!=240*240*3:raise ValueError('Expected a complete RGB scene')
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))
    rows=b''.join(b'\0'+pixels[y*720:(y+1)*720] for y in range(240))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',240,240,8,2,0,0,0))+
                     chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b''))


def normalized_checks(dump,assets):
    """Compare complete real-decoder scenes at identical inputs, with declared corrections."""
    factory=SceneMachine('factory',dump,assets)
    native=SceneMachine('native',dump,assets)
    corrected=SceneMachine('factory-weather-corrected',dump,assets)
    rows=[]
    cases=[(replace(Inputs(),icon=item['code'],step=index%10,temperature=-5 if index%2 else 26,
                    fahrenheit=index%2,miles=(index//2)%2,generation=index+1),0)
           for index,item in enumerate(assets['weather'])]
    for animation,item in enumerate(assets['animations']):
        for cursor in sorted({0,item['frame_count']//2,item['frame_count']-1}):
            cases.append((replace(Inputs(),animation=animation,valid=False),cursor))
    for index,(data,cursor) in enumerate(cases):
        for machine in (factory,native,corrected):
            machine.panel=Panel(); machine.render(data,cursor=cursor)
        literal=sum(a!=b for a,b in zip(factory.panel.pixels,native.panel.pixels))
        expected=sum(a!=b for a,b in zip(corrected.panel.pixels,native.panel.pixels))
        media_equal=factory.media_calls==native.media_calls
        rows.append({'theme':'classic','case':index,'inputs':data.__dict__,'cursor':cursor,
                     'literal_different_pixels':literal,'corrected_different_pixels':expected,
                     'jpeg_decomp_calls':{m.variant:m.jpeg_decomp_calls for m in (factory,native)},
                     'media_selection_equal':media_equal,
                     'compared_pixels':57600,
                     'passed':expected==0 and media_equal and factory.jpeg_decomp_calls==native.jpeg_decomp_calls==5})
    factory=Machine('factory'); native=Machine('native'); corrected=Machine('factory-corrected')
    for index,(hour,minute,second) in enumerate([(0,0,0),(0,0,1),(3,15,15),(6,30,30),(9,45,45),(12,0,59),(23,59,59)]):
        # Keep history across the trace; clearing old hands is part of the algorithm.
        for machine in (factory,native,corrected):
            machine.seed(hour,minute,second); machine.dial(reset=index==0)
        literal=sum(a!=b for a,b in zip(factory.panel.pixels,native.panel.pixels))
        expected=sum(a!=b for a,b in zip(corrected.panel.pixels,native.panel.pixels))
        rows.append({'theme':'dial','case':index,'time':[hour,minute,second],
                     'literal_different_pixels':literal,'corrected_different_pixels':expected,
                     'approved_fix':'analog-perpendicular-stroke-offsets','compared_pixels':57600,'passed':expected==0})
    return {'passed':all(row['passed'] for row in rows),'cases':rows,
            'scope':'Complete RGB565 frames, real media decoders, same canonical inputs and explicit factory corrections.'}
