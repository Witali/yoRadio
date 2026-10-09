"""Frozen exact EOF replay, including interrupted-observation rejection."""
def verdict(name, check):
    try:
        evidence=check()
        return dict(name=name,result='PASS',evidence=evidence)
    except (AssertionError,ValueError,IndexError,KeyError,StopIteration) as error:
        return dict(name=name,result='FAIL',reason=str(error))

def eof_evidence(playing, tail, name):
    assert playing['case']==name+':playing' and tail['case']==name+':terminal','Unexpected EOF observation order'
    assert not playing.get('interrupted') and not tail.get('interrupted'),'Interrupted EOF observation; retain the original failure'
    assert any(s['audio'] and s.get('pcm_sample_rate') for s in playing['samples']),'No decoded playback'
    samples=tail['samples']
    stopped=next(i for i,s in enumerate(samples) if not s['audio'])
    assert len(samples)-stopped>=2,'No confirmed stopped state'
    assert all(not s['audio'] and s['format']=='stream ended' and not s['pcm_sample_rate']
               and not s['pcm_channels'] for s in samples[stopped:]),'Stale or failed terminal state'
    return dict(terminal_samples=len(samples)-stopped,
                scope='REST samples replayed; WebSocket verdict is original evidence only.')
