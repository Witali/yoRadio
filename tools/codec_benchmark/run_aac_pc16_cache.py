#!/usr/bin/env python3
"""Validate reconstructed PS-value caching and retain the paired PCM evidence."""
import sys
import run_aac_bfp16 as common
import run_aac_pc16_write as port

def parse_log(log):
    result=port.parse_log(log)
    for s in result['storage']:
        active=s['variant']==1 and s['calls']>0
        if s['cache_bytes']!=(288 if active else 0):
            raise ValueError('Wrong cache memory accounting')
        if active:
            if min(s['cache_hits'],s['cache_misses'])<=0:
                raise ValueError('Decoded-value cache not exercised')
            if s['cache_hits']+s['cache_misses']!=s['stores']:
                raise ValueError('Missing delay read/write coverage')
        elif s['cache_hits'] or s['cache_misses']:
            raise ValueError('Unexpected cache use in native control')
    result.update(experiment='espressif_ps_pc16_decoded_cache',
                  cache_stack_bytes=288,cache_lifetime='one PS decorrelation call')
    return result

if __name__=='__main__':
    args=common.make_parser(__doc__,'pc16-cache').parse_args()
    sys.exit(common.run(args,log_parser=parse_log,config_key='YORADIO_AAC_PS_PC16_CACHE',axis='variant'))
