"""TCP telemetry must reject corrupt bytes, gaps and missing tail events."""
from pathlib import Path
import sys
import unittest
import zlib

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from web_tcp import parse, window


def frame(kind, words, at=1):
    body='PERF T'+kind+'2:'+''.join(f'{n:08x}' for n in words)
    return dict(at=at,line=body+f'{zlib.crc32(body.encode()):08x}')


class TcpFrames(unittest.TestCase):
    def test_mapping_and_signed_error(self):
        value=parse(frame('C',[123,456,32000|(1<<16)|(4<<24),255|(255<<8)|(249<<16)|(2<<24),5]))
        self.assertEqual(value,dict(at=1.0,kind='event',seq=123,us=456,port=32000,dir=1,
                                   flags=4,before=255,after=255,result=-7,pending=2,dropped=5))
        self.assertEqual(parse(frame('L',[3,1001,2|(4<<16),1|(5<<8)|(2<<16)|(1<<24),0]))['established'],4)

    def test_every_hex_digit_change_and_deletion_rejected(self):
        row=frame('C',[123,456,789,0,0])
        for offset in range(9,57):
            with self.subTest(offset=offset):
                line=row['line']; replacement='1' if line[offset]!='1' else '0'
                with self.assertRaises(ValueError):parse(dict(at=1,line=line[:offset]+replacement+line[offset+1:]))
                with self.assertRaises(ValueError):parse(dict(at=1,line=line[:offset]+line[offset+1:]))

    def test_merge_and_bad_time(self):
        row=frame('C',[1,2,3,0,0])
        with self.assertRaises(ValueError):parse(dict(at=1,line=row['line']+'\r'+row['line']))
        with self.assertRaises(ValueError):parse(dict(at=float('nan'),line=row['line']))
        self.assertIsNone(parse(dict(at=1,line='PERF decoder: other telemetry')))

    def rows(self):
        return [frame('S',[10,100,0,0,10],1),frame('L',[3,1000,0,0x01000501,0],1.1),
                frame('C',[11,200,32000,0,0],1.5),frame('S',[11,300,0,0,11],2),
                frame('L',[4,1000,0,0x01000501,0],2.1),frame('S',[11,400,0,0,11],3)]

    def test_anchored_window(self):
        result=window(self.rows(),.8,3.2)
        self.assertEqual(len(result['events']),1)
        self.assertEqual(result['start'],1)
        self.assertAlmostEqual(result['last_edge_seconds'],.2)

    def test_missing_last_event_detected_by_watermark(self):
        rows=self.rows(); del rows[2]
        with self.assertRaisesRegex(ValueError,'watermark exposes'):window(rows,.8,3.2)

    def test_duplicate_event_and_missing_listener(self):
        rows=self.rows(); rows.insert(3,rows[2])
        with self.assertRaisesRegex(ValueError,'duplicate TCP'):window(rows,.8,3.2)
        rows=self.rows(); rows[4]=frame('L',[5,1000,0,0x01000501,0],2.1)
        with self.assertRaisesRegex(ValueError,'listener sample'):window(rows,.8,3.2)

    def test_drop_inconsistency_and_long_capture_gap(self):
        rows=self.rows(); rows[3]=frame('S',[11,300,1,0,11],2)
        with self.assertRaisesRegex(ValueError,'ring dropped'):window(rows,.8,3.2)
        with self.assertRaises(ValueError):parse(frame('S',[11,300,0,1,11]))
        with self.assertRaisesRegex(ValueError,'coverage'):window(self.rows(),-3,3.2)

    def test_counter_wrap(self):
        rows=[frame('S',[0xffffffff,1,0,0,0xffffffff],1),
              frame('L',[1,1000,0,0x01000501,0],1.1),
              frame('C',[0,2,32000,0,0],1.2),frame('S',[0,3,0,0,0],2)]
        self.assertEqual(window(rows,.9,2.1)['events'][0]['seq'],0)


if __name__=='__main__':unittest.main()
