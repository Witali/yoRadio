"""Read client trace files; capture host TCP metadata after a 10048, no board I/O."""
import json
from pathlib import Path
import subprocess
import threading
import time


class FailureMonitor:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.closed = threading.Event()
        self.rows = []
        self.thread = threading.Thread(target=self.read, daemon=True)
        self.thread.start()

    def read(self):
        offsets = {}
        seen = set()
        while not self.closed.wait(.2):
            for path in self.directory.glob('*-request-phases.jsonl'):
                with path.open() as source:
                    source.seek(offsets.get(path,0))
                    while True:
                        line = source.readline()
                        if not line or not line.endswith('\n'): break
                        offsets[path] = source.tell()
                        try: row = json.loads(line)
                        except json.JSONDecodeError: continue
                        key = (path.stem,row['request'])
                        if row.get('winerror') != 10048 or key in seen: continue
                        seen.add(key)
                        output = self.directory/(path.stem+'-'+str(row['request'])+'-host-sockets.json')
                        event = dict(trace=path.name,request=row['request'],failure_at=row['at'],
                                     detected_at=time.monotonic(),output=output.name)
                        self.rows.append(event)
                        try:
                            result = subprocess.run(['powershell.exe','-NoProfile','-File',
                                str(Path(__file__).with_name('capture-sockets.ps1')),
                                '-Output',str(output)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
                            event.update(code=result.returncode,exists=output.exists())
                        except Exception as error:
                            event['exception'] = type(error).__name__
                        event['ended_at'] = time.monotonic()
                        (self.directory/'host-failure-monitor.json').write_text(json.dumps(self.rows,indent=2)+'\n')

    def close(self):
        self.closed.set()
        self.thread.join(25)
        assert not self.thread.is_alive(), 'Host snapshot monitor did not stop'
        (self.directory/'host-failure-monitor.json').write_text(json.dumps(self.rows,indent=2)+'\n')
