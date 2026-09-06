"""Verify the ordinary PDM weak-tone observation directly from saved bits."""
import argparse
import json
from pathlib import Path
import numpy as np
import measure_pdm_matrix as model
from measure_rcpdm_feedback_ab import save


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args=parser.parse_args()
    report=json.loads(args.report.read_text(encoding="utf-8"))
    if not report["complete"]:
        raise ValueError("Comparison is not complete")
    result=dict(report_sha256=model.original.sha(args.report), source_sha256=model.original.sha(Path(__file__)),
        bit_rate_hz=6144000, trim_frames_each_end=12000, cases=[])
    for case_id in ("zero", "tone-1000hz-60db", "tone-1000hz-80db"):
        case=next(c for c in report["cases"] if c["id"]==case_id)
        inputs=np.fromfile(model.ROOT/case["pcm"], dtype="<i2")
        if model.original.sha(model.ROOT/case["pcm"])!=case["pcm_sha256"]:
            raise ValueError("Input PCM changed")
        row=dict(id=case_id, pcm_min=int(inputs.min()), pcm_max=int(inputs.max()),
            nonzero_pcm_samples=int(np.count_nonzero(inputs)), variants={})
        for name in report["configs"]:
            file=args.capture/f"{case_id}.{name}.bin"
            if model.original.sha(file)!=case["bitstream_sha256"][name]:
                raise ValueError("Bitstream changed")
            words=np.fromfile(file, dtype="<u4")[12000*4:-12000*4]
            unique=np.unique(words)
            alternating=bool(len(unique)==1 and unique[0] in (0x55555555,0xaaaaaaaa))
            row["variants"][name]=dict(bitstream_sha256=case["bitstream_sha256"][name],
                words_checked=len(words), unique_words=len(unique), alternating_only=alternating,
                constant_word=hex(int(unique[0])) if len(unique)==1 else None)
        result["cases"].append(row)
    weak=next(c for c in result["cases"] if c["id"]=="tone-1000hz-80db")
    if not weak["nonzero_pcm_samples"] or not weak["variants"]["pdm128"]["alternating_only"]:
        raise ValueError("Weak-PDM observation was not reproduced")
    save(args.output, result)
    print(json.dumps(result, indent=2))


if __name__=="__main__":
    main()
