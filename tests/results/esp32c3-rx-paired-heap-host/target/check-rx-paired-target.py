"""Compile the actual probe for RV32 with pinned target flags, without flashing."""
import hashlib,json,shlex,subprocess
from pathlib import Path
root=Path('.build/c3-rx-paired-host').resolve();root.mkdir(exist_ok=True)
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-radio-wifi-probe')
rows=json.loads((build/'compile_commands.json').read_text())
row=next(r for r in rows if r['file'].replace('\\','/').endswith('/main/audio_service.c'))
source=Path('idf/esp32c3-oled-native/main/rx_buffer_diagnostic.c').resolve()
args=shlex.split(row['command'])
# CMake uses an unquoted Windows compiler path here, followed by POSIX-style
# escaped -D string values. Preserve the observed path's backslashes.
compiler=row['command'].split(' ',1)[0]
assert Path(compiler).is_file(),compiler
args[0]=compiler
args[args.index('-o')+1]=str(root/'rx_buffer.o')
args[args.index('-c')+1]=str(source)
args.extend(['-DCONFIG_YORADIO_RX_BUFFER_DIAGNOSTICS=1','-fstack-usage'])
result=subprocess.run(args,cwd=row['directory'],capture_output=True)
(root/'target-compile.log').write_bytes(result.stdout+result.stderr)
assert result.returncode==0,result.stderr.decode(errors='replace')
usage=(root/'rx_buffer.su').read_text()
poll=next(line for line in usage.splitlines() if 'rx_buffer_diagnostic_poll' in line)
stack=int(poll.split('\t')[1]);assert stack<=1536,poll
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=dict(result='PASS',scope='Target object compile, ABI/stack checks only; no full firmware link or physical run',
    compiler=args[0],command=args,cwd=row['directory'],source_sha256=sha(source),
    object_sha256=sha(root/'rx_buffer.o'),sdkconfig_sha256=sha(build/'sdkconfig'),
    source_flags_override='CONFIG_YORADIO_RX_BUFFER_DIAGNOSTICS=1',poll_stack_bytes=stack)
(root/'target-review.json').write_text(json.dumps(report,indent=2)+'\n')
print('RV32 probe compile PASS; poll stack',stack,'bytes')
