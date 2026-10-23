"""Read-only verification of every preserved wire map and foundation reference.

Checks top-level manifest bytes and nested application/SDK/overlay/composed/TLS
maps against explicit preserved paths. Crypto archives are executable cache
inputs excluded from the archive; their hashes are checked separately and
reported as external rather than being presented as preserved source files.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'tests/results/native-runtime-transfer-20261018'
COUNTS=Counter()
CHECKS=[]

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):return json.loads(path.read_text())
def rel(value):
    path=Path(value.replace('\\','/'))
    assert not path.is_absolute() and '..' not in path.parts,value
    return path
def check(path,expected,kind):
    assert path.is_file(),('missing',str(path))
    actual=digest(path)
    assert actual==expected,('hash mismatch',str(path),expected,actual)
    COUNTS[kind]+=1
    CHECKS.append({'file':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':expected,'kind':kind})
def mapping(base,entries,kind):
    assert isinstance(entries,dict)
    for key,value in entries.items():
        assert isinstance(value,str) and len(value)==64,(key,value)
        check(base/rel(key),value,kind)
def overlay(base,value):
    mapping(base/'sdk-sources/components/esp_http_server/src',value['sdk_source_sha256'],'overlay_sdk_source')
    mapping(base/'sdk-sources/components/esp_http_server',value['sdk_header_sha256'],'overlay_sdk_header')
    mapping(base/'generated',value['generated_sha256'],'overlay_generated')
def crypto(target,expected):
    cache=ROOT/'.build'/('native-tls-crypto-v602' if target=='cyd' else 'native-tls-crypto-v611')
    check(cache/'libpinned-mbedtls.a',expected,'external_crypto_archive')

names=['time-wire-cyd','wifi-wire-c3','wifi-wire-cyd-http','wifi-wire-cyd-tls']
manifest=load(ARCHIVE/'archive-manifest.json')
for relative,expected in manifest['files'].items():
    if rel(relative).parts[0] in names:check(ARCHIVE/rel(relative),expected,'archive_manifest')
for name in names:
    base=ARCHIVE/name;report=load(base/'report.json');assert report['passed']
    mapping(base/'sources',report['source_sha256'],'application_source')
    check(base/'report.json',manifest[name]['reports']['report.json'],'primary_report')
    if name=='time-wire-cyd':
        mapping(base/'composed/sdk-sources',report['sdk_sha256'],'sdk_source')
        mapping(base/'composed',report['generated_sha256'],'generated')
        mapping(base/'composed/crypto-config',report['crypto_config_sha256'],'crypto_config')
        mapping(base/'tls-foundation-sources',report['tls_source_sha256'],'tls_source')
        overlay(base/'composed',report['sdk_overlay'])
        for field,filename in [('httpd_foundation_report_sha256','httpd-foundation-report.json'),('tls_foundation_report_sha256','tls-foundation-report.json')]:
            check(base/filename,report[field],'foundation_report')
        foundation=load(base/'tls-foundation-report.json')
        assert foundation['source_sha256']==report['tls_source_sha256']
        crypto('cyd',report['crypto_archive_sha256'])
        identity=load(base/'crypto-identity.json')
        assert identity['fingerprint']==foundation['crypto_fingerprint']
    else:
        for key,value in report['input_report_sha256'].items():check(base/'foundation-reports'/(key+'.json'),value,'foundation_report')
        wifi=load(base/'foundation-reports/wifi.json');ws=load(base/'foundation-reports/ws.json')
        assert wifi['passed'] and ws['passed']
        mapping(base/'ws-sources',ws['source_sha256'],'ws_foundation_source')
        for variant,value in report['variants'].items():
            assert value['passed'];part=base/variant;target=variant.split('-')[0]
            assert value['wifi_source_sha256']==wifi['source_sha256']
            assert value['sdk_sha256']==ws['variants'][target]['sdk_sha256']
            assert value['sdk_overlay']==ws['variants'][target]['overlay']
            mapping(base/'wifi-sources',value['wifi_source_sha256'],'wifi_source')
            mapping(part/'sdk-sources',value['sdk_sha256'],'sdk_source')
            mapping(part,value['composed_sha256'],'composed')
            check(part/'model.h',value['generated_model_sha256'],'generated_model')
            overlay(part,value['sdk_overlay'])
            if 'tls_source_sha256' in value:
                mapping(part/'tls-sources',value['tls_source_sha256'],'tls_source')
                check(part/'tls-foundation-report.json',value['tls_report_sha256'],'foundation_report')
                foundation=load(part/'tls-foundation-report.json')
                assert foundation['passed'] and foundation['source_sha256']==value['tls_source_sha256']
                crypto(target,value['crypto_archive_sha256'])
for name in names:
    for path in (ARCHIVE/name).rglob('*'):
        if not path.is_file():continue
        assert path.suffix.lower() not in {'.pem','.key','.crt','.ntls','.csv','.bin'},path
        content=path.read_bytes()
        # Code can contain the literal PEM label as a parser/test constant;
        # an actual PEM object has a newline after its BEGIN label.
        assert b'-----BEGIN PRIVATE KEY-----\n' not in content,path
        assert b'-----BEGIN RSA PRIVATE KEY-----\n' not in content,path
pending=[str(p.relative_to(ARCHIVE)).replace('\\','/') for name in names for p in (ARCHIVE/name).rglob('*') if p.is_file() and str(p.relative_to(ARCHIVE)).replace('\\','/') not in manifest['files']]
result={'passed':True,'counts':dict(COUNTS),'archive_manifest_sha256':digest(ARCHIVE/'archive-manifest.json'),
        'supplemental_files_pending_manifest_registration':pending,'checks':CHECKS,
        'scope':'Read-only file integrity, no protocol test rerun; external crypto archives checked distinctly from preserved text sources.'}
(ROOT/'.build/native-runtime-wire-nested-integrity.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS nested wire integrity:',json.dumps(dict(COUNTS),sort_keys=True))
print('Pending archive manifest registration:',len(pending))
