from pathlib import Path
import importlib.util
import json
import sys

control = Path(sys.argv.pop(1)).resolve(strict=True)
repo = Path.cwd().resolve()
assert control.is_relative_to(repo / ".build")
spec = importlib.util.spec_from_file_location("openeth", repo / "tests/run-cyd-full-app-openeth.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
original = runner.station_fixture

def fixture(codec):
    assert codec == "flac"
    data = control.read_bytes()
    frames, md5 = runner.flac_streaminfo(data)
    baseline = original(codec)
    assert (frames, md5) == (baseline["pcm_frames"], baseline["pcm_md5"])
    return dict(baseline, data=data)

runner.station_fixture = fixture
raise SystemExit(runner.main())
