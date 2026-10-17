"""Check control-flow facts against independent tiny RISC-V instruction graphs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import assist_c_port as port

TOOL = Path(port.__file__)
TEMP_ROOT = None


def decoded(*rows):
    """Build decoded text with explicit RV32/RVC byte sizes, independent of CFG code."""
    return '\n'.join(f'{address:x}: {encoding} {instruction}' for address, encoding, instruction in rows)


class FlowTests(unittest.TestCase):
    def graph(self, text):
        """Analyze one complete synthetic function and retain all reported facts."""
        functions = port.parse(text)
        self.assertEqual(len(functions), 1)
        return port.structure(*functions[0])

    def test_short_hex_targets_and_compressed_fallthrough(self):
        text = decoded((0x1000, 'c501', 'beqz a0,1008 <done>'),
                       (0x1002, '00000013', 'nop'), (0x1006, '8082', 'ret'),
                       (0x1008, '8082', 'ret'))
        graph = self.graph(text)
        self.assertEqual(graph['blocks'][0]['successors'], ['0x1002', '0x1008'])
        self.assertEqual(graph['return_sites'], ['0x1006', '0x1008'])

    def test_offset_ra_is_not_canonical_return(self):
        self.assertEqual(port.Instruction(0, 4, '00000067', 'jalr', 'zero,4(ra)').kind(), 'indirect')
        self.assertEqual(port.Instruction(0, 4, '00008067', 'jalr', 'zero,0(ra)').kind(), 'return')
        self.assertEqual(port.Instruction(0, 4, '00008067', 'jalr', 'x0,0(x1)').kind(), 'return')
        self.assertEqual(port.Instruction(0, 4, '00050067', 'jalr', 'zero,0(a0)').kind(), 'indirect')
        self.assertEqual(port.Instruction(0, 2, '8082', 'jr', 'x1').kind(), 'return')

    def test_separate_elf_sections_can_have_descending_addresses(self):
        functions = port.parse('42001000 <flash_helper>:\n42001000: 8082 ret\n'
                               '40370000 <iram_helper>:\n40370000: 8082 ret\n')
        self.assertEqual([name for name, _ in functions], ['flash_helper', 'iram_helper'])

    def test_natural_self_loop(self):
        graph = self.graph(decoded((0x1000, '450d', 'li a0,3'), (0x1002, '157d', 'addi a0,a0,-1'),
                                  (0x1004, 'fd7d', 'bnez a0,1002'), (0x1006, '8082', 'ret')))
        self.assertEqual(graph['natural_loops'], [{'header': '0x1002', 'latch': '0x1002', 'blocks': ['0x1002']}])

    def test_irreducible_back_edge_is_only_candidate(self):
        graph = self.graph(decoded((0x1000, '00000063', 'beqz a0,1010'),
            (0x1004, '0000006f', 'j 1014'), (0x1008, '8082', 'ret'),
            (0x1010, '0000006f', 'j 1014'), (0x1014, '00000063', 'bnez a1,1004'),
            (0x1018, '8082', 'ret')))
        self.assertFalse(graph['natural_loops'])
        self.assertIn({'source': '0x1014', 'target': '0x1004'}, graph['back_edge_candidates'])
        self.assertFalse(next(block for block in graph['blocks'] if block['address'] == '0x1008')['reachable'])

    def test_gap_does_not_merge_disconnected_instructions(self):
        graph = self.graph(decoded((0x1000, '00000013', 'nop'), (0x1008, '8082', 'ret')))
        self.assertEqual(len(graph['blocks']), 2)
        self.assertFalse(graph['blocks'][1]['reachable'])
        self.assertTrue(any(row['kind'] == 'gap' for row in graph['warnings']))

    def test_invalid_layout_is_rejected(self):
        for text in (decoded((0x1000, '00000013', 'nop'), (0x1000, '8082', 'ret')),
                     decoded((0x1000, '00000013', 'nop'), (0x1002, '8082', 'ret')),
                     decoded((0x1000, '123456', 'nop'))):
            with self.subTest(text=text), self.assertRaises(ValueError):
                port.parse(text)

    def test_stack_hints_include_epilogue_and_abi_aliases(self):
        graph = self.graph(decoded((0x1000, '1141', 'addi sp,sp,-16'),
            (0x1002, 'c606', 'sw ra,12(sp)'), (0x1004, 'c422', 'sw s0,8(sp)'),
            (0x1006, '40b2', 'lw ra,12(sp)'), (0x1008, '4422', 'lw s0,8(sp)'),
            (0x100a, '0141', 'addi sp,sp,16'), (0x100c, '8082', 'ret')))
        self.assertEqual(graph['prologue'][0]['stack_bytes'], 16)
        self.assertEqual(graph['epilogues'][0]['return_address'], '0x100c')
        self.assertEqual(graph['epilogues'][0]['stack_bytes'], 16)
        self.assertEqual(set(graph['epilogues'][0]['restored_registers']), {'ra', 's0'})

    def test_signed_unsigned_conditions(self):
        self.assertEqual(port.branch_condition(port.Instruction(0, 4, '', 'bltu', 'a0,a1,1000')), 'r[10] < r[11]')
        self.assertEqual(port.branch_condition(port.Instruction(0, 4, '', 'blt', 'a0,a1,1000')), '(int32_t)r[10] < (int32_t)r[11]')
        self.assertEqual(port.register('x0'), 'UINT32_C(0)')

    def test_unresolved_indirect_and_trap_are_visible(self):
        graph = self.graph(decoded((0x1000, '8502', 'jr a0'), (0x1002, '9002', 'ebreak')))
        self.assertFalse(graph['blocks'][1]['reachable'])
        self.assertTrue(any(row['kind'] == 'indirect' for row in graph['warnings']))

    def test_subroutine_inside_range_requires_boundary_review(self):
        graph = self.graph(decoded((0x1000, '000000ef', 'jal ra,1008'),
                                  (0x1004, '8082', 'ret'), (0x1008, '8082', 'ret')))
        self.assertIn({'kind': 'call_inside_range', 'address': '0x1000', 'target': '0x1008'}, graph['warnings'])

    def test_factory_clock_theme_has_no_natural_loop(self):
        source = TOOL.parent.parent / 'reference/assembly/read_clock_theme_at_4200dfdc.asm'
        graph = self.graph(source.read_text())
        self.assertEqual(graph['entry'], '0x4200dfdc')
        self.assertEqual(graph['instructions'], 50)
        self.assertEqual(graph['return_sites'], ['0x4200e068'])
        self.assertEqual([row['target'] for row in graph['calls']],
                         ['0x4203b178', '0x4203b114', '0x400004a8', '0x4203b192'])
        self.assertEqual(graph['prologue'][0]['stack_bytes'], 32)
        self.assertEqual(graph['epilogues'][0]['stack_bytes'], 32)
        self.assertFalse(graph['natural_loops'])
        self.assertIn({'source': '0x4200e06a', 'target': '0x4200e020'}, graph['back_edge_candidates'])
        self.assertFalse(graph['warnings'])


class CommandTests(unittest.TestCase):
    def setUp(self):
        """Keep temporary artifacts under the caller-selected scratch directory."""
        self.temporary = tempfile.TemporaryDirectory(dir=TEMP_ROOT)
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.source = self.folder / 'factory.asm'
        self.source.write_text('42001000 <.flash.text+0x1000>:\n' + decoded(
            (0x42001000, '1141', 'addi sp,sp,-16'), (0x42001002, 'c501', 'beqz a0,42001008'),
            (0x42001004, '0141', 'addi sp,sp,16'), (0x42001006, '8082', 'ret'),
            (0x42001008, '0141', 'addi sp,sp,16'), (0x4200100a, '8082', 'ret')))

    def command(self, *arguments, expected=0):
        """Exercise the public CLI rather than calling its formatting functions."""
        result = subprocess.run([sys.executable, str(TOOL), str(self.source), *map(str, arguments)],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, expected, result.stderr)
        return result

    def test_reports_names_conditions_and_source_identity(self):
        symbols = self.folder / 'names.json'
        symbols.write_text(json.dumps({'functions': [{'address': '0x42001000', 'logical_name': 'read_theme',
                                                       'native_module': 'app/web/settings_api.c'}], 'globals': []}))
        report, markdown = self.folder / 'report.json', self.folder / 'report.md'
        self.command('--symbols', symbols, '--json', report, '--markdown', markdown)
        data = json.loads(report.read_text())
        self.assertEqual(data['source_sha256'], hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertEqual(data['functions'][0]['name'], 'read_theme')
        self.assertEqual(data['functions'][0]['native_module'], 'app/web/settings_api.c')
        self.assertIn('r[10] == UINT32_C(0)', markdown.read_text())
        self.assertIn('0x42001008', markdown.read_text())

    def test_bounds_and_invalid_ranges(self):
        data = json.loads(self.command('--start', '0x42001004', '--stop', '0x42001008', '--name', 'bounded').stdout)
        self.assertEqual(data['functions'][0]['name'], 'bounded')
        self.assertEqual(data['functions'][0]['instructions'], 2)
        self.command('--start', '0x42001008', '--stop', '0x42001004', expected=2)
        self.command('--start', '0x42001001', expected=2)

    def test_refuse_input_overwrite_and_existing_outputs(self):
        original = self.source.read_bytes()
        self.command('--json', self.source, '--force', expected=2)
        self.assertEqual(self.source.read_bytes(), original)
        target = self.folder / 'existing.json'
        target.write_text('keep')
        self.command('--json', target, expected=2)
        self.assertEqual(target.read_text(), 'keep')

    def test_empty_input_fails(self):
        self.source.write_text('not decoded instructions')
        self.command(expected=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--temp-root', type=Path)
    options, arguments = parser.parse_known_args()
    TEMP_ROOT = options.temp_root
    if TEMP_ROOT:
        TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    unittest.main(argv=[__file__, *arguments])
