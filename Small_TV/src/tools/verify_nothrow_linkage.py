"""Verify the real NVS allocation caller selects the new no-exceptions wrappers."""
import argparse
import json
from pathlib import Path

from reverse.nothrow_linkage import verify


def main():
    """Save new build evidence only after matching complete wrapper and NVS bodies."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('elf','app','object','nvs','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Preserve existing nothrow linkage report')
    report=verify(args.elf.read_bytes(),args.app.read_bytes(),args.object.read_bytes(),args.nvs.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(passed=True,functions=len(report['functions']),nvs=report['nvs_page_load']['name'])))


if __name__=='__main__':main()
