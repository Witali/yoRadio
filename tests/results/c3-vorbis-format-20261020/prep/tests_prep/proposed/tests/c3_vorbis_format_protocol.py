"""Counted public raw C3 protocol only; never translates logs or starts a target."""
import re

PREFIX = 'C3_VORBIS_FORMAT_'

def need(ok, message):
    if not ok: raise RuntimeError(message)

def fixture_accounting(header):
    def values(name):
        body = re.search(r'\b'+name+r'\[\]\s*=\s*\{([^}]+)\}',header).group(1)
        return [int(x) for x in body.split(',') if x.strip()]
    offsets,modes = values('fixture_offsets'),values('fixture_long_mode')
    need(len(offsets) == 69 and len(modes) == 68 and modes.count(1) == 67,'Pinned fixture packet/mode counts')
    sizes = [b-a for a,b in zip(offsets,offsets[1:])]
    def pcm(long):
        blocks = [long if mode else 256 for mode in modes]
        return [0]+[a+b for a,b in zip(blocks,blocks[1:])]  # /4 samples * 4 stereo bytes.
    need(sum(pcm(8192)) == 1089792 and pcm(8192).count(16384) == 66,'Pinned 8192 overlap accounting')
    return sizes,pcm

def validate_log(log, scope, control, header, *, returncode, timed_out):
    """Return observations only. A qualifying caller supplies actual process facts."""
    need(scope in ('baseline','acceptance') and control in (None,'old-guard'),'Unknown scope/control')
    need(not control or scope == 'acceptance','old-guard requires acceptance scope')
    need(type(returncode) is int and returncode == 0 and timed_out is False,'Nonzero/incomplete process or timeout')
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|TimeoutExpired|timed out',log),'Target failure/timeout')
    lines = log.splitlines()
    need(not any('VORBIS_FORMAT_' in line and not line.startswith(PREFIX) for line in lines),'Foreign/malformed protocol prefix')
    sizes,pcm = fixture_accounting(header)
    expected = [rf'BEGIN expected_rejection={int(scope == "baseline")} coordinator=0',
                r'VENDOR_OPEN rate=192000 long=8192 result=0 handle=1']
    expected += [rf'VENDOR_PACKET packet={i} consumed={size} pcm={pcm(8192)[i]} sample_rate=192000 channel=2 bits=16 canaries=1 core=0'
                 for i,size in enumerate(sizes)]
    expected += [r'VENDOR_COMPLETE packets=68 pcm=1089792 nonzero=[1-9]\d* full8192=66']
    pairs = [(48000,2048),(192000,8192),(64000,8192)]
    if scope == 'acceptance' and not control: pairs += [(63999,8192),(48000,8192)]
    for rate,long in pairs:
        output = pcm(long); reference_rate = 192000 if long == 8192 else rate
        expected += [rf'PAIR_PACKET rate={rate} long={long} packet={i} consumed={size} pcm={output[i]} '
                     rf'vendor_expected_rate={reference_rate} vendor_rate={reference_rate} checked_expected_rate={rate} checked_rate={rate} '
                     r'expected_channel=2 vendor_channel=2 checked_channel=2 expected_bits=16 vendor_bits=16 checked_bits=16 exact=1 canaries=1 core=0'
                     for i,size in enumerate(sizes)]
        expected += [rf'EXACT rate={rate} long={long} packets=68 pcm={sum(output)} full8192={output.count(16384)}']
    if control:
        expected += [r'FAILURE legal_candidate_open_required']
    else:
        nonzero = r'(?:-[1-9]\d*|[1-9]\d*)'
        if scope == 'baseline': expected += [rf'LEGAL_REJECT rate={rate} long=8192 result={nonzero} header_error=1' for rate in (63999,48000)]
        expected += [rf'INVALID_REJECT case={case} result={nonzero} header_error=1'
                     for case in ('zero_rate','short32','long16384','short_exceeds_long')]
        expected += ([r'BASELINE low_rejected=2 high_exact=2 normal_exact=1 invalid_rejected=4 core=0'] if scope == 'baseline' else
                     [r'COMPLETE low_exact=2 high_exact=2 normal_exact=1 invalid_rejected=4 core=0'])
    actual = [line[len(PREFIX):] for line in lines if line.startswith(PREFIX)]
    need(len(actual) == len(expected),f'Protocol line count: expected {len(expected)}, got {len(actual)}')
    for i,(line,pattern) in enumerate(zip(actual,expected)):
        need(re.fullmatch(pattern,line),f'Protocol line {i}: {line!r}; expected {pattern!r}')
    return dict(protocol_lines=len(actual),vendor_packets=len(sizes),exact_pairs=len(pairs),
                exact_pair_packets=len(pairs)*len(sizes),exact_failure='legal_candidate_open_required' if control else None)
