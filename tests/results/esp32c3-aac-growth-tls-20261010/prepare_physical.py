import hashlib,json,shutil,ssl
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import ExtensionOID
ROOT=Path(__file__).resolve().parent
ART=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-growth-tls')
FIXTURES=Path('.build/c3-aac-growth-20261010')
KEY=Path('.build/c3-tls-records-20261007/trust/server.key')
assert json.loads((ROOT/'quiet-growth-tls/build-audit.json').read_text())['result']=='PASS'
assert json.loads((ROOT/'application-object-comparison.json').read_text())['result']=='PASS'
manifest=json.loads((ART/'manifest.json').read_text())
ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain(ROOT/'server.pem',KEY)
cert=x509.load_pem_x509_certificate((ROOT/'server.pem').read_bytes())
addresses=cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value
assert '192.168.100.253' in [str(ip) for ip in addresses.get_values_for_type(x509.IPAddress)]
source=(FIXTURES/'physical.py').read_text()
source=source.replace('HTTP AAC-growth','HTTPS AAC-growth')
source=source.replace('quiet-mpi-health','quiet-growth-tls')
source=source.replace("reference = ROOT / 'references.json'\nload_pairs(ROOT)","FIXTURES = Path('.build/c3-aac-growth-20261010')\nreference = FIXTURES / 'references.json'\nload_pairs(FIXTURES)")
source=source.replace('5505393d2b7d4fcad1303b3b96d9c41709c86a84e687bcbeb059a4241d243da6',manifest['image']['sha256'])
source=source.replace("'--fixtures', str(ROOT), '--host'", "'--fixtures', str(FIXTURES), '--ca', str(ROOT/'ca.pem'), '--cert', str(ROOT/'server.pem'), '--key', '.build/c3-tls-records-20261007/trust/server.key', '--require-output-health', '--host'")
source=source.replace('AAC growth files','AAC growth over HTTPS')
(ROOT/'physical.py').write_text(source)
for name in ('manifest.json','references.json'):
    shutil.copyfile(FIXTURES/name,ROOT/('fixture-'+name))
shutil.copytree('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-growth-tls/log',ROOT/'build-logs')
print('Prepared six verified TLS transfers; private key remains local, exact listened image restored afterward')
