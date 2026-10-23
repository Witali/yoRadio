"""Fetch one pinned public source archive; never execute its contents."""
from pathlib import Path, PurePosixPath
import hashlib
import io
import json
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '.build/cyd-vorbis-public-tremor-source-01'
URL = ('https://android.googlesource.com/platform/external/tremor/+archive/'
       '0ad0141e864cfbb130db4f22e279d421832e7336/Tremor.tar.gz')


def main():
    assert not OUT.exists(), 'Fresh source destination required'
    with urllib.request.urlopen(URL, timeout=45) as response:
        assert response.status == 200
        data = response.read(4 * 1024 * 1024 + 1)
        assert 0 < len(data) <= 4 * 1024 * 1024
        transport = dict(request_url=URL, final_url=response.geturl(),
                         status=response.status, headers=dict(response.headers))
    members = []
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        for item in archive.getmembers():
            name = PurePosixPath(item.name)
            assert not name.is_absolute() and '..' not in name.parts
            assert item.isdir() or item.isfile(), 'Only regular public source files/directories'
            if item.isfile():
                assert item.size <= 1024 * 1024
                raw = archive.extractfile(item).read()
                assert len(raw) == item.size
                members.append((name.as_posix(), raw))
    assert len({name for name, _ in members}) == len(members)
    assert {'floor0.c', 'codebook.c', 'lsp_lookup.h', 'COPYING'} <= {name for name, _ in members}
    OUT.mkdir()
    (OUT / 'Tremor.tar.gz').write_bytes(data)
    rows = []
    for name, raw in members:
        dest = (OUT / 'source' / name).resolve()
        assert dest.is_relative_to((OUT / 'source').resolve())
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open('xb') as stream:
            stream.write(raw)
        rows.append(dict(path='source/' + name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
    record = dict(schema='pinned-public-tremor-source-download-v1', transport=transport,
                  revision='0ad0141e864cfbb130db4f22e279d421832e7336',
                  archive=dict(path='Tremor.tar.gz', bytes=len(data), sha256=hashlib.sha256(data).hexdigest()),
                  files=rows, source_contents_executed=False, decoder_executed=False)
    (OUT / 'SOURCE.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(source_files=len(rows), archive_bytes=len(data),
                         archive_sha256=record['archive']['sha256'], contents_executed=False)))


if __name__ == '__main__':
    main()
