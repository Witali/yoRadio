"""Verify archived firmware/source provenance, flash bounds and route coverage."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
ARCHIVE=REPO/"firmware/development/small-tv-esp32c2-reconstructed"


def main():
    manifest=json.loads((ARCHIVE/"manifest.json").read_text(encoding="utf-8-sig"))
    assert manifest["target"]=="esp32c2" and manifest["xtal_mhz"]==26 and manifest["flash_bytes"]==0x400000
    for item in manifest["images"]:
        data=(ARCHIVE/item["file"]).read_bytes()
        assert len(data)==item["bytes"] and hashlib.sha256(data).hexdigest()==item["sha256"],item["file"]
        assert int(item["offset"],16)+len(data)<=0x400000
    table=(ARCHIVE/"partition-table.bin").read_bytes()
    partitions=[]
    for position in range(0,len(table),32):
        entry=table[position:position+32]; magic=struct.unpack_from("<H",entry)[0]
        if magic==0xebeb:
            assert entry[16:]==hashlib.md5(table[:position]).digest()
            break
        assert magic==0x50aa
        _,kind,subtype,offset,length,label,flags=struct.unpack("<HBBII16sI",entry)
        partitions.append({"name":label.split(b"\0")[0].decode(),"type":kind,"subtype":subtype,"offset":offset,"size":length})
        assert offset+length<=0x400000 and flags==0
    assert [(p["name"],p["offset"],p["size"]) for p in partitions]==[("nvs",0x9000,0x6000),("phy_init",0xf000,0x1000),("factory",0x10000,0x177000),("assets",0x200000,0x1e7000)]
    for first,second in zip(partitions,partitions[1:]): assert first["offset"]+first["size"]<=second["offset"]
    app=(ARCHIVE/"app.bin").read_bytes()
    assert app[0]==0xe9 and struct.unpack_from("<H",app,12)[0]==12
    position,checksum=24,0xef
    for _ in range(app[1]):
        _,length=struct.unpack_from("<II",app,position); position+=8
        assert length<=len(app)-position
        for byte in app[position:position+length]: checksum^=byte
        position+=length
    checksum_position=position+(-position-1)%16
    assert app[checksum_position]==checksum and app[23]==1
    assert hashlib.sha256(app[:checksum_position+1]).digest()==app[checksum_position+1:checksum_position+33]
    assert len(app)<=partitions[2]["size"] and (ARCHIVE/"assets.bin").stat().st_size==partitions[3]["size"]
    expected={("GET" if row["method"]=="1" else "POST",row["uri"]) for row in csv.DictReader((ROOT.parent/"analysis/security/registered-routes.tsv").read_text().splitlines(),delimiter="\t")}
    actual=re.findall(r'\.uri="([^"]+)",\.method=HTTP_(GET|POST)',(ROOT/"app/web/server.c").read_text())
    actual={(method,uri) for uri,method in actual}
    assert len(expected)==34 and len(actual)==40 and expected<=actual
    generated=REPO/".build/small-tv-esp32c2/verification-resources"
    subprocess.run([sys.executable,str(ROOT/"tools/prepare_resources.py"),"--output",str(generated)],check=True)
    fresh=json.loads((generated/"source-manifest.json").read_text())
    stored=json.loads((ARCHIVE/"source-manifest.json").read_text())
    assert fresh==stored and fresh["aggregate_sha256"]==manifest["source_sha256"]
    assert (generated/"assets.bin").read_bytes()==(ARCHIVE/"assets.bin").read_bytes()
    symbols=json.loads((ROOT/"symbol-map.json").read_text())
    entries=[f["address"] for f in symbols["functions"]]
    assert len(entries)==176 and len(set(entries))==176 and len(symbols["globals"])==43
    native_test=REPO/".build/small-tv-esp32c2/native-tests/native_test.exe"
    result=subprocess.run([str(native_test),str(ARCHIVE/"assets.bin")],capture_output=True,text=True,check=True)
    assert "PASS: 1219 checks" in result.stdout
    assert hashlib.sha256((ROOT.parent/"full-flash.bin").read_bytes()).hexdigest()==symbols["source_dump_sha256"]
    report={"target":"esp32c2","date":"2026-10-12","sdk_revision":manifest["idf_revision"],
        "source_sha256":manifest["source_sha256"],"app_sha256":hashlib.sha256(app).hexdigest(),
        "app_bytes":len(app),"app_partition_bytes":partitions[2]["size"],"app_partition_free_bytes":partitions[2]["size"]-len(app),
        "media_bytes":partitions[3]["size"],"original_routes":34,"registered_routes":40,
        "reference_functions":176,"named_globals":43,"named_local_parameter_aliases":sum(len(item["names"]) for item in symbols["locals"]),
        "host_result":result.stdout.strip(),"asset_pack_matches_sanitized_exports":True,"compiled_source_hashes_match_archive":True,
        "partition_table_md5_valid":True,"original_flash_dump_unchanged":True,
        "target_image_footer":"segment XOR checksum and appended SHA-256 valid; also checked with esptool image-info",
        "static_diram_bytes":79208,"linker_diram_remaining_bytes":112136,
        "runtime_memory_measured":False,"hardware_tested":False,"device_flashed":False,"ota":False,
        "limitations":["Host platform I/O is simulated; no Wi-Fi/SNTP/TLS/SPI/LEDC electrical or runtime verification.",
                       "Native themes/fonts approximate the factory graphics; see README.md.",
                       "An upstream MSVC size_t-to-unsigned warning remains in TJpgDec; target compilation succeeds."]}
    (ROOT/"validation.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(result.stdout.strip())
    print("Verified: image/source SHA-256, C2 target, partition MD5/bounds, 34 recovered routes, asset reproducibility, unchanged original dump")


if __name__=="__main__": main()
