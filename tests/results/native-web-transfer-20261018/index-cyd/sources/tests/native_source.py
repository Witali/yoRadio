"""Follow include-only compatibility files when extracting production code."""
from pathlib import Path
import re


def canonical(path):
    path=Path(path).resolve()
    seen=set()
    while path not in seen:
        seen.add(path)
        text=path.read_text()
        text=re.sub(r'//[^\n]*|/\*.*?\*/','',text,flags=re.S)
        text=re.sub(r'^\s*#pragma once[^\n]*','',text,flags=re.M).strip()
        forward=re.fullmatch(r'#include\s+"([^"]+)"\s*',text)
        if not forward:return path
        target=(path.parent/forward[1]).resolve()
        if not target.is_file():return path
        path=target
    raise ValueError(f'Cyclic include-only compatibility source: {path}')


def source_closure(paths):
    return list(dict.fromkeys([*paths,*(canonical(path) for path in paths),Path(__file__).resolve()]))
