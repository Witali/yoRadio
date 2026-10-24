"""Replay archived production JPEG format/RAM evidence without launching a VM."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import re
import subprocess

from photo_format_matrix_contract import validate,sha,require_lossless_modes
from photo_format_matrix_qemu import fixtures,factory_pixels
from verify_jpeg_clock_evidence import protected


def source_hashes(root,pins,revision=None):
    """Read historical committed identities without changing the current checkout."""
    if revision is None:return {name:sha((root/name).read_bytes()) for name in pins}
    commit=subprocess.check_output(['git','rev-parse','--verify',revision+'^{commit}'],cwd=root,text=True).strip()
    assert re.fullmatch('[0-9a-f]{40}',commit)
    names=sorted(pins)
    assert all('\n' not in name and not Path(name).is_absolute() and '..' not in Path(name).parts for name in names)
    data=subprocess.run(['git','cat-file','--batch'],cwd=root,
        input=''.join(commit+':'+name+'\n' for name in names).encode(),stdout=subprocess.PIPE,check=True).stdout
    at=0;result={}
    for name in names:
        end=data.index(b'\n',at);header=data[at:end].split();assert len(header)==3 and header[1]==b'blob'
        size=int(header[2]);body=data[end+1:end+1+size];at=end+size+2
        if body.startswith(b'version https://git-lfs.github.com/spec/v1\n'):
            result[name]=re.search(rb'oid sha256:([0-9a-f]{64})',body)[1].decode()
        else:result[name]=sha(body)
    assert at==len(data);return result


def verify(path,root,source_revision=None,seen=()):
    """Reconstruct all saved physical images and validate independent format oracles."""
    path=path.resolve();assert path not in seen and len(seen)<8
    proof=json.loads(path.read_text());assert proof['passed'] and not proof['all_functionality_verified']
    assert proof['schema_version'] in (1,2)
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
    images={};resolved={proof['flash_base_sha256']:base}
    for row in proof['images']:
        # Schema2 bases are earlier complete images: reject cycles/forward refs.
        if proof['schema_version']==2:assert 'base_sha256' in row
        parent=row.get('base_sha256',proof['flash_base_sha256'])
        assert parent in resolved and len(resolved[parent])==0x400000
        data=bytearray(resolved[parent]);previous=-4096
        for sector in row['sectors']:
            offset=sector['offset'];payload=blobs[sector['sha256']]
            assert len(payload)==4096 and offset%4096==0 and previous<offset<=len(data)-4096
            data[offset:offset+4096]=payload;previous=offset
        key=row['profile'],row['when'];assert key not in images and sha(data)==row['sha256']
        images[key]=bytes(data)
        resolved[row['sha256']]=images[key]
    manifest_path=root/proof['fixture_manifest'] if proof.get('fixture_manifest') else None
    corpus,rows,_=fixtures(manifest_path);oracles={r['name']:r for r in rows}
    if manifest_path:require_lossless_modes(oracles,manifest_path)
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
        if proof.get('stopped_process_images'):
            owned=[*plan['backing']['extents'],*plan['metadata']['extents'],*plan['caches'][4]['extents']]
            mutable=([(0x9000,0xf000),(0x3e7000,0x3e8000),(0x264000,0x27d000)]+
                [(r['offset'],r['offset']+r['bytes']) for r in owned])
            protected(images[name,'before'],images[name,'after'],mutable)
            last=report['cases'][-1]
            assert images[name,'after']==images[name+'/'+last['directory'],'after']
        summaries.append(validate(report,corpus,oracles,plan,json.loads(read('resource-layout.json')),
            json.loads(read('diagnostic-layout.json')),read))
        covered += [r['name'] for r in report['cases'] if 'recovery_for' not in r]
        uart=raw[prefix+'/vm/uart.log'];assert uart.count(b'ESP-ROM:esp32c2')==1
        assert not any(s in uart for s in (b'Guru Meditation',b'assert failed',b'abort() was called',b'watchdog got triggered'))
    assert len(covered)==len(set(covered))==proof['corpus_vectors']
    assert (set(covered)==corpus.keys())==proof['complete_corpus']
    if 'primary_outcomes' in proof:
        outcomes=Counter();recoveries=0;workflows=0
        keys={'flash-write-limit':'flash_write_limit','heap-headroom':'heap_headroom',
            'backing-capacity':'backing_capacity','unsupported-jpeg':'unsupported',
            'truncated-jpeg':'truncated','invalid-jpeg':'invalid'}
        for report in reports:
            workflows+=len(report['cases'])
            for row in report['cases']:
                if 'recovery_for' in row:recoveries+=1;continue
                if row['start']['status']!=200:key='source_slot_limit'
                elif row['finish']['status']==200:key='accepted'
                else:key=keys[row['finish']['body'].split(';')[0]]
                outcomes[key]+=1
        assert dict(outcomes)==proof['primary_outcomes']
        assert recoveries==proof['successful_recoveries'] and workflows==proof['workflows']
    observed=source_hashes(root,proof['source_pins'],source_revision)
    for name,digest in proof['source_pins'].items():assert observed[name]==digest,name
    manifest=json.loads((root/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text())
    assert manifest['elf_sha256']==proof['elf_sha256'] and manifest['source_sha256']==proof['source_sha256']
    modes={(row['finish']['diagnostic']['privacy']['precision'],row['finish']['diagnostic']['privacy']['components'])
        for report in reports for row in report['cases'] if row.get('finish',{}).get('status')==200 and
        row['finish']['diagnostic']['privacy']['process']==0xc3}
    result=dict(passed=True,complete_corpus=proof['complete_corpus'],corpus_vectors=len(covered),runs=summaries,
        physical_images=len(images),lossless_modes=sorted(modes))
    if proof.get('base_corpus'):
        row=proof['base_corpus'];base_path=(path.parent/row['file']).resolve();assert base_path.is_relative_to(path.parent)
        assert sha(base_path.read_bytes())==row['sha256']
        base_proof=json.loads(base_path.read_text())
        for key in ('app_sha256','elf_sha256','source_sha256'):assert base_proof[key]==proof[key]
        accepted=verify(base_path,root,row['source_revision'],(*seen,path))
        assert accepted['complete_corpus'] and accepted['corpus_vectors']==70
        result['base_corpus_verified']=True;result['combined_corpus_vectors']=70+len(covered)
        combined=modes|{tuple(pair) for pair in accepted['lossless_modes']}
        assert combined=={(bits,channels) for bits in range(2,17) for channels in (1,3,4)}
        result['verified_lossless_precision_color_pairs']=len(combined)
    return result


def main():
    """Read committed evidence and re-execute only the isolated factory pixel oracle."""
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--source-revision',help='Verify historical source pins in this Git commit without resetting files')
    args=parser.parse_args();print(json.dumps(verify(args.proof,args.root,args.source_revision)))


if __name__=='__main__':main()
