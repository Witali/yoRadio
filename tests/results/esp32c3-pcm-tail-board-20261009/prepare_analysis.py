"""Prepare the same strict sustained analysis plus separate PCM-tail replay."""
from pathlib import Path

root=Path(__file__).resolve().parent
previous=root.parent/'c3-input-prefill-20261009'
text=(previous/'summarize.py').read_text()
text=text.replace('Replay initial-prefill evidence without changing original verdicts.',
                  'Replay PCM-tail integration evidence without changing original verdicts.')
text=text.replace("sys.path.insert(0, str(REPO/", "SOURCES=ROOT/'sources' if (ROOT/'sources/tools').is_dir() else REPO\nsys.path.insert(0, str(SOURCES/")
text=text.replace("HELPER = REPO/", "HELPER = SOURCES/")
text=text.replace("(HELPER,Path(__file__),REPO/", "(HELPER,Path(__file__),SOURCES/")
text=text.replace('from staged_dma import parse as parse_dma',
                  'from staged_dma import parse as parse_dma\nfrom short_summary import summarize as summarize_short')
text=text.replace("    for name in ('restoration',", "    summary['phases']['short-pcm-tails']=summarize_short()\n    for name in ('restoration',")
text=text.replace("prefill_events=len(v['prefill'])", "prefill_events=len(v.get('prefill',[]))")
(root/'summarize.py').write_text(text)

text=(previous/'verify_evidence.py').read_text()
text=text.replace('Validate prefill evidence identity;', 'Validate PCM-tail evidence identity;')
text=text.replace("sys.path.insert(0,str(REPO/", "SOURCES=ROOT/'sources' if (ROOT/'sources/tools').is_dir() else REPO\nsys.path.insert(0,str(SOURCES/")
text=text.replace('esp32c3-idf-6.1-r9a97-input-prefill500', 'esp32c3-idf-6.1-r9a97-pcm-tail')
text=text.replace("expected_phases=['hev2-ten-minutes'", "expected_phases=['short-pcm-tails','hev2-ten-minutes'")
text=text.replace("    assert item['prefill'], 'Missing proof that prefill executed in '+name",
                  "    if name!='short-pcm-tails':\n        assert item['prefill'], 'Missing proof that prefill executed in '+name\n    else:\n        assert item['measured_cases']==60 and item['total']==62")
text=text.replace("prefill_events=len(item['prefill'])", "prefill_events=len(item.get('prefill',[]))")
(root/'verify_evidence.py').write_text(text)
