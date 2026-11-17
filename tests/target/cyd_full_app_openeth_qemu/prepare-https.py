"""Generate a disposable HTTPS identity and its NVS partition for QEMU."""
import argparse
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nvsgen', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / '.build') or output == ROOT / '.build':
        raise ValueError('Use a fresh HTTPS fixture directory under .build')
    output.mkdir(parents=True)
    prepare = runpy.run_path(str(HERE / 'prepare-profile.py'))
    pack = runpy.run_path(str(ROOT / 'idf/components/native_web_transport/tools/pack_tls_bundle.py'))
    from cryptography.hazmat.primitives import serialization

    with tempfile.TemporaryDirectory(prefix='cyd-qemu-https-') as folder:
        local = Path(folder)
        prepare['write_local_ca'](local, '127.0.0.1')
        key = serialization.load_pem_private_key((local / 'server-key.pem').read_bytes(), None)
        pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL,
                                serialization.NoEncryption())
        pack['validate_key_profile'](pem)
        bundle = pack['build_bundle']((local / 'server.pem').read_bytes(), pem)
        csv = local / 'nvs.csv'
        csv.write_bytes(pack['encode_output'](bundle, nvs_csv=True))
        subprocess.run([sys.executable, '-B', args.nvsgen.resolve(strict=True), 'generate',
                        csv, output / 'nvs.bin', '0x5000'], check=True)
        (output / 'ca.pem').write_bytes((local / 'ca.pem').read_bytes())
    print('Prepared a local HTTPS NVS image for QEMU')


if __name__ == '__main__':
    main()
