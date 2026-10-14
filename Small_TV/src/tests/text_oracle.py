"""Execute real text/UTF-8 RV32 code against independent BDF and factory bitmap data."""
from __future__ import annotations
import argparse
from array import array
import hashlib
import json
from pathlib import Path
import random
import struct

from control_oracle import verify_inputs
from machine_oracle import Machine, Panel, ROOT, SCRATCH

PROJECT=ROOT/'Small_TV/src'


def source_fonts():
    """Read the original bitmap files and raw BDF without using generated headers."""
    folder=PROJECT/'resources/factory'
    manifest=json.loads((folder/'manifest.json').read_text())
    factory={row['name']:(row,(folder/(row['name']+'.bin')).read_bytes()) for row in manifest['tables']}
    for row,data in factory.values():
        if hashlib.sha256(data).hexdigest()!=row['sha256']:
            raise ValueError('Original font source changed')
    bdf=PROJECT/'third_party/spleen/spleen-6x12.bdf'
    glyphs={}
    for block in bdf.read_text().split('STARTCHAR ')[1:]:
        lines=block.splitlines()
        code=int(next(line.split()[1] for line in lines if line.startswith('ENCODING ')))
        rows=lines[lines.index('BITMAP')+1:lines.index('ENDCHAR')]
        glyphs[code]=[[bool(int(row,16)&(0x80>>x)) for x in range(6)] for row in rows]
    return factory,glyphs,bdf


def glyph_pixels(code,height,factory,spleen):
    """Build expected logical cells from immutable source rows, including fallback."""
    width=height//2
    name='ascii'+str(height)
    if code in (0x2103,0x2109):
        row,data=factory['temperature_units']
        base=72 if code==0x2109 else 0
        return [[bool(data[base+y*3+x//8]&(1<<(x%8))) for x in range(24)] for y in range(24)]
    row,data=factory[name]
    if row['first']<=code<row['first']+row['count']:
        base=(code-row['first'])*row['stride']*height
        return [[bool(data[base+y*row['stride']+x//8]&(1<<(x%8))) for x in range(width)] for y in range(height)]
    if code in spleen:
        source=spleen[code]
        return [[source[y*12//height][x*6//width] for x in range(width)] for y in range(height)]
    return glyph_pixels(ord('?'),height,factory,spleen)


def expected_panel(tokens,height,factory,spleen,x=0,y=10,left=0,right=240,transparent=False,complete=False,clip_height=False):
    """Compose expected pixels and guards independently of the native text decoder."""
    pixels=array('H',[0x4567])*57600
    for code in tokens:
        shape=glyph_pixels(code,height,factory,spleen)
        advance=height if code in (0x2103,0x2109) else height//2
        spacing=5 if transparent and height==16 and advance==8 else advance
        if x>=right or (complete and max(len(shape[0]),spacing)>right-x):
            break
        for gy,row in enumerate(shape):
            for gx,ink in enumerate(row):
                px,py=x+gx,y+gy
                if left<=px<right and 0<=py<240 and (not clip_height or gy<height) and (not transparent or ink):
                    pixels[py*240+px]=0xffff if ink else 0
        x+=spacing
    return pixels


def decoded_checks(native):
    """Compare Unicode scalar decoding with Python's UTF-8 encoding and literal invalid cases."""
    codes=[0x80,0x7ff,0x800,0xd7ff,0xe000,0xffff,0x10000,0x10ffff]
    rng=random.Random(0x32c2)
    codes += [code for code in (rng.randrange(0x110000) for _ in range(200)) if not 0xd800<=code<=0xdfff]
    rows=[]
    for code in codes:
        data=chr(code).encode('utf-8')
        native.cpu.mem_write(SCRATCH+0x3600,data+b'\0')
        native.cpu.mem_write(SCRATCH+0x3700,b'\xff'*4)
        actual=native.call(native.symbols['text_utf8_decode'],SCRATCH+0x3600,len(data),SCRATCH+0x3700)
        consumed=int.from_bytes(native.cpu.mem_read(SCRATCH+0x3700,4),'little')
        rows.append({'scalar':code,'bytes':len(data),'passed':actual==code and consumed==len(data)})
    invalid=[b'\x80',b'\xc0\x80',b'\xc1\xbf',b'\xe0\x80\x80',b'\xed\xa0\x80',
             b'\xf0\x80\x80\x80',b'\xf4\x90\x80\x80',b'\xf5\x80\x80\x80',b'\xe6',b'\xe6\x80',b'\xe6A']
    for data in invalid:
        native.cpu.mem_write(SCRATCH+0x3600,data+b'\0')
        actual=native.call(native.symbols['text_utf8_decode'],SCRATCH+0x3600,len(data),SCRATCH+0x3700)
        consumed=int.from_bytes(native.cpu.mem_read(SCRATCH+0x3700,4),'little')
        rows.append({'invalid_hex':data.hex(),'passed':actual==0xfffd and consumed==1})
    return rows


def prefix_checks(native):
    """Check every cut/capacity around a mixed UTF-8 message with independent prefix encoding."""
    text='AéТ€😀Z'
    source=text.encode()
    native.cpu.mem_write(SCRATCH+0x3600,source+b'\0')
    rows=[]
    for limit in range(len(source)+2):
        for capacity in range(len(source)+3):
            prefix=b''
            for character in text:
                encoded=character.encode()
                if len(prefix)+len(encoded)>limit or len(prefix)+len(encoded)>=capacity:
                    break
                prefix+=encoded
            native.cpu.mem_write(SCRATCH+0x3800,b'\xa5'*64)
            size=native.call(native.symbols['text_utf8_copy'],SCRATCH+0x3801,capacity,SCRATCH+0x3600,limit)
            out=bytes(native.cpu.mem_read(SCRATCH+0x3800,64))
            wanted=b'\xa5'+(prefix+b'\0'+b'\xa5'*(62-len(prefix)) if capacity else b'\xa5'*63)
            rows.append({'source_limit':limit,'capacity':capacity,'passed':size==len(prefix) and out==wanted})
    return rows


def main():
    """Preserve literal stock failures and require complete glyph/decoder/window agreement."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    app=verify_inputs()
    factory_source,spleen,bdf=source_fonts()
    factory,native=Machine('factory'),Machine('native')
    glyphs=[]
    for height in (16,24,32):
        for code in sorted({code for code in spleen if code>=128}|set(range(32,128))):
            result=native.call(native.symbols['factory_glyph'],code,height,SCRATCH+0x3500)
            pointer,width,actual_height,stride=struct.unpack('<4I',native.cpu.mem_read(SCRATCH+0x3500,16))
            data=bytes(native.cpu.mem_read(pointer,actual_height*stride)) if result else b''
            expected=glyph_pixels(code,height,factory_source,spleen)
            actual=[[bool(data[y*stride+x//8]&(1<<(x%8))) for x in range(width)] for y in range(actual_height)] if result else []
            glyphs.append({'codepoint':code,'height':height,'passed':result==1 and actual==expected})
    render=[]
    cases=[('ascii',b'City',[ord(c) for c in 'City']),
           ('cyrillic','Тест'.encode(),list(map(ord,'Тест'))),
           ('latin','Café'.encode(),list(map(ord,'Café'))),
           ('unsupported-cjk','北京'.encode(),[0x5317,0x4eac]),
           ('legacy-celsius',b'\xa1\xe6',[0x2103]),('legacy-fahrenheit',b'\xa8H',[0x2109]),
           ('unicode-celsius','℃'.encode(),[0x2103]),('unicode-fahrenheit','℉'.encode(),[0x2109]),
           ('degree-celsius','°C'.encode(),[0x2103]),('degree-alone','°'.encode(),[0xb0]),
           ('malformed-followed-by-ascii',b'\x81A',[0xfffd,ord('A')]),
           ('truncated-sequence',b'\xe6\x80',[0xfffd,0xfffd]),
           ('mixed','AТестBCDEFG'.encode(),list(map(ord,'AТестBCDEFG')))]
    for height in (16,24,32):
        for name,data,tokens in cases:
            for mode in ('opaque','transparent','bounded','window-left','window-right'):
                native.panel=Panel();native.panel.pixels=array('H',[0x4567])*57600
                native.cpu.mem_write(SCRATCH+0x3600,data+b'\0')
                width=sum(height if code in (0x2103,0x2109) else height//2 for code in tokens)
                actual_width=native.call(native.symbols['display_factory_text_width'],SCRATCH+0x3600,height)
                offset=max(0,width-31) if mode=='window-right' else 0
                x=20-offset if mode.startswith('window') else 20
                right=51 if mode in ('bounded','window-left','window-right') else 240
                if mode.startswith('window'):
                    native.call(native.symbols['display_factory_text_window'],20,10,31,offset,SCRATCH+0x3600,height,0xffff,0)
                elif mode=='bounded':
                    native.call(native.symbols['display_factory_text_bounded'],20,10,31,SCRATCH+0x3600,height,0xffff,0,0)
                else:
                    native.call(native.symbols['display_factory_text'],20,10,SCRATCH+0x3600,height,0xffff,0,int(mode=='transparent'))
                expected=expected_panel(tokens,height,factory_source,spleen,x,10,20,right,mode=='transparent',mode=='bounded',
                                        mode in ('bounded','window-left','window-right'))
                difference=sum(a!=b for a,b in zip(native.panel.pixels,expected))
                render.append({'case':name,'height':height,'mode':mode,'different_pixels':difference,
                               'passed':difference==0 and actual_width==width})
    literal=[]
    for name,data,tokens in cases[:6]:
        factory.panel=Panel();factory.cpu.mem_write(SCRATCH+0x3600,data+b'\0')
        factory.call(0x4200abee,0,10,SCRATCH+0x3600,24,0xffff,0)
        native.panel=Panel();native.cpu.mem_write(SCRATCH+0x3600,data+b'\0')
        native.call(native.symbols['display_factory_text'],0,10,SCRATCH+0x3600,24,0xffff,0,0)
        difference=sum(a!=b for a,b in zip(factory.panel.pixels,native.panel.pixels))
        literal.append({'case':name,'different_pixels':difference,
                        'passed':(difference==0) if name in ('ascii','legacy-celsius','legacy-fahrenheit') else difference>0})
    decode,prefix=decoded_checks(native),prefix_checks(native)
    manifest=json.loads((ROOT/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text())
    report={'passed':all(row['passed'] for row in glyphs+render+literal+decode+prefix),
            'app_sha256':app,'source_sha256':manifest['source_sha256'],
            'factory_elf_sha256':factory.source_sha,'native_elf_sha256':native.source_sha,
            'font_source_sha256':hashlib.sha256(bdf.read_bytes()).hexdigest(),
            'unicode_glyphs':sum(code>=128 for code in spleen),'ascii_glyphs_per_height':96,
            'glyph_checks':glyphs,'render_cases':render,
            'literal_factory':literal,'decode_checks':decode,'prefix_checks':prefix,
            'approved_fixes':['utf8-scalar-rendering','no-celsius-for-arbitrary-high-bytes','complete-utf8-prefix'],
            'scope':__doc__,'adapters':{'factory':factory.executed_adapters,'native':native.executed_adapters}}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Text RV32:',len(glyphs),'glyph checks;',len(render),'renders;',len(decode),'decode;',len(prefix),'prefix; passed=',report['passed'])
    if not report['passed']:
        print('Failures:',[row for row in glyphs+render+literal+decode+prefix if not row['passed']][:8])
        raise SystemExit(1)


if __name__=='__main__':main()
