"""Focused data-only controls for the independent family1 fixture writer."""
import argparse
import importlib.util
import json
from pathlib import Path
import struct


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--generator',type=Path,default=Path(__file__).parent/'fixtures/opus_family1/generate.py')
    args=parser.parse_args();spec=importlib.util.spec_from_file_location('family1_test_data',args.generator)
    g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);cases=0
    def rejects(call):
        nonlocal cases
        try:call()
        except ValueError:cases+=1;return
        raise AssertionError('malformed data was accepted')
    for channels in (3,6,8):
        coupled=1 if channels==3 else 2 if channels==6 else 3;streams=channels-coupled
        transport=struct.pack('<8s6I8s',b'OFAM101\0',channels,streams,coupled,312,9600,11,bytes(range(channels)).ljust(8,b'\0'))
        transport+=(struct.pack('<I',3)+b'\xf8\xff\xfe')*11
        body,info=g.make(transport);parsed=g.parse(body)
        assert parsed['channels']==channels and len(parsed['packets'])==13 and info['pages']==13;cases+=1
        rejects(lambda:g.packets(transport[:-1]));rejects(lambda:g.packets(transport+b'\0'))
        changed=bytearray(transport);changed[32+channels-1]=0;rejects(lambda:g.packets(changed))
        changed=bytearray(body);changed[-1]^=1;rejects(lambda:g.parse(changed))
        rejects(lambda:g.parse(body[:-1]))
    print(json.dumps(dict(passed=True,cases=cases,decoder_executed=False)));return 0


if __name__=='__main__':raise SystemExit(main())
