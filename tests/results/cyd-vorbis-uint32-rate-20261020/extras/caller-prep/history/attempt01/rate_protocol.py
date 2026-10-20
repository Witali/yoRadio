"""Strict CYD public raw uint32-rate protocol; observations only, no execution."""
import re

PREFIX='CYD_VORBIS_RATE_'
FIXTURE_SHA256='839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378'
RATES=(48000,44100,32000,24000,22050,16000,12000,11025,8000,1,63999,64000,
       192000,2147483647,2147483648,4294967295)
PACKET_SIZES=(32,111,107,105,110,106,109,110,107,107,110,106,107,106,106,105,
    105,109,107,103,110,107,108,107,107,106,109,109,108,104,110,109,107,108,
    106,108,108,108,106,105,108,107,105,110,105,108,105,106,103,107,107,105,
    107,110,106,106,106,108,110,110,109,106,108,111,106,105,123,109)
PCM_SIZES=(0,2304)+(4096,)*66
NONZERO=r'(?:-[1-9]\d*|[1-9]\d*)'

def need(ok,message):
    if not ok: raise RuntimeError(message)

def validate_log(log,mode,control=None,*,returncode,timed_out,interrupted):
    """Consume the exact native protocol with explicit real process facts.

    This returns observations. The caller owns qualification and must not
    substitute synthetic process facts or infer firmware success from host tests.
    """
    need(mode in ('baseline','acceptance','limited'),'Unknown explicit rate mode')
    need(control is None or (control=='signed-validity' and mode=='acceptance') or
         (control=='signed-policy' and mode=='limited'),'Unknown/incompatible control')
    need(type(returncode) is int and returncode==0 and timed_out is False and interrupted is False,
         'Nonzero/incomplete/timed-out/interrupted process')
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|TimeoutExpired|timed out',log),
         'Target panic/corruption/timeout')
    raw=log.splitlines()
    need(not any('VORBIS_RATE_' in line and not line.startswith(PREFIX) for line in raw),'Foreign/malformed rate prefix')
    lines=[line[len(PREFIX):] for line in raw if line.startswith(PREFIX)]; cursor=0
    def take(pattern):
        nonlocal cursor
        need(cursor<len(lines),f'Missing protocol line {cursor}')
        match=re.fullmatch(pattern,lines[cursor])
        need(match,f'Protocol line {cursor}: {lines[cursor]!r}; expected {pattern!r}')
        cursor+=1; return match
    take(rf'BEGIN expected_unsigned_rejection={int(mode=="baseline")} limited_policy={int(mode=="limited")} '
         r'cases=16 short=256 long=2048 golden_rate=192000 coordinator=0')
    take(r'WORKER core=1')
    take(rf'ZERO_REJECT rate=0 result={NONZERO} handle=0 handles_closed=1 core=1')
    accepted=rejected=paired=pcm_total=0; failure=None
    for index,rate in enumerate(RATES):
        coord=f'index={index} rate={rate}'
        exceptional=rate==2147483648 and control is not None
        reject=(mode=='baseline' and rate>2147483647) or (mode=='limited' and rate>=64000)
        if exceptional:
            if control=='signed-validity':
                take(rf'CASE_OPEN {coord} golden_rate=192000 vendor_open=0 checked_open={NONZERO} vendor_handle=1 checked_handle=0 core=1')
                failure='legal_unsigned_rate_open_required'
            else:
                take(rf'CASE_OPEN {coord} golden_rate=192000 vendor_open=0 checked_open=0 vendor_handle=1 checked_handle=1 core=1')
                failure='limited_rate_rejection_required'
            take('FAILURE '+failure)
            break
        if reject:
            opened=take(rf'CASE_OPEN {coord} golden_rate=192000 vendor_open=0 checked_open=({NONZERO}) vendor_handle=1 checked_handle=0 core=1').group(1)
            take(rf'CASE_REJECT {coord} result={re.escape(opened)} header_error=1 handles_closed=1 core=1')
            rejected+=1
            continue
        take(rf'CASE_OPEN {coord} golden_rate=192000 vendor_open=0 checked_open=0 vendor_handle=1 checked_handle=1 core=1')
        nz_total=0
        for packet,(size,pcm) in enumerate(zip(PACKET_SIZES,PCM_SIZES)):
            found=take(rf'PACKET {coord} packet={packet} expected={size} vendor_consumed={size} checked_consumed={size} pcm={pcm} '
                rf'vendor_rate=192000 checked_rate={rate} vendor_channel=2 checked_channel=2 vendor_bits=16 checked_bits=16 '
                r'exact=1 canaries=1 nonzero=(\d+) core=1')
            nz=int(found.group(1)); need(0<=nz<=pcm,'Nonzero attestation exceeds actual PCM'); nz_total+=nz
        need(nz_total>0,'Missing nonzero PCM')
        take(rf'CASE_COMPLETE {coord} packets=68 pcm=272640 nonzero={nz_total} handles_closed=1 core=1')
        accepted+=1; paired+=68; pcm_total+=272640
    if not control:
        take(rf'COMPLETE cases=16 accepted={accepted} rejected={rejected} paired_packets={paired} pcm={pcm_total} zero_rejected=1 core=1')
        need((accepted,rejected)=={'acceptance':(16,0),'baseline':(14,2),'limited':(11,5)}[mode],'Mode accounting differs')
    need(cursor==len(lines),'Extra/duplicate/trailing native protocol')
    return dict(accepted=accepted,rejected=rejected,paired_packets=paired,pcm_bytes=pcm_total,
        zero_rejected=1,exact_failure=failure,protocol_lines=cursor)
