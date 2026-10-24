"""Replay an actual bridge failure, its correction and combined protocol losses."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

from network_clients_contract import verify_abi,validate as peers_validate
from network_loss_contract import validate as loss_validate,rejection_checks as loss_rejections
from network_stalled_peer_contract import validate,rejection_checks
from verify_network_clients_evidence import code_reader
from verify_photo_format_matrix_evidence import source_hashes


def sha(data):
    """Identify archived observations and source snapshots by their actual bytes."""
    return hashlib.sha256(data).hexdigest()


def verify(path,root,dependencies,revision=None):
    """Require both stalled peers before/after and all seven losses on either peer."""
    proof=json.loads(path.read_text());assert proof['schema_version']==1 and proof['passed']
    assert not any(proof[k] for k in ('network_lifecycle_complete','all_functionality_verified',
        'lcd_acceptance','rf_acceptance','hardware_tested'))
    blobs={}
    for row in proof['blobs']:
        file=(path.parent/row['file']).resolve();assert file.is_relative_to(path.parent.resolve())
        data=file.read_bytes();assert sha(data)==row['gzip_sha256']
        data=gzip.decompress(data);assert len(data)==row['bytes'] and sha(data)==row['sha256']
        assert row['sha256'] not in blobs;blobs[row['sha256']]=data
    files={}
    for row in proof['raw']:
        assert row['source'] not in files;files[row['source']]=blobs[row['sha256']]
    assert source_hashes(root,proof['source_pins'],revision)==proof['source_pins']
    for name,digest in proof['source_pins'].items():assert sha(files['producer/'+name])==digest
    abi=json.loads(files['abi/layout.json']);verify_abi(abi,files['abi/wire.o'],files['abi/wire.c'])
    assert abi['app_sha256']==proof['app_sha256'] and abi['elf_sha256']==proof['elf_sha256']
    read=code_reader(root/'.build/small-tv-esp32c2/small_tv_reconstructed.elf',proof['elf_sha256'])
    coverage=set();combined=set();controls=0
    for run in proof['runs']:
        report=json.loads(files[run['source']]);kind=run['kind'];peer=report['peer']
        assert report['app_sha256']==proof['app_sha256'] and report['elf_sha256']==proof['elf_sha256']
        assert report['qemu_sha256']==proof['builds'][run['build']]['sha256']
        assert report['wire']==abi['wire']
        for name,address in {**report['entries'],'WIFI_EVENT':report['event_base_object']}.items():
            assert {s['st_value'] for s in read.symbols if s.name==name and s['st_value']}=={address}
        if kind=='stalled':
            key=run['build'],peer;assert key not in coverage;coverage.add(key)
            before_failure=key==('before',0)
            result=validate(report,read,before_failure)
            rejected=rejection_checks(report,read,before_failure)
        else:
            assert kind=='combined' and run['build']=='after' and report['stage']=='all'
            assert peer not in combined;combined.add(peer)
            result=loss_validate(report,read);rejected=loss_rejections(report,read)
        assert result==run['result'] and rejected==run['rejected_controls'];controls+=len(rejected)
        for name,digest in report['inputs_sha256'].items():
            name=name.replace('\\','/')
            if '/Small_TV/src/tests/' in name:
                assert proof['source_pins']['Small_TV/src/tests/'+name.rsplit('/',1)[1]]==digest
            elif name.endswith('/layout.json'):assert sha(files['abi/layout.json'])==digest
    assert coverage=={(build,peer) for build in ('before','after') for peer in (0,1)}
    assert combined=={0,1}
    for build in proof['builds'].values():
        for row in build['files'].values():
            data=files[row['source']];assert sha(data)==row['sha256']
            assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob']
    factory=json.loads(files['factory/report.json'])
    assert factory['native_app_sha256']==proof['app_sha256']
    assert factory['qemu_sha256']==proof['builds']['after']['sha256']
    assert factory['elf_sha256']==proof['factory_elf_sha256']
    assert factory['entries']==dict(wifi_event=0x4200c6e2,httpd_start=0x4200c5ec,httpd_stop=0x4200c578)
    assert factory['event_base_object']==0x3c0f1eb8
    factory_read=code_reader(dependencies/'.build/small-tv-reverse/factory-analysis.elf',proof['factory_elf_sha256'])
    peers_validate(factory,abi['wire'],factory_read,int.from_bytes(factory_read(factory['event_base_object'],4),'little'))
    legacy=json.loads(files['c3/report.json']);assert set(legacy)=={'default','modular'}
    for row in legacy.values():
        assert row['passed'] and all(row['checks'].values()) and row['duration_seconds']==60
        assert row['qemu_sha256']==proof['builds']['after']['sha256']
    return dict(passed=True,actual_before_failure=1,before_healthy_control=1,
        corrected_stalled_peers=2,combined_loss_peers=2,unsafe_controls_rejected=controls,
        network_lifecycle_complete=False)


def main():
    """Check committed observations against exact ELF and producer bytes offline."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--source-revision',help='Read historical producer bytes without resetting')
    args=parser.parse_args();print(json.dumps(verify(args.proof,args.root,args.dependency_root,args.source_revision)))


if __name__=='__main__':main()
