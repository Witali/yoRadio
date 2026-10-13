"""Check real-library late SBR OOM, malformed input, cleanup and recovery in QEMU."""
from collections import Counter
import re
import sys

import run_aac_bfp16 as common
from run_aac_metadata import parse_log as parse_metadata


def parse_pressure(log):
    if re.search(r'assert failed|Guru Meditation|CORRUPT HEAP|aac_pointer: field=', log):
        raise ValueError('Pressure test runtime failure')
    rows = re.findall(r'AAC_EARLY_PRESSURE_CASE early=([01]) target=(\d+) available=(\d+) pending=([01]) '
                      r'lc_result=(-?\d+) lc_frames=(\d+) recovery_frames=15 heap_restored=1', log)
    targets = list(range(32*1024, 112*1024+1, 4*1024))
    if (len(rows) != log.count('AAC_EARLY_PRESSURE_CASE ')
            or [(int(r[0]), int(r[1])) for r in rows] != [(e,t) for e in (0,1) for t in targets]):
        raise ValueError('Incomplete, unordered or duplicate pressure sweep')
    cases = [dict(zip(('early', 'target', 'available', 'pending', 'lc_result', 'lc_frames'), map(int, row)))
             for row in rows]
    for row in cases:
        if not row['target']-64 <= row['available'] <= row['target']+4096:
            raise ValueError('Heap pressure was not applied')
        if row['lc_result'] not in (0, -1, -2) or not 0 <= row['lc_frames'] <= 13:
            raise ValueError('Unexpected LC outcome under pressure')
        if row['lc_result'] == 0 and row['lc_frames'] != 13:
            raise ValueError('Incomplete LC playback accepted')
    totals = re.findall(r'AAC_EARLY_PRESSURE_PASS early=([01]) cases=(\d+) lc_success=(\d+) '
                        r'lc_failure=(\d+) reserved=(\d+) heap=valid', log)
    if (len(totals) != 2 or log.count('AAC_EARLY_PRESSURE_PASS ') != 2
            or re.findall(r'AAC_EARLY_PRESSURE_BEGIN real_heap=1 early=([01])', log) != ['0','1']):
        raise ValueError('Missing pressure success/failure/recovery coverage')
    summaries=[]
    for early in (0,1):
        group=[row for row in cases if row['early']==early]
        successes=sum(row['lc_result']==0 for row in group)
        reserved=sum(row['pending'] for row in group)
        expected=(early,len(group),successes,len(group)-successes,reserved)
        if (tuple(map(int,totals[early]))!=expected or not 0<successes<len(group)
                or bool(reserved)!=bool(early)):
            raise ValueError('Incorrect pressure summary or reservation control')
        summaries.append(dict(early=early,lc_success=successes,lc_failure=len(group)-successes))
    for control,candidate in zip(cases[:len(targets)],cases[len(targets):]):
        if control['lc_result']==0 and candidate['lc_result']!=0:
            raise ValueError('Early owner regresses LC under matched pressure')
    if log.count('AAC_EARLY_PRESSURE_AB_PASS cases=42 no_lc_regression=1')!=1:
        raise ValueError('Missing pressure A/B completion')
    return dict(cases=cases, summaries=summaries,
                recovery_frames=15*len(cases), heap_restored=True,
                scope='Real QEMU heap capacity sweep; no Wi-Fi/TLS or hardware timing qualification')


def parse_log(log, *, require_early_owner=False):
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
    result = dict(faults_pass=True, precision_qualified=False, hardware_tested=False,
                summaries=[], late_oom_cases=4, malformed_cases=4,
                recovery_frames=120, metadata=metadata, outcomes=outcomes)
    if require_early_owner or 'AAC_EARLY_PRESSURE_' in log:
        result['early_owner_pressure'] = parse_pressure(log)
    return result


if __name__ == '__main__':
    parser = common.make_parser(__doc__, 'faults-pc19')
    parser.add_argument('--require-early-owner', action='store_true')
    args = parser.parse_args()
    if args.require_early_owner and '#define CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER 1\n' not in (args.build/'config/sdkconfig.h').read_text():
        parser.error('Early compact owner is not enabled in this test image')
    sys.exit(common.run(args, log_parser=lambda log: parse_log(log, require_early_owner=args.require_early_owner), config_key='YORADIO_QEMU_AAC_LATE_SBR_TEST',
                       pass_key='faults_pass', validation_label='AAC fault handling'))
