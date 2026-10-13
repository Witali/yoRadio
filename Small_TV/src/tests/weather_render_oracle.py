"""Execute both BMP decoders and compare incremental classic-weather framebuffers."""
import argparse
from array import array
from dataclasses import replace
import json
from pathlib import Path
import struct

from classic_oracle import ClassicMachine, Inputs, Panel, ROOT, SCRATCH, layout, UC_HOOK_CODE, REGS, rv
from control_oracle import verify_inputs


class WeatherMachine(ClassicMachine):
    """Run actual BMP algorithms; adapt only flash, allocation and mutex SDK calls."""
    def adapt(self,address,name,callback):
        """Observe the BMP entry without replacing its pixel-decoding instructions."""
        if name == 'bmp-output-recorded':
            self.cpu.hook_add(UC_HOOK_CODE,lambda cpu,pc,size,context:self.observe_weather(cpu),begin=address,end=address)
        else:
            super().adapt(address,name,callback)

    def __init__(self,variant,dump,assets):
        super().__init__(variant,dump,assets)
        self.heap_next, self.allocations = SCRATCH+0x4000, set()
        self.partition_reads, self.fail_read_number = 0, None
        self.native_assets = (ROOT/'firmware/development/small-tv-esp32c2-reconstructed/assets.bin').read_bytes()
        if self.is_factory:
            self.adapt(0x4038e4be,'bmp-malloc',self.allocate)
            self.adapt(0x4038e4da,'bmp-free',self.release)
            if variant == 'factory-weather-corrected':
                self.install_field_corrections()
                self.cpu.hook_add(UC_HOOK_CODE,self.clip_partial_glyph,begin=0x4200950e,end=0x4200950e)
        else:
            size, fields = layout('esp_partition_t')
            partition = bytearray(size)
            struct.pack_into('<I',partition,fields['address'],0x200000)
            struct.pack_into('<I',partition,fields['size'],len(self.native_assets))
            self.cpu.mem_write(SCRATCH+0x2000,bytes(partition))
            self.adapt(self.symbols['esp_partition_find_first'],'asset-partition',lambda:SCRATCH+0x2000)
            self.adapt(self.symbols['xQueueCreateMutex'],'media-mutex-create',lambda:SCRATCH+0x2100)
            self.adapt(self.symbols['xQueueSemaphoreTake'],'media-mutex-take',lambda:1)
            self.adapt(self.symbols['xQueueGenericSend'],'media-mutex-give',lambda:1)
            self.adapt(self.symbols['esp_partition_read'],'bmp-partition-read',self.partition_read)
            if self.call(self.symbols['media_init']) != 0:
                raise AssertionError('Native media initialization failed')

    def observe_weather(self,cpu):
        """Record decoder selection while letting its actual body run."""
        if self.variant == 'factory-weather-corrected' and not self.cpu.mem_read(0x3fcc39d7,1)[0]:
            # The literal image preserves its old icon pointer after /updateCity.
            # This declared correction prevents displaying that stale icon.
            cpu.reg_write(REGS[10],0)
            cpu.reg_write(rv.UC_RISCV_REG_PC,cpu.reg_read(REGS[1]))
            self.executed_adapters['correct-stale-icon']=self.executed_adapters.get('correct-stale-icon',0)+1
            return
        self.weather()

    def allocate(self):
        """Supply bounded row/pixel storage, preserving original allocation ownership."""
        size = self.reg(10)
        if size not in (120,180):
            raise AssertionError('Unexpected original BMP allocation')
        pointer = self.heap_next
        self.heap_next += (size+15)&~15
        if self.heap_next >= SCRATCH+0x70000:
            raise AssertionError('BMP allocation fixture exhausted')
        self.allocations.add(pointer)
        return pointer

    def release(self):
        """Require each original BMP row buffer to be released exactly once."""
        self.allocations.remove(self.reg(10))
        return 0

    def permitted_read(self,offset,size):
        """Restrict adapted flash access to the real public weather BMP slots."""
        if not any(int(row['flash_offset'],16)<=offset and offset+size<=int(row['flash_offset'],16)+0x3c00
                   for row in self.assets['weather']):
            raise AssertionError('Unexpected BMP flash access')

    def flash_read(self):
        """Read immutable factory bytes for BMPs or the existing GIF header fixture."""
        offset,size = self.reg(12),self.reg(13)
        if offset in [int(row['flash_offset'],16) for row in self.assets['animations']]:
            return super().flash_read()
        self.permitted_read(offset,size)
        self.cpu.mem_write(self.reg(11),self.dump[offset:offset+size])
        return 0

    def partition_read(self):
        """Read the archived native asset pack through its real partition boundary."""
        if self.reg(10)!=SCRATCH+0x2000:
            raise AssertionError('Wrong native partition')
        self.partition_reads += 1
        if self.partition_reads == self.fail_read_number:
            return 0x105  # Inject an SDK read error; the decoder body still executes.
        offset,size = self.reg(11),self.reg(13)
        self.permitted_read(offset+0x200000,size)
        self.cpu.mem_write(self.reg(12),self.native_assets[offset:offset+size])
        return 0


def checks(dump,assets,folder):
    """Compare exact decoded pixels and retained display state, without image substitutes."""
    factory,native = WeatherMachine('factory',dump,assets),WeatherMachine('native',dump,assets)
    corrected=WeatherMachine('factory-weather-corrected',dump,assets)
    rows = []
    for item in assets['weather']:
        data = replace(Inputs(),icon=item['code'])
        for machine in (factory,native):
            machine.panel = Panel()
            machine.render(data)
        differences = sum(a!=b for a,b in zip(factory.panel.pixels,native.panel.pixels))
        ink=sum(factory.panel.pixels[y*240+x]!=0 for y in range(10,70) for x in range(180,240))
        rows.append({'kind':'bmp','icon':item['code'],'different_pixels':differences,
                     'compared_icon_pixels':3600,'nonblack_icon_pixels':ink,
                     'media_equal':factory.media_calls==native.media_calls,
                     'passed':not differences and ink>0 and factory.media_calls==native.media_calls})
    sequence = [('Fixture City','Clouds',True,'01d'),('A','Rain',True,'02d'),
                ('FifteenLetters!','Thunderstorm',True,'11d'),('A','Fog',True,'50d'),
                ('','',False,'50d'),('Fixture','Snow',True,'13n'),
                ('ABCDEFGHIJKLMNOP','Thunderstorm',True,'11n'),
                ('W'*64,'ABCDEFGHIJKLMNOPQRS',True,'09d'),('A','Fog',True,'50d'),
                ('','',True,'01d')]
    factory.panel,native.panel,corrected.panel = Panel(),Panel(),Panel()
    for step,(city,main,valid,icon) in enumerate(sequence):
        data = replace(Inputs(),city=city,main=main,valid=valid,icon=icon,
                       generation=step+1,retained_icon=not valid,second=step)
        for machine in (factory,native,corrected):
            machine.render(data,reset=step==0,cursor=0,force_status=True)
        clean = WeatherMachine('native',dump,assets)
        clean.render(data)
        stale = sum(a!=b for a,b in zip(native.panel.pixels,clean.panel.pixels))
        literal = sum(a!=b for a,b in zip(factory.panel.pixels,native.panel.pixels))
        corrected_difference=sum(a!=b for a,b in zip(corrected.panel.pixels,native.panel.pixels))
        row={'kind':'incremental','step':step,'inputs':data.__dict__,'literal_different_pixels':literal,
             'native_vs_clean_pixels':stale,'factory_media':factory.media_calls[:],
             'native_media':native.media_calls[:],'corrected_reference_pixels':corrected_difference,
             'corrected_media_equal':corrected.media_calls==native.media_calls,
             'passed':stale==0 and corrected_difference==0 and corrected.media_calls==native.media_calls}
        rows.append(row)
        if stale:
            native.panel.png(folder/f'incremental-{step}.png')
            clean.panel.png(folder/f'clean-{step}.png')
    if factory.allocations or corrected.allocations:
        raise AssertionError('Original BMP decoder leaked a buffer')
    return rows,factory,native,corrected


def scroll_checks(dump,assets,factory):
    """Check real RV32 motion against independent bitmap/phase expectations, pixel by pixel."""
    native=WeatherMachine('native',dump,assets)
    text='ABCDEFGHIJKLMNOPQRS'
    data=replace(Inputs(),city=text,main='Thunderstorm',description=text,step=6)
    native.render(data)
    baseline=native.panel.pixels[:]
    fields=[(0,10,180,text,0x07e0),(0,40,180,text,0xffff),(160,83,80,'Thunderstorm',0xffe0)]
    glyphs={character:bytes(factory.cpu.mem_read(0x3c0ec3e4+(ord(character)-32)*48,48))
            for character in set(text+'Thunderstorm')}
    rows=[]
    for tick in range(191):
        if tick:
            native.call(native.symbols['factory_scroll_tick'])
        expected=baseline[:]
        offsets=[]
        for left,top,width,label,color in fields:
            limit=len(label)*12-width
            travel=(limit+1)//2
            phase=tick % (2*(15+travel))
            offset=(min(limit,max(0,(phase-15)*2)) if phase<=30+travel
                    else max(0,limit-(phase-30-travel)*2))
            offsets.append(offset)
            for y in range(24):
                for x in range(width):
                    source=x+offset
                    character=label[source//12]
                    bits=glyphs[character][y*2+(source%12)//8]
                    expected[(top+y)*240+left+x]=color if bits&(1<<(source%12%8)) else 0
        differences=sum(a!=b for a,b in zip(native.panel.pixels,expected))
        ready=bool(native.call(native.symbols['factory_scroll_description_ready']))
        rows.append({'kind':'scroll','tick':tick,'offsets':offsets,'different_pixels':differences,
                     'description_ready':ready,'passed':differences==0 and ready==(tick>=78)})
    # Fresh content and a theme re-entry reset the phase; short fields stop moving.
    for kind,updated in [('short',replace(data,city='A',main='Fog',description='clear')),
                         ('theme-reset',data)]:
        native.render(updated,reset=True,force_status=True)
        first=native.panel.pixels[:]
        for _ in range(15):native.call(native.symbols['factory_scroll_tick'])
        rows.append({'kind':kind,'passed':native.panel.pixels==first})
    return rows


def decoder_failure_checks(dump,assets):
    """Inject header/first/middle/final row read errors into the actual compiled decoder."""
    reference=WeatherMachine('native',dump,assets)
    reference.render(Inputs())
    full=reference.panel.pixels[:]
    empty=full[:]
    for y in range(10,70):empty[y*240+180:y*240+240]=array('H',[0])*60
    rows=[]
    for read_number in (1,2,8,61):
        native=WeatherMachine('native',dump,assets)
        native.render(Inputs())
        native.partition_reads=0
        native.fail_read_number=read_number
        native.render(Inputs(),reset=False,force_status=True)
        failed_pixels=sum(a!=b for a,b in zip(native.panel.pixels,empty))
        observed=native.partition_reads==read_number
        native.fail_read_number=None
        native.render(Inputs(),reset=False,force_status=True)
        restored_pixels=sum(a!=b for a,b in zip(native.panel.pixels,full))
        rows.append({'kind':'decoder-read-error','read_number':read_number,'error_observed':observed,
                     'failed_frame_pixels':failed_pixels,'restored_frame_pixels':restored_pixels,
                     'passed':observed and failed_pixels==0 and restored_pixels==0})
    return rows


def main():
    """Bind the decoder/state evidence to the current immutable and archived inputs."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True)
    app_sha=verify_inputs()
    dump=(ROOT/'Small_TV/full-flash.bin').read_bytes()
    assets=json.loads((ROOT/'Small_TV/assets/manifest.json').read_text())
    rows,factory,native,corrected=checks(dump,assets,args.output.parent)
    rows+=scroll_checks(dump,assets,factory)
    rows+=decoder_failure_checks(dump,assets)
    report={'passed':all(row['passed'] for row in rows),'cases':rows,'app_sha256':app_sha,
            'source_sha256':json.loads((ROOT/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text())['source_sha256'],
            'factory_elf_sha256':factory.source_sha,'native_elf_sha256':native.source_sha,
            'adapters':{'factory':factory.executed_adapters,'native':native.executed_adapters,'factory-weather-corrected':corrected.executed_adapters},
            'approved_fixes':['clear-city-full-height','clear-weather-title','clear-unavailable-weather-icon','bound-text-to-field'],
            'requested_changes':['bidirectional-field-scroll'],
            'scope':'Both real BMP decoders and LCD pixels; flash/allocation/mutex boundaries adapted. JPEG output remains recorded. Incremental native pixels compared with fresh rendering and a separately declared corrected factory reference. Scroll frames checked against factory bitmaps and independent phase expectations; injected real-decoder read failures. Only explicit status-update events and active 100-ms scroll steps are modeled here.'}
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Weather render RV32:',len(rows),'cases; passed=',report['passed'])
    raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
