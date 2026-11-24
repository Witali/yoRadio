"""Validate RTC-off native evidence without writes; --write is root-only release.

Never builds, runs a guest, edits source/index/README, rewrites outcomes, or
publishes firmware/private TLS material. All three actual reports must be terminal.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
DESTINATION = ROOT / 'tests/results/cyd-openeth-no-rtc-20261124/native'
SOURCE = '7595a79958b8a2ef56babb24c43259fcf536b6dd'
CONTROLLER_SHA = 'ca236ed51cbb54e06391e7cfb5b88ef465594ccfbd122e52ddcade64f479cc4f'
QEMU_SHA = '28068f674d06c4322aa72989756d7dd3734bb0d06c4aa1acf21b919ccb3465f4'
DRIVER_SHA = 'e4808727b9a3a5a0e1617d57f0d39a11bdf85443b9e3556990ea4822cef60882'
INPUT_SHA = 'b8dfa45339a107eed10d26240f8b83d6fe3b04e4a3911429b023254cb3fdd9a3'
PCM_SHA = '44d9a67ecc2e6a6d382951442fb7bdf687510c784e2e9137036cbe0a38b6f362'
LABEL = 'run-he-ws2-post-eof'
BACKENDS = ('legacy', 'pdm', 'continuous')
FINAL_MARKER = 'clean resources after final WebUI and peer closure'
FAULTS = [('allocation_failures',), ('decoder_failure','sequence'), ('stream_failure','sequence'),
          ('output','failures'), ('output','write_errors'), ('output','configure_errors'),
          ('output','flush_errors'), ('output_driver','errors'), ('output_driver','timeouts'),
          ('output_driver','short_writes'), ('output_driver','saturated')]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(Path(path).read_bytes())


def pin(path):
    path = Path(path)
    before = path.stat()
    digest = hashlib.sha256()
    count = 0
    with path.open('rb') as stream:
        for body in iter(lambda:stream.read(1024*1024),b''):
            digest.update(body)
            count += len(body)
    after = path.stat()
    require((before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns) and
            count==after.st_size, 'Evidence changed while reading: '+str(path))
    return dict(bytes=count,sha256=digest.hexdigest())


def same(path, expected):
    require(pin(path)=={k:expected[k] for k in ('bytes','sha256')}, 'Changed binding: '+str(path))


def child(folder, relative):
    target = (folder / relative).resolve()
    require(target.is_relative_to(folder.resolve()), 'Evidence path escapes its namespace')
    return target


def field(value, *keys):
    for key in keys:
        if not isinstance(value,dict) or key not in value:
            return None
        value = value[key]
    return value


def conjunction(values):
    values = list(values)
    if any(value is False for value in values):
        return False
    return True if values and all(value is True for value in values) else None


def health_gate(value):
    counters = {'.'.join(path):field(value,*path) for path in FAULTS}
    checks = [None if x is None else x==0 for x in counters.values()]
    return dict(passed=conjunction(checks), present=isinstance(value,dict), fault_counters=counters,
                completion_queue_drops=field(value,'output_driver','completion_queue_drops'),
                queue_drop_scope='Separate telemetry, never erased or silently treated as a PCM oracle.')


def websocket_gate(report):
    ws = report.get('websocket')
    if not isinstance(ws,dict):
        return dict(passed=None,present=False)
    phases = ws.get('phases') or {}
    commands = ws.get('command_phases') or {}
    checks = [None if key not in ws else ws[key]==expected for key,expected in
              [('clients',2),('errors',[]),('close_codes',[1000,1000]),('readers_stopped',True),
               ('continuously_drained',True)]]
    complete = all(isinstance(phases.get(key),list) and len(phases[key])==2
                   for key in ('idle','playing','eof'))
    for key in ('idle','playing','eof'):
        checks.append(None if key not in phases else isinstance(phases[key],list) and len(phases[key])==2)
    if complete:
        expected_generation = field(report,'eof_status','generation')
        for index in range(2):
            idle,playing,eof = [phases[key][index] for key in ('idle','playing','eof')]
            checks.append(all(isinstance(x,dict) for x in (idle,playing,eof)))
            if all(isinstance(x,dict) for x in (idle,playing,eof)):
                checks.append(idle.get('audio') is False and playing.get('audio') is True and eof.get('audio') is False)
                receipts = [x.get('receipt') for x in (idle,playing,eof)]
                checks.append(all(type(x) is int for x in receipts) and 0<receipts[0]<receipts[1]<receipts[2])
                checks.append(None if expected_generation is None else
                              playing.get('generation')==eof.get('generation')==expected_generation)
    checks.append(None if 'eof' not in commands else
                  commands==dict(idle=[1,1],playing=[2,2],eof=[3,3]) and ws.get('application_pongs')==[3,3])
    return dict(passed=conjunction(checks),present=True,evidence=ws)


def gates(report, uart, expected_asset):
    peers,wire = report.get('peer_observations'),report.get('tls_application_payload_lengths')
    tls = None if peers is None or wire is None else bool(
        len(peers)==1 and peers[0].get('complete') is True and peers[0].get('sent')==102420 and
        peers[0].get('tls_version')=='TLSv1.2' and peers[0].get('tls_cipher') in
        ('ECDHE-RSA-AES128-GCM-SHA256','ECDHE-RSA-AES256-GCM-SHA384') and
        len(wire)==8 and 24<wire[0]<16408 and wire[1:]==[16408]*6+[4140])
    flushes = [{'frames':int(a),'status':int(b)} for a,b in re.findall(
        rb'^CYD_OPENETH_PCM_FLUSH frames=(\d+) status=(-?\d+)[ \t\r]*$',uart,re.M)]
    digests = [x.decode() for x in re.findall(rb'^CYD_OPENETH_PCM_SHA256 ([0-9a-f]{64})[ \t\r]*$',uart,re.M)]
    fixture = report.get('aac_fixture') or {}
    pcm = None if report.get('pcm_sha256') is None else bool(
        fixture.get('input_bytes')==102420 and fixture.get('input_sha256')==INPUT_SHA and
        fixture.get('pcm_frames')==614400 and fixture.get('pcm_sha256')==PCM_SHA and
        report['pcm_sha256']==PCM_SHA and digests==[PCM_SHA] and
        flushes==report.get('pcm_probe_flushes')==[dict(frames=614400,status=0)])
    assets = {key:report[key] for key in ('web_asset','web_asset_during_playback','web_asset_after_eof') if key in report}
    asset_checks = [None if key not in assets else assets[key]==expected_asset for key in
                    ('web_asset','web_asset_during_playback','web_asset_after_eof')]
    eof,post = report.get('eof_health'),report.get('post_eof_health')
    eof_status,post_status = report.get('eof_status'),report.get('post_eof_status')
    initial = (report.get('health') or [{}])[0]
    stable = None
    if all(isinstance(x,dict) for x in (eof,post,eof_status,post_status)):
        stable = bool(field(initial,'boot_id') is not None and
            field(initial,'boot_id')==eof.get('boot_id')==post.get('boot_id') and
            type(eof.get('uptime_ms')) is int and type(post.get('uptime_ms')) is int and
            post['uptime_ms']>=eof['uptime_ms'] and eof_status==post_status and
            post_status.get('audio') is False and post_status.get('connecting') is False and
            post_status.get('format')=='stream ended' and type(post_status.get('generation')) is int)
    available = {}
    for name in ('health','first_active_health','playing_health','health_during_webui',
                 'eof_health','post_eof_health','last_reachable_health'):
        if name in report:
            values = report[name] if isinstance(report[name],list) else [report[name]]
            available[name] = [health_gate(value) for value in values]
    marker_present = FINAL_MARKER in (report.get('observed') or [])
    marker = True if marker_present else (False if 'post_eof_health' in report or report.get('passed') else None)
    stop_values = [None if key not in report else report[key]==expected for key,expected in
                   [('controller_stop',True),('guest_fault_observed',False),('flash_unchanged',True)]]
    stop_values.append(None if 'qemu_exit_status' not in report else type(report['qemu_exit_status']) is int)
    return dict(
        tls_full_102420_and_record_geometry=dict(passed=tls,wire_lengths=wire,peers=peers),
        pcm_exact_614400=dict(passed=pcm,sha256=report.get('pcm_sha256'),uart_flushes=flushes,uart_digests=digests),
        webui_three_assets=dict(passed=conjunction(asset_checks),expected=expected_asset,observed=assets),
        two_websocket_peers=websocket_gate(report),
        eof_fault_counters_zero=health_gate(eof),
        post_eof_fault_counters_zero=health_gate(post),
        available_health_fault_counters_zero=dict(passed=conjunction(
            item['passed'] for group in available.values() for item in group),observations=available),
        stable_boot_generation_and_eof=dict(passed=stable),
        final_observed_marker=dict(passed=marker,present=marker_present),
        guest_intentionally_stopped_after_observation=dict(passed=conjunction(stop_values),
            qemu_exit_status=report.get('qemu_exit_status')))


def sensitive_scan(body, location):
    rules = {
        'private-key':rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----',
        'cloud-access-key':rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
        'hosted-access-token':rb'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{24,})\b',
        'url-credentials':rb'https?://[^\s/:@]+:[^\s/@]+@',
        'personal-windows-home':rb'(?i)[a-z]:[\\/]+Users[\\/]+(?!Public[\\/]|Default[\\/]|build[\\/])[^\\/\s"\x27]+',
        'personal-posix-home':rb'/(?:home|Users)/(?!build/)[^/\s"\x27]+/',
        'credential-assignment':rb'(?i)\b(?:password|passwd|api[_-]?key|access[_-]?token|client[_-]?secret)\b["\x27]?\s*[=:]\s*["\x27]?[^\s"\x27;,{}]{8,}',
    }
    for category,pattern in rules.items():
        require(not re.search(pattern,body), 'Potential sensitive content ('+category+') in '+location)
    for match in re.finditer(rb'\b[A-Za-z0-9.!#$%&\x27*+/=?^_`{|}~-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b',body):
        domain = match.group(1).lower()
        require(domain in (b'example.com',b'example.net',b'example.org') or
                domain.endswith((b'.invalid',b'.test',b'.example')), 'Potential private email in '+location)


def inspect():
    report_bodies = {backend:(BASE/backend/LABEL/'report.json').read_bytes() for backend in BACKENDS}
    reports = {backend:json.loads(body) for backend,body in report_bodies.items()}
    report_pins = {backend:dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
                   for backend,body in report_bodies.items()}
    require(all(x.get('state') in ('TERMINAL_PASS','TERMINAL_NONPASS') for x in reports.values()),
            'All actual reports must be terminal; no partial/native-running package is allowed')
    progress = load(BASE/'native-matrix-progress.json')
    require([(x['backend'],x['label'],x['state']) for x in progress]==
            [(backend,LABEL,reports[backend]['state']) for backend in BACKENDS], 'Incomplete or changed matrix progress')
    controller = ROOT/'tests/run-cyd-full-app-openeth.py'
    controller_pin = pin(controller)
    require(controller_pin['sha256']==CONTROLLER_SHA,'Controller changed')
    committed = subprocess.check_output(['git','--no-optional-locks','-c','core.longpaths=true',
        'show',SOURCE+':tests/run-cyd-full-app-openeth.py'],cwd=ROOT)
    require(committed.replace(b'\r\n',b'\n')==controller.read_bytes().replace(b'\r\n',b'\n'),
            'Controller differs from released source')
    qemu = ROOT/'.build/cdac-model24/fixed-self-clear/qemu-system-xtensa.exe'
    qemu_pin = pin(qemu)
    require(qemu_pin['sha256']==QEMU_SHA,'QEMU changed')
    helper = ROOT/'tests/target/cyd_full_app_openeth_qemu/websocket_peers.py'
    helper_pin = pin(helper)
    prep = load(BASE/'preflight.json')
    require(prep['source_commit']==SOURCE and prep['generated_sha256']==DRIVER_SHA,'Preparation source/driver changed')
    config_expected = dict(FREERTOS_UNICORE=False,ESP_DEFAULT_CPU_FREQ_MHZ=240,
        ESP_TASK_WDT_TIMEOUT_S=5,ESP_INT_WDT_TIMEOUT_MS=300,LWIP_TCP_WND_DEFAULT=11520,
        LWIP_TCP_RECVMBOX_SIZE=10,LWIP_TCP_SND_BUF_DEFAULT=5760,MBEDTLS_SSL_IN_CONTENT_LEN=16384,
        MBEDTLS_SSL_OUT_CONTENT_LEN=4096,MBEDTLS_DYNAMIC_BUFFER=False,YORADIO_WS_STATUS_RTC_SLOW=False,
        YORADIO_TLS_STATIC_RX_RESERVE=False,YORADIO_AUDIO_STEREO_ONLY=True,YORADIO_NATIVE_DIAGNOSTICS=False)
    copies,guards,summaries = [],[],[]
    for backend in BACKENDS:
        folder = BASE/backend
        report = reports[backend]
        binding_path = folder/(LABEL+'-input-binding.json')
        binding = load(binding_path)
        require(binding['backend']==backend and binding['label']==LABEL and not binding['physical_tested'], 'Wrong run binding')
        require(binding['source_commit']==SOURCE and binding['controller_source_commit']==SOURCE and
                binding['post_eof_health_required'] is True and binding['rtc_workspace'] is False and
                binding['rtc_probe_enabled'] is True,'Wrong source/profile binding')
        require(binding['controller']==controller_pin and binding['qemu']==qemu_pin,'Changed tool binding')
        same(folder/'qualification.json',binding['fixture_qualification'])
        same(folder/'fixture/yoradio_cyd2usb_native.bin',binding['image'])
        same(folder/'fixture/config/sdkconfig.json',binding['config'])
        same(ROOT/'.build/cws24r'/('rtc-'+backend+'-workspace')/'fixture-identity.json',binding['original_fixture_identity'])
        qual = load(folder/'qualification.json')
        require(qual['passed'] is True and qual['source_commit']==SOURCE and qual['rtc_workspace'] is False and
                qual['rtc_probe_enabled'] is True and qual['image']==binding['image'],'Qualification/profile changed')
        require(qual['effective_config_delta']=={'YORADIO_WS_STATUS_RTC_SLOW':
                dict(before_present=True,before=True,after_present=True,after=False)},'Unexpected effective config delta')
        require({k:qual['geometry'][k] for k in ('rtc_slow_used_bytes','rtc_slow_reserved_bytes','rtc_slow_free_bytes')}==
                dict(rtc_slow_used_bytes=104,rtc_slow_reserved_bytes=24,rtc_slow_free_bytes=8064),'RTC geometry changed')
        require(qual['rtc_probe']['bytes']==64 and qual['rtc_probe']['section']=='.rtc.force_slow','RTC probe changed')
        config = load(folder/'fixture/config/sdkconfig.json')
        require({k:config[k] for k in config_expected}==config_expected,'Network/TLS/watchdog/core profile changed')
        baseline = load(folder/'baseline.json')
        driver = child(ROOT,baseline['cache'])/'openeth-rx-overlay/esp_eth_mac_openeth.c'
        require(pin(driver)['sha256']==DRIVER_SHA,'Generated OpenETH driver changed')
        same(folder/'compiled/yoradio_cyd2usb_native.elf',qual['elf'])
        require(report['runner_sha256']==CONTROLLER_SHA and report['qemu_sha256']==QEMU_SHA and
                report['config_sha256']==binding['config']['sha256'] and report['physical_tested'] is False,
                'Report input identity changed')
        require(report['websocket_peer_helper_sha256']==helper_pin['sha256'],'WebSocket helper changed')
        require(type(report.get('passed')) is bool and
                report['passed']==(report['state']=='TERMINAL_PASS'),'Report state/pass flag conflict')
        require(report['task_watchdog_seconds']==5 and report['native_diagnostics'] is False,'Reported policy changed')
        for part in report['flash_parts']:
            same(child(folder/'fixture',part['file']),part)
        app, = [part for part in report['flash_parts'] if part['file']=='yoradio_cyd2usb_native.bin']
        require({k:app[k] for k in ('bytes','sha256')}==binding['image'],'Application flash binding changed')
        uart_path = folder/LABEL/'qemu.log'
        uart = uart_path.read_bytes()
        require(hashlib.sha256(uart).hexdigest()==report['uart_sha256'],'Raw UART binding changed')
        same(folder/LABEL/'report.json',report_pins[backend])
        asset = pin(folder/'fixture/assets/www/script.js.gz')
        independent = gates(report,uart,asset)
        health_fields = ('eof_health','post_eof_health','last_reachable_health')
        summaries.append(dict(backend=backend,label=LABEL,state=report['state'],passed=report['passed'],
            reason=report.get('reason'),gates=independent,
            all_independent_gates_demonstrated=all(x['passed'] is True for x in independent.values()),
            health_evidence={key:report[key] for key in health_fields if key in report},
            missing_final_report_fields=[key for key in ('post_eof_status','post_eof_health') if key not in report],
            image=binding['image'],config=binding['config'],qualification=binding['fixture_qualification'],
            report_binding=report_pins[backend],input_binding=pin(binding_path),
            rtc_geometry=qual['geometry'],qualified_driver_sha256=DRIVER_SHA))
        for origin,target in [(folder/LABEL/'report.json','report.json'),(uart_path,'qemu.log'),
                              (binding_path,'input-binding.json'),(folder/(LABEL+'-terminal.log'),'terminal.log')]:
            copies.append((origin,Path(backend)/LABEL/target,pin(origin)))
        selected = ['qualification.json','rtc-config-delta.json','object-comparison.json','stack-frame.json']
        if (folder/'unlinked-bootloader-date-exception.json').is_file():
            selected.append('unlinked-bootloader-date-exception.json')
        for name in selected:
            origin = folder/name
            require(origin.is_file(),'Missing selected qualification evidence: '+name)
            copies.append((origin,Path('qualification')/backend/name,pin(origin)))
        guards.extend([(folder/'fixture/config/sdkconfig.json',binding['config']),
                       (folder/'fixture/yoradio_cyd2usb_native.bin',binding['image'])])
    copies.append((BASE/'native-matrix-progress.json',Path('matrix-progress.json'),pin(BASE/'native-matrix-progress.json')))
    summary = dict(fixture_source_commit=SOURCE,controller_source_commit=SOURCE,controller=controller_pin,
        qemu=qemu_pin,websocket_helper=helper_pin,rtc_workspace=False,rtc_probe_enabled=True,
        selected_configuration=config_expected,qualified_driver_sha256=DRIVER_SHA,cases=summaries,
        all_original_controller_pass=all(x['state']=='TERMINAL_PASS' for x in summaries),physical_tested=False,
        packager=pin(Path(__file__)),
        scope='Finite RTC-OFF full-app observations with the unchanged strengthened controller. '
              'True/false/null distinguish proved/failed/missing gates. Original states and absent fields are preserved. '
              'last_reachable_health is separately labeled and never substituted for post_eof_health. '
              'RTC access probe remains on; this is not a no-RTC-storage-at-all or physical Wi-Fi/audio qualification.')
    return copies,guards,summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='Root-reviewed creation of the fresh native namespace only')
    parser.add_argument('--release-source-commit',help='Required with --write; must identify the reviewed frozen source')
    args = parser.parse_args()
    require(not args.write or args.release_source_commit==SOURCE,'--write requires the exact reviewed --release-source-commit')
    copies,guards,summary = inspect()
    payloads = []
    for source,relative,expected in copies:
        require(source.suffix in ('.json','.log'),'Only explicitly selected text evidence may be published')
        body = source.read_bytes()
        require(dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())==expected,'Changed evidence before packaging')
        sensitive_scan(body,relative.as_posix())
        payloads.append((source,relative,expected,body))
    summary_body = (json.dumps(summary,indent=2)+'\n').encode()
    sensitive_scan(summary_body,'matrix-summary.json')
    manifest = [{'file':relative.as_posix(),**expected} for _,relative,expected,_ in payloads]
    manifest.append(dict(file='matrix-summary.json',bytes=len(summary_body),
                         sha256=hashlib.sha256(summary_body).hexdigest()))
    manifest.sort(key=lambda item:item['file'])
    manifest_body = (json.dumps(manifest,indent=2)+'\n').encode()
    sensitive_scan(manifest_body,'artifact-manifest.json')
    for source,expected in guards:
        same(source,expected)
    if args.write:
        require(not DESTINATION.exists() and not DESTINATION.is_symlink(),'Never overwrite an existing native namespace')
        require(DESTINATION.resolve().is_relative_to(ROOT.resolve()),'Publication target escapes repository')
        for source,relative,expected,body in payloads:
            same(source,expected)
            target = child(DESTINATION,relative)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(body)
            same(target,expected)
        (DESTINATION/'matrix-summary.json').write_bytes(summary_body)
        (DESTINATION/'artifact-manifest.json').write_bytes(manifest_body)
    print(json.dumps(dict(mode='PACKAGED' if args.write else 'VALIDATED_ONLY',
        destination=DESTINATION.relative_to(ROOT).as_posix(),files=len(payloads)+2,privacy_scan='PASS',
        cases=[dict(backend=x['backend'],state=x['state'],
                    eof_allocation_failures=field(x,'health_evidence','eof_health','allocation_failures'),
                    eof_minimum_heap=field(x,'health_evidence','eof_health','minimum_heap'),
                    missing_final_report_fields=x['missing_final_report_fields'],
                    gates={key:value['passed'] for key,value in x['gates'].items()}) for x in summary['cases']])))


if __name__=='__main__':
    main()
