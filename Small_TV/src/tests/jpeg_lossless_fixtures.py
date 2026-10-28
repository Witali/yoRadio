"""Generate and read independently checked six-bit lossless target inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from color_convert_contract import expected


def sha(data):
    """Bind encoder, corpus metadata, compressed files and reference samples."""
    return hashlib.sha256(data).hexdigest()


def samples(channels):
    """Define source samples without calling either the firmware or JPEG decoder."""
    assert channels in (3,4)
    return bytes((x+2*y+3*c)&63 for y in range(240) for x in range(240) for c in range(channels))


def pixels(channels):
    """Apply the independently qualified Python RGB565 formula to original samples."""
    values=expected(list(samples(channels)),6,1 if channels==3 else 3)
    if sys.byteorder!='little':values.byteswap()
    return values.tobytes()


def load(path):
    """Read exact files inside the bundle and recompute every expected pixel hash."""
    path=path.resolve();manifest=json.loads(path.read_text(encoding='utf-8'))
    assert manifest['schema_version']==1 and manifest['passed']
    assert (manifest['width'],manifest['height'],manifest['precision'],manifest['predictor'])==(240,240,6,4)
    assert manifest['source_formula']=='(x + 2*y + 3*channel) & 63'
    images={};rows=[];pins={str(path):sha(path.read_bytes())}
    for row in manifest['fixtures']:
        name=row['name'];channels=row['channels']
        assert name==f'gradient-lossless-{"rgb" if channels==3 else "cmyk"}-6-p4.jpg'
        file=(path.parent/name).resolve();assert file.parent==path.parent and name not in images
        data=file.read_bytes();assert len(data)==row['bytes']<=102400 and sha(data)==row['sha256']
        assert row['samples_sha256']==sha(samples(channels)) and row['rgb565_sha256']==sha(pixels(channels))
        assert row['decode']['passed'] and (row['decode']['precision'],row['decode']['channels'])==(6,channels)
        assert (row['decode']['width'],row['decode']['height'])==(240,240)
        images[name]=data;rows.append(dict(name=name,expected='valid',rgb565_sha256=row['rgb565_sha256']))
        pins[str(file)]=sha(data)
    assert len(rows)==2 and {r['channels'] for r in manifest['fixtures']}=={3,4}
    pins[str(Path(__file__).resolve())]=sha(Path(__file__).read_bytes())
    pins[str(Path(__file__).with_name('color_convert_contract.py').resolve())]=sha(Path(__file__).with_name('color_convert_contract.py').read_bytes())
    return images,rows,pins


def main():
    """Use an encoder linked to pinned upstream; verify decoded samples against the formula."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-build',type=Path,required=True)
    parser.add_argument('--generator',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    reference=json.loads((args.reference_build/'build.json').read_text())
    assert reference['variant']=='upstream' and reference['patch_sha256'] is None
    assert not reference['flash_tables'] and not reference['compact_pools']
    decoder=Path(reference['executable']);assert sha(decoder.read_bytes())==reference['executable_sha256']
    manifest=dict(schema_version=1,passed=False,width=240,height=240,precision=6,predictor=4,
        source_formula='(x + 2*y + 3*channel) & 63',reference=reference,
        generator_sha256=sha(args.generator.read_bytes()),fixtures=[])
    for mode,channels in [('rgb',3),('cmyk',4)]:
        image=args.output/f'gradient-lossless-{mode}-6-p4.jpg';raw=args.output/(mode+'-samples.raw')
        subprocess.run([str(args.generator.resolve()),str(image.resolve()),str(channels)],check=True)
        result=subprocess.run([str(decoder),'decode',str(image.resolve()),str(raw.resolve()),'0','0'],capture_output=True,check=True)
        decoded=json.loads(result.stdout);assert decoded['passed'] and decoded['precision']==6 and decoded['channels']==channels
        assert (decoded['width'],decoded['height'])==(240,240) and image.stat().st_size<=102400
        assert raw.read_bytes()==samples(channels)
        manifest['fixtures'].append(dict(name=image.name,channels=channels,bytes=image.stat().st_size,
            sha256=sha(image.read_bytes()),samples_sha256=sha(raw.read_bytes()),rgb565_sha256=sha(pixels(channels)),decode=decoded))
    manifest['passed']=True;path=args.output/'lossless6-manifest.json'
    path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    load(path)
    print('PASS source formula, unmodified upstream samples and RGB565:',[(r['name'],r['bytes']) for r in manifest['fixtures']])


if __name__=='__main__':main()
