"""Replay controlled staged-output queue waits, retaining missing/failed evidence."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
SOURCES=ROOT/'sources' if (ROOT/'sources/tools').is_dir() else REPO
sys.path.insert(0,str(SOURCES/'tools/esp32c3_tests'))
from pipeline_flow import FIELDS, flow_summary
from staged_dma import parse as parse_dma
from heap_receive_correlation import paired_metrics
from tls_records import record_evidence

HELPER=SOURCES/'tests/results/esp32c3-qio80-recheck-20261008/sustained_summary.py'
spec=importlib.util.spec_from_file_location('sustained',HELPER)
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
PHASES=('profile-short','profile-long')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def strict_flow(rows,start,end,kind):
    result=flow_summary(rows,start,end,kind)
    selected=[];issues=[]
    marker='PERF FLOW_'+kind+':'
    fields=['gen','window_us']
    for field in FIELDS[kind]:
        fields += [field+'_us',field+'_n',field+'_max']
        if field!='submit': fields += [field+'_timeouts']
    if kind!='DEC': fields+=['overruns']
    for row in rows:
        if marker not in row['line']: continue
        pairs=re.findall(r'(\w+)=(\d+)\b',row['line'])
        values={k:int(v) for k,v in pairs}
        if row['line'].count('PERF ')!=1 or any(sum(k==f for k,v in pairs)!=1 for f in fields):
            issues.append(dict(reason='Missing, duplicate or merged field',row=row));continue
        if not math.isfinite(row['at']) or not values['window_us']:
            issues.append(dict(reason='Invalid time',row=row));continue
        duration=values['window_us']/1e6
        if start<=row['at']-duration and row['at']<=end:
            selected.append(dict(at=row['at'],seconds=duration,**values))
    coverage=helper.interval_coverage(selected,start,end)
    if [dict((k,v) for k,v in w.items() if k not in ('at','seconds')) for w in selected]!=result['windows']:
        issues.append(dict(reason='Strict and canonical field validation disagree'))
    generations={w['gen'] for w in selected}
    if len(generations)!=1: issues.append(dict(reason='Missing or changing generation'))
    result.update(coverage=coverage,issues=issues,intervals=selected,
        complete=not issues and not result['malformed'] and coverage['coverage_complete'])
    return result
