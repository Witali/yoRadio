"""Validate native AAC profile/source channels; does not qualify PCM precision."""
from collections import Counter
import re
import sys

import run_aac_bfp16 as common


def parse_log(log):
    if 'QEMU_AAC_FORMAT_PASS' not in log or re.search(r'assert failed|Guru Meditation|AAC_METADATA_FAILURE',log):
        raise ValueError('Incomplete or failed native AAC metadata run')
    rows=re.findall(r'AAC_METADATA_CASE case=(\w+) label=(\S+) source_channels=(\d+) '
                    r'pcm_channels=(\d+) rate=(\d+) frames=(\d+)',log)
    expected={
        'lc_48000_stereo':('AAC',2,2,48000,26),
        'he_48000_stereo':('HE-AAC',2,2,48000,15),
        'hev2_44100_stereo':('HE-AACv2',2,2,44100,15),
        'he_mono_metadata':('HE-AAC',1,2,32000,11),
    }
    resets=log.count('AAC_METADATA_RESET_PASS')
    if resets not in (0,1):raise ValueError('Duplicate reset evidence')
    counts=Counter(name for name,*_ in rows)
    if counts != Counter(lc_48000_stereo=1,he_48000_stereo=1,hev2_44100_stereo=2,he_mono_metadata=2+resets):
        raise ValueError('Incomplete profile/reopen/independent-decoder coverage')
    for name,label,*values in rows:
        if (label,*map(int,values))!=expected[name]:raise ValueError('Wrong native metadata: '+name)
    end=re.findall(r'AAC_METADATA_PASS frames=(\d+) decoder_isolation=2 mono_duplicated=verified heap=valid',log)
    if len(end)!=1 or int(end[0])!=sum(int(row[-1]) for row in rows):
        raise ValueError('Incomplete metadata frame coverage')
    return dict(metadata_pass=True,precision_qualified=False,summaries=[],
                frames=int(end[0]),resets=resets,cases=[dict(case=name,label=label,
                source_channels=int(source),pcm_channels=int(pcm),rate=int(rate),frames=int(frames))
                for name,label,source,pcm,rate,frames in rows])


if __name__=='__main__':
    args=common.make_parser(__doc__,'metadata').parse_args()
    sys.exit(common.run(args,log_parser=parse_log,config_key='YORADIO_QEMU_AAC_TEST',
                       pass_key='metadata_pass',validation_label='Native metadata'))
