"""Compare complete factory NVS functions with pinned SDK objects and current production."""
import argparse
import json
from pathlib import Path

from reverse.factory_nvs import native_object, qualify


def main():
    """Write a new static report without modifying either firmware image or SDK."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('factory', 'object', 'native', 'app', 'nvs', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('Preserve existing NVS qualification')
    report = qualify(args.factory.read_bytes(), args.object.read_bytes(), args.native.read_bytes(),
                     args.app.read_bytes(), native_object(args.nvs.read_bytes()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(passed=True, functions={k: len(v['functions']) for k, v in report['variants'].items()})))


if __name__ == '__main__': main()
