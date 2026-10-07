"""Check real-library late SBR OOM, malformed input, cleanup and recovery in QEMU."""
from collections import Counter
import re
import sys

import run_aac_bfp16 as common
from run_aac_metadata import parse_log as parse_metadata


def parse_log(log):
    metadata = parse_metadata(log)
    if re.search(r'CORRUPT HEAP|aac_pointer: field=', log):
        raise ValueError('Heap or pointer audit failure')
    oom = re.findall(r'AAC_LATE_OOM_PASS parity=([01]) allocation=(owner|control) '
                     r'suppressed_pcm=1 recovery_frames=15', log)
    expected_oom = Counter((str(parity), allocation) for parity in (0, 1)
                           for allocation in ('owner', 'control'))
    if Counter(oom) != expected_oom or log.count('AAC_LATE_OOM_PASS ') != 4:
        raise ValueError('Missing/duplicate late SBR allocation failure or recovery')
    malformed = re.findall(r'AAC_MALFORMED_PASS case=(\w+) recovery_frames=15', log)
    expected_malformed = Counter(('header_only', 'sbr_truncated',
                                  'sbr_count_overrun', 'fill_count_overrun'))
    if Counter(malformed) != expected_malformed or log.count('AAC_MALFORMED_PASS ') != 4:
        raise ValueError('Missing/duplicate malformed input or recovery')
    if (log.count('AAC_FAULTS_PASS late_oom=4 malformed=4 recoveries=8 heap=valid') != 1
            or log.count('AAC_FAULTS_PASS ') != 1):
        raise ValueError('Missing/duplicate fault suite completion')
    blocks = log.split('AAC_FAULT_BEGIN ')[1:]
    outcomes = []
    for block in blocks:
        name = block.splitlines()[0]
        status = re.findall(r'AAC_FAULT_OUTCOME public_error=(-?\d+) pcm_bytes=0', block)
        if len(status) != 1 or block.count('AAC_FAULT_OUTCOME ') != 1:
            raise ValueError('Missing/duplicate fault outcome')
        error = int(status[0])
        if name.startswith('kind=late_oom '):
            if error != -2:
                raise ValueError('Late OOM must report memory failure')
        elif name.startswith('kind=malformed '):
            if error not in (0, -1, -3, -4):
                raise ValueError('Unexpected malformed-frame result')
        else:
            raise ValueError('Unknown fault case')
        outcomes.append(dict(case=name, public_error=error, pcm_bytes=0))
    expected_begins = Counter('kind=late_oom parity='+parity+' allocation='+allocation
                              for parity, allocation in expected_oom)
    expected_begins.update('kind=malformed case='+name for name in expected_malformed)
    if Counter(row['case'] for row in outcomes) != expected_begins:
        raise ValueError('Incomplete fault begin/outcome matrix')
    return dict(faults_pass=True, precision_qualified=False, hardware_tested=False,
                summaries=[], late_oom_cases=4, malformed_cases=4,
                recovery_frames=120, metadata=metadata, outcomes=outcomes)


if __name__ == '__main__':
    args = common.make_parser(__doc__, 'faults-pc19').parse_args()
    sys.exit(common.run(args, log_parser=parse_log, config_key='YORADIO_QEMU_AAC_LATE_SBR_TEST',
                       pass_key='faults_pass', validation_label='AAC fault handling'))
