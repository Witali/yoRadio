"""Replay archived production JPEG format/RAM evidence without launching a VM."""
import argparse
import gzip
import json
from pathlib import Path

from photo_format_matrix_contract import validate,sha
from photo_format_matrix_qemu import fixtures,factory_pixels


def verify(path,root):
    """Reconstruct all saved physical images and validate independent format oracles."""
    proof=json.loads(path.read_text());assert proof['passed'] and not proof['all_functionality_verified']
    assert not proof['physical_hardware_tested'] and not proof['network_acceptance'] and not proof['lcd_acceptance']
    blobs={}
    for row in proof['blobs']:
        file=(path.parent/row['file']).resolve();assert file.is_relative_to(path.parent.resolve())
        compressed=file.read_bytes();assert sha(compressed)==row['gzip_sha256']
        data=gzip.decompress(compressed);assert sha(data)==row['sha256'] and len(data)==row['bytes']
        assert row['sha256'] not in blobs;blobs[row['sha256']]=data
    raw={}
    for row in proof['raw']:
        assert row['source'] not in raw;raw[row['source']]=blobs[row['sha256']]
    base=blobs[proof['flash_base_sha256']];assert len(base)==0x400000
    images={}
    for row in proof['images']:
        data=bytearray(base);previous=-4096
        for sector in row['sectors']:
            offset=sector['offset'];payload=blobs[sector['sha256']]
            assert len(payload)==4096 and offset%4096==0 and previous<offset<=len(data)-4096
            data[offset:offset+4096]=payload;previous=offset
        key=row['profile'],row['when'];assert key not in images and sha(data)==row['sha256']
        images[key]=bytes(data)
    corpus,rows,_=fixtures();oracles={r['name']:r for r in rows}
    reports=[json.loads(raw[r['prefix']+'/report.json']) for r in proof['runs']]
    if any(row['name']=='rich-baseline-8.jpg' for report in reports for row in report['cases']):
        gold=factory_pixels(corpus['rich-baseline-8.jpg'],Path(proof['dependency_root']))
        assert gold['factory_elf_sha256']==proof['factory_elf_sha256']
        oracles['rich-baseline-8.jpg'].update(gold)
    plan=json.loads(raw[proof['plan_source']]);summaries=[];covered=[]
    for run,report in zip(proof['runs'],reports):
        for key in ('app_sha256','elf_sha256','source_sha256'):assert report[key]==proof[key]
        prefix=run['prefix'];name=run['name']
        def read(relative):
            if relative.endswith(('/before.bin','/after.bin')):
                directory,file=relative.split('/');return images[name+'/'+directory,file[:-4]]
            return raw[prefix+'/'+relative]
        prepared=json.loads(raw[prefix+'/vm/prepared.json'])
        assert sha(images[name,'before'])==prepared['prepared_flash_sha256']
        assert prepared['rom']['elf_sha256']==proof['rom_elf_sha256']
        app=next(row for row in prepared['sources']['images'] if row['file']=='app.bin')
        start=int(app['offset'],0);assert sha(images[name,'before'][start:start+app['bytes']])==proof['app_sha256']
        summaries.append(validate(report,corpus,oracles,plan,json.loads(read('resource-layout.json')),
            json.loads(read('diagnostic-layout.json')),read))
        covered += [r['name'] for r in report['cases'] if 'recovery_for' not in r]
        uart=raw[prefix+'/vm/uart.log'];assert uart.count(b'ESP-ROM:esp32c2')==1
        assert not any(s in uart for s in (b'Guru Meditation',b'assert failed',b'abort() was called',b'watchdog got triggered'))
    assert len(covered)==len(set(covered))==proof['corpus_vectors']
    assert (set(covered)==corpus.keys())==proof['complete_corpus']
    for name,digest in proof['source_pins'].items():assert sha((root/name).read_bytes())==digest,name
    manifest=json.loads((root/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text())
    assert manifest['elf_sha256']==proof['elf_sha256'] and manifest['source_sha256']==proof['source_sha256']
    return dict(passed=True,complete_corpus=proof['complete_corpus'],corpus_vectors=len(covered),runs=summaries,
        physical_images=len(images))


def main():
    """Read committed evidence and re-execute only the isolated factory pixel oracle."""
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3]);args=parser.parse_args()
    print(json.dumps(verify(args.proof,args.root)))


if __name__=='__main__':main()
