"""Pure Windows argv/response models; no executable, compiler or SDK is called."""
from pathlib import Path
import subprocess
import tempfile
import unittest

import windows_compile_command as helper

HERE = Path(__file__).resolve().parent


class C3CompileContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = HERE/'host-models'
        parent.mkdir(exist_ok=True)
        cls.root = Path(tempfile.mkdtemp(prefix='RV32 model ',dir=parent)).resolve()
        # Retain owned construction models as evidence; no recursive cleanup.
        cls.sequence = 0

    def setUp(self):
        type(self).sequence += 1
        self.folder = self.root/f'case-{self.sequence}'
        self.build = self.folder/'build'
        self.cflags = self.build/'toolchain/cflags'
        self.specs = self.build/'specs/picolibc.specs'
        self.source = self.folder/'variant/vorbis_repair/setup.c'
        for path in (self.cflags,self.specs,self.source): path.parent.mkdir(parents=True,exist_ok=True)
        self.specs.write_text('source-only synthetic specs model\n')
        self.source.write_text('/* source-only model, never compiled */\n')
        self.lines = ['-march=rv32imc_zicsr_zifencei','-mtune=esp-base',
                      '"-specs='+self.specs.as_posix()+'"','-D__PICOLIBC_ERRNO_FUNCTION=__errno']
        self.cflags.write_text('\n'.join(self.lines)+'\n')
        # This is an uncreated pathname, not a real or fabricated executable.
        self.compiler = self.folder/'tools with spaces/riscv32-esp-elf-gcc.exe'
        self.argv = [str(self.compiler),'-DESP_PLATFORM','@'+self.cflags.as_posix(),
                     '-I'+str(self.build/'include dir'),'-o',str(self.build/'setup.c.obj'),'-c',str(self.source)]
        self.row = dict(directory=str(self.build),file=str(self.source),arguments=self.argv)

    def prepare(self,row=None):
        return helper.macro_command(row or self.row,self.compiler,self.source)

    def test_windows_quoting_and_preserved_four_line_response(self):
        command = subprocess.list2cmdline(self.argv)  # String formatting only.
        self.assertEqual(helper.windows_argv(command),self.argv)
        row = dict(directory=str(self.build),file=str(self.source),command=command)
        probe,cwd,original,inputs = self.prepare(row)
        self.assertEqual(original,self.argv)
        self.assertEqual(probe,self.argv[:4]+[str(self.source),'-E','-dM'])
        self.assertEqual(cwd,self.build)
        self.assertEqual(set(inputs),{self.cflags,self.specs})
        self.assertIn(self.argv[2],probe)
        helper.check_macro_inputs(inputs)

    def test_wrong_arch_arbitrary_nested_missing_and_extra_responses_reject(self):
        for lines in (self.lines[:1]+['-mlongcalls']+self.lines[2:],
                      self.lines+['-DUNREVIEWED=1'],
                      self.lines[:2]+['@nested']+self.lines[3:]):
            self.cflags.write_text('\n'.join(lines)+'\n')
            with self.assertRaises(ValueError): self.prepare()
        self.cflags.write_text('\n'.join(self.lines)+'\n')
        for args in ([a for a in self.argv if not a.startswith('@')],
                     self.argv+['@other'],
                     [a if not a.startswith('@') else '@'+str(self.build/'other/cflags') for a in self.argv]):
            with self.assertRaises(ValueError): self.prepare(dict(self.row,arguments=args))

    def test_outer_compile_operands_compiler_source_and_output_context_reject(self):
        for args in ([a for a in self.argv if a!='-c'],self.argv+['-c'],self.argv+['-o','second.obj'],
                     ['compiler-launcher']+self.argv,self.argv+['-E'],self.argv+['-MMD'],
                     self.argv+['-Wp,-DUNREVIEWED=1']):
            with self.assertRaises(ValueError): self.prepare(dict(self.row,arguments=args))
        with self.assertRaises(ValueError): self.prepare(dict(self.row,file=str(self.source.with_name('other.c'))))

    def test_both_generated_inputs_must_remain_exact_and_specs_nonempty(self):
        _,_,_,inputs = self.prepare()
        self.cflags.write_bytes(self.cflags.read_bytes()+b'\n')
        with self.assertRaises(ValueError): helper.check_macro_inputs(inputs)
        self.cflags.write_bytes(inputs[self.cflags])
        self.specs.write_bytes(b'changed')
        with self.assertRaises(ValueError): helper.check_macro_inputs(inputs)
        self.specs.write_bytes(b'')
        with self.assertRaisesRegex(ValueError,'empty'): self.prepare()


if __name__=='__main__': unittest.main(verbosity=2)
