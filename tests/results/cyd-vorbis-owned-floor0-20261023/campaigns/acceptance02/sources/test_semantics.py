"""Proposed pure publication-contract controls; synthetic logs are never target proof."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from fixture_reader import verify_contract
from protocol import PREFIX, validate_log

HERE=Path(__file__).resolve().parent


def contract():return json.loads((HERE/'fixture-contract.json').read_bytes())


def changed(field,value):
    c=copy.deepcopy(contract());c['model']['cases'][0][field]=value
    c['contract_sha256']=hashlib.sha256(json.dumps(c['model'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return c


def synthetic(c):
    """Host syntax/control fixture only; no actual PID/process/terminal receipt."""
    lines=[]
    def add(kind,**values):lines.append(PREFIX+kind+' '+' '.join(f'{k}={v}' for k,v in values.items()))
    add('BEGIN',contract=c['contract_sha256'],cases=12,pairs=6,core=0)
    for i,v in enumerate(c['model']['cases']):
        add('FIELDS',case=i,id=v['id'],group=v['group'],first=v['first_bit'],end=v['end_bit'],consumed=v['parse_bits'],
            total_books=v['total_books'],order=v['order'],rate=v['rate'],barkmap=v['barkmap'],ampbits=v['ampbits'],ampdb=v['ampdB'],
            numbooks=len(v['books']),books=','.join(map(str,v['books'])),allocated=40,live=1,vi_unchanged=1,ci_unchanged=1,guards=1,core=0)
        add('CASE',case=i,id=v['id'],live=0,guards=1,core=0)
    for a,b in c['model']['pairs']:add('PAIR',first=a,second=b,publication_equal=1,span_equal=1,bytes=40,core=0)
    add('COMPLETE',cases=12,pairs=6,live=0,core=0)
    return '\n'.join(lines)+'\n'


class RawPublicationControls(unittest.TestCase):
    def reject(self,field,value):
        with self.assertRaisesRegex(ValueError,'published_field:'+field):verify_contract(changed(field,value),HERE)
    def test_all12_actual_raw_headers(self):self.assertEqual(verify_contract(contract(),HERE)['cases'],12)
    def test_order(self):self.reject('order',7)
    def test_rate(self):self.reject('rate',48001)
    def test_barkmap(self):self.reject('barkmap',65)
    def test_ampbits(self):self.reject('ampbits',7)
    def test_ampdb(self):self.reject('ampdB',61)
    def test_books(self):self.reject('books',[1])
    def test_ci_book_count(self):self.reject('total_books',4)
    def test_absolute_start(self):self.reject('first_bit',0)
    def test_absolute_end(self):self.reject('end_bit',0)


class PublicationProtocolControls(unittest.TestCase):
    def check(self,log,**kw):
        values=dict(returncode=0,timed_out=False,interrupted=False,force_stopped=False);values.update(kw)
        return validate_log(log,contract(),**values)
    def reject(self,old,new):
        log=synthetic(contract());self.assertIn(old,log)
        with self.assertRaises(ValueError):self.check(log.replace(old,new,1))
    def test_complete_synthetic_shape(self):self.assertEqual(self.check(synthetic(contract()))['protocol_lines'],32)
    def test_rate_publication(self):self.reject('rate=48000','rate=48001')
    def test_wrong_ci(self):self.reject('ci_unchanged=1','ci_unchanged=0')
    def test_wrong_vi(self):self.reject('vi_unchanged=1','vi_unchanged=0')
    def test_wrong_core(self):self.reject('core=0','core=1')
    def test_wrong_consumption(self):self.reject('consumed=66','consumed=65')
    def test_wrong_size(self):self.reject('allocated=40','allocated=36')
    def test_missing_release(self):self.reject('live=0 guards=1','live=1 guards=1')
    def test_wrong_pair(self):self.reject('publication_equal=1','publication_equal=0')
    def test_missing_record(self):
        with self.assertRaises(ValueError):self.check('\n'.join(synthetic(contract()).splitlines()[1:])+'\n')
    def test_complete_alone(self):
        with self.assertRaises(ValueError):self.check(synthetic(contract()).splitlines()[-1]+'\n')
    def test_nonzero_terminal(self):
        with self.assertRaises(ValueError):self.check(synthetic(contract()),returncode=1)
    def test_timeout(self):
        with self.assertRaises(ValueError):self.check(synthetic(contract()),timed_out=True)
    def test_force_stop(self):
        with self.assertRaises(ValueError):self.check(synthetic(contract()),force_stopped=True)
    def test_interrupted(self):
        with self.assertRaises(ValueError):self.check(synthetic(contract()),interrupted=True)


if __name__=='__main__':unittest.main()
