"""Actual bounded decoder pixels, resource preflight, error categories and object reuse."""
import argparse
from array import array
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from color_convert_contract import expected


def sha(path):
    """Identify actual decoded bytes and all test inputs."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command):
    """Native rejection is a returned status, never a crash/loader failure."""
    result=subprocess.run([str(x) for x in command],capture_output=True,timeout=30)
    assert result.returncode==0,(command,result.returncode,result.stdout,result.stderr)
    return result


def main():
    """Verify real JPEG callbacks while keeping host stdio separate from target NOR acceptance."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',type=Path,required=True)
    parser.add_argument('--reference-build',type=Path,required=True)
    parser.add_argument('--generator-build',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    fixtures=output/'fixtures';fixtures.mkdir()
    build=json.loads((args.build/'build.json').read_text());reference=json.loads((args.reference_build/'build.json').read_text());generator=json.loads((args.generator_build/'build.json').read_text())
    for record in (build,reference,generator):assert sha(Path(record['executable']))==record['executable_sha256']
    inputs=json.loads((args.build/'inputs.json').read_text());assert all(sha(Path(p))==h for p,h in inputs.items())
    exe,ref,gen=[record['executable'] for record in (build,reference,generator)]
    target,first,second=[output/n for n in ('reference.raw','first.rgb','second.rgb')]
    report=dict(passed=False,all_functionality_verified=False,build=build,reference=reference,generator=generator,
                runner_sha256=sha(Path(__file__)),positive=[],limits=[],negative=[],faults=[],transitions=[])

    def decode(image,pool=65536,backing=460800,maximum=240,fault=None,recovery=None):
        """Check API cleanup and actual allocator accounting after both cycles."""
        command=[exe,image,first,second,maximum,pool,backing]
        if fault:command.extend(fault)
        if recovery is not None:command.append(recovery)
        record=json.loads(run(command).stdout)
        assert record['heap_final']==0,record
        for phase in ('first','recovery'):
            d=record[phase];assert d['opened']==d['closed'] and d['pool_peak']<=pool,record
        record.update(first_sha256=sha(first),second_sha256=sha(second))
        return record

    def oracle(image):
        """Independent RGB565 arithmetic applied to unmodified upstream samples."""
        decoded=json.loads(run([ref,'decode',image,target,0,0]).stdout)
        assert decoded['passed'];bits=decoded['precision'];channels=decoded['channels'];data=target.read_bytes()
        samples=list(data) if bits<=8 else list(array('H',data))
        format=0 if channels==1 else 1 if channels==3 else 3 if b'Adobe' in image.read_bytes() else 2
        return hashlib.sha256(expected(samples,bits,format).tobytes()).hexdigest()

    try:
        modes=[('baseline',8),('baseline',12),('progressive420',8),('progressive444',12),
               ('cmyk-progressive',8),('cmyk-progressive',12),('ycck-progressive',12),
               ('gray-progressive',8),('arith-progressive',8)]
        modes += [('lossless-'+c,b) for c in ('gray','rgb','cmyk') for b in range(2,17)]
        for mode,bits in modes:
            image=fixtures/f'{mode}-{bits}.jpg'
            run([ref,'generate',image,'rich-'+mode+'-q83',bits,31,17,1,0,0]);gold=oracle(image)
            record=decode(image);assert record['first']['status']==record['recovery']['status']=='ok',record
            assert record['first_sha256']==record['second_sha256']==gold,(mode,bits,record)
            assert record['recovery']['reused_object'],record
            report['positive'].append(dict(name=image.name,fixture_sha256=sha(image),rgb565_sha256=gold,result=record))
        # Real full-size arrays, not just a small-image capacity estimate.
        image=fixtures/'full-cmyk12.jpg';run([ref,'generate',image,'rich-cmyk-progressive-q83',12,240,240,1,0,0]);gold=oracle(image)
        control=decode(image);assert control['first']['status']=='ok' and control['second_sha256']==gold
        report['positive'].append(dict(name=image.name,fixture_sha256=sha(image),rgb565_sha256=gold,result=control))
        for capacity in (0,1,460799):
            record=decode(image,backing=capacity)
            for phase in ('first','recovery'):
                d=record[phase];assert d['status']=='backing-capacity' and d['required']==460800 and d['available']==capacity and d['available_known'],record
                assert d['opened']==d['rows']==d['visits']['open']==d['visits']['read']==d['visits']['write']==0,record
            report['limits'].append(dict(kind='backing',capacity=capacity,result=record))
        record=decode(image,maximum=239);assert record['first']['status']=='image-dimensions' and record['first']['required']==240 and record['first']['available']==239
        report['limits'].append(dict(kind='dimensions',result=record))
        record=decode(image,pool=1);assert record['first']['status']=='library-pool-limit' and record['first']['required']>1 and record['first']['available']==1
        report['limits'].append(dict(kind='pool',result=record))
        # Legal4x4 CMYK needs524288, unlike the existing460800 fixture maximum.
        for factor,components in ((0x41,3),(0x12,3),(0x42,3),(0x44,4)):
            for bits in (8,12):
                unusual=fixtures/f'sampling-{factor:x}-c{components}-{bits}.jpg';run([gen,unusual,f'{factor:x}',bits,components]);g=oracle(unusual)
                record=decode(unusual,pool=262144,backing=1048576)
                assert record['first']['status']==record['recovery']['status']=='ok' and record['first_sha256']==record['second_sha256']==g,record
                report['positive'].append(dict(name=unusual.name,fixture_sha256=sha(unusual),rgb565_sha256=g,result=record))
                if factor==0x44:
                    refused=decode(unusual,pool=262144)
                    d=refused['first'];assert d['status']=='backing-capacity' and d['required']==524288 and d['available']==460800 and not d['opened'] and not d['rows'],refused
                    report['limits'].append(dict(kind='padded4x4',result=refused))
        # Correct error classes for unsupported coding, malformed structure and EOF.
        data=image.read_bytes()
        for cut in (0,2,len(data)//2,len(data)-2):
            bad=fixtures/f'truncated-{cut}.jpg';bad.write_bytes(data[:cut]);record=decode(bad,fault=('input',999999),recovery=image)
            assert record['first']['status']=='truncated-jpeg' and record['recovery']['status']=='ok' and record['second_sha256']==gold,record
            report['negative'].append(dict(name=bad.name,result=record))
        malformed=fixtures/'not-jpeg.jpg';malformed.write_bytes(b'not a JPEG image');record=decode(malformed,fault=('input',999999),recovery=image)
        assert record['first']['status']=='invalid-jpeg' and record['recovery']['status']=='ok' and record['second_sha256']==gold,record
        report['negative'].append(dict(name=malformed.name,result=record))
        # Declared SOF5 is a real unsupported differential process, not an allocation error.
        unsupported=fixtures/'unsupported-sof5.jpg';assert b'\xff\xc2' in data;unsupported.write_bytes(data.replace(b'\xff\xc2',b'\xff\xc5',1))
        record=decode(unsupported,fault=('input',999999),recovery=image)
        assert record['first']['status']=='unsupported-jpeg' and record['first']['detail']==3 and record['first']['parameter']==0xc5 and record['recovery']['status']=='ok',record
        report['negative'].append(dict(name=unsupported.name,result=record))
        marker=data.index(b'\xff\xc2')
        for name,change,status,detail in (
            ('oversize',lambda p:p.__setitem__(slice(marker+7,marker+9),b'\xff\xff'),'image-dimensions',1),
            ('dnl-height',lambda p:p.__setitem__(slice(marker+5,marker+7),b'\0\0'),'unsupported-jpeg',8),
            ('zero-width',lambda p:p.__setitem__(slice(marker+7,marker+9),b'\0\0'),'invalid-jpeg',0)):
            altered=bytearray(data);change(altered);bad=fixtures/(name+'.jpg');bad.write_bytes(altered)
            record=decode(bad,fault=('input',999999),recovery=image)
            assert record['first']['status']==status and record['first']['detail']==detail,record
            assert record['first']['opened']==record['first']['rows']==0 and record['recovery']['status']=='ok',record
            if name=='oversize':assert record['first']['required']==65535 and record['first']['available']==240,record
            report['negative'].append(dict(name=bad.name,result=record))
        # Header declaration limits are checked before entropy; this does not
        # claim the deliberately altered remainder is a valid complete image.
        rgb=(fixtures/'baseline-8.jpg').read_bytes();sof=rgb.index(b'\xff\xc0');fractional=bytearray(rgb)
        for i,sampling in enumerate((0x31,0x21,0x21)):fractional[sof+11+3*i]=sampling
        bad=fixtures/'fractional-header.jpg';bad.write_bytes(fractional);record=decode(bad,fault=('input',999999),recovery=image)
        assert record['first']['status']=='unsupported-jpeg' and record['first']['detail']==5 and not record['first']['opened'],record
        report['negative'].append(dict(name=bad.name,result=record))
        names=['baseline-8.jpg','baseline-12.jpg','cmyk-progressive-12.jpg','lossless-rgb-16.jpg','gray-progressive-8.jpg',
               'lossless-gray-2.jpg','ycck-progressive-12.jpg','lossless-cmyk-12.jpg','progressive444-12.jpg',
               'arith-progressive-8.jpg','lossless-rgb-2.jpg','full-cmyk12.jpg']
        golds={p['name']:p['rgb565_sha256'] for p in report['positive']}
        for before,after in zip(names,names[1:]+names[:1]):
            record=decode(fixtures/before,fault=('input',999999),recovery=fixtures/after)
            assert record['first']['status']==record['recovery']['status']=='ok' and record['recovery']['reused_object'],record
            assert record['first_sha256']==golds[before] and record['second_sha256']==golds[after],record
            report['transitions'].append(dict(before=before,after=after,result=record))
        # Exhaustive small-image callbacks, selected full-size boundary/middle calls.
        small=fixtures/'cmyk-progressive-12.jpg';small_gold=oracle(small);normal=decode(small)
        expected_status={'alloc':'allocation-failed','input':'input-io','output':'output-io','open':'backing-io','read':'backing-io','write':'backing-io','close':'backing-io','cancel':'cancelled','time':'time-limit','budget':'io-budget'}
        for kind,status in expected_status.items():
            count=normal['first']['visits'][kind]
            # Every cancellation/deadline checkpoint also covers the post-open orphan window.
            for ordinal in range(1,count+1):
                record=decode(small,fault=(kind,ordinal))
                assert record['first']['fault_hits']==1 and record['recovery']['fault_hits']==0,record
                if record['first']['status']=='ok':
                    assert kind=='alloc' and record['first_sha256']==small_gold,record
                else:assert record['first']['status']==status,record
                assert record['recovery']['status']=='ok' and record['second_sha256']==small_gold,record
                if record['first']['pool_retained']:
                    assert record['recovery']['reused_object'],record
                report['faults'].append(dict(operation=kind,ordinal=ordinal,result=record))
            print(kind,count,'callback failures and recoveries passed',flush=True)
        report['passed']=True
    finally:
        report['inputs_unchanged']=all(sha(Path(p))==h for p,h in inputs.items());report['passed'] &= report['inputs_unchanged']
        report['scope']='Actual portable decoder, exact RGB565/preflight/error/cleanup with host stdio source/backing. Not NOR/ESP-IDF/native UI, total target RAM/stack/time, privacy upload workflow or final acceptance.'
        (output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':main()
