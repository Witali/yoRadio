"""Verify saved station/weather overlap using exact-ELF types and raw cache bytes."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from network_clients_contract import verify_abi
from station_event_layout import describe
from station_weather_contract import validate,rejection_checks
from verify_network_clients_evidence import code_reader
from verify_photo_format_matrix_evidence import source_hashes
import weather_qemu as weather


def sha(data):
    """Bind typed observations, source snapshots and historical Git blobs."""
    return hashlib.sha256(data).hexdigest()


def verify(path,root,revision=None):
    """Recompute target ABI and weather values without running or modifying a VM."""
    proof=json.loads(path.read_text());assert proof['schema_version']==1 and proof['passed']
    assert not any(proof[k] for k in ('network_lifecycle_complete','all_functionality_verified',
        'lcd_acceptance','rf_acceptance','hardware_tested'))
    blobs={}
    for row in proof['blobs']:
        file=(path.parent/row['file']).resolve();assert file.is_relative_to(path.parent.resolve())
        data=file.read_bytes();assert sha(data)==row['gzip_sha256']
        data=gzip.decompress(data);assert sha(data)==row['sha256'] and len(data)==row['bytes']
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
    elf=root/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    assert describe(elf)==report['station_layout']
    weather.ROOT=root;weather.vm=SimpleNamespace(digest=sha)
    assert weather.native_layout()==report['weather_layout']
    read=code_reader(elf,proof['elf_sha256'])
    for name,address in report['entries'].items():
        assert {s['st_value'] for s in read.symbols if s.name==name and s['st_value']}=={address}
    result=validate(report,read);assert result==proof['result']
    assert rejection_checks(report,read)==proof['rejected_controls']
    for name,digest in report['inputs_sha256'].items():
        name=name.replace('\\','/')
        if '/Small_TV/src/tests/' in name:
            assert proof['source_pins']['Small_TV/src/tests/'+name.rsplit('/',1)[1]]==digest
    for row in proof['qemu_source']['files'].values():
        data=files[row['source']];assert sha(data)==row['sha256']
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob']
    pilot=json.loads(files['pilot/report.json'])
    assert pilot['passed'] and pilot['owners_stopped'] and len(pilot['cases'])==2
    original=next(digest for name,digest in pilot['inputs_sha256'].items()
        if name.replace('\\','/').endswith('/station_weather_qemu.py'))
    assert sha(files['pilot/producer.py'])==original
    return {**result,'unsafe_controls_rejected':len(proof['rejected_controls'])}


def main():
    """Replay committed evidence with optional exact historical producer sources."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--source-revision',help='Read original producer bytes from Git without resetting')
    args=parser.parse_args();print(json.dumps(verify(args.proof,args.root,args.source_revision)))


if __name__=='__main__':main()
