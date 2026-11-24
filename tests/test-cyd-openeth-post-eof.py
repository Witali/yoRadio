"""Exercise late resource failures through the actual EOF/controller seams."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch


RUNNER = Path(__file__).with_name('run-cyd-full-app-openeth.py')
spec = importlib.util.spec_from_file_location('cyd_openeth_post_eof', RUNNER)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def health(*, allocations=0, boot='same-boot', uptime=3000):
    return dict(boot_id=boot, uptime_ms=uptime, allocation_failures=allocations,
                decoder_failure={'sequence': 0}, stream_failure={'sequence': 0},
                output=dict(failures=0, write_errors=0, configure_errors=0, flush_errors=0),
                output_driver=dict(writes=1, requested_bytes=8, written_bytes=8,
                                   errors=0, timeouts=0, short_writes=0, saturated=False,
                                   completion_queue_drops=4))


def ended_status(generation=4):
    return dict(audio=False, connecting=False, format='stream ended', generation=generation)


class Peers:
    def __init__(self, events, *, closes=True):
        self.events = events
        self.closes = closes
        self.closed = False

    def require_status(self, phase, **expected):
        if phase != 'eof' or expected != dict(audio=False, generation=4):
            raise AssertionError('Unexpected peer phase')
        self.events.append('EOF peer status and pongs')

    def close(self):
        self.events.append('peer close')
        self.closed = True
        return self.closes

    def summary(self):
        return dict(closed=self.closed, close_codes=[1000,1000] if self.closes else [1000,1006])


class PostEofTests(unittest.TestCase):
    def setUp(self):
        self.reset_scenario()

    def reset_scenario(self):
        self.events = []
        self.peers = Peers(self.events)
        self.report = dict(passed=True, audio_backend='dac', observed=[],
                           health=[health(uptime=1000)])

    def observe_then_finish(self, final=None, status=None):
        final = health() if final is None else final
        status = ended_status() if status is None else status

        def read_status(_port, uri):
            self.assertEqual(uri, '/api/native/status')
            self.events.append('final status' if self.peers.closed else 'EOF status')
            return json.dumps(status if self.peers.closed else ended_status())

        def sample(_port):
            self.events.append('final health' if self.peers.closed else 'EOF health')
            return copy.deepcopy(final if self.peers.closed else health(uptime=2000))

        def asset(_port):
            self.events.append('post-EOF asset')
            return dict(bytes=3)

        server = SimpleNamespace(fixtures={'station':dict(data=b'abc', codec='opus',
                                                         pcm_frames=2, pcm_md5=None)})
        guest = SimpleNamespace(poll=lambda: None)
        with patch.object(probe, 'request', side_effect=read_status), \
             patch.object(probe, 'sample', side_effect=sample), \
             patch.object(probe, 'check_asset', side_effect=asset), \
             patch.object(probe, 'guest_log', return_value='CYD_OPENETH_PCM_FLUSH frames=2 status=0\n'):
            probe.observe_eof(1234, server, dict(complete=True,sent=3), guest, RUNNER, 4,
                              self.report, websocket_peers=self.peers)
            probe.finalize_webui_checks(1234, guest, self.report, self.peers, through_eof=True)

    def test_final_sample_follows_asset_pongs_and_normal_peer_close(self):
        self.observe_then_finish()
        for earlier,later in [('post-EOF asset','EOF peer status and pongs'),
                              ('EOF peer status and pongs','peer close'),
                              ('peer close','final status'),('final status','final health')]:
            self.assertLess(self.events.index(earlier), self.events.index(later))
        self.assertEqual(self.report['post_eof_status'], ended_status())
        self.assertEqual(self.report['post_eof_health']['allocation_failures'], 0)
        # This independent telemetry is not an allocation/PCM/output failure.
        self.assertEqual(self.report['post_eof_health']['output_driver']['completion_queue_drops'], 4)

    def test_allocation_after_clean_eof_is_rejected_and_retained(self):
        with self.assertRaisesRegex(RuntimeError, 'Unexpected allocation failure count'):
            self.observe_then_finish(health(allocations=1))
        self.assertEqual(self.report['eof_health']['allocation_failures'], 0)
        self.assertEqual(self.report['post_eof_health']['allocation_failures'], 1)
        self.assertTrue(self.report['websocket']['closed'])

    def test_late_output_failure_is_rejected(self):
        final = health()
        final['output']['failures'] = 1
        with self.assertRaisesRegex(RuntimeError, 'Unexpected output counter'):
            self.observe_then_finish(final)

    def test_late_output_and_driver_subcounters_are_not_hidden(self):
        for group,key in [('output','write_errors'),('output','configure_errors'),
                          ('output','flush_errors'),('output_driver','errors'),
                          ('output_driver','timeouts'),('output_driver','short_writes')]:
            with self.subTest(group=group,key=key):
                self.reset_scenario()
                final = health()
                final[group][key] = 1
                with self.assertRaisesRegex(RuntimeError, 'Unexpected output fault'):
                    self.observe_then_finish(final)

    def test_late_reset_or_uptime_regression_is_rejected(self):
        for final in (health(boot='rebooted'), health(uptime=1999)):
            with self.subTest(final=final):
                self.reset_scenario()
                with self.assertRaisesRegex(RuntimeError, 'Guest reset'):
                    self.observe_then_finish(final)

    def test_late_generation_or_playback_restart_is_rejected(self):
        for change in (dict(generation=5),dict(audio=True),dict(connecting=True),dict(format='stopped')):
            with self.subTest(change=change):
                self.reset_scenario()
                status = ended_status()
                status.update(change)
                with self.assertRaisesRegex(RuntimeError, 'state or generation changed'):
                    self.observe_then_finish(status=status)

    def test_expected_pressure_allocation_remains_exactly_one(self):
        self.report.update(input_reclaim_pcm_reference='a'*32,
                           eof_health=health(allocations=1,uptime=2000), eof_status=ended_status())
        for allocations in (1,0,2):
            with self.subTest(allocations=allocations), \
                 patch.object(probe, 'request', return_value=json.dumps(ended_status())), \
                 patch.object(probe, 'sample', return_value=health(allocations=allocations)):
                operation = lambda:probe.finalize_webui_checks(
                    1234, SimpleNamespace(poll=lambda:None), self.report, through_eof=True)
                if allocations == 1:
                    operation()
                else:
                    with self.assertRaisesRegex(RuntimeError, 'allocation failure count'):
                        operation()

    def test_failed_or_non_eof_modes_only_close_peers(self):
        for through_eof,passed in [(False,True),(True,False)]:
            with self.subTest(through_eof=through_eof,passed=passed):
                self.report['passed'] = passed
                with patch.object(probe, 'sample') as sample, patch.object(probe, 'request') as request:
                    probe.finalize_webui_checks(1234,None,self.report,self.peers,through_eof=through_eof)
                    sample.assert_not_called()
                    request.assert_not_called()
                self.assertEqual(self.report['passed'],passed)

    def test_failed_peer_close_prevents_a_false_final_pass(self):
        self.peers.closes = False
        with patch.object(probe, 'sample') as sample:
            with self.assertRaisesRegex(RuntimeError, 'peer failed or did not close'):
                probe.finalize_webui_checks(1234,None,self.report,self.peers,through_eof=True)
            sample.assert_not_called()
        self.assertEqual(self.report['websocket']['close_codes'],[1000,1006])

    def test_dead_guest_does_not_pass_post_eof_check(self):
        with patch.object(probe, 'sample') as sample:
            with self.assertRaisesRegex(RuntimeError, 'Guest stopped before'):
                probe.finalize_webui_checks(1234,SimpleNamespace(poll=lambda:1),self.report,
                                            self.peers,through_eof=True)
            sample.assert_not_called()

    def test_eof_and_final_matching_boots_cannot_hide_an_earlier_reset(self):
        self.report.update(eof_health=health(boot='rebooted',uptime=2000),eof_status=ended_status())
        with patch.object(probe,'request',return_value=json.dumps(ended_status())), \
             patch.object(probe,'sample',return_value=health(boot='rebooted')):
            with self.assertRaisesRegex(RuntimeError,'Guest reset'):
                probe.finalize_webui_checks(1234,SimpleNamespace(poll=lambda:None),self.report,
                                            through_eof=True)

    def test_guest_must_stay_live_through_the_last_capture(self):
        self.report.update(eof_health=health(uptime=2000),eof_status=ended_status())
        guest = SimpleNamespace(poll=unittest.mock.Mock(side_effect=[None,1]))
        with patch.object(probe,'request',return_value=json.dumps(ended_status())), \
             patch.object(probe,'sample',return_value=health()):
            with self.assertRaisesRegex(RuntimeError,'Guest stopped during'):
                probe.finalize_webui_checks(1234,guest,self.report,through_eof=True)

    def main_with_late_sample(self, last_sample):
        # Run the real main/finally/report path with host IO seams, not QEMU.
        # Playback succeeds with EOF health=0; only the last read sees failure.
        build_parent = probe.ROOT/'.build'
        build_parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='cyd-post-eof-host-',dir=build_parent) as temporary:
            root = Path(temporary)
            build = root/'build'; (build/'config').mkdir(parents=True)
            (root/'rom').mkdir(); (root/'qemu.exe').write_bytes(b'host seam')
            (root/'.build/tls').mkdir(parents=True)
            config = dict(IDF_TARGET='esp32',ETH_USE_OPENETH=True,FREERTOS_UNICORE=False,
                          YORADIO_NATIVE_AUDIO_OUTPUT_PDM=True,YORADIO_OGG_TIMELINE=True,
                          MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE=True,ESP_TASK_WDT_TIMEOUT_S=5)
            (build/'config/sdkconfig.json').write_text(json.dumps(config))
            guest = SimpleNamespace(pid=123,returncode=None)
            guest.poll = lambda:guest.returncode
            guest.terminate = lambda:setattr(guest,'returncode',1)
            guest.wait = lambda **_:guest.returncode
            server = SimpleNamespace(http=SimpleNamespace(server_port=12345),events=[])

            def playback(_port,_server,_guest,_log,report,*_args,**_kwargs):
                report.update(eof_health=health(uptime=2000),eof_status=ended_status(),
                              web_asset_after_eof=dict(bytes=3))

            argv = [str(RUNNER),'--build',str(build),'--qemu',str(root/'qemu.exe'),
                    '--rom',str(root/'rom'),'--output',str(root/'.build/run'),
                    '--tls-material',str(root/'.build/tls'),'--through-eof']
            ready = 'CYD_OPENETH_READY\nNative HTTP server started\nST7789: SPI2 DMA\nPipeline ready:\n'
            with patch.object(probe,'ROOT',root),patch.object(probe.sys,'argv',argv), \
                 patch.object(probe,'flash_parts',return_value=(bytearray(b'host flash'),[])), \
                 patch.object(probe,'local_port',return_value=1234), \
                 patch.object(probe,'station_fixture',return_value={'codec':'opus','data':b'abc'}), \
                 patch.object(probe,'tls_station',return_value=contextlib.nullcontext(server)), \
                 patch.object(probe.subprocess,'Popen',return_value=guest), \
                 patch.object(probe,'guest_log',return_value=ready), \
                 patch.object(probe,'sample',side_effect=[health(uptime=1000),health(uptime=1100),last_sample]), \
                 patch.object(probe,'check_asset',return_value=dict(bytes=3)), \
                 patch.object(probe,'observe_playback',side_effect=playback), \
                 patch.object(probe,'request',return_value=json.dumps(ended_status())), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(probe.main(),1)
            saved = json.loads((root/'.build/run/report.json').read_bytes())
            self.assertEqual(saved['state'],'TERMINAL_NONPASS')
            self.assertTrue(saved['controller_stop'])
            self.assertEqual(saved['qemu_exit_status'],1)
            return saved

    def test_main_saves_late_failure_as_nonpass_and_still_stops_guest(self):
        saved = self.main_with_late_sample(health(allocations=1))
        self.assertEqual(saved['eof_health']['allocation_failures'],0)
        self.assertEqual(saved['post_eof_health']['allocation_failures'],1)
        self.assertIn('Unexpected allocation failure count',saved['reason'])

    def test_late_health_timeout_still_saves_nonpass_and_stops_guest(self):
        saved = self.main_with_late_sample(TimeoutError('Final health timed out'))
        self.assertEqual(saved['post_eof_status'],ended_status())
        self.assertNotIn('post_eof_health',saved)
        self.assertEqual(saved['reason'],'Final health timed out')


if __name__ == '__main__':
    unittest.main()
