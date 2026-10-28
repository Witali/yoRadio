"""Independently verify physical JPEG quotas, zero boots and full LCD captures."""
import argparse
import gzip
import json
from pathlib import Path

from jpeg_clock_contract import validate,rejection_checks
from photo_flash_evidence import ready_frame
import photo_runtime_metrics as metrics
from verify_jpeg_clock_evidence import protected,calendar_rate
from verify_photo_cache_evidence import sha,rgb


def verify(path,root):
    """Reconstruct actual images and count callbacks instead of trusting green flags."""
    proof=json.loads(path.read_text(encoding='utf-8'))
    assert proof['passed'] and not proof['all_functionality_verified'] and not proof['hardware_tested']
    payloads={}
    for row in proof['blobs']:
        file=(path.parent/row['file']).resolve();assert file.is_relative_to(path.parent.resolve())
        encoded=file.read_bytes();assert sha(encoded)==row['gzip_sha256']
        data=gzip.decompress(encoded);assert sha(data)==row['sha256'] and len(data)==row['bytes']
        assert row['sha256'] not in payloads;payloads[row['sha256']]=data
    raw={}
    for row in proof['raw']:
        assert row['source'] not in raw;raw[row['source']]=payloads[row['sha256']]
    read=lambda source:json.loads(raw[source])
    reports={name:read(source) for name,source in proof['report_sources'].items()}
    for name,r in reports.items():
        assert r['passed']==(name!='zero_startup_before'),name
    current=('storage','zero_startup','clocks','artifact')
    for name in current:
        assert reports[name]['app_sha256']==proof['app_sha256']
        assert reports[name]['source_sha256']==proof['source_sha256']
    storage=reports['storage'];assert len(storage['boots'])==2 and all(r['owners_stopped'] for r in storage['boots'])
    assert not storage['network_acceptance'] and not storage['lcd_acceptance']
    assert len(storage['cases'])==2
    plan=read(proof['plan_source'])
    owned=[*plan['backing']['extents'],*plan['metadata']['extents'],*plan['caches'][4]['extents']]
    for case in storage['cases']:
        total=0
        for phase in ('start','finish'):
            row=case[phase];count=0;erases=0
            for event in row['callbacks']:
                address,length=event['address'],event['bytes']
                assert event['status']==0 and any(r['offset']<=address and address+length<=r['offset']+r['bytes'] for r in owned)
                if event['kind']=='program':
                    assert 0<length<=256 and address//256==(address+length-1)//256;count+=length
                else:assert event['kind']=='erase' and length==4096 and address%4096==0;erases+=1
            assert row['program_bytes']==count and row['erase_calls']==erases
            total+=count
        assert total==case['total_program_bytes']==case['finish']['diagnostic']['program_bytes']<=204800
    heavy,gray=storage['cases'];assert heavy['name']=='full-cmyk12.jpg' and heavy['total_program_bytes']==204800
    assert heavy['finish']['status']==400 and heavy['finish']['body']=='flash-write-limit; required=205056 available=204800'
    assert gray['name']=='flat-gray-progressive-8.jpg' and gray['total_program_bytes']==115968
    assert gray['finish']['status']==200 and gray['finish']['body']=='OK'
    zero=storage['zero_start'];assert not zero['callbacks'] and not zero['program_bytes'] and not zero['erase_calls']
    assert zero['status']==400 and zero['body']=='flash-writes-disabled; required=1 available=0'
    cold=storage['cold_zero_draw'];assert cold['source_slot']==4 and cold['status']==0 and cold['policy_kib']==0
    assert cold['raw_callbacks_traced_from_reset'] and not cold['callbacks'] and cold['attempts'][-1]==0

    base=payloads[proof['flash_base_sha256']];assert len(base)==0x400000
    images={}
    for row in proof['images']:
        data=bytearray(base);previous=-4096
        for change in row['sectors']:
            offset=change['offset'];sector=payloads[change['sha256']]
            assert offset%4096==0 and previous<offset<=len(data)-4096 and len(sector)==4096
            data[offset:offset+4096]=sector;previous=offset
        key=row['profile'],row['when'];assert key not in images and sha(data)==row['sha256']
        images[key]=bytes(data)
    assert len(images)==15
    prefixes={('warm','before'):proof['report_sources']['storage'].rsplit('/',1)[0]+'/warm/prepared.json',
        ('cold','before'):proof['report_sources']['storage'].rsplit('/',1)[0]+'/cold/prepared.json',
        ('zero-legacy','before'):proof['report_sources']['zero_startup'].rsplit('/',1)[0]+'/vm/prepared.json',
        ('old-zero-legacy','before'):proof['report_sources']['zero_startup_before'].rsplit('/',1)[0]+'/vm/prepared.json'}
    clock_prefix=proof['report_sources']['clocks'].rsplit('/',1)[0]
    prefixes.update({('clock/'+theme,'before'):clock_prefix+'/'+theme+'/prepared.json' for theme in reports['clocks']['themes']})
    for key,source in prefixes.items():
        prepared=read(source);assert sha(images[key])==prepared['prepared_flash_sha256']
        assert prepared['rom']['elf_sha256']==proof['archival_dependencies']['rom_elf_sha256']
        expected=reports['zero_startup_before'] if key[0]=='old-zero-legacy' else storage
        assert prepared['sources']['source_sha256']==expected['source_sha256']
        entry=next(r for r in prepared['sources']['images'] if r['file']=='app.bin')
        start=int(entry['offset'],0);assert sha(images[key][start:start+entry['bytes']])==expected['app_sha256']==entry['sha256']
    mutable=([(0x9000,0xf000),(0x3e7000,0x3e8000),(0x264000,0x27d000)]+
        [(r['offset'],r['offset']+r['bytes']) for r in owned])
    protected(images['warm','before'],images['warm','after'],mutable)
    protected(images['warm','zero-before'],images['warm','after'],[(0x9000,0xf000),(0x3e7000,0x3e8000)])
    assert images['cold','before']==images['warm','after']==images['cold','after']
    source_sha='45263a1cb1be94439742e66e5cfe09553cc9495aff6efee87ba465b6acebf5ec'
    frame_sha='a3ec07b094d96c0fc6b420ba1a8666639a108c9e925c5f199c3e8f6f8ee10745'
    for key in [('warm','zero-before'),('warm','after'),('cold','after')]:ready_frame(images[key],plan,4,source_sha,frame_sha)
    legacy=reports['zero_startup'];assert legacy['owners_stopped'] and legacy['policy_kib']==0 and legacy['init_status']==0
    assert not legacy['callbacks'] and images['zero-legacy','before']==images['zero-legacy','after']
    stamp=legacy['stamp_offset'];assert images['zero-legacy','after'][stamp:stamp+64]==b'\xff'*64
    for r in plan['candidate_extents']:assert images['zero-legacy','after'][r['offset']:r['offset']+r['bytes']]==b'\xff'*r['bytes']
    prior=reports['zero_startup_before'];assert prior['owners_stopped'] and prior['policy_kib']==0
    assert [(r['kind'],r['address'],r['bytes']) for r in prior['callbacks']]==[('program',stamp+8,32),('program',stamp,8)]
    before,after=images['old-zero-legacy','before'],images['old-zero-legacy','after']
    assert before[stamp:stamp+64]==b'\xff'*64 and after[stamp:stamp+8]==b'STVOWN1\0'
    assert before[:stamp]==after[:stamp] and before[stamp+40:]==after[stamp+40:]
    first_prefix=proof['report_sources']['zero_startup_before'].rsplit('/',2)[0]+'/first-policy-app/'
    old_sources={r['file']:r['sha256'] for r in read(first_prefix+'source-manifest.json')['files']}
    archive=root/'firmware/development/small-tv-esp32c2-reconstructed'
    new_sources={r['file']:r['sha256'] for r in json.loads((archive/'source-manifest.json').read_text())['files']}
    assert [name for name in sorted(old_sources.keys()|new_sources.keys()) if old_sources.get(name)!=new_sources.get(name)]==['app/media/photo_storage.c']
    old_storage=raw[first_prefix.rsplit('/',2)[0]+'/first-policy-photo-storage.c']
    assert sha(old_storage)==old_sources['app/media/photo_storage.c']

    clocks=reports['clocks'];validate(clocks);assert rejection_checks(clocks)==clocks['contract_rejections']
    prefix=proof['report_sources']['clocks'].rsplit('/',1)[0]
    layout=read(prefix+'/resource-layout.json');assert layout['elf_sha256']==clocks['elf_sha256']
    frames=0
    for theme,flow in clocks['themes'].items():
        calendar_rate(flow['frames']);profile='clock/'+theme
        protected(images[profile,'before'],images[profile,'after'],mutable)
        ready_frame(images[profile,'after'],plan,4,source_sha,frame_sha)
        for index,row in enumerate(flow['frames']):
            data=rgb(raw[f'{prefix}/{theme}/{index}-complete.png'])
            assert len(data)==57600*3 and sha(data)==row['actual_sha256']==row['native_sha256']==row['factory_sha256'];frames+=1
        for phase in ('entry','exit'):
            observed=flow['resources'][phase];ram=raw[f'{prefix}/{theme}/'+observed['ram_file']]
            assert sha(ram)==observed['ram_sha256']
            derived=metrics.inspect(layout,ram,observed['worker']['tcb_address'])
            for field in ('worker','current_task','heaps','free_8bit_bytes','sum_individual_heap_minima'):assert derived[field]==observed[field]
    assert frames==15
    assert reports['native']['checks']>=6290 and len(reports['native']['routes'])==42
    assert reports['transport']['cases']==34 and reports['transport']['checks']==348557
    assert len(reports['transport_mutants']['cases'])==18
    assert len(reports['policy_mutants']['cases'])==7 and reports['policy_mutants']['cases'][0]['name']=='control'
    assert all(r['exit_code']==1 for r in reports['policy_mutants']['cases'][1:])
    assert reports['dom']['cases']==16 and not reports['dom']['real_browser_tested']
    assert reports['artifact']['cases']==6
    for source in proof['uart_sources']:
        data=raw[source];assert data.count(b'ESP-ROM:esp32c2')==1
        assert not any(word in data for word in (b'Guru Meditation',b'assert failed',b'abort() was called',b'watchdog got triggered'))
    assert len(proof['uart_sources'])==6
    for name,digest in proof['source_pins'].items():assert sha((root/name).read_bytes())==digest,name
    manifest=json.loads((archive/'manifest.json').read_text())
    for row in manifest['images']:assert sha((archive/row['file']).read_bytes())==row['sha256']
    assert (archive/'app.bin').read_bytes()[176:208].hex()==manifest['elf_sha256']
    assert sha((archive/'app.bin').read_bytes())==proof['app_sha256'] and manifest['source_sha256']==proof['source_sha256']
    return dict(passed=True,default_program_limit=204800,heavy_program_bytes=204800,gray_program_bytes=115968,
        zero_cache_and_startup_callbacks=0,cold_complete_flash_unchanged=True,frames=frames,compared_pixels=frames*57600,
        physical_images=len(images),current_processes_reaped=6)


def main():
    """Read only saved bytes; never emulate, reset or modify a device."""
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    args=parser.parse_args();print(json.dumps(verify(args.proof,args.root)))


if __name__=='__main__':main()
