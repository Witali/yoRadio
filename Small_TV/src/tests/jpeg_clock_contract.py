"""Require complete clean clock pixels and bounded progress over the whole decode."""
from copy import deepcopy
import datetime as dt


def validate(report):
    """Reject a short, paused-clock, native-only or falsely labeled successful run."""
    def require(value,message):
        if not value:raise ValueError('JPEG clock: '+message)

    require(report['passed'] and report['inputs_unchanged'] and report['complete_theme_matrix'],'partial/changing run')
    require(report['network_acceptance'] is False and report['hardware_tested'] is False,'LCD proof mislabeled')
    require(set(report['themes'])=={'classic','simple','dial'},'missing clock theme')
    for theme,flow in report['themes'].items():
        require(flow['passed'] and flow['owners_stopped'] and flow['theme']==theme,'failed/unreaped theme')
        require(flow['control']==report['control'],'mixed workload')
        checks={'all_pixels_checked','real_minute_rollover','hardware_breakpoints_only','no_guest_state_writes','protected_flash_exact'}
        require(checks<=set(flow['checks']) and all(flow['checks'][k] for k in checks),'missing integrity check')
        frames=flow['frames'];require(len(frames)>=3,'too few complete frames')
        times=[]
        for row in frames:
            require(row['passed'] and row['compared_pixels']==57600 and row['different_pixels']==0 and
                    row['factory_different_pixels']==0 and row['actual_sha256']==row['native_sha256']==row['factory_sha256'],
                    'incomplete or different full-frame reference')
            require(row['code_unchanged'] and row['backlight']['brightness']==1000,'code/brightness changed')
            require(not row['background'],'wrong owner')
            if not report['control']:require(row['source_slot']==4,'wrong active decode source')
            require(row['active']==row['active_end']==(not report['control']),'no actual foreground decode overlap')
            c=row['clock'];stamp=dt.datetime(c['year'],c['month'],c['day'],c['hour'],c['minute'],c['second'])
            require(stamp.date()==dt.date(2026,10,13) and stamp.hour==20,'wrong synchronized calendar')
            times.append(stamp)
        require(len(set(times))>=3 and len({(t.hour,t.minute) for t in times})>=2,'frozen clock/missing minute rollover')
        require(all(a<=b for a,b in zip(times,times[1:])),'calendar moved backward')
        gaps=[b['guest_seconds']-a['guest_seconds'] for a,b in zip(frames,frames[1:])]
        require(all(0<=gap<=2.5 for gap in gaps) and flow['max_frame_gap_guest_seconds']==max(gaps),'unbounded frame gap')
        if not report['control']:
            require(flow['decoder_status']==0 and flow['finish_status']==200 and flow['finish_body']=='OK','decode did not complete')
            require(flow['decoder_entry'] and flow['decoder_return'],'missing actual decoder boundaries')
            require(0<=frames[0]['guest_seconds']-flow['decoder_entry_guest']<=2.5 and
                    0<=flow['decoder_exit_guest']-frames[-1]['guest_seconds']<=2.5,'unobserved decode prefix/tail')


def rejection_checks(report):
    """Prove green flags cannot waive overlap, factory pixels, clock or whole-duration coverage."""
    validate(report)
    flow=lambda data:data['themes']['simple']
    mutations=[
        ('missing-theme',lambda x:x['themes'].pop('dial')),
        ('unreaped',lambda x:flow(x).update(owners_stopped=False)),
        ('partial-pixels',lambda x:flow(x)['frames'][0].update(compared_pixels=57599)),
        ('wrong-pixel',lambda x:flow(x)['frames'][0].update(different_pixels=1)),
        ('native-only',lambda x:flow(x)['frames'][0].update(factory_different_pixels=1)),
        ('code-write',lambda x:flow(x)['frames'][0].update(code_unchanged=False)),
        ('wrong-owner',lambda x:flow(x)['frames'][0].update(background=True)),
        ('too-few-frames',lambda x:flow(x).update(frames=flow(x)['frames'][:2])),
        ('missing-rollover',lambda x:[r['clock'].update(minute=34) for r in flow(x)['frames']]),
        ('frame-gap',lambda x:flow(x)['frames'][-1].update(guest_seconds=flow(x)['frames'][-2]['guest_seconds']+3)),
        ('network-label',lambda x:x.update(network_acceptance=True)),
        ('missing-protection',lambda x:flow(x)['checks'].pop('protected_flash_exact')),
    ]
    if not report['control']:
        mutations.extend([
            ('no-decode-overlap',lambda x:flow(x)['frames'][0].update(active=False)),
            ('wrong-source',lambda x:flow(x)['frames'][0].update(source_slot=0)),
            ('failed-decode',lambda x:flow(x).update(finish_status=400)),
            ('unobserved-tail',lambda x:flow(x).update(decoder_exit_guest=flow(x)['frames'][-1]['guest_seconds']+3)),
        ])
    result=[]
    for name,mutate in mutations:
        changed=deepcopy(report);mutate(changed)
        try:validate(changed)
        except ValueError:result.append(name)
        else:raise ValueError('JPEG clock contract accepted '+name)
    return result
