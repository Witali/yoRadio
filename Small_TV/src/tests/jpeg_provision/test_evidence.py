"""Negative controls for archived full-image/bootstrap verification."""
import argparse
import copy
import gzip
import json
from pathlib import Path
import tempfile

from verify_evidence import sha, verify


def main():
    """Refuse damaged archives and even consistently rehashed protected writes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[4])
    args = parser.parse_args()
    args.proof = args.proof.resolve()
    assert verify(args.proof, args.root)['passed']
    original = json.loads(args.proof.read_text(encoding='utf-8'))
    passed = []
    with tempfile.TemporaryDirectory(prefix='negative-evidence-', dir=args.proof.parent) as folder:
        temporary = Path(folder)
        # The temporary proof lives beside the original so its existing relative
        # blob references stay valid. Only this explicitly created file is removed.
        with tempfile.NamedTemporaryFile(prefix='negative-evidence-', suffix='.json',
                                         dir=args.proof.parent, delete=False) as stream:
            probe = Path(stream.name)
        try:
            for name in ('gzip-digest', 'image-digest', 'duplicate-process',
                         'sector-order', 'source-digest', 'rehashed-protected-write'):
                proof = copy.deepcopy(original)
                if name == 'gzip-digest':
                    proof['blobs'][0]['gzip_sha256'] = '0'*64
                elif name == 'image-digest':
                    proof['images'][0]['sha256'] = '0'*64
                elif name == 'duplicate-process':
                    proof['qemu']['cases'][-1] = proof['qemu']['cases'][0]
                elif name == 'sector-order':
                    row = next(x for x in proof['images'] if len(x['sectors']) > 1)
                    row['sectors'].reverse()
                elif name == 'source-digest':
                    proof['source_pins'][next(iter(proof['source_pins']))] = '0'*64
                else:
                    def payload(digest):
                        row = next(x for x in proof['blobs'] if x['sha256'] == digest)
                        return gzip.decompress((args.proof.parent/row['file']).read_bytes())

                    def add(data):
                        digest = sha(data)
                        if not any(x['sha256'] == digest for x in proof['blobs']):
                            encoded = gzip.compress(data, mtime=0)
                            path = temporary/(digest+'.gz');path.write_bytes(encoded)
                            proof['blobs'].append(dict(file=path.relative_to(args.proof.parent).as_posix(),
                                sha256=digest, bytes=len(data), gzip_sha256=sha(encoded)))
                        return digest

                    row = next(x for x in proof['images'] if x['source'].endswith('/erased/after-0.bin'))
                    data = bytearray(payload(proof['flash_base_sha256']))
                    for change in row['sectors']:
                        data[change['offset']:change['offset']+4096] = payload(change['sha256'])
                    # Model a forbidden photo write and update every affected
                    # checksum/report consistently. Only preservation can reject it.
                    data[0x200000] ^= 1
                    row['sectors'] = [x for x in row['sectors'] if x['offset'] != 0x200000]
                    row['sectors'].append(dict(offset=0x200000, sha256=add(bytes(data[0x200000:0x201000]))))
                    row['sectors'].sort(key=lambda x:x['offset'])
                    row['sha256'] = sha(data)
                    target = next(x for x in proof['qemu']['cases'] if x['case'] == 'erased' and x['boot'] == 0)
                    target['after_sha256'] = row['sha256']
                    raw = next(x for x in proof['raw'] if x['source'] == proof['qemu_report_source'])
                    raw['sha256'] = add(json.dumps(proof['qemu']).encode())
                probe.write_text(json.dumps(proof), encoding='utf-8')
                try:
                    verify(probe, args.root)
                except AssertionError:
                    passed.append(name)
                else:
                    raise AssertionError('Unsafe evidence accepted: '+name)
        finally:
            probe.unlink()
    print(json.dumps(dict(passed=True, rejected=passed)))


if __name__ == '__main__':
    main()
