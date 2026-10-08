import hashlib,json,re,subprocess
from pathlib import Path
root=Path('.build/c3-flac-watchdog-20261008')
variants={'physical':'floor','profile-physical':'profile'}
summary={}
for directory,variant in variants.items():
 p=root/directory
 final=json.loads((p/'final-board.json').read_text())
 assert final['result']=='PASS'
 cases=[];faults=[];cpu=[];rssi=[]
 for suite in sorted(p.glob('flac-*')):
  if not suite.is_dir():continue
  report=json.loads((suite/'report.json').read_text())
  cases.extend(dict(cycle=suite.name,**r) for r in report['cases'] if r['name']!='restore-board')
  rows=json.loads((suite/'performance.json').read_text())
  faults.extend(dict(cycle=suite.name,**r) for r in rows if re.search('PANIC|Runtime watchdog|allocation failed|TLS failure|decode (?:error|failed)',r['line']))
  for r in rows:
   if 'PERF CPU:' in r['line']:
    cpu.append(dict(at=r['at'],**{k:float(v) for k,v in re.findall(r'(busy|idle|stream|decode|output|wifi|tcpip|web)=([0-9.]+)%',r['line'])}))
  for batch in json.loads((suite/'status.json').read_text()):
   rssi.extend(s['rssi'] for s in batch['samples'] if 'rssi' in s)
 addresses=sorted({address for row in faults for address in re.findall(r'(?:MEPC|RA)=(0x[0-9a-f]+)',row['line'])})
 build=Path('idf/esp32c3-oled-native')/('build-idf-6.1-r9a97f6c54ec6-rx6-reserve-'+variant)
 symbols=''
 if addresses:
  addr2line='C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-addr2line.exe'
  symbols=subprocess.check_output([addr2line,'-a','-f','-C','-e',str(build/'yoradio_esp32c3_oled_native.elf'),*addresses],text=True)
  (root/(variant+'-fault-symbols.txt')).write_text(symbols)
 image=Path('firmware/development')/('esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-'+variant)
 summary[variant]=dict(image=json.loads((image/'manifest.json').read_text())['image'],cases=cases,
  passed=sum(r['result']=='PASS' for r in cases),total=len(cases),faults=faults,
  watchdog_replays=[r for r in faults if 'events=' in r['line']],
  allocation_failures=sum('allocation failed' in r['line'] or 'allocation_bytes=' in r['line'] for r in faults),
  cpu_samples=len(cpu),cpu_peaks={key:max(row[key] for row in cpu) for key in ('busy','tcpip','web')},
  rssi_range=[min(rssi),max(rssi)],restored=final['result'])
(root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for variant,data in summary.items():print(variant,{k:data[k] for k in ('passed','total','allocation_failures','watchdog_replays','cpu_peaks','rssi_range')})
