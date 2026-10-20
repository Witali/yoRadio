"""Strict public raw bank protocol only; no process, codec or target execution."""
import re

PROFILES={'cyd':('CYD_VORBIS_BLOCK_',1),'c3':('C3_VORBIS_BLOCK_',0)}
KINDS=('SS','SL','LS','LL')
PATTERNS=([0]+[1]*67,[0,0,1,1,0]+[1]*65,[int(x=='L') for x in 'SSLLLSLSSSLLSS'])

def need(ok,message):
    if not ok: raise RuntimeError(message)

def checked_banks(banks):
    need(isinstance(banks,list) and len(banks)==3,'All three frozen banks required')
    for bank,name,rate,modes in zip(banks,('identity','transitions','minimal'),(192000,192000,48000),PATTERNS):
        need(bank['name']==name and bank['source_rate']==rate and bank['mode_flags']==modes and all(type(x) is int for x in bank['mode_flags']),'Wrong bank identity/rate/modes')
        offsets=bank['offsets']
        need(len(offsets)==len(modes)+1 and offsets[0]==0 and
             all(type(x) is int and 0<=x<=0xffffffff for x in offsets) and
             all(a<b for a,b in zip(offsets,offsets[1:])),'Wrong frozen packet offsets')
    return banks

def validate_log(log,banks,profile,*,manifest_sha256,minimal_rate_rebind_qualified,returncode,timed_out,interrupted):
    """Require actual owned-process/rebind facts. Return observations, never qualification."""
    need(profile in PROFILES,'Unknown explicit target profile')
    need(isinstance(manifest_sha256,str) and re.fullmatch('[0-9a-f]{64}',manifest_sha256),'Missing frozen encoded-bank manifest SHA')
    need(minimal_rate_rebind_qualified is True,'Minimal48000-to192000 independent proof required')
    need(type(returncode) is int and returncode==0 and timed_out is False and interrupted is False,
         'Incomplete/nonzero/interrupted/timeout process')
    checked_banks(banks); prefix,core=PROFILES[profile]
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|TimeoutExpired|timed out',log),
         'Target panic/corruption/timeout')
    raw=log.splitlines()
    need(not any('VORBIS_BLOCK_' in line and not line.startswith(prefix) for line in raw),'Foreign/malformed native prefix')
    lines=[line[len(prefix):] for line in raw if line.startswith(prefix)]; cursor=0
    def take(pattern):
        nonlocal cursor
        need(cursor<len(lines),f'Missing protocol line {cursor}')
        found=re.fullmatch(pattern,lines[cursor])
        need(found,f'Protocol line {cursor}: {lines[cursor]!r}; expected {pattern!r}')
        cursor+=1; return found
    take(rf'BEGIN banks=3 cases=108 paired_packets=5472 target_rate=192000 coordinator=0 worker={core} '
         rf'minimal_source_rate=48000 minimal_rate_rebind=1 manifest={manifest_sha256}')
    cases=packets=groups=total_pcm=0
    for bank in banks:
        name,offsets,modes=bank['name'],bank['offsets'],bank['mode_flags']; count=len(modes)
        take(rf'BANK_BEGIN bank={name} packets={count} source_rate={bank["source_rate"]} target_rate=192000 core={core}')
        bank_packets=bank_pcm=bank_groups=0
        for s in range(6,14):
            for l in range(s,14):
                short,long=1<<s,1<<l; coord=f'bank={name} short={short} long={long}'
                take(rf'CASE_BEGIN {coord} packets={count} rate=192000 vendor_open=0 checked_open=0 handles=1 core={core}')
                transition_counts=[0]*4; transition_pcm=[0]*4; nonzero=[0]*4; case_pcm=0
                for i,(a,b) in enumerate(zip(offsets,offsets[1:])):
                    size=b-a; pcm=0 if not i else (1<<(l if modes[i-1] else s))+(1<<(l if modes[i] else s))
                    kind=2*modes[i-1]+modes[i] if i else None; label=KINDS[kind] if i else 'P'
                    found=take(rf'PACKET {coord} packet={i} expected={size} vendor_consumed={size} checked_consumed={size} pcm={pcm} '
                         rf'vendor_rate=192000 checked_rate=192000 vendor_channel=2 checked_channel=2 vendor_bits=16 checked_bits=16 '
                         rf'exact=1 canaries=1 transition={label} nonzero=(\d+) core={core}')
                    nz=int(found.group(1)); need(0<=nz<=pcm,'Nonzero-byte attestation outside actual PCM size')
                    if i:
                        transition_counts[kind]+=1; transition_pcm[kind]+=pcm; nonzero[kind]+=nz
                    case_pcm+=pcm
                for kind in range(4):
                    if transition_counts[kind]:
                        need(nonzero[kind]>0,'Missing nonzero PCM for present transition')
                        take(rf'TRANSITION {coord} kind={KINDS[kind]} packets={transition_counts[kind]} '
                             rf'pcm={transition_pcm[kind]} nonzero={nonzero[kind]} core={core}')
                        groups+=1; bank_groups+=1
                take(rf'CASE_COMPLETE {coord} packets={count} pcm={case_pcm} handles_closed=1 core={core}')
                cases+=1; packets+=count; total_pcm+=case_pcm; bank_packets+=count; bank_pcm+=case_pcm
        take(rf'BANK_COMPLETE bank={name} cases=36 paired_packets={bank_packets} pcm={bank_pcm} transition_groups={bank_groups} core={core}')
    need((cases,packets,groups)==(108,5472,360),'Required full matrix accounting differs')
    take(rf'COMPLETE banks=3 cases=108 paired_packets=5472 pcm={total_pcm} transition_groups=360 core={core}')
    need(cursor==len(lines),'Extra/duplicate/trailing protocol lines')
    return dict(cases=cases,paired_packets=packets,transition_groups=groups,pcm_bytes=total_pcm,protocol_lines=cursor)
