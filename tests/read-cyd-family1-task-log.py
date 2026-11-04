"""Read complete actual family1 task/public PCM observations as data only."""
import hashlib
import importlib.util
from pathlib import Path
import re


def need(value,reason):
    if not value:raise ValueError(reason)


def fields(line):
    tag,*parts=line.split();pairs=[part.split('=',1) for part in parts]
    need(pairs and all(len(pair)==2 for pair in pairs) and len({key for key,_ in pairs})==len(pairs),'complete unique observation fields')
    words={'fixture','id','kind','sha256','stage','hex','role','sdk','operation','phase','function',
           'owner_role','priority_provenance'};row={}
    for key,value in pairs:
        if key in words:row[key]=value
        else:need(re.fullmatch('-?[0-9]+',value),'strict actual integer observation');row[key]=int(value)
    return tag,row


def padding_expectations(contract):
    entries={row['id']:row for row in contract['entries']};expected=[]
    for plan in contract['cases']:
        logical=sum((entries[link['reference']]['logical_frames'] if link['reference'] in entries else 528000)*2 for link in plan['links'])
        tail=logical%1024
        if not tail:continue
        expected.append(dict(fixture=plan['name'],schedule=plan['schedule'],page_style=plan['page_style'],ordinal=len(expected)+1,
            phase='FLUSH',block_bytes=1024,logical_before=logical-tail,wire_before=logical-tail,
            logical_bytes=tail,wire_bytes=1024,padding_bytes=1024-tail,zero_checked=1,core=1,priority=6))
    return expected


def validate_padding_records(records,contract):
    expected=padding_expectations(contract)
    need(records==expected,'exact once-only final configured DMA padding: logical/wire/zero/phase/size/count metadata')
    return expected


def validate_padding_flow(rows,contract):
    source=rendered=case_index=0;seen=False
    entries={row['id']:row for row in contract['entries']}
    for tag,row in rows:
        if tag=='CYD_F1_LINK':source+=1
        elif tag=='CYD_F1_RENDER_LINK':rendered+=1
        elif tag=='CYD_F1_RENDER_PADDING':
            need(case_index<len(contract['cases']),'no padding after the final case')
            plan=contract['cases'][case_index]
            need(not seen and source==rendered==len(plan['links']),'padding follows every exact logical source/render span once')
            seen=True
        elif tag=='CYD_F1_TASK_CASE':
            need(case_index<len(contract['cases']),'one declared complete case')
            plan=contract['cases'][case_index]
            logical=sum((entries[link['reference']]['logical_frames'] if link['reference'] in entries else 528000)*2 for link in plan['links'])
            need(source==rendered==len(plan['links']) and seen==(logical%1024!=0),'complete case follows exact logical spans and only its required final padding')
            case_index+=1;source=rendered=0;seen=False
    need(case_index==len(contract['cases']) and source==rendered==0 and not seen,'no early, intermediate or extra final padding flow')


def validate_cancellation_records(rows,expected_fixtures):
    """Correlate public calls by identity/time; never read a private phase."""
    def selected(tag):return [row for found,row in rows if found==tag]
    owners=selected('CYD_F1_CONTROL_OWNER')
    profiles=[('controller',0,1,'sdk_main_startup'),('stream',0,3,'wrapped_task_creation'),
              ('decode',1,5,'wrapped_task_creation'),('output',1,6,'wrapped_task_creation')]
    need(len(owners)==4,'all four actual public control-owner identities required')
    for owner,(role,core,declared,provenance) in zip(owners,profiles):
        need(isinstance(owner.get('task_handle'),int) and 0<owner['task_handle']<=0xffffffff and owner==dict(
            role=role,task_handle=owner['task_handle'],core=core,declared_priority=declared,priority_provenance=provenance,
            effective_priority_limit=25,live_base_query=0,creation_profile_checked=1),'exact original startup/creation provenance, never a live base-priority query')
    owner_by_handle={owner['task_handle']:owner for owner in owners}
    need(len(owner_by_handle)==4,'distinct actual controller/stream/decode/output public task handles')
    starts=selected('CYD_F1_CONTROL_ACQUIRE_START');returns=selected('CYD_F1_CONTROL_ACQUIRE_RETURN');held=selected('CYD_F1_CONTROL_ACQUIRE_HELD')
    count=len(expected_fixtures)
    need([row['acquire'] for row in starts]==[row['acquire'] for row in returns]==[row['acquire'] for row in held]==list(range(1,count+1)) and
         [row['fixture'] for row in starts]==expected_fixtures,'every actual acquisition start/real return/HELD identity is present')
    need(count>0 and max(i for i,(tag,_) in enumerate(rows) if tag=='CYD_F1_CONTROL_OWNER')<
         min(i for i,(tag,_) in enumerate(rows) if tag=='CYD_F1_CONTROL_ACQUIRE_START'),'owner identities published before any actual acquisition')
    acquisitions={}
    for start,returned,parked in zip(starts,returns,held):
        need(start['fixture']==returned['fixture']==parked['fixture'] and start['time_us']<=returned['time_us']<=parked['time_us'] and
             start['timeout_ms']==10000 and start['source_generation']==returned['source_generation']>0 and
             returned['result']==0 and returned['real_returned']==1 and returned['token_epoch']==parked['token_epoch']>0 and
             parked['live_clients']==parked['live_decoders']==parked['input_ready']==parked['input_reading']==parked['input_writing']==parked['driver_live']==0 and
             parked['input_available']==parked['input_leased']==1 and parked['pauses_after']>parked['pauses_before'],
             'real acquire returns success/token after every owner/driver is quiet, with exact source identity')
        acquisitions[start['acquire']]=(start,returned,parked)
    pause_starts=selected('CYD_F1_CONTROL_PAUSE_START');pause_returns=selected('CYD_F1_CONTROL_PAUSE_RETURN')
    need([row['pause'] for row in pause_starts]==[row['pause'] for row in pause_returns]==list(range(1,2*count)),
         'all public pause(true/false) starts and real returns are complete')
    pauses={}
    for start,returned in zip(pause_starts,pause_returns):
        required={'fixture','pause','acquire','acquire_active','requested','core','priority','time_us',
                  'task_handle','owner_role','declared_priority','priority_provenance'}
        need(required<=set(start) and required|{'real_returned'}<=set(returned),'complete public caller and effective-priority observations')
        need(all(start[key]==returned[key] for key in ('fixture','pause','acquire','acquire_active','requested','core',
             'task_handle','owner_role','declared_priority','priority_provenance')) and
             start['time_us']<=returned['time_us'] and returned['real_returned']==1 and start['core'] in (0,1) and start['priority']>0,
             'each exact public pause argument is forwarded and really returns')
        need(start['task_handle'] in owner_by_handle,'pause caller names a captured actual task handle')
        owner=owner_by_handle[start['task_handle']]
        for observed in (start,returned):
            need(observed['owner_role']==owner['role'] and observed['core']==owner['core'] and
                 observed['declared_priority']==owner['declared_priority'] and observed['priority_provenance']==owner['priority_provenance'] and
                 owner['declared_priority']<=observed['priority']<owner['effective_priority_limit'],
                 'stable actual owner/creation priority with independently sampled effective priority in the pinned scheduler range')
        need(start['acquire'] in acquisitions,'public pause belongs to a real acquisition')
        acquire,_,parked=acquisitions[start['acquire']]
        need(start['fixture']==acquire['fixture'],'public cancellation lifecycle fixture identity')
        if start['requested']:
            need(owner['role']=='controller' and start['requested']==start['acquire_active']==1 and acquire['time_us']<=start['time_us']<=returned['time_us']<=parked['time_us'],
                 'pause(true) is bracketed by the real request to HELD interval')
        else:
            need(owner['role'] in ('stream','decode','output') and start['acquire_active']==0 and start['acquire']<count and parked['time_us']<=start['time_us'],
                 'real pause(false) follows HELD and only precedes a resumed lifecycle')
        pauses[start['pause']]=(start,returned)
    for index in range(1,count+1):
        true=[value for value in pauses.values() if value[0]['acquire']==index and value[0]['requested']==1]
        false=[value for value in pauses.values() if value[0]['acquire']==index and value[0]['requested']==0]
        need(len(true)==1 and len(false)==int(index<count),'one real cancellation and exactly its required resume')
    writes=selected('CYD_F1_WRITE_RETURN');cancelled=[]
    need(writes and [row['call'] for row in writes]==list(range(1,len(writes)+1)),'every actual write returns once in original order')
    for row in writes:
        need(row['before_status']==row['after_status']==0 and row['before_bytes']==row['after_bytes']==32 and row['equal']==1 and
             row['core']==1 and row['priority']==6 and 0<row['data_bytes']<=3072 and row['data_bytes']%2==0 and
             row['start_us']<=row['return_us'],'source is independently hashed and unchanged on every real return, regardless of status')
        if row['result']==0:continue
        # ESP-IDF6.0.2 esp_err.h documents0x103 as ESP_ERR_INVALID_STATE.
        need(row['result']==0x103 and row['cancelling']==row['pause_requested']==1 and row['acquire_return'] in acquisitions,
             'only documented INVALID_STATE is permitted inside an actual cancellation interval')
        acquire,_,parked=acquisitions[row['acquire_return']]
        need(row['pause_start'] in pauses,'cancelled write has a genuine public pause call')
        pause,real_return=pauses[row['pause_start']]
        need(pause['requested']==1 and pause['acquire']==row['pause_acquire']==row['acquire_return'] and
             pause['fixture']==row['fixture']==acquire['fixture'] and row['source_generation']==acquire['source_generation'] and
             acquire['time_us']<=pause['time_us']<=row['return_us']<=parked['time_us'] and real_return['time_us']<=parked['time_us'] and
             0<=row['pause_return']<=row['pause_start'],
             'actual return is positively correlated to a completed real public request and later HELD, without a fabricated generation label')
        if row['pause_return']:
            need(row['pause_return'] in pauses and pauses[row['pause_return']][0]['requested']==1,
                 'observed last real pause(true) return cannot name a false or nonexistent call')
        cancelled.append(row)
    return dict(acquire_starts=starts,acquire_returns=returns,acquire_held=held,pause_starts=pause_starts,
                pause_returns=pause_returns,write_returns=writes,cancelled_write_returns=cancelled,
                public_owner_provenance=owners,live_base_priority_queried=False,effective_priority_may_change=True,
                private_phase_read=False,source_hash_checked_after_errors=True)


def fairness_expectations(contract):
    entries={row['id']:row for row in contract['entries']}
    views={(row['reference'],row['style'],row['gain_q8']):row for row in contract['immutable_storage']['views']}
    result=[]
    for plan in contract['cases']:
        encoded=sum(views[(link['reference'],'split' if plan['page_style'] and link['reference']<13 else 'whole',link['gain_q8'])]['bytes'] for link in plan['links'])
        for partial in ([1,0] if plan['id'] in ('T1','T2') else [0]):
            position=entries[plan['reference']]['hold_offset'] if partial else encoded
            result.append(dict(fixture=plan['name'],ordinal=len(result)+1,schedule=plan['schedule'],page_style=plan['page_style'],
                encoded_bytes=encoded,position=position,partial_transport=partial,complete_transport=1-partial))
    return result


def validate_stream_fairness_records(records,contract):
    expected=fairness_expectations(contract);one_byte=[]
    need(len(records)==len(expected),'every real HTTP client has one forwarding scheduler census')
    for row,identity in zip(records,expected):
        need(all(row[key]==value for key,value in identity.items()) and row['generation']>0 and row['core']==0 and row['priority']==3 and
             row['cleanup_real_returned']==1 and row['diagnostic_delays']==0,
             'exact public HTTP identity and actual stream owner; observer adds no delays')
        need(row['positive_bytes']==row['position'] and 0<row['positive_reads']<=row['positive_bytes'] and
             0<row['max_positive_read']<=4096 and row['positive_reads']*row['max_positive_read']>=row['positive_bytes'] and
             0<row['first_positive_us']<=row['last_positive_us']<=row['cleanup_us'],
             'all positive public input bytes and read extents are counted before real cleanup')
        need(row['one_tick_started']==row['one_tick_returned']>=0 and row['other_started']==row['other_returned']>=0,
             'all observed public scheduler calls return with their actual tick argument')
        if row['one_tick_started']:
            need(0<row['first_delay_read']<=row['last_delay_read']<=row['positive_reads'] and
                 row['first_positive_us']<=row['first_delay_us']<=row['last_delay_us']<=row['cleanup_us'],
                 'actual one-tick calls are inside the positive-read window')
        else:
            need(row['first_delay_read']==row['last_delay_read']==row['first_delay_us']==row['last_delay_us']==0,
                 'no unobserved scheduler call is claimed')
        if row['schedule']==1 and row['complete_transport']:
            need(row['max_positive_read']==1 and row['positive_reads']==row['positive_bytes']==row['encoded_bytes'],
                 'complete one-byte schedule retains every original positive input byte')
            one_byte.append(row)
            if row['fixture']=='full120':
                need(row['one_tick_returned']>0 and row['first_delay_read']<row['positive_reads'],
                     'long complete one-byte stream genuinely yields before input completion')
    need(any(row['fixture']=='full120' for row in one_byte),'long one-byte production fairness witness is present')
    return dict(client_records=records,complete_one_byte=one_byte,diagnostic_delays_added=False,idle_feed_added=False,
                public_vTaskDelay_forwarded=True,private_state_read=False)


def validate(log,contract):
    need(not re.search(r'CYD_F1_TASK_FAILURE|Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack (?:overflow|smashing)',log,re.I),
         'no actual reference/task/runtime fault')
    text=log.replace('\r\n','\n');lines=text.splitlines()
    need(not any('CYD_F1_' in line and not line.startswith('CYD_F1_') for line in lines),'all observation records intact')
    lines=[line for line in lines if line.startswith('CYD_F1_')]
    need(lines and lines[0]=='CYD_F1_TASK_BOOT sdk=v6.0.2 actual_tasks=1 actual_output=1 public_raw=1 hardware=0','actual complete public-raw task boot scope')
    rows=[fields(line) for line in lines[1:]]
    known={'CYD_F1_REFERENCE_BUDGET','CYD_F1_REFERENCE_OPEN','CYD_F1_REFERENCE_CALL','CYD_F1_REFERENCE_CLOSE',
        'CYD_F1_REFERENCE_PCM','CYD_F1_REFERENCE_CASE','CYD_F1_REFERENCE_COMPLETE','CYD_F1_REFERENCE_WORKSPACE','CYD_F1_TASK_PROFILE',
        'CYD_F1_STATE_INFO','CYD_F1_TASK_CASE','CYD_F1_RENDER_CASE','CYD_F1_LINK','CYD_F1_RENDER_LINK','CYD_F1_RENDER_PADDING',
        'CYD_F1_TASK_FIXTURE','CYD_F1_MEMORY','CYD_F1_METADATA','CYD_F1_OBS_OPEN','CYD_F1_OBS_CALL','CYD_F1_OBS_CLOSE',
        'CYD_F1_CONTROL_HTTP_OPEN','CYD_F1_CONTROL_HTTP_CLOSE','CYD_F1_CONTROL_TRANSPORT_HELD',
        'CYD_F1_CONTROL_STOP_REQUEST','CYD_F1_CONTROL_STOP_RETURN','CYD_F1_CONTROL_STOP_QUIET','CYD_F1_CONTROL_DISCARD',
        'CYD_F1_ORDERED_PACKET_CENSUS','CYD_F1_TASK_COMPLETE','CYD_F1_WRITE_RETURN',
        'CYD_F1_CONTROL_ACQUIRE_START','CYD_F1_CONTROL_ACQUIRE_RETURN','CYD_F1_CONTROL_ACQUIRE_HELD',
        'CYD_F1_CONTROL_PAUSE_START','CYD_F1_CONTROL_PAUSE_RETURN','CYD_F1_STREAM_FAIRNESS',
        'CYD_F1_CONTROL_OWNER',
        'CYD_F1_WORD_LIMITS','CYD_F1_WORD_HEAP','CYD_F1_WORD_COMPLETE',
        'CYD_F1_REALLOC_NULL','CYD_F1_ALLOC_CALLBACK','CYD_F1_ALLOC_COMPLETE','CYD_F1_NATIVE_FAULTS','CYD_F1_ALLOC_OWNER'}
    need(all(tag in known for tag,_ in rows),'only declared genuine public reference/task records')
    spec=importlib.util.spec_from_file_location('passive_family1_allocation_fault_reader',
        Path(__file__).with_name('read-cyd-family1-allocation-faults.py'))
    allocation_reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(allocation_reader)
    allocation_faults=allocation_reader.validate_allocation_faults(rows,contract)
    def select(tag):return [row for found,row in rows if found==tag]
    padding=validate_padding_records(select('CYD_F1_RENDER_PADDING'),contract)
    validate_padding_flow(rows,contract)
    cancellation=validate_cancellation_records(rows,[case['name'] for case in contract['cases'] if case['id']=='T2']+[contract['cases'][-1]['name']])
    fairness=validate_stream_fairness_records(select('CYD_F1_STREAM_FAIRNESS'),contract)
    budgets=select('CYD_F1_REFERENCE_BUDGET')
    need(budgets==[dict(fixed_ms=90000,ordinary_ms=30000,whole_qemu_ms=600000,reset_on_progress=0)],'exact fixed entry deadlines; no progress reset')
    references=select('CYD_F1_REFERENCE_CASE');ref_complete=select('CYD_F1_REFERENCE_COMPLETE')
    need([row['index'] for row in references]==list(range(13)) and
         ref_complete==[dict(cases=13,live=0,private_helpers=0,production_tasks=0,heap_integrity=1)],'all independent direct-public references before application')
    profiles=select('CYD_F1_TASK_PROFILE')
    need(profiles==[dict(role=role,**contract['task_bindings'][role]) for role in ('stream','decode','output')],'all original dual-core task profiles')
    need(next(i for i,line in enumerate(lines) if line.startswith('CYD_F1_REFERENCE_COMPLETE '))<
         next(i for i,line in enumerate(lines) if line.startswith('CYD_F1_TASK_PROFILE ')),'reference owners finish before production tasks start')
    state_infos=select('CYD_F1_STATE_INFO')
    need(state_infos and all(row['rate']==48000 and 1<=row['channels']<=8 and row['bits']==16 and row['channels_are_core']==0 for row in state_infos) and
         {3,6,8}<={row['channels'] for row in state_infos if row['current']},'actual public state preserves complete confirmed logical channel geometry')
    pcm=[bytearray() for _ in references]
    for row in select('CYD_F1_REFERENCE_PCM'):
        index=row['index'];need(0<=index<13 and re.fullmatch('(?:[0-9a-f]{2})+',row['hex']),'only labelled local reference byte records')
        body=bytes.fromhex(row['hex']);need(row['offset']==len(pcm[index]) and row['bytes']==len(body)<=256,'every reference byte in exact order')
        pcm[index].extend(body)
    entries={row['id']:row for row in contract['entries']};raw_refs={}
    metadata=[]
    for plan in contract['cases']:
        for _ in range(2 if plan['id'] in ('T1','T2') else 1):
            for index,link in enumerate(plan['links']):
                entry=entries.get(link['reference'])
                metadata.append(dict(fixture=plan['name'],index=index,layout=1 if entry else 0,
                    channels=entry['channels'] if entry else 2,gain_q8=link['gain_q8'],core=1,priority=6,sequence=1))
    need(select('CYD_F1_METADATA')==metadata,'every original per-link/partial ordered metadata event has correct layout, channels and gain')
    for ref in references:
        index=ref['index'];entry=entries[index];body=bytes(pcm[index])
        need(ref['complete']==1 and ref['private_helpers']==0 and not ref['driver'] and not ref['live'] and
             ref['channels']==entry['channels'] and ref['frames']==entry['logical_frames'] and ref['pcm_bytes']==entry['pcm_bytes']==len(body) and
             ref['sha256']==hashlib.sha256(body).hexdigest() and ref['opens']==ref['closes']==entry['streams'] and ref['calls']>0 and
             ref['core']==1 and ref['priority']==3 and 0<ref['stack_free']<=16384 and ref['before']>0 and ref['after']>0 and
             ref['heap_min']>0 and 0<ref['largest_internal']<=ref['after'],'whole independent public reference/resource identity')
        raw_refs[index]=dict(bytes=len(body),sha256=ref['sha256'])
        workspace=[row for row in select('CYD_F1_REFERENCE_WORKSPACE') if row['index']==index]
        need(workspace and workspace[0]['operation']=='SCRATCH' and workspace[0]['phase']=='BEFORE' and
             workspace[1]['operation']=='SCRATCH' and workspace[1]['phase']=='AFTER' and workspace[1]['result']==0 and
             workspace[1]['present']==1 and workspace[0]['requested']==workspace[1]['requested']==5760*(2 if entry['coupled'] else 1)*2,
             'independent legal maximum public scratch allocated before real opens')
        need(all(row['heap_free']>0 and 0<row['largest_internal']<=row['heap_free'] and 0<row['heap_min']<=row['heap_free'] and
                 (row['phase']=='BEFORE' and row['result']==-1 or row['phase']=='AFTER' and row['result']==0 and row['present']==1) for row in workspace),
             'all immediate independent allocation/open/plane observations retain actual successful outcomes and resources')
        opens=[row for row in select('CYD_F1_REFERENCE_OPEN') if row['index']==index]
        closes=[row for row in select('CYD_F1_REFERENCE_CLOSE') if row['index']==index]
        calls=[row for row in select('CYD_F1_REFERENCE_CALL') if row['index']==index]
        need(len(opens)==ref['opens'] and len(closes)==ref['closes'] and len(calls)==ref['calls'] and
             all(row['result']==0 and row['handle']==1 for row in opens) and all(row['result']==0 for row in closes) and closes[-1]['live']==0 and
             [row['call'] for row in calls]==list(range(1,len(calls)+1)) and all(0<=row['consumed']<=row['input'] and
             0<=row['decoded']<=row['capacity'] and row['result'] in (0,-8) for row in calls),'every original public reference API event accounted')
    cases=select('CYD_F1_TASK_CASE');render_cases=select('CYD_F1_RENDER_CASE')
    need(len(cases)==len(render_cases)==contract['complete_output_cases']==48 and
         [(row['fixture'],row['id'],row['schedule'],row['page_style']) for row in cases]==
         [(row['name'],row['id'],row['schedule'],row['page_style']) for row in contract['cases']],'all complete lifecycle/map/chain schedules, including active C8/120ms')
    source_links=select('CYD_F1_LINK');render_links=select('CYD_F1_RENDER_LINK')
    need(len(source_links)==len(render_links)==sum(len(plan['links']) for plan in contract['cases']),'complete logical source/driver matrix')
    link_cursor=http_count=0
    for case,render,plan in zip(cases,render_cases,contract['cases']):
        http_count+=2 if plan['id'] in ('T1','T2') else 1
        source_total=driver_total=0
        for index,link in enumerate(plan['links']):
            reference=link['reference'];entry=entries.get(reference)
            size=entry['pcm_bytes'] if entry else 2112000;channels=entry['channels'] if entry else 2;layout=1 if entry else 0
            digest=raw_refs[reference]['sha256'] if entry else ('b63b58b563d2a20d90a7bef235e5c1099dc52433db19083492d9c7098345469f' if reference==13 else 'e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910')
            source=source_links[link_cursor];driver=render_links[link_cursor];link_cursor+=1
            identity=dict(fixture=plan['name'],index=index,reference=reference,channels=channels,layout=layout,gain_q8=link['gain_q8'])
            need(source==dict(identity,bytes=size,sha256=digest),'every complete unchanged mapped/trimmed source byte hash')
            need(all(driver[key]==value for key,value in identity.items()) and driver['volume']==plan['volume'] and
                 driver['bytes']==size//channels and re.fullmatch('[a-f0-9]{64}',driver['sha256']),'real ordered final driver link extent/metadata')
            source_total+=size;driver_total+=size//channels
        need(case['pcm_bytes']==source_total and render['mono_bytes']==driver_total and render['fixture']==case['fixture'] and
             render['volume']==plan['volume'] and case['opens']==case['closes'] and case['http_cleanup']==http_count and
             case['writes']>0 and case['metadata']==1 and re.fullmatch('[a-f0-9]{64}',case['sha256']) and
             re.fullmatch('[a-f0-9]{64}',render['sha256']),'actual complete case extent and owner census')
        surplus=(1024-driver_total%1024)%1024
        need(render['wire_bytes']==driver_total+surplus and render['padding_bytes']==surplus and render['padding_blocks']==int(surplus>0),
             'every actual logical mono span plus exact configured zero-padded DMA wire extent')
        if plan['id']=='T0':need(case['ordered_eof']==1,'real EOF lifecycle')
        if plan['id']=='T1':need(case['stop_reopen']==case['discard_after_request']==case['stop_quiet']==1 and 0<case['partial_pcm']<source_total,'genuine partial Stop/discard/quiet/reopen')
        if plan['id']=='T2':need(all(case[key]==1 for key in ('maintenance_resume','held_quiet','play_blocked','token_consumed','stale_rejected')) and 0<case['partial_pcm']<source_total,'genuine partial maintenance/token/stale/resume')
    end=select('CYD_F1_TASK_COMPLETE');census=select('CYD_F1_ORDERED_PACKET_CENSUS')
    need(len(end)==1 and lines[-1].startswith('CYD_F1_TASK_COMPLETE '),'one genuine final record')
    end=end[0];need(all(end[key]==value for key,value in [('cases',48),('references',13),('opens',195),('closes',195),('http_cleanup',58),
        ('output_flushes',48),('heap_integrity',1),('private_abi',0),('independent_codec_conformance',0),('native_oom_injected',0),('hardware',0),('post_output_oracle_pending',1)]) and
        end['process_calls']>0 and end['resizes']==end['retries'] and end['driver_created']==end['driver_deleted']>0 and end['driver_writes']>0 and end['preloads']>0,
        'complete actual native owner/resource census, with post-run Decimal gate still required')
    need(len(census)==1 and census[0]['packets']==census[0]['layout_stamps']==census[0]['gain_stamps']==end['layout_stamps']==end['gain_stamps']>0 and census[0]['order']==1,
         'every PCM packet applies real layout then gain before write')
    need(len(cancellation['write_returns'])==census[0]['packets'],'all successful and cancelled real write returns have independent source hash evidence')
    for role,size in [('stream',6144),('decode',16384),('output',4096)]:need(0<end[role+'_stack_free']<=size,'real original task stack margin')
    need(0<end['heap_min']<=end['heap_free'] and 0<end['largest_internal']<=end['heap_free'],'real whole-task memory observations')
    memory=select('CYD_F1_MEMORY');need(len(memory)==58 and all(0<row['heap_min']<=row['heap_free'] and 0<row['largest_internal']<=row['heap_free'] for row in memory),'every EOF/Stop/maintenance heap observation')
    controls=[(tag.removeprefix('CYD_F1_CONTROL_'),row) for tag,row in rows if tag.startswith('CYD_F1_CONTROL_')]
    http_open=select('CYD_F1_CONTROL_HTTP_OPEN');http_close=select('CYD_F1_CONTROL_HTTP_CLOSE')
    need(len(http_open)==len(http_close)==58 and [row['ordinal'] for row in http_open]==list(range(1,59)) and
         [row['ordinal'] for row in http_close]==list(range(1,59)) and all(a['generation']==b['generation']>0 and
         a['fixture']==b['fixture'] and a['core']==0 and a['priority']==3 and b['result']==0 for a,b in zip(http_open,http_close)),
         'all genuine HTTP clients retain one generation and close once')
    need(all(a['generation']==b['generation'] for a,b in zip(fairness['client_records'],http_open)),
         'scheduler census belongs to the same genuine HTTP generation')
    held=select('CYD_F1_CONTROL_TRANSPORT_HELD');need(len(held)==10,'all ten cancellations have real held reads')
    for row in held:
        entry=next(e for e in entries.values() if e['name']==row['fixture'])
        need(row['position']==row['boundary']==entry['hold_offset']<row['encoded'] and row['genuine_read']==1 and row['core']==0 and row['priority']==3,
             'genuine early first-complete-audio-page hold before encoded EOF')
    discards=select('CYD_F1_CONTROL_DISCARD')
    need([row['sequence'] for row in discards]==list(range(1,len(discards)+1)) and all(row['core']==1 and row['priority']==6 and row['real_returned']==1 for row in discards),
         'every actual output-owner discard sequence is forwarded')
    for plan in [row for row in contract['cases'] if row['id']=='T1']:
        name=plan['name'];parts={tag:[row for found,row in controls if found==tag and row['fixture']==name] for tag in ('STOP_REQUEST','STOP_RETURN','STOP_QUIET')}
        need(all(len(value)==1 for value in parts.values()),'one real Stop interval per partial fixture')
        request,returned,quiet=(parts[tag][0] for tag in ('STOP_REQUEST','STOP_RETURN','STOP_QUIET'))
        matches=[row for row in discards if row['sequence']==request['before_sequence']+1];need(len(matches)==1,'later real discard for this Stop');discard=matches[0]
        need(request['before_generation']+1==returned['stop_generation']==quiet['stop_generation'] and request['time_us']<=returned['time_us']<=quiet['time_us'] and
             request['time_us']<=discard['time_us']<=quiet['time_us'] and discard['fixture']==name and quiet['discard_sequence']==discard['sequence'] and
             quiet['discard_snapshot_generation']==discard['snapshot_generation'],'real Stop sequence/time/owner correlation without invented generation labels')
        need(quiet['live_clients']==quiet['live_decoders']==quiet['input_ready']==quiet['input_reading']==quiet['input_writing']==0 and
             quiet['input_available']==quiet['input_leased']==quiet['no_eof']==1 and quiet['quiet_ticks']>=25 and
             all(quiet[key]==discard[key] for key in ('pcm_bytes','mono_bytes','writes','driver_writes')),'all real owners and output stay quiet before reopen')
    events=[(tag.removeprefix('CYD_F1_OBS_'),row) for tag,row in rows if tag.startswith('CYD_F1_OBS_')]
    live={};closed=[];calls=0
    for tag,row in events:
        instance=row['instance']
        if tag=='OPEN':
            need(row['result']==0 and instance not in live and instance==len(closed)+len(live)+1 and row['generation']>0,'one real successful public handle open')
            live[instance]=dict(row,calls=0,resizes=0,retries=0,pending=False)
        else:
            need(instance in live and all(row[key]==live[instance][key] for key in ('fixture','link','kind','stream')),'event belongs to original live public owner')
            state=live[instance]
            if tag=='CALL':
                calls+=1;state['calls']+=1;need(row['call']==state['calls'] and row['consumed']<=row['input'] and row['decoded']<=row['capacity'],'all real call bounds/sequence')
                if row['retry']:need(state['pending'] and row['advanced']==1 and row['result']==0,'real next-call resize retry');state['retries']+=1
                else:need(not state['pending'],'required resize retry cannot disappear')
                state['pending']=row['result']==-8
                if state['pending']:need(not row['decoded'] and row['needed']>row['capacity'],'real public buffer request');state['resizes']+=1
                else:need(row['result']==0,'genuine native codec error is not a format allowance')
            elif tag=='CLOSE':
                need(row['calls']==state['calls'] and row['resizes']==state['resizes']==row['retries']==state['retries'] and not state['pending'] and not row['buffer_pending'],'complete public handle call/retry census')
                if row['kind']=='simple':need(row['drained']==1,'real stock legacy EOF drained before final public close')
                if row['result']==0:closed.append(state);del live[instance]
                else:need(row['pending']==1,'real close refusal preserves live ownership')
            else:need(False,'known public observer event')
    need(not live and len(closed)==195 and calls==end['process_calls'] and sum(row['resizes'] for row in closed)==end['resizes'],'all195 actual public handles close and all calls accounted')
    queued=[]
    for name in ('LAYOUT_GAIN_CHAIN','REVERSE_120_CHAIN'):
        completed=0;seen=set()
        for tag,row in rows:
            if row.get('fixture')!=name:continue
            if tag=='CYD_F1_LINK':completed+=1
            if tag=='CYD_F1_OBS_OPEN' and row['link'] and row['link'] not in seen:
                if completed<row['link']:queued.append(dict(fixture=name,next_link=row['link'],source_links_complete=completed))
                seen.add(row['link'])
    need(queued,'actual next-link decoder opens while earlier layout/gain PCM is queued')
    return dict(cases=cases,render_cases=render_cases,source_links=source_links,render_links=render_links,
        references=references,reference_complete=ref_complete[0],reference_pcm=raw_refs,reference_workspace=select('CYD_F1_REFERENCE_WORKSPACE'),complete=end,memory=memory,
        public_controls=controls,public_events=events,public_state_infos=state_infos,metadata=select('CYD_F1_METADATA'),render_padding=padding,
        cancellation=cancellation,stream_fairness=fairness,queued_boundaries=queued,allocation_faults=allocation_faults,
        same_vendor_integration_oracle=True,independent_codec_conformance=False,physical_audio_qualified=False),[bytes(body) for body in pcm]
