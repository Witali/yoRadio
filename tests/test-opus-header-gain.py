"""Verify exact paired gain mutations and construction guards; no decoder runs."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GENERATOR=ROOT/'tests/fixtures/opus_header_gain/generate.py'
spec=importlib.util.spec_from_file_location('reviewed_opus_gain_fixture_generator',GENERATOR)
generator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve()
    assert out.is_relative_to(ROOT/'.build') and not out.exists();out.mkdir(parents=True)
    report=dict(passed=False,cases=[],decoder_executed=False,native_target_executed=False,sources={})
    report_path=out/'report.json'
    for path in (Path(__file__).resolve(),GENERATOR,generator.SOURCE):
        body=path.read_bytes();target=out/'sources'/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
        report['sources'][path.relative_to(ROOT).as_posix()]=dict(snapshot=target.relative_to(out).as_posix(),sha256=hashlib.sha256(body).hexdigest(),bytes=len(body))
    def good(name):report['cases'].append(dict(name=name,passed=True))
    def rejected(name,fn):
        try:fn()
        except ValueError:good(name)
        else:raise AssertionError(name+' accepted')
    try:
        source=generator.SOURCE.read_bytes();pages,packets=generator.parse(source)
        assert len(pages)==15 and len(packets)==553;good('complete-original-pages-packets')
        for tag in generator.comments(packets[1]):
            assert not tag.upper().startswith((b'R128_TRACK_GAIN=',b'R128_ALBUM_GAIN='))
        good('original-tags-have-no-gain-adjustments')
        one=generator.generate(out/'generation01');two=generator.generate(out/'generation02')
        for name,value in generator.VARIANTS:
            a=(out/'generation01'/(name+'.ogg')).read_bytes();b=(out/'generation02'/(name+'.ogg')).read_bytes()
            assert a==b and generator.verify_pair(source,a,value)==one['variants'][name]==two['variants'][name]
            assert one['variants'][name]['audio']==one['audio'];good('repeatable-complete-'+name)
        assert (out/'generation01/zero.ogg').read_bytes()==source;good('zero-exact-original')
        for gain in (-32768,-1,1,32767):
            changed=generator.mutate(source,gain);generator.verify_pair(source,changed,gain);good('signed-range-'+str(gain))
        for gain in (-32769,32768,1.5):rejected('invalid-gain-'+str(gain),lambda gain=gain:generator.mutate(source,gain))
        gain_start=pages[0]['payload']+16
        bad=bytearray(source);bad[gain_start+1]^=6
        rejected('gain-without-crc-rejected',lambda:generator.parse(bad))
        bad=bytearray(source);bad[pages[0]['payload']+12]^=1;bad[22:26]=bytes(4);bad[22:26]=generator.crc(bad[:pages[0]['end']]).to_bytes(4,'little')
        rejected('crc-valid-unrelated-head-change-rejected',lambda:generator.verify_pair(source,bytes(bad),0))
        page=pages[-1];bad=bytearray(source);bad[-1]^=1;bad[page['offset']+22:page['offset']+26]=bytes(4)
        bad[page['offset']+22:page['offset']+26]=generator.crc(bad[page['offset']:page['end']]).to_bytes(4,'little')
        rejected('crc-valid-audio-change-rejected',lambda:generator.verify_pair(source,bytes(bad),0))
        rejected('truncated-first-page-rejected',lambda:generator.parse(source[:pages[0]['end']-1]))
        rejected('truncated-final-page-rejected',lambda:generator.parse(source[:-1]))
        tag=b'R128_TRACK_GAIN=0';vendor=b'gain-test'
        tags=b'OpusTags'+len(vendor).to_bytes(4,'little')+vendor+(1).to_bytes(4,'little')+len(tag).to_bytes(4,'little')+tag
        assert len(tags)<=len(packets[1]) and pages[1]['packets']==1
        tags+=bytes(len(packets[1])-len(tags))
        bad=bytearray(source);page=pages[1];bad[page['payload']:page['end']]=tags
        bad[page['offset']+22:page['offset']+26]=bytes(4)
        bad[page['offset']+22:page['offset']+26]=generator.crc(bad[page['offset']:page['end']]).to_bytes(4,'little')
        rejected('existing-R128-gain-tag-rejected',lambda:generator.mutate(bytes(bad),1536))
        plus=math.pow(10,1536/(20*256));minus=math.pow(10,-1536/(20*256))
        assert abs(plus*minus-1)<1e-15 and 1.995<plus<1.996 and .501<minus<.502;good('normative-signed-gain-factors')
        for name,pin in report['sources'].items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==pin['sha256']==hashlib.sha256((out/pin['snapshot']).read_bytes()).hexdigest()
        report['passed']=report['all_source_bindings_current']=True
    except Exception as error:report['failure']=dict(type=type(error).__name__,reason=str(error))
    finally:report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=report['passed'],cases=len(report['cases']),decoder_executed=False,native_target_executed=False,
                          capture=out.relative_to(ROOT).as_posix(),failure=report.get('failure'))))
    return 0 if report['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
