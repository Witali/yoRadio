"""Account passive SDK allocation callbacks and actual word-plane recovery.

This reader never executes a capture or changes a failed native result. The
whole-task reader separately verifies every source PCM byte hash and lifecycle;
the word reader separately validates all pointer identities and real frees.
"""
import re

CALLBACK_KEYS={'sequence','bytes','caps','function','attempt','generation','core','isr','decoder_owner','forwarded','stack_pointer'}
OWNER_KEYS={'task_handle','stack_low','stack_high','stack_bytes','stream_stack_low','stream_stack_high',
    'output_stack_low','output_stack_high','public_bounds','unique_checked','callback_task_lookup','stack_dereferenced','owner_core','owner_priority'}
NULL_KEYS={'fixture','link','reference','generation','attempt','bytes','old_pointer','returned_pointer',
    'callback_first','callback_count','real_returned','time_us','core','priority'}
COMPLETE_KEYS={'callbacks','forwarded','unknown','overflow','registrations','registration_errors','realloc_calls',
    'realloc_returns','realloc_nulls','inflight','observer_static_bytes','callback_capacity','final_maintenance',
    'diagnostic_delays','private_heap','hardware'}
FAULT_KEYS={'allocation_failures','allocation_size','allocation_caps','decoder_failures','decoder_generation',
    'decoder_codec','decoder_stage','decoder_result','decoder_completion','decoder_input_bytes',
    'decoder_allocation_sequence','stream_failures','stream_generation','stream_completion','stream_result',
    'output_failures','output_generation','output_stage','output_write_errors','output_configure_errors',
    'output_flush_errors','output_result'}
TAGS={'CYD_F1_REALLOC_NULL','CYD_F1_ALLOC_CALLBACK','CYD_F1_ALLOC_COMPLETE','CYD_F1_NATIVE_FAULTS','CYD_F1_ALLOC_OWNER'}


def need(value,reason):
    if not value:raise ValueError(reason)


def validate_allocation_faults(rows,contract):
    """Require complete attribution, including an honest zero-event run."""
    def select(tag):return [row for found,row in rows if found==tag]
    callbacks=select('CYD_F1_ALLOC_CALLBACK');nulls=select('CYD_F1_REALLOC_NULL')
    ends=select('CYD_F1_ALLOC_COMPLETE');faults=select('CYD_F1_NATIVE_FAULTS')
    need(len(ends)==len(faults)==1,'one actual allocation census and all native fault counters')
    end,fault=ends[0],faults[0]
    owners=select('CYD_F1_ALLOC_OWNER');need(len(owners)==1 and set(owners[0])==OWNER_KEYS,'one complete public decoder stack publication')
    owner=owners[0]
    need(all(isinstance(v,int) and 0<=v<2**32 for v in owner.values()) and owner['task_handle']>0 and
         owner['stack_high']-owner['stack_low']==owner['stack_bytes']==16384 and
         owner['stream_stack_high']-owner['stream_stack_low']==6144 and owner['output_stack_high']-owner['output_stack_low']==4096 and
         owner['public_bounds']==owner['unique_checked']==owner['owner_core']==1 and owner['owner_priority']==5 and
         owner['callback_task_lookup']==owner['stack_dereferenced']==0,'original public task bounds,profile and callback-safe lookup scope')
    ranges=[(owner[a],owner[b]) for a,b in [('stack_low','stack_high'),('stream_stack_low','stream_stack_high'),('output_stack_low','output_stack_high')]]
    need(all(0<a<b<2**32 for a,b in ranges) and all(b<=c or d<=a for i,(a,b) in enumerate(ranges) for c,d in ranges[i+1:]),
         'positive nonoverflowing and mutually disjoint actual public stack extents')
    need(set(end)==COMPLETE_KEYS and set(fault)==FAULT_KEYS,'complete declared callback and native-health fields')
    need(all(isinstance(v,int) and 0<=v<2**32 for k,v in fault.items() if not k.endswith('_result')) and
         all(isinstance(v,int) and -(2**31)<=v<2**31 for k,v in fault.items() if k.endswith('_result')),
         'bounded complete native-health counters and signed results')
    need(all(fault[key]==0 for key in FAULT_KEYS-{'allocation_failures','allocation_size','allocation_caps'}),
         'no decoder,stream,output failure or hidden residual failure details')
    need(all(isinstance(v,int) and 0<=v<2**32 for v in end.values()),'bounded public allocation census')
    need(end['callbacks']==end['forwarded']==end['realloc_nulls']==fault['allocation_failures']==len(callbacks)==len(nulls) and
         end['realloc_calls']==end['realloc_returns']>=len(nulls) and end['unknown']==end['overflow']==end['registration_errors']==end['inflight']==0,
         'every original health callback is forwarded once and matched to an actual nonzero realloc NULL; unknown/overflow fail')
    need(end['registrations']==1 and end['callback_capacity']==8 and 0<end['observer_static_bytes']<=1024 and
         end['final_maintenance']==1 and end['diagnostic_delays']==end['private_heap']==end['hardware']==0,
         'single original callback, bounded passive DRAM and final real quiescence')
    count=len(callbacks)
    need(all(set(row)==CALLBACK_KEYS for row in callbacks) and all(set(row)==NULL_KEYS for row in nulls),
         'complete declared callback and actual NULL-return fields')
    need(count<=8 and [row['sequence'] for row in callbacks]==list(range(1,count+1)),
         'every callback record appears once in its actual global sequence')
    for row in callbacks:
        need(set(row)==CALLBACK_KEYS and row['function']=='heap_caps_realloc' and row['caps']==6144 and
             row['core']==row['decoder_owner']==row['forwarded']==1 and row['isr']==0 and
             all(isinstance(row[k],int) and 0<row[k]<2**32 for k in ('bytes','attempt','generation')),
             'actual pinned SDK realloc(DEFAULT|INTERNAL) callback from the synchronous decoder owner')
        need(isinstance(row['stack_pointer'],int) and owner['stack_low']<=row['stack_pointer']<owner['stack_high'],
             'actual callback SP lies within the once-published decoder stack; no stack memory was read')
    if callbacks:
        need((fault['allocation_size'],fault['allocation_caps'])==(callbacks[-1]['bytes'],callbacks[-1]['caps']),
             'native health retains the last real callback size/caps')
    else:need(fault['allocation_size']==fault['allocation_caps']==0,'zero events retain zero health allocation details')
    need([row['attempt'] for row in nulls]==sorted({row['attempt'] for row in nulls}),
         'distinct failed actual realloc attempts retain owner order')
    need(all(row['attempt']<=end['realloc_calls'] for row in nulls),'failed attempts belong to the complete actual-call census')
    fault_index=next(i for i,(tag,_) in enumerate(rows) if tag=='CYD_F1_NATIVE_FAULTS')
    end_index=next(i for i,(tag,_) in enumerate(rows) if tag=='CYD_F1_ALLOC_COMPLETE')
    owner_index=next(i for i,(tag,_) in enumerate(rows) if tag=='CYD_F1_ALLOC_OWNER')
    need(owner_index<fault_index and all(owner_index<i for i,(tag,_) in enumerate(rows) if tag=='CYD_F1_REALLOC_NULL'),
         'actual public stack publication precedes every attributed failed return')
    word_ends=[(i,row) for i,(tag,row) in enumerate(rows) if tag=='CYD_F1_WORD_COMPLETE']
    need(len(word_ends)==1 and fault_index<word_ends[0][0]<end_index and
         word_ends[0][1]['live_planes']==word_ends[0][1]['live_bytes']==word_ends[0][1]['inflight']==0 and
         word_ends[0][1]['successes']==word_ends[0][1]['frees'] and
         not any(tag=='CYD_F1_WORD_HEAP' for tag,_ in rows[word_ends[0][0]+1:]),
         'all actual word ownership terminates before allocation accounting with no late operation')
    need(fault_index<end_index and all(i<fault_index for i,(tag,_) in enumerate(rows) if tag=='CYD_F1_REALLOC_NULL') and
         all(fault_index<i<end_index for i,(tag,_) in enumerate(rows) if tag=='CYD_F1_ALLOC_CALLBACK'),
         'complete fault snapshot and retained callbacks precede terminal checks; no late allocation event')
    entries={entry['id']:entry for entry in contract['entries']}
    plans={}
    for plan in contract['cases']:
        key=plan['name'];links=tuple(link['reference'] for link in plan['links'])
        need(key not in plans or plans[key]==links,'same-named schedules retain the exact original links')
        plans[key]=links
    active={};recoveries=[];last_time=0
    for index,(tag,row) in enumerate(rows):
        if tag=='CYD_F1_OBS_OPEN':
            active[row['instance']]=row
        elif tag=='CYD_F1_OBS_CLOSE':
            if row['result']==0:active.pop(row['instance'],None)
        elif tag=='CYD_F1_REALLOC_NULL':
            need(set(row)==NULL_KEYS and row['returned_pointer']==0 and row['real_returned']==1 and
                 row['core']==1 and row['priority']==5 and 0<row['bytes']<=23040 and row['time_us']>=last_time and
                 isinstance(row['old_pointer'],int) and 0<=row['old_pointer']<2**32,
                 'genuine returned nonzero small-byte realloc failure, original pointer and decoder profile')
            last_time=row['time_us']
            matched=[c for c in callbacks if c['attempt']==row['attempt']]
            need(len(matched)==row['callback_count']==1 and matched[0]['sequence']==row['callback_first'] and
                 matched[0]['bytes']==row['bytes'] and matched[0]['generation']==row['generation'],
                 'callback identity,size,generation and synchronous actual NULL are exactly correlated')
            need(row['fixture'] in plans and 0<=row['link']<len(plans[row['fixture']]) and
                 plans[row['fixture']][row['link']]==row['reference'] and row['reference'] in entries,
                 'failure belongs to a declared original family1 logical link')
            entry=entries[row['reference']];mapping=entry['mapping']
            planes=len(set(mapping)-{255});streams=set()
            for channel in mapping:
                if channel!=255:streams.add(channel//2 if channel<2*entry['coupled'] else channel-entry['coupled'])
            need(1<=planes<=8 and row['bytes']%(2*planes)==0,'whole unique-channel integer PCM planes from original public mapping')
            samples=row['bytes']//(2*planes);plane_bytes=(samples*2+3)&~3
            live=[o for o in active.values() if o['fixture']==row['fixture'] and o['link']==row['link'] and o['generation']==row['generation']]
            need(len(live)==len(streams) and all(o['kind']=='raw' for o in live) and {o['stream'] for o in live}==streams,
                 'all independently declared real raw stream owners are live at the failure')
            group=[];cursor=index+1
            while cursor<len(rows) and len(group)<2*planes:
                found,item=rows[cursor];cursor+=1
                need(found not in {'CYD_F1_REALLOC_NULL','CYD_F1_OBS_CALL','CYD_F1_OBS_CLOSE','CYD_F1_ALLOC_COMPLETE'},
                     'all replacement planes really allocate before decode resumes or owners close')
                if found=='CYD_F1_WORD_HEAP':group.append(item)
            need(len(group)==2*planes,'complete subsequent actual word allocation group')
            allocations=[]
            for before,after in zip(group[::2],group[1::2]):
                need(before['operation']==after['operation']=='ALLOC' and before['stage']=='BEFORE' and after['stage']=='AFTER' and
                     before['pointer']==0 and after['pointer']>0 and before['real_returned']==0 and after['real_returned']==1 and
                     all(before[k]==after[k] for k in ('allocation','generation','bytes','caps','fixture')) and
                     after['fixture']==row['fixture'] and after['generation']==row['generation'] and after['bytes']==plane_bytes and
                     after['caps']==2050 and after['core']==before['core']==1 and after['priority']==before['priority']==5,
                     'each original-mapping plane uses the actual successful INTERNAL|32BIT public return')
                allocations.append(after)
            need(len({a['pointer'] for a in allocations})==planes and len({a['allocation'] for a in allocations})==planes,
                 'every fallback plane is a distinct actual public allocation')
            resumed=set();completed=False;freed=set()
            for found,item in rows[cursor:]:
                if found=='CYD_F1_CONTROL_HTTP_OPEN':break
                if found=='CYD_F1_OBS_CALL' and item.get('fixture')==row['fixture'] and item.get('link')==row['link'] and item['result']==0 and item['decoded']>0:
                    need(item['kind']=='raw','fallback resumes genuine raw public decoders');resumed.add(item['stream'])
                if found=='CYD_F1_LINK' and item['fixture']==row['fixture'] and item['index']==row['link']:
                    need(item['reference']==row['reference'] and item['bytes']==entry['pcm_bytes'] and item['channels']==entry['channels'] and
                         item['layout']==1 and re.fullmatch('[a-f0-9]{64}',item['sha256']),
                         'same generation completes the whole original logical source PCM span')
                    completed=True
            for found,item in rows[cursor:]:
                if found=='CYD_F1_WORD_HEAP' and item['operation']=='FREE' and item['stage']=='AFTER':
                    for allocation in allocations:
                        if item['allocation']==allocation['allocation']:
                            need(all(item[k]==allocation[k] for k in ('pointer','bytes','caps','generation','fixture')) and item['real_returned']==1,
                                 'each recovery plane reaches its exact real public free')
                            need(item['allocation'] not in freed,'each recovery plane is freed once');freed.add(item['allocation'])
            need(resumed==streams and completed and len(freed)==planes,
                 'every raw stream resumes,whole current-generation PCM completes,and all recovery planes are freed')
            recoveries.append(dict(attempt=row['attempt'],callback=matched[0]['sequence'],fixture=row['fixture'],link=row['link'],
                reference=row['reference'],generation=row['generation'],byte_request=row['bytes'],planes=planes,
                plane_bytes=plane_bytes,allocation_ids=[a['allocation'] for a in allocations],exact_frees=len(freed)))
    need(len(recoveries)==count,'no callback is accepted by an unobserved or inferred recovery')
    return dict(completed=True,owner=owner,callbacks=callbacks,actual_null_returns=nulls,recoveries=recoveries,
        native_faults=fault,terminal=end,unknown_callbacks_allowed=False,scripted_failures=False,
        native_OOM_injection_qualified=False,physical_hardware=False)
