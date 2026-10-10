from pathlib import Path
root=Path(__file__).resolve().parent
old=Path('.build/c3-tls-renegotiation-20261010')
source=(old/'physical.py').read_text()
source=source.replace('esp32c3-idf-6.1-r9a97-quiet-growth-tls','esp32c3-idf-6.1-r9a97-quiet-prefill500-reneg')
source=source.replace('7871681aef75c9bb89caffab97f073eabe62b272ff8dc20f710cb4473c56b6fd','5096f10df159662a534a939f93da126c806345106b3b009af822ff00883a37c3')
source=source.replace("'--mode', 'small',", "'--mode', 'small', '--mode', 'large',")
source=source.replace("PYTHONPATH=str(ROOT/'packages')", "PYTHONPATH=str(Path('.build/c3-tls-renegotiation-20261010/packages').resolve())")
(root/'physical.py').write_text(source)
(root/'fixture-inputs.json').write_bytes((old/'fixture-inputs.json').read_bytes())
(root/'dependencies.json').write_bytes((old/'dependencies.json').read_bytes())
(root/'requirements-tls-renegotiation.txt').write_bytes(Path('tools/audio_test_server/requirements-tls-renegotiation.txt').read_bytes())
(root/'review.py').write_bytes((old/'review.py').read_bytes())
print('Prepared four-case prefill experiment with exact restoration')
