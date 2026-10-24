"""Verify archived AP peer/HTTP traces and target-compiled event ABI offline."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile
from network_clients_contract import validate, rejection_checks, verify_abi
from verify_photo_format_matrix_evidence import source_hashes


def sha(data):
    """Use content identity for every archived observation and producer."""
    return hashlib.sha256(data).hexdigest()


def code_reader(path, digest):
    """Resolve captured guest instructions and event-base pointers in the exact ELF."""
    data = path.read_bytes(); assert sha(data) == digest
    elf = ELFFile(io.BytesIO(data))
    segments = [(s['p_vaddr'], s.data()) for s in elf.iter_segments()
                if s['p_type'] == 'PT_LOAD' and s['p_filesz']]
    table = elf.get_section_by_name('.symtab')
    symbols = list(table.iter_symbols()) if table else []
    def read(address, size):
        matches = [data[address-start:address-start+size] for start, data in segments
                   if start <= address <= start+len(data)-size]
        assert matches and all(value == matches[0] for value in matches)
        return matches[0]
    read.symbols = symbols
    return read


def verify(path, root, dependencies, revision=None):
    """Reject missing peers, failed requests, invalid handles or broadened scope."""
    proof = json.loads(path.read_text())
    assert proof['schema_version'] == 1 and proof['passed']
    assert not any(proof[key] for key in ('network_lifecycle_complete',
        'all_functionality_verified','lcd_acceptance','rf_acceptance','physical_hardware_tested'))
    blobs = {}
    for row in proof['blobs']:
        file = (path.parent/row['file']).resolve()
        assert file.is_relative_to(path.parent.resolve())
        data = file.read_bytes(); assert sha(data) == row['gzip_sha256']
        raw = gzip.decompress(data)
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
        assert row['sha256'] not in blobs; blobs[row['sha256']] = raw
    files = {}
    for row in proof['raw']:
        assert row['source'] not in files; files[row['source']] = blobs[row['sha256']]
    abi = json.loads(files['abi/layout.json'])
    verify_abi(abi, files['abi/wire.o'], files['abi/wire.c'])
    assert abi['app_sha256'] == proof['app_sha256']
    assert abi['elf_sha256'] == proof['native_elf_sha256']
    assert source_hashes(root,proof['source_pins'],revision) == proof['source_pins']
    for name,digest in proof['source_pins'].items():
        assert sha(files['producer/'+name]) == digest
    abi_script = next(digest for name,digest in abi['inputs_sha256'].items()
                      if name.replace('\\','/').endswith('/tests/network_event_abi.py'))
    assert abi_script == proof['source_pins']['Small_TV/src/tests/network_event_abi.py']
    readers = {
        'reconstructed': code_reader(root/'.build/small-tv-esp32c2/small_tv_reconstructed.elf',proof['native_elf_sha256']),
        'original': code_reader(dependencies/'.build/small-tv-reverse/factory-analysis.elf',proof['factory_elf_sha256']),
    }
    results = []; coverage = set()
    for run in proof['runs']:
        report = json.loads(files[run['source']]); flavor = report['firmware']
        assert (report['qemu_sha256'], flavor) not in coverage
        coverage.add((report['qemu_sha256'], flavor))
        assert report['qemu_sha256'] in proof['qemu_sources']
        assert report['elf_sha256'] == proof[('factory' if flavor == 'original' else 'native')+'_elf_sha256']
        assert report['native_app_sha256'] == proof['app_sha256']
        read = readers[flavor]
        if flavor == 'original':
            assert report['entries'] == dict(wifi_event=0x4200c6e2,
                httpd_start=0x4200c5ec,httpd_stop=0x4200c578)
            assert report['event_base_object'] == 0x3c0f1eb8
        else:
            for name,address in {**report['entries'],'WIFI_EVENT':report['event_base_object']}.items():
                assert {s['st_value'] for s in read.symbols if s.name == name and s['st_value']} == {address}
        base = int.from_bytes(read(report['event_base_object'],4),'little')
        results.append(validate(report,abi['wire'],read,base))
        assert rejection_checks(report,abi['wire'],read,base) == run['rejected_controls']
        for name,digest in report['inputs_sha256'].items():
            if '/Small_TV/src/tests/' in name.replace('\\','/'):
                relative = 'Small_TV/src/tests/'+name.replace('\\','/').rsplit('/',1)[1]
                assert proof['source_pins'][relative] == digest
        qemu = proof['qemu_sources'][report['qemu_sha256']]
        for relative,row in qemu['files'].items():
            source = files[row['source']]
            assert sha(source) == row['sha256']
            assert hashlib.sha1(b'blob '+str(len(source)).encode()+b'\0'+source).hexdigest() == row['git_blob']
    assert len(coverage) == 4 and len(proof['qemu_sources']) == 2
    return dict(passed=True,runs=results,unsafe_controls_rejected=24,
                network_lifecycle_complete=False,rf_acceptance=False)


def main():
    """Recheck committed evidence without launching a VM or changing its state."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--source-revision',help='Read historical producer pins from Git without resetting files')
    args = parser.parse_args()
    print(json.dumps(verify(args.proof,args.root,args.dependency_root,args.source_revision)))


if __name__ == '__main__': main()
