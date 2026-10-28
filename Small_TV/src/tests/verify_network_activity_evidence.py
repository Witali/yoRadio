"""Replay saved AP request/peer overlap without executing a guest or using LCD."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

from network_activity_contract import validate, rejection_checks
from network_clients_contract import verify_abi
from verify_network_clients_evidence import code_reader
from verify_photo_format_matrix_evidence import source_hashes


def sha(data):
    """Identify exact observation, ABI and producer bytes."""
    return hashlib.sha256(data).hexdigest()


def verify(path,root,revision=None):
    """Require the exact native ELF, compiled ABI, model blobs and full replay."""
    proof=json.loads(path.read_text());assert proof['schema_version']==1 and proof['passed']
    assert not any(proof[k] for k in ('network_lifecycle_complete','all_functionality_verified',
        'lcd_acceptance','rf_acceptance','hardware_tested'))
    blobs={}
    for row in proof['blobs']:
        file=(path.parent/row['file']).resolve()
        assert file.is_relative_to(path.parent.resolve())
        data=file.read_bytes();assert sha(data)==row['gzip_sha256']
        data=gzip.decompress(data)
        assert len(data)==row['bytes'] and sha(data)==row['sha256']
        assert row['sha256'] not in blobs;blobs[row['sha256']]=data
    files={}
    for row in proof['raw']:
        assert row['source'] not in files;files[row['source']]=blobs[row['sha256']]
    assert source_hashes(root,proof['source_pins'],revision)==proof['source_pins']
    for name,digest in proof['source_pins'].items():assert sha(files['producer/'+name])==digest
    report=json.loads(files['final/report.json']);abi=json.loads(files['abi/layout.json'])
    verify_abi(abi,files['abi/wire.o'],files['abi/wire.c'])
    assert report['app_sha256']==abi['app_sha256']==proof['app_sha256']
    assert report['elf_sha256']==abi['elf_sha256']==proof['elf_sha256']
    assert report['qemu_sha256']==proof['qemu_sha256']
    fixture=(root/proof['fixture']).read_bytes();assert sha(fixture)==proof['fixture_sha256']
    read=code_reader(root/'.build/small-tv-esp32c2/small_tv_reconstructed.elf',proof['elf_sha256'])
    for name,address in {**report['entries'],**report['activity_entries'],
            'WIFI_EVENT':report['event_base_object']}.items():
        assert {s['st_value'] for s in read.symbols if s.name==name and s['st_value']}=={address}
    base=int.from_bytes(read(report['event_base_object'],4),'little')
    result=validate(report,abi['wire'],fixture,read,base)
    assert result==proof['result']
    assert rejection_checks(report,abi['wire'],fixture,read,base)==proof['rejected_controls']
    for name,digest in report['inputs_sha256'].items():
        name=name.replace('\\','/')
        if '/Small_TV/src/tests/' in name and not name.endswith('.jpg'):
            assert proof['source_pins']['Small_TV/src/tests/'+name.rsplit('/',1)[1]]==digest
    for relative,row in proof['qemu_source']['files'].items():
        data=files[row['source']];assert sha(data)==row['sha256']
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob']
    pilot=json.loads(files['pilot/report.json'])
    assert pilot['passed'] and pilot['owners_stopped'] and pilot['cycles']==1
    original=next(digest for name,digest in pilot['inputs_sha256'].items()
                  if name.replace('\\','/').endswith('/network_activity_qemu.py'))
    assert sha(files['pilot/producer.py'])==original
    return {**result,'unsafe_controls_rejected':len(proof['rejected_controls'])}


def main():
    """Recheck saved typed observations; never launch QEMU or modify any image."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--source-revision',help='Replay exact historical producers from Git without resetting')
    args=parser.parse_args();print(json.dumps(verify(args.proof,args.root,args.source_revision)))


if __name__=='__main__':main()
