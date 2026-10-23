"""Freeze the actual, already completed C3 build's macro probe context."""
import hashlib, json, struct, sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root/'tests'))
from windows_compile_command import windows_argv

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
out = root/'.build/c3-vorbis-format-baseline-01'
build = out/'build'
prep = root/'.build/c3-vorbis-format-project-prep-01'
pins_path = prep/'pins.json'
assert sha(pins_path) == 'a433b95841ae724549fb845058d61da3c12b01167efa7f9ca748ed46ecca970d'
pins = json.loads(pins_path.read_text())
for item in pins['files']:
    p = prep/item['relative']
    assert p.stat().st_size == item['bytes'] and sha(p) == item['sha256'], str(p)
for item in pins['external_inputs']:
    p = Path(item['path'])
    assert p.stat().st_size == item['bytes'] and sha(p) == item['sha256'], str(p)
receipt = json.loads((out/'sdk-build-result.json').read_text(encoding='utf-8-sig'))
assert receipt['status'] == 'TERMINAL_SUCCESS' and receipt['returncode'] == 0
desc = json.loads((build/'project_description.json').read_text())
assert desc['target'] == 'esp32c3'
elf = build/desc['app_elf']
assert struct.unpack_from('<H', elf.read_bytes(), 18)[0] == 243
compdb = build/'compile_commands.json'
rows = json.loads(compdb.read_text())
source = lambda r: (Path(r['directory'])/r['file']).resolve()
actual = [r for r in rows if source(r).is_relative_to(root)]
reviewed = {out/'sources/project/main/main.c',out/'variant/vorbis_repair/setup.c',out/'variant/vorbis_repair/output.c'}
generated = {build/'project_elf_src_esp32c3.c',build/'x509_crt_bundle.S'}
assert len(actual) == 5 and {source(r) for r in actual} == reviewed|generated
assert (build/'project_elf_src_esp32c3.c').stat().st_size == 0
assert '.rodata.embedded' in (build/'x509_crt_bundle.S').read_text()
setup = out/'variant/vorbis_repair/setup.c'
row = next(r for r in actual if source(r) == setup)
cwd = Path(row['directory']).resolve()
assert cwd == build
raw = row.get('arguments') or windows_argv(row['command'])
cc = Path(pins['tools']['compiler']).resolve()
assert Path(raw[0]).resolve() == cc == Path(desc['c_compiler']).resolve()
assert raw.count('-c') == 1 and raw.count('-o') == 1
responses = [a for a in raw if a.startswith('@')]
cflags, specs = build/'toolchain/cflags', build/'specs/picolibc.specs'
assert len(responses) == 1 and (cwd/responses[0][1:]).resolve() == cflags
assert cflags.read_text().splitlines() == [
    '-march=rv32imc_zicsr_zifencei', '-mtune=esp-base',
    '"-specs='+specs.as_posix()+'"', '-D__PICOLIBC_ERRNO_FUNCTION=__errno']
assert specs.stat().st_size > 0
argv, i = [raw[0]], 1
while i < len(raw):
    arg = raw[i]
    if arg == '-c': i += 1
    elif arg == '-o':
        assert i+1 < len(raw)
        i += 2
    else:
        assert not arg.startswith(('-o','--output','-save-temps','-MF','-MT','-MQ','-Wp,'))
        assert arg not in ('-E','-S','-M','-MM','-MD','-MMD','-MP','-MG')
        argv.append(arg)
        i += 1
assert sum((cwd/a).resolve() == setup for a in argv[1:] if not a.startswith(('-','@'))) == 1
argv += ['-E','-dM']
env_path = out/'compiler-environment.json'
env = json.loads(env_path.read_text(encoding='utf-8-sig'))
assert set(env) == {'PATH','IDF_PATH','IDF_TOOLS_PATH','IDF_PYTHON_ENV_PATH'}
snap = out/'macro-inputs'
assert not snap.exists() and not (out/'macro-context.json').exists()
snap.mkdir()
frozen = {}
for p in (cflags,specs,*sorted(generated)):
    destination = snap/p.relative_to(build)
    destination.parent.mkdir(parents=True, exist_ok=True)
    data = p.read_bytes()
    destination.write_bytes(data)
    frozen[str(p)] = {'sha256':sha(p),'snapshot':str(destination.relative_to(out))}
report = dict(schema='actual-c3-rv32-macro-context-v1', sdk_build_only=True,
    row=row, original_argv=raw, argv=argv, directory=str(cwd), compiler_sha256=sha(cc),
    compile_database_sha256=sha(compdb), compiler_environment_sha256=sha(env_path),
    build_outputs={str(p.relative_to(out)):sha(p) for p in (elf,build/desc['app_bin'],out/'sdkconfig',compdb,env_path)},
    reviewed_sources={str(p.relative_to(out)):sha(p) for p in sorted(reviewed)},
    sdk_generated_sources={str(p.relative_to(out)):sha(p) for p in sorted(generated)},
    frozen_inputs=frozen, preparation_script_sha256=sha(__file__), target_executed=False)
with (out/'macro-context.json').open('x',encoding='utf-8',newline='\n') as f:
    f.write(json.dumps(report,indent=2)+'\n')
print(json.dumps({'prepared':str(out/'macro-context.json'),'reviewed_source_tus':len(reviewed),'sdk_generated_tus':len(generated),'elf_machine':243}))
