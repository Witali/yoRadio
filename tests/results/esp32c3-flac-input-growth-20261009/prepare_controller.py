from pathlib import Path
root = Path(__file__).resolve().parent
text = Path('tests/results/esp32c3-prefill-matched-20261009/physical.py').read_text()
text = text.replace('Targeted AAC EOF and matched-code FLAC A/B/A; restore saved production.',
                    'Matched FLAC queue growth A/B/A, switching and AAC TLS recovery.')
text = text.replace('.build/c3-prefill-matched-20261009', '.build/c3-flac-input-growth-20261009')
text = text.replace('r9a97-prefill-min\'+name', 'r9a97-flac-input\'+name')
text = text.replace("for name in ('0','250')", "for name in ('0','4')")
text = text.replace("manifests['250']", "manifests['4']")
old = "require(json.loads(Path('.build/c3-prefill-control-20261009/build-audit.json').read_text())['result']=='PASS','Control build unaudited')"
new = "require(all(v['result']=='PASS' for v in json.loads((ROOT/'build-audit.json').read_text()).values()),'Builds unaudited')"
assert old in text
text = text.replace(old,new)
text = text.replace("def run_phase(label,variant,suite,extra,timeout):", "def run_phase(label,variant,suite,extra,timeout,records=False):")
old = "    started=time.monotonic();print('START',label,flush=True)"
new = """    if records:
        command=[sys.executable,'-X','utf8','tools/esp32c3_tests/trace_transport.py',
            '--runner','tls_records','--',*shared,'--firmware',str(paths[variant]),
            '--ca',str(TRUST/'ca.pem'),'--cert',str(TRUST/'server.pem'),
            '--key',str(TRUST/'server.key'),'--seconds','75','--mode','grow',
            '--pacing-ratio','1.0','--output',str(OUT/label)]
    started=time.monotonic();print('START',label,flush=True)"""
assert old in text
text = text.replace(old,new)
start = text.index("    activate('250','eof-candidate')")
end = text.index("    save('settings-after-tests.json'", start)
text = text[:start] + """    for label,variant in (('flac-control-before','0'),('flac-candidate','4'),('flac-control-after','0')):
        activate(variant,label)
        run_phase(label,variant,'load',['--case','stress-flac-48000-2ch-16bit-610s',
            '--fixture-manifest','.build/c3-reserve-soak-20261008/fixtures/manifest.json',
            '--load-seconds','180','--load-idle-recovery','--sustained-protocol','https',*tls],timeout=330)
    activate('4','switch-candidate')
    run_phase('switch','4','switch',['--case','flac-level8','--case','he-48000-stereo',
        '--case','hev2-44100-stereo','--cycles','3'],timeout=210)
    run_phase('eof-https','4','eof',['--case','flac-level8','--case','hev2-44100-stereo',
        '--eof-protocol','https',*tls],timeout=240)
    run_phase('records-after-switch','4',None,[],timeout=165,records=True)
""" + text[end:]
text = text.replace("require(not OUT.exists(),'Preserve physical evidence')", """require(not OUT.exists(),'Preserve physical evidence')""")
(root/'physical.py').write_text(text)
compile(text,str(root/'physical.py'),'exec')
print('Prepared guarded A/B/A and restoration controller')
