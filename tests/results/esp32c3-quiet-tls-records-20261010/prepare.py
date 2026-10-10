from pathlib import Path
root=Path(__file__).resolve().parent
source=Path('.build/c3-aac-growth-tls-20261010/physical.py').read_text()
source=source.replace('HTTPS AAC-growth campaign','TLS record-size campaign')
source=source.replace('from aac_growth import load_pairs\n','')
source=source.replace("FIXTURES = Path('.build/c3-aac-growth-20261010')\nreference = FIXTURES / 'references.json'\nload_pairs(FIXTURES)\n",'')
source=source.replace("    reference_sha256=sha(reference.read_bytes()),\n",'')
source=source.replace("'tools/esp32c3_tests/aac_growth.py'","'tools/esp32c3_tests/quiet_tls_records.py'")
source=source.replace("'--fixtures', str(FIXTURES), ",'')
source=source.replace("'--require-output-health', ","'--seconds', '75', ")
source=source.replace('AAC growth over HTTPS','measured quiet TLS records')
source=source.replace("str(OUT / 'files')","str(OUT / 'records')")
source=source.replace("OUT / 'files.log'","OUT / 'records.log'")
assert 'load_pairs' not in source and 'reference' not in source and 'FIXTURES' not in source
(root/'physical.py').write_text(source)
for name in ('ca.pem','server.pem'):
    (root/name).write_bytes((Path('.build/c3-aac-growth-tls-20261010')/name).read_bytes())
print('Prepared bounded controller and public certificates')
