"""Verify archived clock, independent HTTP, physical cache and restart evidence."""
import argparse
from copy import deepcopy
import datetime as dt
import gzip
import json
from pathlib import Path
import re
import struct

from jpeg_clock_contract import validate, rejection_checks
from photo_flash_evidence import journal, ready_frame, rejection_checks as damaged_flash
from verify_photo_cache_evidence import rgb, sha


def calendar_rate(frames):
    """Reject clock speed drift despite plausible pictures and monotonic dates."""
    stamps=[dt.datetime(**{k:r['clock'][k] for k in
        ('year','month','day','hour','minute','second')}) for r in frames]
    first=frames[0]['guest_seconds']
    assert all(abs((stamp-stamps[0]).total_seconds()-(row['guest_seconds']-first))<=1.25
        for row,stamp in zip(frames,stamps)), 'Calendar rate differs from guest timer'


def protected(before, after, mutable):
    """Compare every physical byte outside the declared writable intervals."""
    assert len(before)==len(after)==0x400000
    cursor=0
    for start,end in sorted(mutable):
        assert 0<=start<end<=len(before)
        assert before[cursor:start]==after[cursor:start]
        cursor=max(cursor,end)
    assert before[cursor:]==after[cursor:]


def verify(path, root):
    """Reconstruct full images, actual PNG pixels and canonical journal records."""
    proof=json.loads(path.read_text(encoding='utf-8'))
    assert proof['passed'] and not proof['all_functionality_verified']
    assert not proof['physical_hardware_tested'] and not proof['physical_power_cut_tested']
    blobs={}
    for row in proof['blobs']:
        file=(path.parent/row['file']).resolve();assert file.is_relative_to(path.parent.resolve())
        encoded=file.read_bytes();assert sha(encoded)==row['gzip_sha256']
        data=gzip.decompress(encoded)
        assert sha(data)==row['sha256'] and len(data)==row['bytes'] and row['sha256'] not in blobs
        blobs[row['sha256']]=data
    raw={}
    for row in proof['raw']:
        assert row['source'] not in raw;raw[row['source']]=blobs[row['sha256']]
    read=lambda name:json.loads(raw[name])
    reports={name:read(source) for name,source in proof['report_sources'].items()}
    manifest=json.loads((root/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text())
    app_sha=next(row['sha256'] for row in manifest['images'] if row['file']=='app.bin')
    for report in reports.values():
        assert report['passed'] and report['app_sha256']==app_sha
        assert report['elf_sha256']==manifest['elf_sha256'] and report['source_sha256']==manifest['source_sha256']
    count=0
    for name in ('lcd-final','lcd-control'):
        report=reports[name];assert report['control']==(name=='lcd-control')
        validate(report);assert rejection_checks(report)==report['contract_rejections']
        prefix=proof['report_sources'][name].rsplit('/',1)[0]
        for theme,flow in report['themes'].items():
            assert read(prefix+'/'+theme+'/clock-report.json')==flow
            calendar_rate(flow['frames'])
            for index,row in enumerate(flow['frames']):
                pixels=rgb(raw[f'{prefix}/{theme}/{index}-complete.png'])
                assert len(pixels)==57600*3
                assert sha(pixels)==row['actual_sha256']==row['native_sha256']==row['factory_sha256']
                count+=1
    assert count==60
    rate_mutant=deepcopy(reports['lcd-control']['themes']['simple']['frames'])
    rate_mutant[-1]['clock']['second']+=3
    try:calendar_rate(rate_mutant)
    except AssertionError:pass
    else:raise AssertionError('Calendar drift negative control accepted')

    base=blobs[proof['flash_base_sha256']];assert len(base)==0x400000
    images={}
    for row in proof['images']:
        data=bytearray(base);previous=-4096
        for change in row['sectors']:
            offset=change['offset'];sector=blobs[change['sha256']]
            assert offset%4096==0 and previous<offset<=len(data)-4096 and len(sector)==4096
            data[offset:offset+4096]=sector;previous=offset
        key=row['profile'],row['when'];assert key not in images and sha(data)==row['sha256']
        images[key]=bytes(data)
    assert len(images)==20
    plan=json.loads(raw[proof['plan_source']])
    ordinary=[(0x9000,0xf000),(0x3e7000,0x3e8000)]
    media=ordinary+[(0x264000,0x27d000)]+[(r['offset'],r['offset']+r['bytes']) for r in plan['candidate_extents']]
    for name in ('lcd-final','lcd-control'):
        for theme in reports[name]['themes']:
            profile=name+'/'+theme
            before,after=images[profile,'before'],images[profile,'after']
            prepared=read(proof['report_sources'][name].rsplit('/',1)[0]+'/'+theme+'/prepared.json')
            assert sha(before)==prepared['prepared_flash_sha256']
            protected(before,after,media)
            if name=='lcd-control':
                assert not journal(after,plan)['entries'][4]['ready']
                assert struct.unpack_from('<I',after,0x3e7000+0x1a8+4*4)[0]==0
    for name in ('http-long','http-control'):
        before,first,cold=(images[name,key] for key in ('before','after-0','after-1'))
        protected(before,first,ordinary if name=='http-control' else media)
        protected(first,cold,ordinary if name=='http-control' else media)
        report=reports[name];assert report['control']==(name=='http-control')
        assert report['lcd_tested'] is False and report['rf_tested'] is False
        assert report['protected_bytes_unchanged'] and len(report['boots'])==2
        assert all(row['owners_stopped'] and row['rom_boots']==1 and row['probe_connections']<=1 for row in report['boots'])
        probes=[p for case in report['cases'] for p in case['probes']]
        assert len(probes)==(160 if name=='http-control' else 862)
        assert all(p.get('status')==200 and 'error' not in p and 0<=p['seconds']<=10 for p in probes)
    http=reports['http-long'];assert http['cold_source_exact'] and http['finish_host_timeout']==900
    expected=[('full-cmyk12.jpg',200,'OK'),('flat-sampling44-8.jpg',400,'backing-capacity;'),
        ('flat-sampling44-12.jpg',400,'heap-headroom;'),('rich-progressive420-8.jpg',200,'OK'),
        ('flat-gray-progressive-8.jpg',200,'OK')]
    assert len(http['cases'])==len(expected)
    for case,(name,status,body) in zip(http['cases'],expected):
        assert case['name']==name and case['status']==status and case['body'].startswith(body)
        assert case['source_sha256']==sha((root/'Small_TV/src/tests/fixtures/jpeg_extended'/name).read_bytes())
        if status==400:
            numbers=re.search(r'required=(\d+) available=(\d+)',case['body'])
            assert numbers and int(numbers[1])>int(numbers[2])
        else:assert case['body']=='OK' and case['responsive_during_finish']>0

    upstream=read(proof['gray_reference']['report_source'])
    samples=raw[proof['gray_reference']['samples_source']]
    assert upstream['passed'] and upstream['precision']==8 and upstream['channels']==1
    assert len(samples)==57600 and set(samples)=={128}
    frame=b''.join(struct.pack('<H',(v>>3)<<11|(v>>2)<<5|v>>3) for v in samples)
    frame_sha=sha(frame);source_sha=sha((root/'Small_TV/src/tests/fixtures/jpeg_extended/flat-gray-progressive-8.jpg').read_bytes())
    assert frame_sha==proof['gray_reference']['rgb565_sha256']
    successful=[('lcd-final/'+theme,'after') for theme in ('classic','simple','dial')]
    successful += [('http-long','after-0'),('http-long','after-1'),('recovery','after')]
    for key in successful:ready_frame(images[key],plan,4,source_sha,frame_sha)
    assert len(damaged_flash(images['http-long','after-1'],plan,4,source_sha,frame_sha))==3
    recovery=reports['recovery'];before,after=images['recovery','before'],images['recovery','after']
    assert sha(before)==recovery['interrupted_flash_sha256'] and sha(after)==recovery['after_sha256']
    assert not journal(before,plan)['entries'][4]['ready']
    assert struct.unpack_from('<I',before,0x3e7000+0x1b8)[0]==0
    assert journal(before,plan)['generation']==1 and journal(after,plan)['generation']==2
    assert ready_frame(after,plan,4,source_sha,frame_sha)==recovery['cache']
    assert recovery['owners_stopped'] and recovery['protected_flash_exact'] and not recovery['physical_power_cut_tested']
    assert all(p['status']==200 for p in recovery['probes'])
    protected(before,after,media)
    prepared=read(proof['report_sources']['recovery'].rsplit('/',1)[0]+'/vm/prepared.json')
    assert sha(before)==prepared['prepared_flash_sha256']
    for source in proof['accepted_uart_sources']:
        data=raw[source];assert data.count(b'ESP-ROM:esp32c2')==1
        assert not any(word in data for word in (b'Guru Meditation',b'assert failed',b'abort() was called',b'watchdog got triggered'))
    assert len(proof['accepted_uart_sources'])==11
    for source in proof['prepared_sources']:
        assert read(source)['rom']['elf_sha256']==proof['archival_dependencies']['rom_elf_sha256']
    for name,digest in proof['source_pins'].items():assert sha((root/name).read_bytes())==digest,name
    archive=root/'firmware/development/small-tv-esp32c2-reconstructed'
    for row in manifest['images']:assert sha((archive/row['file']).read_bytes())==row['sha256']
    assert (archive/'app.bin').read_bytes()[176:208].hex()==manifest['elf_sha256']
    return dict(passed=True,frames=count,compared_pixels=count*57600,physical_images=len(images),
        http_workload_gets=862,http_control_gets=160,accepted_processes_reaped=11,
        gray_frame_sha256=frame_sha,physical_power_cut_tested=False)


def main():
    """Read immutable archived evidence without starting emulation or writing flash."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    args=parser.parse_args();print(json.dumps(verify(args.proof,args.root)))


if __name__=='__main__':main()
