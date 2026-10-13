"""Execute real RV32 date jumps and retained simple/classic calendar pixels."""
import argparse
from array import array
from dataclasses import replace
import datetime as dt
import json
from pathlib import Path
import struct

from classic_oracle import ClassicMachine, Inputs, UC_HOOK_CODE
from control_oracle import verify_inputs
from machine_oracle import Machine, Panel, ROOT, SCRATCH


class SimpleReference(Machine):
    """Declare a date-band clear while retaining the original text and clock instructions."""
    def __init__(self):
        super().__init__('factory')
        self.cpu.hook_add(UC_HOOK_CODE,self.clear_date,begin=0x4200abee,end=0x4200abee)

    def clear_date(self,cpu,pc,size,context):
        """Correct only the simple date's omitted background erase at y=180..203."""
        if self.reg(11)==180 and self.reg(13)==24:
            for y in range(180,204):self.panel.pixels[y*240:(y+1)*240]=array('H',[0])*240
            key='correct-simple-date-clear'
            self.executed_adapters[key]=self.executed_adapters.get(key,0)+1


def simple_time(machine,data,reset,minute_event=False,corrected=False):
    """Seed canonical calendar fields and execute the actual simple renderer entry."""
    machine.seed(data.hour,data.minute,data.second,
                 7 if corrected and data.weekday==0 else data.weekday,data.date_format,data.hour12)
    if machine.is_factory:
        day=7 if corrected and data.weekday==0 else data.weekday
        machine.cpu.mem_write(0x3fcbffc8,struct.pack('<I6B',data.year,data.month,data.day,
            data.hour,data.minute,data.second,day))
    else:
        yday=dt.date(data.year,data.month,data.day).timetuple().tm_yday-1
        machine.cpu.mem_write(SCRATCH+0x200,struct.pack('<9i',data.second,data.minute,data.hour,
            data.day,data.month-1,data.year-1900,data.weekday,yday,0)+bytes(8))
    machine.simple(reset=reset,minute_update=minute_event,second_update=True)


def checks(dump,assets,folder):
    """Compare full retained frames with clean native output and declared factory corrections."""
    dates=[(2025,1,1,14),(2026,1,1,14),(2026,1,1,14),(2024,3,1,14),
           (2025,3,2,14),(2026,10,13,15),(2026,1,1,16),(2026,1,1,16)]
    rows=[]
    identities={}
    for theme in ('classic','simple'):
        if theme=='classic':
            factory=ClassicMachine('factory',dump,assets)
            native=ClassicMachine('native',dump,assets)
            clean=ClassicMachine('native',dump,assets)
            corrected=ClassicMachine('factory-classic-corrected',dump,assets)
        else:
            factory,native,clean,corrected=Machine('factory'),Machine('native'),Machine('native'),SimpleReference()
        identities={'factory_elf_sha256':factory.source_sha,'native_elf_sha256':native.source_sha}
        for mode in range(3):
            for hour12 in range(2):
                for machine in (factory,native,corrected):machine.panel=Panel()
                previous=None
                for step,(year,month,day,minute) in enumerate(dates):
                    date=dt.date(year,month,day)
                    data=replace(Inputs(),year=year,month=month,day=day,weekday=(date.weekday()+1)%7,
                                 hour=18,minute=minute,second=7,date_format=mode,hour12=hour12)
                    key=(year,month,day,data.hour,minute)
                    changed=previous is None or key!=previous
                    if theme=='classic':
                        for machine in (factory,native):machine.render(data,reset=step==0,cursor=0)
                        if changed:
                            # The outer gate also ignores date changes at the same
                            # second: invalidate only the corrected cache to raise
                            # a clock event, then let its own clock body redraw.
                            corrected.cpu.mem_write(0x3fcc3a27,b'\xff')
                            corrected.cpu.mem_write(0x3fcc3a26,b'\x01')
                        corrected.render(data,reset=step==0,cursor=0)
                        clean.panel=Panel()
                        clean.render(data,reset=True,cursor=0)
                    else:
                        for machine in (factory,native):simple_time(machine,data,step==0)
                        simple_time(corrected,data,step==0,minute_event=changed,corrected=True)
                        clean.panel=Panel()
                        simple_time(clean,data,True)
                    stale=sum(a!=b for a,b in zip(native.panel.pixels,clean.panel.pixels))
                    reference=sum(a!=b for a,b in zip(native.panel.pixels,corrected.panel.pixels))
                    literal=sum(a!=b for a,b in zip(native.panel.pixels,factory.panel.pixels))
                    row={'theme':theme,'date_format':mode,'hour12':hour12,'step':step,
                         'inputs':data.__dict__,'calendar_or_minute_changed':changed,
                         'native_vs_clean_pixels':stale,'corrected_reference_pixels':reference,
                         'literal_different_pixels':literal,'passed':stale==0 and reference==0}
                    rows.append(row)
                    if not row['passed']:
                        if mode==0 and hour12==0:
                            native.panel.png(folder/f'{theme}-{step}-native.png')
                            clean.panel.png(folder/f'{theme}-{step}-clean.png')
                    previous=key
    return rows,identities


def main():
    """Bind positive and negative results to the exact archived binary and real ELF bytes."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True)
    app=verify_inputs()
    dump=(ROOT/'Small_TV/full-flash.bin').read_bytes()
    assets=json.loads((ROOT/'Small_TV/assets/manifest.json').read_text(encoding='utf-8'))
    rows,identities=checks(dump,assets,args.output.parent)
    manifest=json.loads((ROOT/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text(encoding='utf-8'))
    report={'passed':all(row['passed'] for row in rows),'cases':rows,'app_sha256':app,
            'source_sha256':manifest['source_sha256'],**identities,
            'approved_fixes':['calendar-change-with-unchanged-minute','clear-shortened-simple-date','standard-sunday'],
            'scope':'Both actual RV32 renderers, all framebuffer pixels on calendar/year/yday-collision jumps with unchanged seconds/minutes and long-to-short date changes. Corrected original invalidates its previous-second cache and raises the missing minute-refresh flag on calendar changes, maps Sunday 0 to supported 7 and clears the simple date band. No SNTP transport or physical timing claim.'}
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Calendar RV32:',len(rows),'cases; passed=',report['passed'])
    raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
