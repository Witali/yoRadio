"""Compare physical A/B boot readiness or externally captured interrupt latency."""
import argparse
import json
import math
from pathlib import Path
import statistics

from common import require


def summarize(samples):
    require(len(samples)>=30,'At least 30 measured samples per configuration are required')
    require(all(isinstance(v,(float,int)) and math.isfinite(v) and v>0 for v in samples),
            'Invalid or missing timing sample')
    ordered=sorted(samples)
    return dict(count=len(samples),median=statistics.median(samples),
                p99=ordered[math.ceil(.99*len(ordered))-1],maximum=max(samples))


def compare(before,after,max_ratio,budget):
    left,right=summarize(before),summarize(after)
    require(right['p99'] <= left['p99']*max_ratio,'P99 latency regression exceeds selected ratio')
    require(right['maximum'] <= budget,'Maximum latency exceeds selected absolute budget')
    return dict(baseline=left,candidate=right,p99_ratio=right['p99']/left['p99'])


def load(path,kind):
    data=json.loads(path.read_text())
    if kind=='boot':
        cases=[r for r in data['cases'] if r['name'].startswith('boot-ready:')]
        require(all(r['result']=='PASS' for r in cases),'A boot/readiness measurement failed')
        return [r['evidence']['ready_ms'] for r in cases]
    require(data.get('unit')=='us' and data.get('source')=='external-edge-capture',
            'IRQ tests require external edge measurements in microseconds')
    require(bool(data.get('firmware_sha256')) and bool(data.get('probe_description')),
            'Missing firmware/probe provenance')
    return data['latency_us']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--kind',choices=('boot','irq'),required=True)
    parser.add_argument('--max-ratio',type=float,default=1.25)
    parser.add_argument('--budget',type=float,required=True,help='Maximum ms for boot, us for IRQ')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=compare(load(args.baseline,args.kind),load(args.candidate,args.kind),args.max_ratio,args.budget)
    result.update(kind=args.kind,unit='ms' if args.kind=='boot' else 'us')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
