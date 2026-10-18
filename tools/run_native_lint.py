"""Run esp-clang-tidy over every project-owned C/C++ unit in an IDF build.

Configure a separate IDF_TOOLCHAIN=clang build with its own sdkconfig first.
The production GCC build and external SDK/vendor sources are left untouched.
Warnings are retained for triage; parse/tool errors make the run incomplete.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC = re.compile(r'^(.*?):(\d+):(\d+): (warning|error): (.*?)(?: \[([^\]]+)\])?$', re.M)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', required=True, type=Path)
    parser.add_argument('--clang-tidy', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--jobs', type=int, default=2)
    args = parser.parse_args()
    build = args.build_dir.resolve()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)  # Preserve earlier complete/failed runs.
    entries = json.loads((build/'compile_commands.json').read_text())
    files = set()
    for entry in entries:
        path = Path(entry['file'])
        if not path.is_absolute():
            path = Path(entry['directory'])/path
        path = path.resolve()
        if path.suffix.lower() not in ('.c', '.cc', '.cpp', '.cxx') or not path.is_relative_to(ROOT):
            continue
        relative = path.relative_to(ROOT)
        if any(part.startswith('build') or part.startswith('.') for part in relative.parts[:-1]):
            continue
        files.add(path)
    if not files:
        raise RuntimeError('No project-owned translation units in the compilation database')
    # Match both slash conventions in Clang's header paths on Windows.
    header_filter = re.escape(ROOT.as_posix()).replace('/', r'[/\\]') + r'[/\\]'
    config = ROOT/'.clang-tidy'
    version = subprocess.check_output([str(args.clang_tidy), '--version'], text=True)

    def check(path):
        relative = path.relative_to(ROOT).as_posix()
        stem = relative.replace('/', '__')
        command = [str(args.clang_tidy), str(path), '-p', str(build),
                   '--config-file='+str(config), '--header-filter='+header_filter,
                   '--export-fixes='+str(out/(stem+'.yaml'))]
        try:
            result = subprocess.run(command, cwd=ROOT, capture_output=True,
                                    text=True, encoding='utf-8', errors='replace', timeout=180)
            code = result.returncode
            log = result.stdout + result.stderr
        except subprocess.TimeoutExpired as error:
            code = -1
            log = 'Analysis timed out after 180 seconds\n'
            for data in (error.stdout, error.stderr):
                if data:
                    log += data.decode(errors='replace') if isinstance(data, bytes) else data
        (out/(stem+'.log')).write_text(log, encoding='utf-8')
        diagnostics = [dict(file=m[0], line=int(m[1]), column=int(m[2]),
                            severity=m[3], message=m[4], check=m[5])
                       for m in DIAGNOSTIC.findall(log)]
        errors = [d for d in diagnostics if d['severity']=='error']
        print(f'{relative}: exit={code}, warnings={sum(d["severity"]=="warning" for d in diagnostics)}, errors={len(errors)}', flush=True)
        return dict(file=relative, source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    returncode=code, complete=code==0 and not errors, diagnostics=diagnostics)

    with ThreadPoolExecutor(max_workers=max(1,args.jobs)) as pool:
        results = list(pool.map(check, sorted(files)))
    report = dict(tool=version.strip(), build_dir=build.relative_to(ROOT).as_posix(),
                  config_sha256=hashlib.sha256(config.read_bytes()).hexdigest(),
                  source_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
                  dirty=bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=no'], cwd=ROOT, text=True).strip()),
                  units=len(results), complete=all(r['complete'] for r in results), results=results)
    # A complete analysis with warnings is a baseline, not a clean-code claim.
    report['warnings'] = sum(d['severity']=='warning' for r in results for d in r['diagnostics'])
    report['errors'] = sum(d['severity']=='error' for r in results for d in r['diagnostics'])
    (out/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'Analysis complete={report["complete"]}: {len(results)} units, {report["warnings"]} warnings, {report["errors"]} errors')
    return 0 if report['complete'] else 1


if __name__=='__main__':
    sys.exit(main())
