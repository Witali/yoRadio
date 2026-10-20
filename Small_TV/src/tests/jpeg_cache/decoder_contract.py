"""Actual persistent JPEG -> verified RGB565 cache -> cold readonly display."""
from array import array
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from color_convert_contract import expected


def sha(path):
    """Bind real fixture and decoded output bytes to the independent oracle."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command):
    """Domain failures return structured data; a crash cannot pass a test."""
    result=subprocess.run([str(p) for p in command],capture_output=True,timeout=30)
    assert result.returncode==0,(command,result.returncode,result.stdout,result.stderr)
    return result


def main():
    """Keep physical bytes across two jobs; never accept partial or unverified output."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',type=Path,required=True)
    parser.add_argument('--reference-build',type=Path,required=True)
    parser.add_argument('--traffic',type=Path,required=True)
    parser.add_argument('--decoder-oracle',type=Path,required=True)
    parser.add_argument('--generator-build',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);fixtures=out/'fixtures';fixtures.mkdir()
    build=json.loads((args.build/'build.json').read_text());reference=json.loads((args.reference_build/'build.json').read_text())
    generator=json.loads((args.generator_build/'build.json').read_text())
    for row in (build,reference,generator):assert sha(Path(row['executable']))==row['executable_sha256']
    pins=json.loads((args.build/'inputs.json').read_text());pins[str(Path(__file__).resolve())]=sha(Path(__file__))
    assert all(sha(Path(p))==h for p,h in pins.items())
    exe,ref=build['executable'],reference['executable'];first,cold,raw=[out/n for n in ('first.rgb','cold.rgb','reference.raw')]
    report=dict(passed=False,all_functionality_verified=False,build=build,reference=reference,generator=generator,inputs_sha256=pins,positive=[],limits=[],negative=[],faults=[],stops=[])

    def oracle(image):
        """Unmodified upstream samples plus independent RGB565 math, not cache hashes."""
        row=json.loads(run([ref,'decode',image,raw,0,0]).stdout);assert row['passed']
        bits,channels=row['precision'],row['channels'];data=raw.read_bytes()
        samples=list(data) if bits<=8 else list(array('H',data))
        format=0 if channels==1 else 1 if channels==3 else 3 if b'Adobe' in image.read_bytes() else 2
        pixels=expected(samples,bits,format)
        if sys.byteorder!='little':pixels.byteswap()
        return hashlib.sha256(pixels.tobytes()).hexdigest()

    def decode(image,fault=None):
        """Verify source/decoder/cache cleanup and exact cold reuse behavior."""
        pins[str(image.resolve())]=sha(image)
        command=[exe,image,first,cold]
        if fault:command.extend(map(str,fault))
        row=json.loads(run(command).stdout);assert row['heap_final']==0,row
        row.update(first_sha256=sha(first),cold_sha256=sha(cold))
        return row

    try:
        traffic=json.loads((args.traffic/'report.json').read_text());assert traffic['passed']
        for item in traffic['cases']:
            source=args.traffic/'fixtures'/(item['name']+'.jpg');assert sha(source)==item['fixture_sha256']
            shutil.copyfile(source,fixtures/source.name)
        # Predictor4 compresses real full-size lossless16 into the actual photo
        # slot, unlike the existing129680-byte predictor1 example.
        for mode in ('gray','rgb','cmyk'):
            for bits in range(2,17):
                image=fixtures/f'lossless-{mode}-{bits}-p4.jpg'
                run([ref,'generate',image,'lossless-'+mode,bits,240,240,4,0,0])
        for image in sorted(fixtures.glob('*.jpg')):
            if image.stat().st_size>102400:
                row=decode(image)
                for phase in ('first','recovery'):
                    d=row[phase];assert d['cache_result']==10 and d['source_required']==image.stat().st_size and d['source_available']==102400,row
                    assert not d['decoded'] and not d['source_calls'] and not d['program_bytes'] and not d['erases'],row
                report['limits'].append(dict(name=image.name,kind='source-slot',result=row))
                continue
            gold=oracle(image);row=decode(image)
            assert row['first']['cache_result']==row['recovery']['cache_result']==0,row
            assert row['first']['decoded'] and not row['recovery']['decoded'] and row['decode_attempts']==1,row
            assert row['first_sha256']==row['cold_sha256']==gold and row['first']['ready'] and row['recovery']['ready'],row
            assert row['recovery']['program_bytes']==row['recovery']['erases']==0,row
            report['positive'].append(dict(name=image.name,fixture_sha256=sha(image),rgb565_sha256=gold,result=row))
            print('PASS cached pixels/cold readonly hit:',image.name,flush=True)
        full=fixtures/'rich-cmyk-progressive-12.jpg';gold=oracle(full);control=decode(full)
        report['traffic']=dict(name=full.name,result=control)
        # Real format/resource failures cannot publish a cache, even after rows.
        for name,status in (('sampling-44-c4-8.jpg','backing-capacity'),('sampling-44-c4-12.jpg','library-pool-limit'),
                            ('unsupported-sof5.jpg','unsupported-jpeg'),('truncated-44400.jpg','truncated-jpeg'),('not-jpeg.jpg','invalid-jpeg')):
            source=args.decoder_oracle/'fixtures'/name
            image=fixtures/('negative-'+name);shutil.copyfile(source,image);row=decode(image)
            if image.stat().st_size>102400:
                for phase in ('first','recovery'):
                    d=row[phase];assert d['cache_result']==10 and d['source_required']==image.stat().st_size and d['source_available']==102400 and not d['decoded'] and not d['program_bytes'],row
                report['limits'].append(dict(name=image.name,kind='source-slot',result=row));continue
            for phase in ('first','recovery'):
                d=row[phase];assert d['cache_result']!=0 and d['decoder_status']==status and not d['ready'],row
                if status in ('backing-capacity','library-pool-limit'):assert not d['frame_program_bytes'] and not d['scratch_program_bytes'],row
            assert first.stat().st_size==cold.stat().st_size==0,row
            report['negative'].append(dict(name=image.name,status=status,result=row))
        for bits,status in ((8,'backing-capacity'),(12,'library-pool-limit')):
            image=fixtures/f'flat-sampling44-{bits}.jpg';run([generator['executable'],image,'44',bits,4,'flat'])
            assert image.stat().st_size<=102400;row=decode(image)
            for phase in ('first','recovery'):
                d=row[phase];assert d['decoder_status']==status and not d['ready'] and not d['frame_program_bytes'] and not d['scratch_program_bytes'],row
            report['negative'].append(dict(name=image.name,status=status,result=row))
        # Cover global source/hash/invalidation/scratch/row/commit/display phases,
        # including boundaries and the final physical operation after publication.
        total=control['first']['calls'];ordinals=sorted({1,2,6,7,17,174,180,200,256,512,total-1,total}|{max(1,total*i//32) for i in range(1,32)})
        for ordinal in ordinals:
            row=decode(full,('physical',ordinal));assert row['first']['physical_fault_hits']==1 and row['first']['cache_result']!=0,row
            assert row['recovery']['cache_result']==0 and row['recovery']['ready'] and row['cold_sha256']==gold,row
            report['faults'].append(dict(kind='physical',ordinal=ordinal,result=row))
        # A valid-looking quantization/entropy read can change pixels without a
        # JPEG parse error. Check every actual input call AND its readbacks.
        remaining=full.stat().st_size
        for first_call in control['first_input_calls']:
            size=min(1024,remaining);remaining-=size
            for ordinal in range(first_call,first_call+1+(size+255)//256):
                row=decode(full,('silent',ordinal))
                assert row['first']['physical_fault_hits']==1 and row['first']['cache_result']==7 and not row['first']['ready'],row
                assert row['first']['decoder_status']=='input-io' and row['first']['callback_error']==7,row
                assert row['recovery']['cache_result']==0 and row['cold_sha256']==gold,row
                report['faults'].append(dict(kind='silent-source',ordinal=ordinal,result=row))
        assert remaining==0
        for kind,reason in (('time',2),('budget',3),('cancel',1)):
            for ordinal in (1,7,17,256,total//2,total):
                row=decode(full,(kind,ordinal))
                assert row['first']['cache_result']!=0 and row['first']['calls']==ordinal and row['first']['stop']==reason,row
                if row['first']['decoded'] and row['first']['decoder_status']!='ok':
                    assert row['first']['decoder_status']=={'time':'time-limit','budget':'io-budget','cancel':'cancelled'}[kind],row
                assert row['recovery']['cache_result']==0 and row['cold_sha256']==gold,row
                report['stops'].append(dict(kind=kind,ordinal=ordinal,result=row))
        for ordinal in (1,2,3,175,350,500,1000):
            row=decode(full,('hash',ordinal));assert row['first']['hash_fault_hits']==1 and row['first']['cache_result']!=0,row
            assert row['recovery']['cache_result']==0 and row['cold_sha256']==gold,row
            report['faults'].append(dict(kind='hash',ordinal=ordinal,result=row))
        report['passed']=True
    finally:
        report['inputs_unchanged']=all(sha(Path(p))==h for p,h in pins.items());report['passed'] &= report['inputs_unchanged']
        report['scope']='Actual JPEG decoder + persistent source/SHA/NOR/journal/frame cache, independent pixel oracle, partial physical/crypto/global-stop failures and cold readonly reuse. Host model only; native UI/HTTP/privacy/target cache execution/full RAM/stack/power-loss hardware remain open.'
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('PASS JPEG cache pipeline:',len(report['positive']),'images,',len(report['faults']),'fault recoveries,',len(report['stops']),'stops',flush=True)


if __name__=='__main__':main()
