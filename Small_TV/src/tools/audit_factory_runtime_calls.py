"""Audit complete runtime bodies that own the five previously unmatched C.JAL sites."""
import argparse
import json
from pathlib import Path

from audit_factory_xrefs import sha
from reverse.runtime_call_gaps import load_objects, qualify


def main():
    """Read pinned images/objects and save a new report without editing firmware or SDK."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('factory','native','build','library','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Preserve existing runtime audit')
    inputs = {name:getattr(args,name).read_bytes() for name in ('factory','native','library')}
    parts = load_objects(args.build,args.library)
    report = qualify(inputs['factory'],inputs['native'],parts)
    if any(sha(getattr(args,name).read_bytes()) != sha(raw) for name,raw in inputs.items()):
        raise ValueError('Runtime audit input changed')
    report['inputs_unchanged'] = True
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(passed=True,functions={k:len(v['functions']) for k,v in report['variants'].items()},
                         output=str(args.output))))


if __name__ == '__main__':
    main()
