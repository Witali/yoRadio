"""Check ICY wire boundaries, negotiation, pacing accounting and reference PCM."""
import hashlib
from io import BytesIO
from pathlib import Path
import shutil
import subprocess
import sys
import time
import unittest
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from audio_test_server.icy import IcyFramer
from audio_test_server.server import Server
from audio_test_server.fixtures import load_fixtures


def strip_icy(wire, interval):
    stream, audio, metadata = BytesIO(wire), bytearray(), []
    while True:
        block = stream.read(interval)
        audio.extend(block)
        if len(block) < interval:
            break
        length = stream.read(1)
        assert len(length) == 1
        payload = stream.read(length[0]*16)
        assert len(payload) == length[0]*16
        metadata.append(payload)
    return bytes(audio), metadata


class IcyServerTest(unittest.TestCase):
    def test_validation(self):
        for interval in (True, -1, 0, 1.5, 2**31):
            with self.assertRaises(ValueError): IcyFramer(interval)
        for metadata in ([], [b'x'*4081], ['text']):
            with self.assertRaises(ValueError): IcyFramer(1, metadata)

    def test_boundaries_and_fragmentation(self):
        metadata = (b'', b"StreamTitle='A';", b'x'*4080)
        for interval in (1, 16, 1023, 4096, 45000):
            for size in (0, interval-1, interval, interval+1, interval*4):
                audio = bytes(i % 256 for i in range(size))
                for chunk in (7, 1024):
                    with self.subTest(interval=interval, size=size, chunk=chunk):
                        framer = IcyFramer(interval, metadata)
                        wire = b''.join(framer.feed(audio[i:i+chunk]) for i in range(0,size,chunk))
                        restored, blocks = strip_icy(wire, interval)
                        self.assertEqual(restored, audio)
                        self.assertEqual(len(wire), framer.wire_length(size))
                        self.assertEqual(len(blocks), size//interval)
                        self.assertEqual(len(wire)-size, framer.metadata_bytes)
                        for i, block in enumerate(blocks):
                            expected = metadata[i % len(metadata)]
                            self.assertEqual(block, expected.ljust((len(expected)+15)//16*16,b'\0'))

    def test_http_negotiation_and_accounting(self):
        data = bytes(range(256))*41
        specs = {'test':dict(data=data,seconds=.05,codec='mp3',mime='audio/mpeg')}
        with Server('127.0.0.1',0,specs,icy_interval=1023,delivery_stats=True,pacing_ratio=1.0) as server:
            for requested in (False, True):
                headers = {'Icy-MetaData':'1'} if requested else {}
                request = Request(f'http://127.0.0.1:{server.http.server_port}/file/test',headers=headers)
                with urlopen(request,timeout=5) as response:
                    wire = response.read()
                    self.assertEqual(int(response.headers['Content-Length']), len(wire))
                    self.assertEqual(response.headers.get('icy-metaint'), '1023' if requested else None)
                self.assertEqual(strip_icy(wire,1023)[0] if requested else wire, data)
                deadline = time.perf_counter()+2
                while not server.events[-1].get('seconds') and time.perf_counter()<deadline:
                    time.sleep(.005)
                event = server.events[-1]
                self.assertTrue(event['complete'])
                self.assertEqual(event['sent'],len(data))
                self.assertEqual(sum(w['bytes'] for w in event['delivery']['windows']),len(wire))
                if requested:
                    self.assertEqual(event['wire_sent'],len(wire))
                    self.assertEqual(event['icy_insertions'],len(data)//1023)
                    self.assertEqual(event['icy_metadata_bytes'],len(wire)-len(data))

    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required for independent PCM comparison')
    def test_ffmpeg_pcm_equivalence(self):
        specs = load_fixtures()
        name = 'mp3-320'
        command = ['ffmpeg','-hide_banner','-loglevel','error','-i']
        tail = ['-f','s16le','-acodec','pcm_s16le','pipe:1']
        plain = subprocess.run(command+['pipe:0']+tail,input=specs[name]['data'],capture_output=True,check=True,timeout=20)
        self.assertGreater(len(plain.stdout),100000)
        for interval in (1023, 45000):
            with Server('127.0.0.1',0,specs,unpaced_files=True,icy_interval=interval,
                        icy_metadata=(b"StreamTitle='Test';",b'',b'x'*4080)) as server:
                url = f'http://127.0.0.1:{server.http.server_port}/file/{name}'
                framed = subprocess.run(command+[url]+tail,capture_output=True,check=True,timeout=20)
                self.assertEqual(framed.stderr,b'')
                self.assertEqual(hashlib.sha256(framed.stdout).digest(),hashlib.sha256(plain.stdout).digest())
                self.assertGreater(server.events[0]['icy_insertions'],0)

    def test_cli_entry_points(self):
        for entry in ([str(ROOT/'tools/audio_test_server/server.py')], ['-m','tools.audio_test_server.server']):
            result = subprocess.run([sys.executable,*entry,'--help'],cwd=ROOT,capture_output=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn(b'--icy-interval',result.stdout)


if __name__ == '__main__': unittest.main()
