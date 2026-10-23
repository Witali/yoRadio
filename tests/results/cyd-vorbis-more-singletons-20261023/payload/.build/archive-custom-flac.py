from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
groups={'shared-eof':'flac-shared-component-eof','c3-maintenance-api':'flac-shared-c3-maintenance','sdk-components':'flac-shared-sdk-components'}
source=(root/'.build/archive-native-web.py').read_text()
source=source.replace('native-web-transfer-20261018','custom-flac-transfer-20261018')
source,count=re.subn(r'groups=\{.*?\n\}', 'groups='+repr(groups), source,count=1,flags=re.S)
assert count==1
exec(compile(source,__file__,'exec'))
