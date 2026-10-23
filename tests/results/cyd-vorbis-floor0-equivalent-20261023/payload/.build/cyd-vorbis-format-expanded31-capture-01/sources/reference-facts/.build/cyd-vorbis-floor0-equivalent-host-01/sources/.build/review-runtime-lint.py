import hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
campaigns={};new={}
for board,relative in [('cyd','.build/lint-cyd-runtime-transfer-full'),('c3','.build/lint-c3-runtime-transfer-complete-01')]:
 path=ROOT/relative;report=json.loads((path/'report.json').read_text());manifest=json.loads((path/'source-manifest.json').read_text())
 build=ROOT/report['build_dir'];files=set()
 for entry in json.loads((build/'compile_commands.json').read_text()):
  source=Path(entry['file']);source=(source if source.is_absolute() else Path(entry['directory'])/source).resolve()
  if source.suffix.lower() not in ('.c','.cc','.cpp','.cxx') or not source.is_relative_to(ROOT):continue
  rel=source.relative_to(ROOT)
  overlay=source.parent==build/'native-httpd-rfc6455' and source.name in ('httpd_ws.c','httpd_parse.c')
  if not overlay and any(part.startswith(('build','.')) for part in rel.parts[:-1]):continue
  files.add(rel.as_posix())
 assert files=={row['file'] for row in report['results']},(board,files^{row['file'] for row in report['results']})
 for row in report['results']:
  assert hashlib.sha256((path/'sources'/row['file']).read_bytes()).hexdigest()==row['source_sha256']
 assert report['complete'] and report['errors']==0
 old=json.loads((ROOT/f'.build/lint-{board}-ota-transfer-full/report.json').read_text())
 def key(d):return d['file'].replace('\\','/').lower(),d['check'],d['message']
 previous=Counter(key(d) for row in old['results'] for d in row['diagnostics']);added=[]
 for row in report['results']:
  for diagnostic in row['diagnostics']:
   if previous[key(diagnostic)]:previous[key(diagnostic)]-=1
   else:added.append(dict(unit=row['file'],**diagnostic))
 new[board]=added
 campaigns[board]=dict(report=relative+'/report.json',source_manifest=relative+'/source-manifest.json',units=report['units'],warnings=report['warnings'],errors=report['errors'],all_current_compile_database_project_units_present=True,all_reported_source_snapshots_sha256_verified=True,header_build_snapshots=len(manifest['dependencies']),prior_units=old['units'],prior_warnings=old['warnings'],new_warning_instances=len(added))
report=dict(passed=True,campaigns=campaigns,new_warnings=new,triage=[
 dict(finding='C3 native_wifi_json.c:61 clang-analyzer-security.ArrayBound',classification='False positive with infeasible trace and independently checked guard invariant',evidence=['.build/lint-c3-runtime-transfer-full/idf__components__native_wifi_store__native_wifi_json.c.log','.build/native-wifi-json-lint-triage-01/report.json','.build/native-wifi-json-boundary-lint-01/report.json'],reason='hex4 produces at most 0xFFFF; saved trace takes >=0x10000 after skipping surrogate composition. Separately successful append guard implies used+size<capacity without size_t overflow, so NUL remains within action[5]. Existing actual grammar suite passes2445 groups,20000 malformed probes and4 mutants; exact-helper synthetic suite passes416784 ASan/UBSan checks. No source rewrite or suppression.'),
 dict(finding='CYD time_settings.c:48 increment in short-circuit OR',classification='Valid sequenced C operation; no reproduced defect',reason='Left operand at==end is fully evaluated before right operand *at++, and short circuit prevents dereference at end. Pointer is incremented only while strictly inside bounded name. Existing settings host qualification remains the behavioral evidence; no cosmetic rewrite.'),
 dict(finding='CYD time_settings.c:85 memcpy without NUL',classification='Binary record magic, intentional fixed4-byte field',reason='NTIM is an82-byte binary record; record[4] is version1, not a string terminator. No string consumer reads this field; comparisons use memcmp4.'),
 dict(finding='Boolean strcmp/strcasecmp/memcmp and calloc assignment',classification='Intentional boolean comparisons or checked allocation',reason='Nonzero comparison means unequal; equality inversion is explicit in validation. calloc assignment result is immediately tested and allocation failure sets NO_MEMORY before workspace use.'),
 dict(finding='Six custom FLAC narrowing warnings newly visible on CYD',classification='Same bounded shared implementation and six findings already analyzed in C3 baseline; not new behavior',reason='readUint at these call sites consumes2/4/5bits; Rice result is computed from uint32 folded value and lies in int32 range. Existing signed-field/Rice/bounds/PCM campaign retains distinct hashes and scope. No new conformance, runtime CYD or performance claim.')
],new_reproduced_high_risk_defects=0,remaining='Prior AAC private owner-view finding remains deferred; this delta review does not declare every baseline warning harmless. Full Clang AST analysis succeeded, but experimental CYD Clang20.1.1 optimized code generation crashed in time_settings_valid (v4i1 BUILD_VECTOR); GCC production compilation passed. This is not firmware execution or physical qualification.',source_proof='CYD completed original report provides exact unit hashes. C3 recovered61 saved exit0/log units, freshly completed2 missing units, and analyzed1 newly registered web_wifi unit. Original C3 attribution reconstructed using unchanged committed source modulo checkout CRLF, pre-analysis frozen upload candidate and mtimes; not claimed as complete original pre-analysis snapshot. Every reported unit now has verified exact frozen bytes. Header/build snapshots captured after analysis are labeled as such.',no_tracked_source_changes=True)
dest=ROOT/'.build/runtime-lint-review.json';assert not dest.exists();dest.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(campaigns,indent=2));print('No reproduced new high-risk defect; JSON security finding is an infeasible analyzer path')
