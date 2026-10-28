"""Qualify every Vorbis window shape against a high-precision sine oracle.

No decoder, deferred target, radio, overlap history or PCM is executed. Commands
use the existing owned-process supervisor; all inputs and raw captures survive.
"""
import argparse, ast, functools, hashlib, json, math, os, re, struct, subprocess, sys, time, uuid
from decimal import Decimal, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ('native_vorbis_numeric', 'native_vorbis_packet_frame',
              'native_vorbis_floor1_product', 'native_vorbis_transform', 'native_vorbis_window')
PI = Decimal('3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628')
BOUND = 2e-15  # absolute coefficient error; output error <=BOUND*abs(input)+4*true_min


def need(test, message):
    if not test:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def linux(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def sine(x):
    term = total = x
    for k in range(1, 100):
        term *= -x*x / Decimal((2*k)*(2*k+1))
        following = total + term
        if following == total:
            return following
        total = following
    raise ValueError('Decimal sine convergence')


@functools.lru_cache(maxsize=8)
def coefficients(n):
    with localcontext() as context:
        context.prec = 70
        return tuple(float(sine(PI/2 * sine(PI*Decimal(2*i+1)/Decimal(2*n))**2))
                     for i in range(n//2))


def sample(i):
    fixed = (sys.float_info.max,-sys.float_info.max,math.ulp(0.0),-math.ulp(0.0),
             0.0,-0.0,float.fromhex('0x1p-1000'),-float.fromhex('0x1p800'),1.0,-1.0)
    return fixed[i%12] if i%12 < 10 else (i%1021-510)*.03125


def inspect_capture(body):
    offset = 0
    def raw(size):
        nonlocal offset
        need(size <= len(body)-offset, 'complete capture field')
        result = body[offset:offset+size]; offset += size
        return result
    def u32(): return struct.unpack('<I', raw(4))[0]
    def doubles(count): return struct.unpack('<'+str(count)+'d', raw(8*count))
    need(raw(8) == b'VWINDOW1' and u32() == 8, 'window capture header')
    references = {}; maximum_coefficient = maximum_output = 0.0; count = 0
    for n in (64,128,256,512,1024,2048,4096,8192):
        need(u32() == n, 'all legal plans in order')
        values = doubles(n//2); reference = coefficients(n); references[n] = reference
        for i, (value, expected) in enumerate(zip(values, reference)):
            need(math.isfinite(value) and 0 < value <= 1, 'positive finite window')
            need(abs(value-expected) <= BOUND, 'Decimal coefficient bound')
            need(abs(value*value+values[-1-i]*values[-1-i]-1) <= 4e-15, 'power complementarity')
            if i: need(value >= values[i-1], 'monotone rise')
            maximum_coefficient = max(maximum_coefficient, abs(value-expected)); count += 1
    need(u32() == 288, 'complete shape corpus')
    samples = zeroed = plateau = 0
    for small_index in range(8):
        for large_index in range(small_index, 8):
            s, l = 64 << small_index, 64 << large_index
            for flags in range(8):
                need((u32(),u32(),u32()) == (s,l,flags), 'ordered complete configuration/flags')
                w, prev, following = flags&1, (flags>>1)&1, (flags>>2)&1
                n = l if w else s
                p = l if w and prev else s; q = l if w and following else s
                # Geometric center placement, independent of production's begin/end loops.
                center_left, center_right = n//4, 3*n//4
                expected_shape = (n,p,q,center_left-p//4,center_left+p//4,
                                  center_right-q//4,center_right+q//4)
                need(tuple(u32() for _ in range(7)) == expected_shape, 'every window coordinate')
                exponent = struct.unpack('<q',raw(8))[0]
                need(exponent == (-(1<<63) if flags&2 else (1<<63)-1), 'full retained int64 exponent')
                source, output = doubles(n), doubles(n)
                for i, (value, actual) in enumerate(zip(source, output)):
                    need(struct.pack('<d',value)==struct.pack('<d',sample(i+flags)), 'every declared input bit')
                    # Scatter each ascending and descending half over a unity interior.
                    left = i-(center_left-p//4); right = center_right+q//4-1-i
                    if left < 0 or right < 0:
                        expected = 0.0; zeroed += 1
                        need(struct.pack('<d',actual) == bytes(8), 'canonical +0 outside support')
                    elif left < p//2:
                        expected = value*references[p][left]
                    elif right < q//2:
                        expected = value*references[q][right]
                    else:
                        expected = value; plateau += 1
                        need(struct.pack('<d',actual) == struct.pack('<d',value), 'bit-preserved plateau')
                    need(math.isfinite(actual), 'finite output without overflow')
                    error = abs(actual-expected)
                    need(error <= BOUND*abs(value) + 4*math.ulp(0.0), 'fixed window product bound')
                    if value: maximum_output = max(maximum_output,error/abs(value))
                    samples += 1
    need(offset == len(body), 'no trailing or missing capture bytes')
    return dict(passed=True, cases=288, configurations=36, flags_per_configuration=8,
        coefficients=count, windowed_samples=samples, zeroed_samples=zeroed,
        plateau_samples=plateau, maximum_coefficient_error=maximum_coefficient,
        maximum_output_error_over_input=maximum_output, coefficient_bound=BOUND)


def corruption_controls(body):
    first = 16 + sum(4+4*n for n in (64,128,256,512,1024,2048,4096,8192))
    changes = [('header',0,b'X'),('coefficient',16,struct.pack('<d',math.nan)),
        ('geometry',first+12,struct.pack('<I',63)),('exponent',first+40,bytes(8)),
        ('source',first+48,bytes(8)),('output',first+48+64*8,struct.pack('<d',math.nan))]
    bad = [(name,body[:offset]+replacement+body[offset+len(replacement):])
           for name,offset,replacement in changes]
    bad.extend([('truncated',body[:-1]),('trailing',body+b'X')])
    for name, corrupt in bad:
        try:
            inspect_capture(corrupt)
        except (ValueError,struct.error):
            continue
        raise ValueError('corruption was accepted: '+name)
    return [name for name,_ in bad]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--verify-capture', type=Path)
    args = parser.parse_args()
    if args.verify_capture:
        body = args.verify_capture.read_bytes()
        result = inspect_capture(body)
        result['corruption_controls'] = corruption_controls(body)
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps(result)); return 0
    out = args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists(), 'fresh task-local output')
    out.mkdir(parents=True)
    report = dict(completed=False,passed=False,commands=[],sources={},sanitizers=['address','undefined'],
        native_executed=False,production_selected=False,overlap_executed=False,PCM_executed=False)
    def save():
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path, label):
        target = out/'sources'/label; target.parent.mkdir(parents=True,exist_ok=True)
        body = path.read_bytes(); target.write_bytes(body)
        report['sources'][label] = sha(body)
        return body
    def run(name, argv):
        nonce = uuid.uuid4().hex
        request, receipt, stop = (out/(name+suffix) for suffix in ('.request.json','.receipt.json','.stop'))
        request.write_text(json.dumps(dict(nonce=nonce,argv=list(map(str,argv)),timeout=60,
            receipt=linux(receipt),stop=linux(stop))),encoding='utf-8')
        command = (['wsl.exe','--exec','python3'] if os.name=='nt' else [sys.executable])+[
            linux(out/'supervisor.py'),linux(request)]
        row = dict(name=name,nonce=nonce,argv=command,child_argv=list(map(str,argv)),request_sha256=sha(request.read_bytes()))
        report['commands'].append(row); save(); child = None; started = time.monotonic()
        try:
            with (out/(name+'.stdout.log')).open('xb') as stdout, (out/(name+'.stderr.log')).open('xb') as stderr:
                child = subprocess.Popen(command,stdout=stdout,stderr=stderr,stdin=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                row['transport_pid'] = child.pid; child.wait(timeout=80)
        finally:
            if child is not None and child.poll() is None:
                stop.write_text(nonce,encoding='ascii')
                try: child.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    child.kill(); child.wait(timeout=5); row['forced_transport_stop'] = True
            observed = json.loads(receipt.read_bytes()) if receipt.exists() else {}
            row.update(elapsed_seconds=time.monotonic()-started,supervisor=observed,
                transport_exit=None if child is None else child.poll())
            save()
        need(row['transport_exit']==0 and not row.get('forced_transport_stop'), 'owned transport terminal: '+name)
        need(observed.get('nonce')==nonce and observed.get('request_sha256')==row['request_sha256'] and
            observed.get('state')=='terminal' and observed.get('final') is True and
            observed.get('child_reaped') is True and observed.get('group_gone') is True and
            observed.get('new_session') is True and observed.get('child_pid')==observed.get('owned_pgid') and
            observed.get('child_returncode')==0, 'owned child terminal: '+name)
        return (out/(name+'.stdout.log')).read_text(encoding='utf-8')
    save()
    try:
        freeze(Path(__file__), 'runner.py')
        for component in COMPONENTS:
            folder = ROOT/'idf/components'/component
            for path in sorted(folder.rglob('*')):
                if path.is_file(): freeze(path,'components/'+component+'/'+path.relative_to(folder).as_posix())
        freeze(ROOT/'tests/native/vorbis_window_host.c','native/vorbis_window_host.c')
        origin = freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-origin.py')
        supervisor = [ast.literal_eval(node.value) for node in ast.parse(origin).body if isinstance(node,ast.Assign)
            and any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(supervisor)==1,'one owned-process supervisor')
        (out/'supervisor.py').write_text(supervisor[0],encoding='utf-8',newline='\n')
        report['supervisor_sha256'] = sha((out/'supervisor.py').read_bytes()); save()
        report['compiler_version'] = run('compiler-version',['gcc','--version'])
        common = ['gcc','-std=c11','-O1','-g','-UNDEBUG','-fno-fast-math','-ffp-contract=off',
            '-fno-pie','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer',
            '-Wall','-Wextra','-Werror', *['-I'+linux(out/'sources/components'/name/'include') for name in COMPONENTS]]
        run('compile',[*common,linux(out/'sources/components/native_vorbis_window/window.c'),
            linux(out/'sources/native/vorbis_window_host.c'),'-no-pie','-lm','-o',linux(out/'window')])
        text = run('execute',['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1',
            'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',linux(out/'window'),linux(out/'capture.bin')])
        match = re.fullmatch(r'WINDOW_CAPTURE cases=288 refusals=(\d+) checks=(\d+)\s*',text)
        need(match is not None and not (out/'execute.stderr.log').read_bytes(),'complete guarded capture')
        measurements = inspect_capture((out/'capture.bin').read_bytes())
        report['corruption_controls'] = corruption_controls((out/'capture.bin').read_bytes())
        for name, digest in report['sources'].items():
            need(sha((out/'sources'/name).read_bytes()) == digest, 'unchanged frozen source')
        report.update(completed=True,passed=True,measurements=measurements,
            controls=dict(refusals=int(match[1]),checks=int(match[2])),
            capture_sha256=sha((out/'capture.bin').read_bytes()),binary_sha256=sha((out/'window').read_bytes()))
        save(); print(json.dumps({key:report[key] for key in ('completed','passed','controls','measurements')})); return 0
    except BaseException as error:
        report['error'] = repr(error); save(); raise


if __name__ == '__main__':
    raise SystemExit(main())
