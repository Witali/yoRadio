import hashlib,json,shutil,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent; ROOT=BASE.parents[1]
backend=sys.argv[1]; d=BASE/'sdk'/backend; linked=Path(sys.argv[2])
load=lambda p:json.loads(Path(p).read_bytes())
def pin(p):
 b=Path(p).read_bytes(); return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
static=load(d/'static-qualification.json'); clang=load(d/'clang-status.json'); link=load(linked); headers=load(d/'lint-pbuf-system-inclusive.json')
assert static['passed']and clang['state']=='TERMINAL_PASS'and link['passed']
assert link['verifier']['sha256']=='d4e636beb193d9a52460f587300cc07cae4b93285e3b8b3a04cd7a7337dcd90b'
assert pin(BASE/'qualify-linked-pbuf.py')['sha256']==link['verifier']['sha256']
assert link['elf']['sha256']==static['elf']['sha256']
assert len(link['tcp_out_sites'])==4 and link['wrapper_real_call_dominates_exits_without_cycle']
calls={name for c in link['wrapper_calls']for name in c['target']['names']}
assert calls=={'pbuf_alloc','xPortEnterCriticalTimeout','vPortExitCritical'},'Unexpected reachable hot-path call'
assert headers['errors']==0
destination=d/'link-qualification.json'
if linked.resolve()!=destination.resolve():
 assert not destination.exists(); shutil.copyfile(linked,destination)
q=dict(**static,scope='Build/static/link/Clang qualification for diagnostic pbuf attribution only; no native runtime or physical acceptance.',
 pbuf_probe_enabled=True,rtc_probe_enabled=True,fixture=str((d/'fixture').relative_to(ROOT)).replace('\\','/'),
 baseline_binding=dict(source_commit='7595a79958b8a2ef56babb24c43259fcf536b6dd',snapshot=static['baseline_snapshot'],objects_zip=static['baseline_objects_zip']),
 project_clang=clang['results'],sdk_frontends=clang['sdk_frontends'],typed_compiler_config_delta=clang['typed_config_delta'],
 sdk_header_warnings=headers['warnings'],sdk_header_warning_scope=headers['scope'],
 link_verification=dict(report=pin(destination),verifier=link['verifier'],four_tcp_sites_wrapped=True,wrapper_real_once=True,
  wrapper_calls=sorted(calls),hot_heap_log_or_unexpected_helper_calls=False,same_object_clone_blind_spot=link['same_object_clone_blind_spot']))
assert not(d/'qualification.json').exists(); (d/'qualification.json').write_text(json.dumps(q,indent=2)+'\n')
print('FINAL SDK QUALIFIED',backend,q['image']['bytes'],'header warnings',headers['warnings'])
