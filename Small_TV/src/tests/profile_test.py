"""Check the owned Small TV profile against firmware wiring and generic QEMU routing."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[3]
PROFILE=ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'


class ProfileTests(unittest.TestCase):
    """Validate contracts that can break actual boot, time and HTTP forwarding."""
    def test_firmware_wiring(self):
        """Use production board definitions rather than copying GPIO constants into the test."""
        pins={name:int(value) for name,value in re.findall(r'#define LCD_GPIO_(\w+) (\d+)',
            (ROOT/'Small_TV/src/app/include/board.h').read_text(encoding='utf-8'))}
        profile=json.loads(PROFILE.read_text(encoding='utf-8'))
        self.assertEqual(profile['soc'],'esp32c2')
        self.assertEqual(len(profile['devices']),1)
        lcd=profile['devices'][0]
        self.assertEqual((lcd['bus'],lcd['model']),('spi2','st7789'))
        self.assertEqual(lcd['pins'],{name.lower():value for name,value in pins.items()})
        self.assertTrue(lcd['backlight_active_low'])
        self.assertTrue(lcd['properties']['panel-inverted'])
        self.assertEqual(lcd['properties']['visible-width'],240)
        self.assertNotIn('cs',lcd['pins']) # Factory display remains permanently selected.

    def test_offline_and_hardware_only(self):
        """Network metadata must not implicitly turn a hardware-only/offline launch online."""
        offline=compile_profile(PROFILE,'esp32c2')
        self.assertEqual(offline['network_arguments'],[])
        self.assertEqual(offline['service_urls'],[])
        with tempfile.TemporaryDirectory(dir=ROOT/'.build/small-tv-parity',prefix='profile-') as folder:
            if not Path(folder).resolve().is_relative_to(ROOT.resolve()):
                raise ValueError('Temporary profile is outside the workspace')
            path=Path(folder)/'hardware.json'
            data=json.loads(PROFILE.read_text(encoding='utf-8'))
            del data['network']
            path.write_text(json.dumps(data),encoding='utf-8')
            hardware=compile_profile(path,'esp32c2')
        self.assertEqual(hardware['arguments'],offline['arguments'])
        self.assertEqual(hardware['network_arguments'],[])

    def test_clock_and_setup_names(self):
        """Explicit profile DNS/SSID values keep real firmware association and SNTP working."""
        config=network_profile(PROFILE)
        self.assertEqual(config['station_ssid'],'yoRadio-QEMU')
        self.assertEqual(config['softap_client_ssid'],'Small_TV')
        self.assertEqual(config['ntp_hosts'],['ntp1.aliyun.com','cn.pool.ntp.org','pool.ntp.org'])
        clock=compile_profile(PROFILE,'esp32c2',network='clock')
        args=clock['network_arguments']
        self.assertIn('esp32c3-wifi.ntp-hosts='+';'.join(config['ntp_hosts']),args)
        self.assertIn('esp32c3-wifi.station-ssid='+config['station_ssid'],args)
        self.assertEqual(args.count('-nic'),1)
        self.assertIn('user,model=esp32c3-wifi,restrict=on',args)
        self.assertFalse(any('service-hosts=' in item or 'guestfwd=' in item for item in args))
        setup=compile_profile(PROFILE,'esp32c2',network='setup')['network_arguments']
        self.assertIn('esp32c3-wifi.softap-client-ssid='+config['softap_client_ssid'],setup)

    def test_generic_fixture_and_overrides(self):
        """Route profile URLs through generic ServicePort; preserve Host/port/path metadata."""
        compiled=compile_profile(PROFILE,'esp32c2',network='clock',service_port=19000)
        self.assertEqual(compiled['service_urls'],['http://api.openweathermap.org/data/2.5/weather'])
        self.assertIn('esp32c3-wifi.service-hosts=api.openweathermap.org',compiled['network_arguments'])
        self.assertFalse(any('weather-services=' in item for item in compiled['network_arguments']))
        nic=compiled['network_arguments'][compiled['network_arguments'].index('-nic')+1]
        self.assertIn('guestfwd=tcp:10.0.2.100:80-tcp:127.0.0.1:19000',nic)
        urls=['http://first.service.test/a','http://second.service.test:8081/b',
              'http://first.service.test/another?private-key=excluded']
        override=compile_profile(PROFILE,'esp32c2',network='setup',service_port=19000,service_urls=urls)
        self.assertEqual(override['service_urls'],['http://first.service.test/a',
            'http://second.service.test:8081/b','http://first.service.test/another'])
        routes=override['network_arguments'][override['network_arguments'].index('-nic')+1]
        self.assertIn('tcp:192.168.43.100:80-tcp:127.0.0.1:19000',routes)
        self.assertIn('tcp:192.168.43.101:8081-tcp:127.0.0.1:19000',routes)
        self.assertEqual(routes.count('guestfwd='),2)


def main():
    """Record exact profile/board/compiler inputs; full firmware tests remain separate."""
    global compile_profile,network_profile
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    (ROOT/'.build/small-tv-parity').mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(args.qemu_root/'tools'))
    from esp_board import compile_profile
    from esp_services import network_profile
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProfileTests))
    paths=[PROFILE,ROOT/'Small_TV/src/app/include/board.h',
           ROOT/'Small_TV/qemu/parity/compare.py',ROOT/'Small_TV/qemu/run.ps1']
    report={'passed':result.wasSuccessful(),'tests':result.testsRun,
            'inputs':[{'file':str(path.relative_to(ROOT)).replace('\\','/'),
                       'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths],
            'compiler_sha256':{name:hashlib.sha256((args.qemu_root/'tools'/name).read_bytes()).hexdigest()
                               for name in ('esp_board.py','esp_services.py','small_tv_web.py')},
            'scope':__doc__,'errors':[str(case) for case,_ in result.errors],
            'failures':[str(case) for case,_ in result.failures]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()
