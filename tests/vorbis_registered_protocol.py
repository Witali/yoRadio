"""Strict public raw registry protocol; matrix is the pinned positions/slopes JSON.

validate_log(log, matrix, target, control=None, *, returncode, timed_out, interrupted)
returns JSON-safe counts and actual PCM hashes, never a numerical qualification.
Only a terminal process with the exact complete protocol or named binding control
qualifies. Unknown, duplicated, missing or reordered protocol events are errors.
"""
import hashlib
import re


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def validate_log(log, matrix, target, control=None, *, returncode, timed_out, interrupted):
    need(type(returncode) is int and returncode==0 and timed_out is False and interrupted is False,
         'actual terminal process facts required')
    need(target in ('esp32','esp32c3') and control in (None,'register-open','register-decode'), 'target/control')
    core=1 if target=='esp32' else 0
    cases=matrix['cases']
    need(len(cases)==14 and len({c['id'] for c in cases})==14 and
         all(type(c['expected_valid']) is bool for c in cases) and
         [c['expected_valid'] for c in cases]==[True]*8+[False]*6, 'complete fourteen-case matrix')
    for c in cases:
        sizes, offsets=c['expected_packet_bytes'],c['offsets']
        need(re.fullmatch(r'\S+',c['id']) and len(sizes)==14 and sizes[0]==0 and
             all(type(n) is int and 1<n<=4096 for n in sizes[1:]) and sum(sizes)==28160 and
             len(offsets)==15 and offsets[0]==0 and all(a<b for a,b in zip(offsets,offsets[1:])), 'packet geometry')
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP',log), 'panic is not qualification')
    lines=[line for line in log.replace('\r\n','\n').splitlines()
           if line.startswith(('FLOOR1_','VORBIS_REGISTRY_'))]
    at=0
    def take(expected):
        nonlocal at
        need(at<len(lines) and lines[at]==expected, f'event{at}: expected {expected}')
        at+=1
    def match(pattern):
        nonlocal at
        found=re.fullmatch(pattern,lines[at]) if at<len(lines) else None
        need(found is not None,f'event{at}: malformed packet/metadata')
        at+=1
        return found.groups()
    take(f'FLOOR1_START coordinator=0 decoder={core}')
    take(f'VORBIS_REGISTRY_BEGIN cases=14 packets=112 retries=312 core={core}')
    take(f'VORBIS_REGISTRY_INITIAL empty=1 unsupported=1 core={core}')
    hashes={}; primer=[]; packet_count=retry_count=metadata_count=0
    for case,c in enumerate(cases):
        take(f'VORBIS_REGISTRY_REGISTER case={case} result=0 ops=1 supported=1 core={core}')
        if case==0 and control=='register-open':
            break
        take(f'VORBIS_REGISTRY_BIND_OPEN case={case} match=1 core={core}')
        if case==0 and control=='register-decode':
            break
        take(f'VORBIS_REGISTRY_BIND_DECODE case={case} match=1 core={core}')
        take(f'VORBIS_REGISTRY_BIND_OTHER case={case} reset=1 close=1 core={core}')
        if not c['expected_valid']:
            take(f'FLOOR1_OPEN case={case} result=-1 handle=0')
            take(f'FLOOR1_REJECT case={case} name={c["id"]} result=-1 handle=0 core={core}')
            take(f'VORBIS_REGISTRY_UNREGISTER case={case} empty=1 unsupported=1 core={core}')
            continue
        take(f'FLOOR1_OPEN case={case} result=0 handle=1')
        pcm=bytearray()
        for packet,size in enumerate(c['expected_packet_bytes']):
            if size:
                for attempt in range(3):
                    take(f'VORBIS_REGISTRY_RETRY case={case} packet={packet} attempt={attempt} result=-8 consumed=0 decoded=0 needed={size} untouched=1 canaries=1 core={core}')
                    retry_count+=1
            values=match(rf'VORBIS_REGISTRY_META case={case} packet={packet} result=(-?\d+) sample_rate=(\d+) channel=(\d+) bits=(\d+) core={core}')
            result,rate,channel,bits=map(int,values)
            need((result,rate,channel,bits)==(0,48000,2,16) or
                 (not size and result==-9 and 0<=rate<=0xffffffff and 0<=channel<=255 and 0<=bits<=255), 'public metadata')
            if not size:primer.append(result)
            metadata_count+=1
            consumed,count,hexdump=match(rf'FLOOR1_PCM case={case} packet={packet} consumed=(\d+) bytes=(\d+) hex=([0-9a-f]*)')
            data=bytes.fromhex(hexdump)
            need(int(consumed)==c['offsets'][packet+1]-c['offsets'][packet] and int(count)==len(data)==size, 'complete packet consumption/PCM')
            pcm.extend(data);packet_count+=1
        need(len(pcm)==28160 and any(pcm), 'full nonzero case PCM')
        hashes[str(case)]=hashlib.sha256(pcm).hexdigest()
        take(f'VORBIS_REGISTRY_CLOSE case={case} called=1 core={core}')
        take(f'VORBIS_REGISTRY_UNREGISTER case={case} empty=1 unsupported=1 core={core}')
        take(f'FLOOR1_ACCEPT case={case} name={c["id"]} packets=14 pcm=28160 renderer_repair=1 core={core}')
    if control:
        failure='registry_open_binding' if control=='register-open' else 'registry_decode_binding'
        take(f'FLOOR1_FAILURE case=0 reason={failure}')
        take(f'VORBIS_REGISTRY_CLEANUP case=0 closed=0 empty=1 unsupported=1 core={core}')
    else:
        take(f'VORBIS_REGISTRY_COMPLETE registrations=14 bindings=14 closes=8 unregistrations=14 metadata=112 retries=312 core={core}')
        take(f'FLOOR1_COMPLETE accepted=8 rejected=6 packets=112 pcm=225280 core={core}')
        need((packet_count,retry_count,metadata_count)==(112,312,112), 'complete registry counts')
    take('FLOOR1_CONTROLLED_STOP')
    need(at==len(lines), 'extra protocol events')
    return dict(control_effective=bool(control), exact_failure=failure if control else None,
        registered_callbacks_qualified=not control,target_capture_completed=not control,
        registrations=1 if control else 14,bindings=0 if control else 14,closes=0 if control else 8,
        unregistrations=1 if control else 14,pcm_packets=packet_count,metadata_packets=metadata_count,
        retries=retry_count,pcm_bytes=225280 if not control else 0,pcm_sha256=hashes,
        primer_info_results=primer,core=core,vendor_comparison_available=False,
        independent_reference_compared=False,full_G6_qualified=False)
