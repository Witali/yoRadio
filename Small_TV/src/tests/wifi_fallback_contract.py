"""Validate real DHCP-delay evidence consistently in the suite and publishers."""
from copy import deepcopy


def require(value,message):
    """Reject incomplete or inconsistent observations even with Python assertions disabled."""
    if not value:raise ValueError(message)


def test_pin(report):
    """Find the one recorded observer script independently of its worktree location."""
    keys=[key for key in report['inputs_sha256']
          if key.replace('\\','/').endswith('/Small_TV/src/tests/wifi_fallback_qemu.py')]
    require(len(keys)==1,'Missing or ambiguous Wi-Fi observer identity')
    return keys[0]


def validate_wifi_fallback(report,expected):
    """Require held DHCP and later STA recovery from both immutable applications."""
    try:
        require(report['passed'] is True and report['inputs_unchanged'] is True,
                'Wi-Fi waiting did not pass with unchanged inputs')
        for key in ['app_sha256','native_elf_sha256','qemu_sha256']:
            require(report[key]==expected[key],'Wi-Fi waiting used a different '+key)
        require(report['inputs_sha256'][test_pin(report)]==expected['test_sha256'],
                'Wi-Fi observer changed after execution')
        require(set(report['flows'])=={'original','reconstructed'},'Wi-Fi waiting omitted an application')
        require(set(report['failure_flows'])=={'original','reconstructed'},'Missing real SDK failure/setup cases')
        require(report['flows']['reconstructed']['sources']['source_sha256']==expected['source_sha256'],
                'Wi-Fi waiting used different production sources')
        for variant,flow in report['flows'].items():
            require(flow['passed'] is True and flow['executable_media_unchanged'] is True,
                    'Wi-Fi waiting modified code/media or failed: '+variant)
            required={'held_station_mode','no_premature_restart','no_ip_before_release',
                      'recovered_station','saved_station_mode','same_boot_after_release','no_panic','station_http'}
            require(set(flow['checks'])==required and all(value is True for value in flow['checks'].values()),
                    'Wi-Fi waiting omitted an acceptance condition')
            filt=flow['filter']
            require(filt['status']=='on' and filt['queue']=='tx' and filt['interval']==120000000
                    and bool(filt['netdev']),'External DHCP buffering was not configured')
            held,recovered=flow['before_release'],flow['after_release']
            require(30<=held['guest_seconds']<120 and recovered['guest_seconds']>=held['guest_seconds'],
                    'DHCP was not held beyond the premature timeout')
            for row in [held,recovered]:
                require(row['mode_ram']==1 and row['mode_raw']==1 and row['rom_boots']==1
                        and row['ap_active'] is False,'Station mode or boot changed while waiting')
            require(held['connected'] is False and recovered['connected'] is True,
                    'DHCP release did not change real guest connectivity')
            require(held in flow['observations'] and recovered in flow['observations'],
                    'Missing sampled station transitions')
            require(all(row['rom_boots']<=1 for row in flow['observations']),
                    'Observer saw an unexpected restart')
        app=next(row for row in report['flows']['reconstructed']['sources']['images'] if row['file']=='app.bin')
        require(app['sha256']==expected['app_sha256'],'Wi-Fi VM booted another application image')
        for variant,flow in report['failure_flows'].items():
            require(flow['passed'] is True and flow['executable_media_unchanged'] is True,
                    'Real SDK failure/setup case failed: '+variant)
            required={'setup_saved','restart_once','external_ap_offline','setup_http',
                      'no_station_after_restore','setup_active','no_panic'}
            require(set(flow['checks'])==required and all(value is True for value in flow['checks'].values()),
                    'Missing actual SDK failure/setup acceptance condition')
            require(flow['external_ap_was_offline'] is True,'External AP did not stay offline during retries')
            failed,setup=flow['before_restore'],flow['after_restore']
            for row in [failed,setup]:
                require(row['mode_ram']==2 and row['mode_raw']==2 and row['rom_boots']==2
                        and row['connected'] is False,'Failed station did not persist setup and restart once')
            require(setup['ap_active'] is True and setup['guest_seconds']>=failed['guest_seconds'],
                    'Setup did not become active after restart')
            require(failed in flow['observations'] and setup in flow['observations'],
                    'Missing SDK failure/setup transitions')
            require(all(row['rom_boots']<=2 for row in flow['observations']),'Setup restart loop observed')
            require(flow['sources']==report['flows'][variant]['sources'],
                    'Failure and DHCP cases booted different images')
    except (KeyError,TypeError,StopIteration) as error:
        raise ValueError('Incomplete Wi-Fi waiting evidence') from error


def rejection_checks(report,expected):
    """Prove that stale identities, early setup and unobserved recovery cannot publish."""
    validate_wifi_fallback(report,expected)
    pin=test_pin(report)
    mutations=[('failed',('passed',),False),('changed-inputs',('inputs_unchanged',),False),
        ('wrong-app',('app_sha256',),'0'*64),('wrong-elf',('native_elf_sha256',),'0'*64),
        ('wrong-qemu',('qemu_sha256',),'0'*64),('wrong-test',('inputs_sha256',pin),'0'*64),
        ('missing-factory',('flows','original'),None),
        ('wrong-source',('flows','reconstructed','sources','source_sha256'),'0'*64),
        ('early-setup',('flows','reconstructed','before_release','mode_raw'),2),
        ('early-reset',('flows','reconstructed','before_release','rom_boots'),2),
        ('early-ip',('flows','original','before_release','connected'),True),
        ('short-delay',('flows','original','before_release','guest_seconds'),10),
        ('filter-off',('flows','original','filter','status'),'off'),
        ('filter-flushed',('flows','original','filter','interval'),1000000),
        ('no-recovery',('flows','reconstructed','after_release','connected'),False),
        ('no-http',('flows','reconstructed','checks','station_http'),False),
        ('panic',('flows','reconstructed','checks','no_panic'),False),
        ('changed-media',('flows','reconstructed','executable_media_unchanged'),False),
        ('missing-failure-case',('failure_flows','original'),None),
        ('ap-not-offline',('failure_flows','original','external_ap_was_offline'),False),
        ('failure-not-saved',('failure_flows','reconstructed','after_restore','mode_raw'),1),
        ('restart-loop',('failure_flows','reconstructed','after_restore','rom_boots'),3),
        ('missing-setup-http',('failure_flows','reconstructed','checks','setup_http'),False)]
    checks=[]
    for name,path,value in mutations:
        changed=deepcopy(report)
        target=changed
        for key in path[:-1]:target=target[key]
        target[path[-1]]=value
        try:validate_wifi_fallback(changed,expected)
        except ValueError:checks.append({'name':name,'passed':True})
        else:raise AssertionError('Wi-Fi contract accepted invalid evidence: '+name)
    return checks


def validate_wifi_fallback_guards(report):
    """Require every mandatory evidence rejection before publishing a passing gate."""
    names={'failed','changed-inputs','wrong-app','wrong-elf','wrong-qemu','wrong-test',
           'missing-factory','wrong-source','early-setup','early-reset','early-ip','short-delay',
           'filter-off','filter-flushed','no-recovery','no-http','panic','changed-media',
           'missing-failure-case','ap-not-offline','failure-not-saved','restart-loop','missing-setup-http'}
    checks=report.get('contract_checks',[])
    require(len(checks)==len(names) and {row['name'] for row in checks}==names
            and all(row['passed'] is True for row in checks),'Missing Wi-Fi waiting rejection checks')
