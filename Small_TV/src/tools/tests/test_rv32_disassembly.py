"""Check ISA-qualified exports against an ELF parser, real GNU tools and literal RV32 execution."""
import argparse
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_RISCV,UC_MODE_RISCV32
from unicorn import riscv_const as rv
from reverse import rv32_disassembly as view
import assist_c_port as port
from audit_factory_xrefs import Image,sha

OPTIONS=None


class EncodingTests(unittest.TestCase):
    def test_every_compressed_call_immediate_against_literal_cpu(self):
        """All 2048 encodings must set RA/PC like RV32 C.JAL and leave s6 unchanged."""
        cpu=Uc(UC_ARCH_RISCV,UC_MODE_RISCV32);cpu.mem_map(0x1f000,0x4000);pc=0x20000
        for immediate in range(2048):
            word=0x2001|(immediate<<2);cpu.mem_write(pc,word.to_bytes(2,'little'))
            cpu.ctl_remove_cache(pc,pc+2)
            cpu.reg_write(rv.UC_RISCV_REG_RA,0xdeadbeef);cpu.reg_write(rv.UC_RISCV_REG_S6,17)
            cpu.emu_start(pc,0x23000,count=1)
            self.assertEqual(cpu.reg_read(rv.UC_RISCV_REG_PC),view.compressed_jal_target(word,pc))
            self.assertEqual(cpu.reg_read(rv.UC_RISCV_REG_RA),pc+2)
            self.assertEqual(cpu.reg_read(rv.UC_RISCV_REG_S6),17)

    def test_target_wrap_and_invalid_encodings(self):
        """PC arithmetic wraps at 32 bits; other compressed opcodes must be rejected."""
        self.assertEqual(view.compressed_jal_target(0x2001,0xffffffff),0xffffffff)
        self.assertEqual(view.compressed_jal_target(0x2009,0xfffffffe),0)
        for word in (-1,0x10000,0xa001,0x8082,0,True):
            with self.subTest(word=word),self.assertRaises(ValueError):view.compressed_jal_target(word,0x1000)

    def test_section_bytes_addresses_and_isa_attributes(self):
        """An independent ELF reader must recover exactly the input bytes and no load segments."""
        regions=[('.text',0x42000020,bytes.fromhex('712b8280')),('.iram.text',0x40380000,bytes.fromhex('4111'))]
        data=view.elf_view(regions);elf=ELFFile(io.BytesIO(data))
        self.assertEqual(data,view.elf_view(regions));self.assertEqual(elf.elfclass,32)
        self.assertTrue(elf.little_endian);self.assertEqual(elf.num_segments(),0)
        self.assertEqual(elf['e_machine'],'EM_RISCV');self.assertEqual(elf['e_flags'],1)
        for name,address,code in regions:
            section=elf.get_section_by_name(name);self.assertEqual(section['sh_addr'],address)
            self.assertEqual(section.data(),code);self.assertEqual(section['sh_flags'],6)
        self.assertIsNone(elf.get_section_by_name('.data'))
        attr=elf.get_section_by_name('.riscv.attributes')
        self.assertEqual(attr['sh_type'],'SHT_RISCV_ATTRIBUTES');self.assertEqual(attr['sh_flags'],0)
        self.assertIn(view.ISA.encode()+b'\0',attr.data())

    def test_bad_region_geometry_is_rejected(self):
        """Reject duplicate, overlapping, partial, reserved and overflowing code views."""
        cases=[[],[('.text',1,b'\x82\x80')],[('.text',0,b'')],[('.text',0,b'\x82')],
               [('.text',0xffffffff,b'\x82\x80')],[('.text',0,b'\x82\x80'),('.text',4,b'\x82\x80')],
               [('.text',0,b'\x82\x80'),('.other',0,b'\x82\x80')],
               [('../outside',0,b'\x82\x80')],[('.riscv.attributes',0,b'\x82\x80')]]
        for regions in cases:
            with self.subTest(regions=regions),self.assertRaises(ValueError):view.elf_view(regions)


class ToolTests(unittest.TestCase):
    def setUp(self):
        """Use an owned unique child directory for the actual GNU invocations."""
        if OPTIONS.objdump is None:self.skipTest('Pass --objdump for actual GNU acceptance')
        self.root=OPTIONS.temp_root.resolve();self.root.mkdir(parents=True,exist_ok=True)
        self.temporary=tempfile.TemporaryDirectory(prefix='test-rv32-',dir=self.root)
        folder=Path(self.temporary.name).resolve();self.assertTrue(folder.is_relative_to(self.root))
        self.addCleanup(self.temporary.cleanup);self.folder=folder

    def test_every_compressed_call_is_printed_and_parsed_correctly(self):
        """The real decoder and transfer assistant must retain every link-producing jump."""
        base=0x10000;code=b''.join((0x2001|(value<<2)).to_bytes(2,'little') for value in range(2048))
        with view.Disassembler(OPTIONS.objdump,[('.text',base,code)],self.folder) as decoder:
            output=decoder.text(canonical=True);first=decoder.metadata
            functions=port.parse(output);items=[item for _,rows in functions for item in rows]
            self.assertEqual(len(items),2048)
            for index,item in enumerate(items):
                self.assertEqual(item.kind(),'call');self.assertEqual(item.target(),view.compressed_jal_target(0x2001|(index<<2),base+index*2))
                self.assertFalse(item.original_assembly)
        self.assertFalse(list(self.folder.glob('rv32-view-*')))
        with view.Disassembler(OPTIONS.objdump,[('.text',base,code)],self.folder) as decoder:
            self.assertEqual(first,decoder.metadata)

    def test_wrong_isa_fails_before_export_and_cleans_temporary_view(self):
        """A real RV64 interpretation must fail the independent link-instruction canary."""
        with mock.patch.object(view,'ISA',view.ISA.replace('rv32','rv64',1)):
            with self.assertRaisesRegex(ValueError,'canary'):
                with view.Disassembler(OPTIONS.objdump,[('.text',0x1000,b'\x82\x80')],self.folder):
                    self.fail('Wrong ISA should never open an accepted view')
        self.assertFalse(list(self.folder.glob('rv32-view-*')))

    def test_invalid_requested_range_is_rejected(self):
        """A bounded export may not extend outside or split its original halfwords."""
        with view.Disassembler(OPTIONS.objdump,[('.text',0x1000,b'\x82\x80'*2)],self.folder) as decoder:
            for start,stop in ((0x1001,0x1004),(0x1000,0x1005),(0,0x1002),(0x1004,0x1000),(None,0x1002)):
                with self.subTest(start=start,stop=stop),self.assertRaises(ValueError):decoder.text(start,stop)

    def test_existing_dump_export_cli_preserves_code_and_exposes_factory_call(self):
        """Exercise the public IROM exporter on the verified capture and a real missed call."""
        if OPTIONS.dump is None or OPTIONS.factory_elf is None:self.skipTest('Pass --dump and --factory-elf')
        output=self.folder/'selected';tool=Path(__file__).resolve().parents[1]/'disassemble_factory.py'
        result=subprocess.run([sys.executable,'-B',str(tool),'--objdump',str(OPTIONS.objdump),
            '--dump',str(OPTIONS.dump),'--output',str(output),'--ranges','0x420aeb64:0x420aeb72'],
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr.decode())
        manifest=json.loads((output/'manifest.json').read_bytes());record=manifest['functions'][0]
        image=Image(OPTIONS.factory_elf.read_bytes())
        self.assertEqual(record['code_sha256'],sha(image.read(0x420aeb64,14,True)))
        parsed=port.analyze((output/record['assembly']).read_text(),'factory-create')
        self.assertEqual(parsed[0]['calls'],[{'address':'0x420aeb6e','target':'0x420af10a','logical_name':None}])
        self.assertFalse(any(w['kind']=='rv32_decode_corrected' for w in parsed[0]['warnings']))
        self.assertFalse(list(output.glob('*.bin')));self.assertFalse(list(output.glob('*.elf')))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--objdump',type=Path);parser.add_argument('--dump',type=Path)
    parser.add_argument('--factory-elf',type=Path);parser.add_argument('--temp-root',type=Path,required=True)
    OPTIONS,args=parser.parse_known_args();unittest.main(argv=[__file__,*args])
