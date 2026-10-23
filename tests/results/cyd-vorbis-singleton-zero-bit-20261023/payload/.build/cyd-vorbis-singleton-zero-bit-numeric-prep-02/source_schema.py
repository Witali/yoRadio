"""Exact zero8 source file facts; no alternate corpus schemas or fallback hashes."""
import re

from pcm_metrics import need

FILE_KINDS = ('identification', 'comment', 'setup', 'audio', 'ogg')
RAW_KINDS = FILE_KINDS[:-1]


def source_file_fact(source, kind):
    need(type(source) is dict and type(kind) is str and kind in FILE_KINDS,
         'Exact zero8 source case and declared file kind required')
    files, raw_hashes = source.get('files'), source.get('raw_sha256')
    need(type(files) is dict and set(files) == set(FILE_KINDS) and
         type(raw_hashes) is dict and set(raw_hashes) == set(RAW_KINDS),
         'Zero8 requires five file facts and exactly four raw hash identities')
    for name in FILE_KINDS:
        fact = files[name]
        need(type(fact) is dict and set(fact) == {'bytes', 'sha256'} and
             type(fact['bytes']) is int and fact['bytes'] > 0 and
             type(fact['sha256']) is str and re.fullmatch('[0-9a-f]{64}', fact['sha256']),
             'Exact positive byte count and lowercase SHA256 file fact required')
        if name in RAW_KINDS:
            need(raw_hashes[name] == fact['sha256'], 'File fact and raw SHA256 identity must agree')
    return dict(files[kind])
