from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'.build/verify-web-evidence.py').read_text(encoding='utf-8')
source=source.replace('native-web-transfer-20261018','native-ota-transfer-20261018')
source=source.replace('native-web-evidence-git.json','native-ota-evidence-git.json')
exec(compile(source,__file__,'exec'))
