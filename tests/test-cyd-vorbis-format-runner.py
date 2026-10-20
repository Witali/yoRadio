"""Host-only runner checks; no SDK, compiler, reference codec or emulator launch."""
import importlib.util
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from windows_compile_command import macro_command, windows_argv, check_macro_inputs

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('format_runner', HERE/'run-cyd-vorbis-format-qemu.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
HEADER = (HERE/'target/cyd_vorbis_format_qemu/main/fixture.h').read_text()


def protocol(scope='acceptance', control=False):
    sizes, pcm = runner.fixture_accounting(HEADER)
    rows = [f'BEGIN expected_rejection={int(scope == "baseline")} coordinator=0',
            'VENDOR_OPEN rate=192000 long=8192 result=0 handle=1']
    rows += [f'VENDOR_PACKET packet={i} consumed={n} pcm={pcm(8192)[i]} sample_rate=192000 channel=2 bits=16 canaries=1 core=1' for i,n in enumerate(sizes)]
    rows += ['VENDOR_COMPLETE packets=68 pcm=1089792 nonzero=1000000 full8192=66']
    pairs = [(48000,2048),(192000,8192),(64000,8192)]
    if scope == 'acceptance' and not control: pairs += [(63999,8192),(48000,8192)]
    for rate,long in pairs:
        reference_rate = 192000 if long == 8192 else rate
        rows += [f'PAIR_PACKET rate={rate} long={long} packet={i} consumed={n} pcm={pcm(long)[i]} '
                 f'vendor_expected_rate={reference_rate} vendor_rate={reference_rate} checked_expected_rate={rate} checked_rate={rate} '
                 f'expected_channel=2 vendor_channel=2 checked_channel=2 expected_bits=16 vendor_bits=16 checked_bits=16 exact=1 canaries=1 core=1'
                 for i,n in enumerate(sizes)]
        rows += [f'EXACT rate={rate} long={long} packets=68 pcm={sum(pcm(long))} full8192={pcm(long).count(16384)}']
    if control: rows += ['FAILURE legal_candidate_open_required']
    else:
        if scope == 'baseline': rows += [f'LEGAL_REJECT rate={rate} long=8192 result=-1 header_error=1' for rate in (63999,48000)]
        rows += [f'INVALID_REJECT case={case} result=-1 header_error=1' for case in ('zero_rate','short32','long16384','short_exceeds_long')]
        rows += [('BASELINE low_rejected=2' if scope == 'baseline' else 'COMPLETE low_exact=2')+
                 ' high_exact=2 normal_exact=1 invalid_rejected=4 core=1']
    return '\n'.join('CYD_VORBIS_FORMAT_'+row for row in rows)


class WindowsCompileContext(unittest.TestCase):
    def test_joined_include_and_escaped_define(self):
        self.assertEqual(windows_argv(r'"C:\Tool Dir\gcc.exe" -I"C:\Source Dir\include"'),
                         [r'C:\Tool Dir\gcc.exe',r'-IC:\Source Dir\include'])
        args = [r'C:\Tool Dir\gcc.exe',r'-DNAME="two words"',r'-IC:\Source Dir\include',r'C:\Source Dir\setup.c']
        self.assertEqual(windows_argv(subprocess.list2cmdline(args)),args)

    def test_only_compile_and_output_are_removed(self):
        # Paths need not exist; preparing argv performs no writes or compilation.
        cwd = (HERE/'synthetic compile dir').resolve()
        cc, source = cwd/'Tool Dir/gcc.exe',cwd/'source dir/setup.c'
        argv = [str(cc),'-DTEST="two words"','-Iinclude dir','-mtext-section-literals','-o','obj dir/setup.obj','-c',str(source)]
        row = dict(directory=str(cwd),file=str(source),command=subprocess.list2cmdline(argv))
        result, actual_cwd, original, generated = macro_command(row,cc,source)
        self.assertEqual(original,argv)
        self.assertEqual(actual_cwd,cwd)
        self.assertEqual(result,[*argv[:4],str(source),'-E','-dM'])
        self.assertEqual(generated,{})
        row['arguments'] = argv
        row['command'] = 'deliberately not used'
        self.assertEqual(macro_command(row,cc,source)[0],result)
        for extra in ('@missing.rsp','-MFdep.d','-MD'):
            row['arguments'] = [*argv,extra]
            with self.subTest(extra=extra),self.assertRaises(ValueError): macro_command(row,cc,source)
        row['arguments'] = [str(cwd/'other-gcc.exe'),'-c',str(source)]
        with self.assertRaises(ValueError): macro_command(row,cc,source)
        for argv_bad in ([str(cc),str(source)], [*argv,'-c'], [*argv,'-o','other.obj']):
            row['arguments'] = argv_bad
            with self.subTest(argv=argv_bad),self.assertRaises(ValueError): macro_command(row,cc,source)

    def test_reviewed_cflags_remains_an_unchanged_argument_and_is_bound(self):
        temporary = tempfile.TemporaryDirectory(prefix='rsp-host-',dir=HERE.parent)
        try:
            build = Path(temporary.name).resolve()/'build with spaces'
            cflags, specs = build/'toolchain/cflags',build/'specs/picolibc.specs'
            cflags.parent.mkdir(parents=True); specs.parent.mkdir(parents=True)
            lines = ['-Wno-frame-address','-mlongcalls','-fno-builtin-memcpy',
                     '-fno-builtin-memset','-fno-builtin-bzero','"-specs='+specs.as_posix()+'"']
            content = ('\n'.join(lines)+'\n').encode()
            cflags.write_bytes(content); specs.write_bytes(b'*cpp:\n-DTEST=1\n')
            cc, source = build/'tools/gcc.exe',build/'source/setup.c'
            argv = [str(cc),'@'+str(cflags),'-DKEEP="two words"','-o','obj/setup.obj','-c',str(source)]
            row = dict(directory=str(build),file=str(source),command=subprocess.list2cmdline(argv))
            result,cwd,original,bound = macro_command(row,cc,source)
            self.assertEqual(original,argv)
            self.assertEqual(result,[*argv[:3],str(source),'-E','-dM'])
            self.assertEqual(result[1],argv[1])
            self.assertEqual(set(bound),{cflags,specs})
            check_macro_inputs(bound)
            for path in (cflags,specs):
                original_bytes = path.read_bytes()
                path.write_bytes(original_bytes+b'changed')
                with self.subTest(changed=path),self.assertRaises(ValueError): check_macro_inputs(bound)
                path.write_bytes(original_bytes)
            bad_contents = [content+b'@nested\n',content+b'-DLIMIT_TO_64kHz=1\n',
                            content.replace(b'-mlongcalls',b'-mwrongflag'),
                            content.replace(lines[-1].encode(),('-specs='+specs.as_posix()).encode()),
                            content.replace(lines[-1].encode(),('"-specs='+str(build.parent/'other.specs')+'"').encode())]
            for wrong in bad_contents:
                cflags.write_bytes(wrong)
                with self.subTest(content=wrong),self.assertRaises(ValueError): macro_command(row,cc,source)
            cflags.write_bytes(content)
            row['arguments'] = [*argv,'@'+str(cflags)]
            with self.assertRaises(ValueError): macro_command(row,cc,source)
            row['arguments'] = [argv[0],'@'+str(build/'other.rsp'),*argv[2:]]
            with self.assertRaises(ValueError): macro_command(row,cc,source)
            row['arguments'] = argv
            specs.unlink()
            with self.assertRaises(FileNotFoundError): macro_command(row,cc,source)
        finally:
            if not Path(temporary.name).resolve().is_relative_to(HERE.parent.resolve()):
                raise RuntimeError('Refusing temporary cleanup outside this prep')
            temporary.cleanup()


class CountedProtocol(unittest.TestCase):
    def test_complete_modes(self):
        for scope,control,pairs in (('baseline',False,3),('acceptance',False,5),('acceptance',True,3)):
            with self.subTest(scope=scope,control=control):
                result = runner.validate_log(protocol(scope,control),scope,control,HEADER)
                self.assertEqual(result['exact_pair_packets'],pairs*68)
                self.assertEqual(result['vendor_packets'],68)

    def test_missing_duplicate_reordered_or_unwritten_packet_rejected(self):
        log = protocol()
        rows = log.splitlines()
        changed = rows[:]
        changed[3],changed[4] = changed[4],changed[3]
        cases = ['\n'.join(rows[:3]+rows[4:]),log+'\n'+rows[0],'\n'.join(changed),
                 log.replace('packet=10 consumed=','packet=10 consumed=99',1),
                 log.replace('canaries=1','canaries=0',1),log.replace('exact=1','exact=0',1),
                 log+'\nGuru Meditation Error',log.replace('pcm=1089792','pcm=1089791',1)]
        for i,case in enumerate(cases):
            with self.subTest(case=i),self.assertRaises(RuntimeError): runner.validate_log(case,'acceptance',False,HEADER)

    def test_control_requires_exact_failure_after_full_prerequisites(self):
        log = protocol('acceptance',True)
        for altered in (log.replace('legal_candidate_open_required','vendor_high8192_open_required'),
                        log.replace('VENDOR_COMPLETE','VENDOR_INCOMPLETE'),
                        log+'\nassert failed',protocol('baseline')):
            with self.assertRaises(RuntimeError): runner.validate_log(altered,'acceptance',True,HEADER)

    def test_baseline_cannot_be_acceptance(self):
        with self.assertRaises(RuntimeError): runner.validate_log(protocol('baseline'),'acceptance',False,HEADER)

    def test_vendor_metadata_failure_is_not_baseline_reproduction(self):
        log = ('CYD_VORBIS_FORMAT_BEGIN expected_rejection=1 coordinator=0\n'
               'CYD_VORBIS_FORMAT_VENDOR_OPEN rate=192000 long=8192 result=0 handle=1\n'
               'CYD_VORBIS_FORMAT_VENDOR_METADATA packet=1 result=0 consumed=15 decoded=8448 sample_rate=0 channel=2 bits=16\n'
               'CYD_VORBIS_FORMAT_FAILURE vendor_high8192_metadata\n')
        with self.assertRaises(RuntimeError): runner.validate_log(log,'baseline',False,HEADER)

    def test_zero_or_mismatched_metadata_rejected_including_priming(self):
        for scope in ('baseline','acceptance'):
            source = protocol(scope).splitlines()
            for index,line in enumerate(source):
                if 'PACKET ' in line and (' packet=0 ' in line or ' packet=1 ' in line):
                    fields = (('sample_rate',0),('channel',0),('bits',0)) if 'VENDOR_PACKET' in line else (
                        ('vendor_expected_rate',64000),('vendor_rate',0),('checked_expected_rate',1),('checked_rate',0),
                        ('vendor_channel',0),('checked_channel',1),('vendor_bits',0),('checked_bits',24))
                    for field,value in fields:
                        altered = source[:]
                        altered[index] = re.sub(r'\b'+field+r'=\d+',field+'='+str(value),line,count=1)
                        self.assertNotEqual(altered[index],line)
                        with self.subTest(scope=scope,line=index,field=field),self.assertRaises(RuntimeError):
                            runner.validate_log('\n'.join(altered),scope,False,HEADER)

    def test_header_rejections_require_specific_error_attestation(self):
        for scope in ('baseline','acceptance'):
            log = protocol(scope)
            for altered in (log.replace('header_error=1','header_error=0',1),
                            log.replace(' header_error=1','',1),
                            log.replace('result=-1 header_error=1','result=0 header_error=1',1)):
                with self.subTest(scope=scope),self.assertRaises(RuntimeError):
                    runner.validate_log(altered,scope,False,HEADER)


if __name__ == '__main__': unittest.main()
