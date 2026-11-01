"""Independent expected-byte framing controls, without decoder execution."""
import argparse
import importlib.util
import json
from pathlib import Path
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--module',type=Path,default=Path(__file__).parent/'fixtures/opus_multistream_public/framing.py')
    args=parser.parse_args();spec=importlib.util.spec_from_file_location('public_multistream_framing_test',args.module)
    f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);cases=0
    examples=[(b'\xf8\x03abc',b'\xf8abc',[3]),(b'\xf9\x03abcdef',b'\xf9abcdef',[3,3]),
        (b'\xfa\x02\x03ABxyz',b'\xfa\x02ABxyz',[2,3]),(b'\xfb\x03\x02abcdef',b'\xfb\x03abcdef',[2,2,2]),
        (b'\xfb\x83\x01\x02\x03ABCDEF',b'\xfb\x83\x01\x02ABCDEF',[1,2,3]),
        (b'\xfb\x42\x03\x02abcd\0\0\0',b'\xfb\x42\x03abcd\0\0\0',[2,2]),
        (b'\xf8\xfc\x0c'+b'x'*300,b'\xf8'+b'x'*300,[300]),(b'\xf8\xff\xff'+b'x'*1275,b'\xf8'+b'x'*1275,[1275]),
        (b'\xf8\0',b'\xf8',[0])]
    for original,common,sizes in examples:
        row=f.split_element(original+b'next-stream',True)
        assert row['original']==original and row['common']==common and row['consumed']==len(original) and row['frame_bytes']==sizes;cases+=1
        row=f.split_element(common,False);assert row['original']==row['common']==common and row['frame_bytes']==sizes;cases+=1
    rows=f.split_multistream(b'\xf8\x03abc\xf8def',2)
    assert [v['original'] for v in rows]==[b'\xf8\x03abc',b'\xf8def'] and [v['offset'] for v in rows]==[0,5];cases+=1
    def reject(call):
        nonlocal cases
        try:call()
        except ValueError:cases+=1;return
        raise AssertionError('invalid framing accepted')
    for packet,framing in [(b'',True),(b'\xf8',True),(b'\xf8\xff',True),(b'\xf8\x05abc',True),
        (b'\xf9abc',False),(b'\xfb',True),(b'\xfb\0',True),(b'\xfb\x31',True),(b'\xfb\x07',True),
        (b'\xfb\x42\xff',True),(b'\xfa\x05ab',False),(b'\xf8'+b'x'*1276,False)]:reject(lambda p=packet,s=framing:f.split_element(p,s))
    reject(lambda:f.split_multistream(b'\xf8\x03abc\xf9defghi',2))
    print(json.dumps(dict(passed=True,cases=cases,decoder_executed=False)));return 0
if __name__=='__main__':raise SystemExit(main())
