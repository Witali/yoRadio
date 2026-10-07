"""Check bounded send timing and real HTTP payload equivalence."""
from pathlib import Path
import sys
import time
import unittest
from urllib.request import urlopen
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audio_test_server.server import DeliveryStats, Server


class DeliveryStatsTest(unittest.TestCase):
    def test_write_delays_totals_tail_and_overflow(self):
        event={}
        stats=DeliveryStats(10,event)
        stats.MAX_WINDOWS=2
        stats.write(100,10,10.2,10)
        stats.write(300,10.8,11.2,10.4)
        stats.write(200,11.3,11.5,None)
        stats.finish(11.6)
        rows=event['delivery']['windows']
        self.assertEqual([r['bytes'] for r in rows],[400,200])
        self.assertEqual([r['writes'] for r in rows],[2,1])
        self.assertAlmostEqual(rows[0]['write_seconds'],.6)
        self.assertAlmostEqual(rows[0]['max_write_seconds'],.4)
        self.assertAlmostEqual(rows[0]['max_late_seconds'],.4)
        self.assertTrue(event['delivery']['finished'])
        stats.write(10,12,13)
        self.assertEqual(len(rows),2)
        self.assertEqual(event['delivery']['dropped_windows'],1)

    def test_http_bytes_and_default_off(self):
        data=bytes(range(256))*20
        specs={'test':dict(data=data,seconds=.08,codec='mp3',mime='audio/mpeg')}
        for enabled in (False,True):
            for unpaced in (False,True):
                with self.subTest(enabled=enabled,unpaced=unpaced):
                    with Server('127.0.0.1',0,specs,delivery_stats=enabled,unpaced_files=unpaced) as server:
                        port=server.http.server_address[1]
                        with urlopen(f'http://127.0.0.1:{port}/file/test',timeout=3) as response:
                            self.assertEqual(response.read(),data)
                        deadline=time.monotonic()+2
                        while time.monotonic()<deadline and not server.events[0].get('seconds'):
                            time.sleep(.005)
                        event=server.events[0]
                        self.assertTrue(event['complete'])
                        self.assertEqual(event['sent'],len(data))
                        self.assertEqual('delivery' in event,enabled)
                        if enabled:
                            stats=event['delivery']
                            self.assertTrue(stats['finished'])
                            self.assertEqual(stats['dropped_windows'],0)
                            self.assertEqual(sum(r['bytes'] for r in stats['windows']),len(data))
                            self.assertGreaterEqual(sum(r['write_seconds'] for r in stats['windows']),0)


if __name__=='__main__':unittest.main()
