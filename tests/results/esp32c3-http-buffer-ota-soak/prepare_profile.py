import json
from pathlib import Path
root=Path(__file__).resolve().parent
diff=json.loads((root/'default-config-diff.json').read_text())['changes']
aliases={'CONFIG_FLASHMODE_DIO','CONFIG_FLASHMODE_QIO','CONFIG_ESPTOOLPY_FLASHMODE_VAL','CONFIG_L2_TO_L3_COPY','CONFIG_TCP_WND_DEFAULT','CONFIG_TCP_RECVMBOX_SIZE'}
lines=['# Exact runtime settings of the tested ESP-IDF 6.1 radio candidate.']
for key,values in diff.items():
    if key in aliases:continue
    lines.append('# '+key+' is not set' if values['tested']=='n' else key+'='+values['tested'])
dest=root/'tested-radio.defaults';assert not dest.exists();dest.write_text('\n'.join(lines)+'\n')
print(dest,len(lines)-1,'primary Kconfig settings')
