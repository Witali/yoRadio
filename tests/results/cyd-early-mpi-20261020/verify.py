"""Offline integrity/selected-entry check. Reads only this archive."""
from pathlib import Path
import gzip
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parent
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def read_json(name):return json.loads((ROOT/name).read_bytes())
def require(value,message):
    if not value:raise ValueError(message)

manifest=read_json('manifest.json')
expected={row['path']:row for row in manifest['files']}
actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'manifest.json'}
require(len(expected)==len(manifest['files']) and set(expected)==actual,'Complete root manifest file set')
for name,row in expected.items():
    path=(ROOT/name).resolve()
    require(path.is_relative_to(ROOT),'Manifest path escapes archive')
    raw=path.read_bytes()
    require(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'Manifest bytes: '+name)

mapping=read_json('path-map.json')['entries']
by_id={row['id']:row for row in mapping}
require(len(by_id)==len(mapping),'Unique mapping IDs')
decoded={}
for row in mapping:
    require(re.fullmatch('[0-9a-f]{64}',row['sha256']) and isinstance(row['bytes'],int) and row['bytes']>=0,'Mapping identity')
    require(row['original_path'] and row['read_from'] and row['roles'],'Mapping provenance')
    if row['disposition']=='omitted':
        require(bool(row.get('reason')) and 'stored_path' not in row,'Explicit omission')
        continue
    require(row['disposition']=='stored','Mapping disposition')
    name=row['stored_path']
    require(name in expected,'Stored payload present in manifest')
    if row['sha256'] not in decoded:
        stored=(ROOT/name).read_bytes()
        require(len(stored)==row['stored_bytes'] and sha(stored)==row['stored_sha256'],'Encoded payload identity')
        require(row['encoding'] in ('raw','gzip'),'Payload encoding')
        raw=gzip.decompress(stored) if row['encoding']=='gzip' else stored
        require(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'Decoded payload identity')
        require(not raw.startswith((b'\x7fELF',b'MZ',b'!<arch>\n')),'Executable/archive payload must be omitted')
        decoded[row['sha256']]=raw
    else:
        require(len(decoded[row['sha256']])==row['bytes'],'Shared payload size')

def document(row):
    require(row['disposition']=='stored','JSON document omitted')
    return json.loads(decoded[row['sha256']])
bound=read_json('bindings.json')['bindings']
for b in bound:
    value=document(by_id[b['container_id']])
    for token in b['hash_tokens']:value=value[token]
    require(value==by_id[b['target_id']]['sha256'],'Original report/source hash binding')

index=read_json('index.json')
reports={name:document(by_id[number]) for name,number in index['primary_report_ids'].items()}
require(reports['host-02']['passed'] and reports['host-02']['all_bound_inputs_current'],'Authoritative host')
require(reports['qemu-01']['passed'] and reports['qemu-01']['all_bound_inputs_current'],'Authoritative target')
require(reports['qualification-01']['passed'] and reports['preflight-02']['passed'],'Aggregate and preflight')
require(len(reports['preflight-02']['cases'])==9,'Nine preflight controls')
require(reports['review-01']['findings'] and reports['review-02']['finding_closed'] and not reports['review-02']['findings'],'Historical finding and closure')
require(not reports['wrong-sdk-pin-02']['passed'] and not reports['wrong-sdk-pin-02']['variants'],'Expected pin rejection')
require('Unsupported SDK commit:' in reports['wrong-sdk-pin-02']['error'],'Exact pin rejection reason')
require('Historical ordering only' in index['host01_scope'],'Host01 superseded scope')
require(index['status']=={'canonical_source_integrated':True,'default_enabled':False,'host_pass':True,'isolated_target_pass':True,
    'production_exports':'pending','actual_radio_pre_app_lock_state':'pending','physical_benefit':'unproven'},'Exact qualification limits')
q=reports['qemu-01']
require(q['sdk_commit']=='7101770dc6db2667b3c477cc31365dd1acd6db4e','SDK pin')
require(set(q['variants'])=={'canonical','skip-acquire','skip-release','void-oom'} and all(v['passed'] for v in q['variants'].values()),'Four exact target variants')
def mapped_log(suffix):
    values=[r for r in mapping if r['original_path'].replace('\\','/').endswith('/cyd-early-mpi-qemu-01/'+suffix)]
    require(len(values)==1,'Unique final target log: '+suffix)
    return decoded[values[0]['sha256']].decode(errors='replace').replace('\r\n','\n')
log=mapped_log('canonical-qemu.log')
require(log.count('EARLY_MPI_COMPLETE warm_pairs=17 dualcore=1 increments=2000 public_api=1 crypto_calculations=0')==1,'Canonical completion')
require('classification=lazy_at_fixture' in log,'Fixture-only lazy observation')
for name,marker in [('skip-acquire','warm_acquire_once'),('skip-release','warm_release_once')]:
    log=mapped_log(name+'-qemu.log')
    require(re.findall(r'^EARLY_MPI_FAILURE (.+)$',log,re.M)==[marker] and log.count('EARLY_MPI_CONTROLLED_STOP')==1,'Exact semantic control')
log=mapped_log('void-oom-qemu.log')
require(len(re.findall(r'^EARLY_MPI_OOM_QUEUE_NULL phase=1 lock=0x[0-9a-f]+$',log,re.M))==1,'Actual null constructor marker')
stack=mapped_log('void-oom-whole-backtrace.log')
for symbol in ['lock_init_generic','lock_acquire_generic','__wrap__lock_acquire','esp_crypto_mpi_lock_acquire','native_tls_early_mpi_prepare','app_main']:
    require(symbol in stack,'Exact OOM stack: '+symbol)
require(read_json('current-verification.json')['all_read_inputs_unchanged_after'],'Archival current-input check')
print(json.dumps({'passed':True,'manifest_files':len(expected),'mapped_versions':len(mapping),
    'decoded_payloads':len(decoded),'json_hash_bindings':len(bound),'offline_only':True},indent=2))
