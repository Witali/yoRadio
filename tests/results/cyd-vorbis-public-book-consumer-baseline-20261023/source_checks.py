"""Source-only AST/raw hashes/JSON metadata and selected-path preflight; no proposed imports."""
import ast
import builtins
import difflib
import hashlib
import json
from pathlib import Path
import symtable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def need(ok, reason):
    if not ok: raise AssertionError(reason)


def indexed(value):
    return value['files'] if isinstance(value['files'], dict) else {row['path']:row for row in value['files']}


def main():
    output, ready = HERE/'source-checks.json', HERE/'readiness.json'
    need(not output.exists() and not ready.exists(), 'Immutable source-only closure')
    trees = {p.relative_to(HERE).as_posix():ast.parse(p.read_bytes(),filename=str(p)) for p in HERE.rglob('*.py') if p.is_file()}
    origins = json.loads((HERE/'source-origins.json').read_bytes());need(len(origins['inputs'])==7,'Exact seven source origins')
    for row in origins['inputs']:
        old,new=Path(row['source']),HERE/row['snapshot'];need(old.stat().st_size==new.stat().st_size==row['bytes'] and sha(old)==sha(new)==row['sha256'],'Exact retained source origin')
    def definition(tree,name):return next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    for name in ('need','windows_args','dependency_rows'):
        need(ast.dump(definition(trees['compile_context.py'],name),include_attributes=False)==ast.dump(definition(trees['provenance/base-compile_context_base.py'],name),include_attributes=False),'Exact pure compiler metadata helper AST')
    for name in ('pack.py','verify.py','compile_context.py'):
        table=symtable.symtable((HERE/name).read_text(),name,'exec');bound={s.get_name() for s in table.get_symbols() if s.is_assigned() or s.is_imported() or s.is_namespace()}
        allowed=bound|set(dir(builtins))|{'__file__','__name__','__doc__'}
        def scan(block):
            missing={s.get_name() for s in block.get_symbols() if s.is_referenced() and s.is_global() and s.get_name() not in allowed};need(not missing,(name,missing))
            for child in block.get_children():scan(child)
        scan(table)
    plan=json.loads((HERE/'plan.template.json').read_bytes());selected=[];preparations={};metadata={}
    def exists(path,kind):
        p=Path(path).resolve();need(p.is_relative_to(ROOT) and (p.is_dir() if kind=='directory' else p.is_file()),'Missing or outside selected path: '+str(p));selected.append(dict(path=str(p),kind=kind));return p
    for row in plan['preparations']:
        root=exists(row['path'],'directory');index=exists(root/row['index'],'file');need(sha(index)==row['index_sha256'],'Pinned preparation index')
        value=json.loads(index.read_bytes());entries=indexed(value);names={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        need(names==set(entries)|{row['index']},'Complete separate preparation inventory')
        for name,fact in entries.items():
            q=exists(root/name,'file');need(q.stat().st_size==fact['bytes'] and sha(q)==fact['sha256'],'Every unchanged source/raw fixture/preparation byte')
        preparations[row['name']]=dict(root=root,index=value,physical_files=len(names))
    need({k:v['physical_files'] for k,v in preparations.items()}=={'source':159,'runtime':19,'controller':199,'proposal-only':5},'Actual18-indexed runtime distinction')
    reports={};terminals={};schema_projections=0
    def fields(value,names,kind):
        nonlocal schema_projections
        for name in names:need(name in value,'Missing consumed '+kind+' JSON field: '+name);schema_projections+=1
    for row in plan['roles']:
        root=exists(row['path'],'directory');q=exists(root/'report.json','file');need(sha(q)==row['report_sha256'],'Actual role report pin');report=json.loads(q.read_bytes());reports[row['role']]=report
        q=exists(row['terminal_path'],'file');need(sha(q)==row['terminal_sha256'],'Actual outer receipt pin');terminal=json.loads(q.read_bytes());terminals[row['role']]=terminal
        for path,fact in terminal.get('logs',{}).items():need(exists(path,'file').stat().st_size==fact['bytes'],'Actual outer log entry size')
        for command in report['commands']:
            if row['role']=='host':
                fields(command,('name','argv','cwd','terminal','timed_out','interrupted','returncode','stdout','stderr','elapsed_seconds'),'host child')
                for stream in ('stdout','stderr'):
                    fact=command[stream];fields(fact,('path','bytes','sha256'),'host stream');need(exists(root/fact['path'],'file').stat().st_size==fact['bytes'],'Every732 host log exists/size')
            else:
                fields(command,('name','argv','cwd','state','exit_status','timed_out','interrupted','force_stopped','pid'),'SDK command')
                if command['name']!='qemu':
                    fields(command,('stdout_sha256','stderr_sha256'),'SDK ordinary command')
                    for stream in ('stdout','stderr'):exists(root/(command['name']+'.'+stream+'.log'),'file')
                else:
                    for stream in ('qemu.serial.log','qemu.stderr.log','qemu.qmp.stdout.log','qemu.qmp.requests.jsonl'):
                        fields(command[stream],('bytes','sha256'),'QMP stream');need(exists(root/stream,'file').stat().st_size==command[stream]['bytes'],'Actual QMP stream size')
        if row['role']=='SDK':
            for origin,fact in report['inputs'].items():
                fields(fact,('bytes','sha256','snapshot'),'SDK frozen input');q=exists(root/fact['snapshot'],'file');need(q.stat().st_size==fact['bytes'],'Every declared SDK snapshot entry size')
            for name in report['build_outputs']:exists(root/name,'file')
            for name in ('build/compile_commands.json','build/project_description.json','build/cyd_vorbis_owned_book_unit.map','build/flasher_args.json','configure-compiler-environment.json','build-compiler-environment.json','sdk-configure-process.json','sdk-build-process.json'):
                q=exists(root/name,'file')
                if q.suffix=='.json':metadata[name]=json.loads(q.read_text(encoding='utf-8-sig'))
        else:exists(root/'consumer-baseline','file')
    for row in plan['extra_receipts']:
        q=exists(row['path'],'file');need(sha(q)==row['sha256'],'Extra actual receipt pin');value=json.loads(q.read_bytes())
        for path,fact in value.get('logs',{}).items():need(exists(path,'file').stat().st_size==fact['bytes'],'Extra receipt stream size')
    for row in plan['extra_files']+plan['record_only']+[plan['checkpoint']]:need(sha(exists(row['path'],'file'))==row['sha256'],'Pinned actual factual/record-only note')
    need(plan['checkpoint']['sha256']=='475f4aa9281585e8d2cc1b2588dceb04caf4af1a5951d8d280644317ef105577','Original immutable checkpoint')
    need(any(r['sha256']=='40cc70076360fc54df72172dc2db7e0f0e5c9042a68f67d45580d6e85be16a6a' for r in plan['record_only']),'Separate deferred-step note')
    runtime=preparations['runtime']['root'];source=preparations['source']['root'];contract=json.loads((runtime/'contract.json').read_bytes());model=contract['model'];sdk=reports['SDK'];host=reports['host']
    qmp=next(r for r in sdk['commands'] if r['name']=='qemu');summary=json.loads(Path(plan['extra_files'][0]['path']).read_bytes())
    proposal=json.loads((preparations['proposal-only']['root']/'readiness.json').read_bytes());analysis=json.loads((preparations['proposal-only']['root']/'source-analysis.json').read_bytes())
    bindings={'r':[sdk],'host':[host],'context':[sdk['compile_context']],'desc':[metadata['build/project_description.json']],'q':[qmp],'recipe':[metadata['build/flasher_args.json']],
        'summary':[summary],'proposal':[proposal],'analysis':[analysis],'contract':[contract],'model':[model],'compile_row':[host['commands'][0]],'terminal':[terminals['SDK']],
        'case':model['cases'],'b':[c['book'] for c in model['cases']],'probe':[p for c in model['cases'] for p in c['book']['probes']],
        'record':host['records'],'comparison':[r['comparison'] for r in host['records'] if r['comparison'] is not None]}
    parents={child:node for node in ast.walk(trees['verify.py']) for child in ast.iter_child_nodes(node)}
    def shadowed(node,alias):
        while node in parents:
            node=parents[node]
            if isinstance(node,(ast.ListComp,ast.SetComp,ast.DictComp,ast.GeneratorExp)) and any(
                isinstance(name,ast.Name) and name.id==alias for generator in node.generators for name in ast.walk(generator.target)):
                return True
        return False
    for alias,values in bindings.items():
        used={n.slice.value for n in ast.walk(trees['verify.py']) if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Name) and n.value.id==alias and isinstance(n.slice,ast.Constant) and isinstance(n.slice.value,str) and not shadowed(n,alias)}
        for value in values:fields(value,sorted(used),alias)
    for row in sdk['compile_context']['actual_dependencies']:fields(row,('path','bytes','sha256'),'every GCC dependency row')
    for name in ('sdk-configure-process.json','sdk-build-process.json'):fields(metadata[name],('action','terminal','exit_status','pid','cwd','argv'),'SDK child receipt')
    for name in ('configure-compiler-environment.json','build-compiler-environment.json'):fields(metadata[name],('PATH','IDF_PATH','IDF_TOOLS_PATH','IDF_PYTHON_ENV_PATH'),'SDK environment')
    need(len(host['commands'])==366 and len(host['records'])==365 and len(sdk['commands'])==14,'Complete actual command counts')
    need(sum(r['comparison'] is None for r in host['records'])==34 and sum(r['comparison'] is not None for r in host['records'])==331,'Distinct available/unavailable host vectors; no numerical remeasurement')
    for role in plan['roles']:
        need('/public-book-consumer-zero-guard-prep-' not in role['path'].replace('\\','/'),'Deferred draft never a role')
    for old,new,diff in [('provenance/base-pack.py','pack.py','pack-adaptation.diff'),('provenance/base-verify.py','verify.py','verify-adaptation.diff'),('provenance/base-compile_context_base.py','compile_context.py','compile-context-extraction.diff')]:
        (HERE/diff).write_text(''.join(difflib.unified_diff((HERE/old).read_text().splitlines(True),(HERE/new).read_text().splitlines(True),fromfile=old,tofile=new)),encoding='utf-8',newline='\n')
    (HERE/'metadata-preflight.json').write_text(json.dumps(dict(schema='public-book-baseline-source-metadata-preflight-v1',source_only=True,selected_entries=selected,
        actual_named_JSON_field_projections=schema_projections,all_selected_paths_exist=True,all_fixed_named_actual_JSON_fields_exist=True,
        Linux_tools_not_resolved_as_Windows_paths=True,tool_or_app_binary_or_raw_command_log_payload_read_or_hashed=False,
        recorded_JSON_vector_metadata_read=True,proposed_code_imported_or_executed=False),indent=2)+'\n',encoding='utf-8',newline='\n')
    result=dict(schema='public-book-baseline-archive-source-checks-v1',result='SOURCE_ONLY_READY_FOR_ROOT_REVIEW',AST_files=len(trees),exact_raw_source_origins=7,exact_pure_helper_AST_definitions=3,
        physical_preparation_files={k:v['physical_files'] for k,v in preparations.items()},selected_entry_checks=len(selected),actual_named_JSON_field_projections=schema_projections,
        SDK_commands=14,SDK_records=439,SDK_exact_vectors=365,host_commands=366,host_calls=365,host_log_streams=732,host_available_exact_vectors=331,host_UBSan_NONPASS=34,
        source_only=True,proposed_code_imported_or_executed=False,pack_verify_tests_oracle_protocol_compiler_SDK_QEMU_PCM_Git_executed=False,
        prior_target_PCM_replayed=False,guard_draft_read_collected_executed_or_qualified=False,standalone=True,archive_dependencies=[],canonical_mutated=False)
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    inventory={p.relative_to(HERE).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(HERE.rglob('*')) if p.is_file()}
    ready.write_text(json.dumps(dict(schema='public-book-baseline-archive-source-readiness-v1',source_only=True,files=inventory),indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(result=result['result'],indexed_files=len(inventory),readiness_sha256=sha(ready),proposed_code_executed=False)))


if __name__=='__main__':main()
