"""Compile unsafe journal variants and require real runtime assertion failures."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

PROJECT=Path(__file__).resolve().parents[2]


def sha(path):
    """Pin actual bytes used to build/run each independent negative control."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Quick mode keeps all state/corruption/identity tests; full fault gate is separate."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--vs-dev-cmd',type=Path,default=Path('C:/Program Files/Microsoft Visual Studio/18/Community/Common7/Tools/VsDevCmd.bat'))
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    source=PROJECT/'storage/jpeg_journal.c';test=Path(__file__).with_name('native_test.c')
    original=source.read_text()
    mutants={
        'erase_current_head':('journal->have_head ? journal->bank^1u : 0','journal->have_head ? journal->bank : 0',1),
        'skip_invalidation':('if (!journal->have_head || !journal->matching || journal->entries[slot].ready)','if (false)',1),
        'publish_unverified_frame':('verifier->verify(verifier->context,journal->pending_slot,journal->config.frame_bytes,entry.frame_sha256)',
                                   'false',1),
        'trust_unverified_hit':('verifier->verify(verifier->context,slot,journal->config.frame_bytes,entry->frame_sha256)',
                               '(verifier->verify(verifier->context,slot,journal->config.frame_bytes,entry->frame_sha256),false)',1),
        'skip_body_crc':('body_crc(body) != get32(body+CRC_OFFSET)','false',1),
        'skip_commit_footer':('*valid = valid_footer(journal,footer);','*valid = true;',1),
        'select_oldest':('generation > journal->generation','generation < journal->generation',1),
        'ignore_layout':('!memcmp(journal->body+24,journal->config.layout_id,32)','true',1),
        'ignore_codec':('!memcmp(journal->body+56,journal->config.codec_id,32)','true',1),
        'wrap_generation':('if (journal->generation == UINT64_MAX) return JPEG_JOURNAL_LIMIT;',
                           'if (false) return JPEG_JOURNAL_LIMIT;',2),
        'ignore_read_error':('journal->last_io_error = journal->device.read(journal->device.context,address,data,bytes);',
                            '(void)journal->device.read(journal->device.context,address,data,bytes); journal->last_io_error = 0;',1),
        'skip_erase_verification':('verify_bytes(journal,address,NULL,JPEG_NOR_SECTOR_BYTES,true)','JPEG_JOURNAL_OK',1),
    }
    inputs=[source,PROJECT/'storage/jpeg_journal.h',PROJECT/'storage/jpeg_nor.c',PROJECT/'storage/jpeg_nor.h',
            test,Path(__file__),args.fixtures/'journal_fixture.h',args.vs_dev_cmd]
    report=dict(passed=False,full_power_cut_matrix_run=False,cases=[],inputs_sha256={str(p.resolve()):sha(p) for p in inputs})
    try:
        for name,(before,after,count) in mutants.items():
            if original.count(before)!=count:raise ValueError('Mutation anchor changed: '+name)
            folder=(args.output/name).resolve();folder.mkdir()
            changed,executable=folder/'mutant.c',folder/'mutant.exe'
            changed.write_text(original.replace(before,after),encoding='utf-8',newline='\n')
            batch=folder/'compile.cmd'
            batch.write_text('@echo off\ncall "'+str(args.vs_dev_cmd.resolve())+'" -arch=x64 -host_arch=x64 >nul\n'
                'if errorlevel 1 exit /b 1\ncd /d "'+str(folder)+'"\nwhere cl > compiler-path.txt\n'
                'cl /nologo /std:c11 /O2 /W3 /D_CRT_SECURE_NO_WARNINGS /I"'+str(args.fixtures.resolve())+'" '
                '/I"'+str(PROJECT/'storage')+'" "'+str(test)+'" "'+str(changed)+'" "'+str(PROJECT/'storage/jpeg_nor.c')+'" '
                '/Fe"'+str(executable)+'" /link bcrypt.lib\nexit /b %errorlevel%\n',encoding='utf-8',newline='\r\n')
            compiled=subprocess.run(['cmd.exe','/d','/c',str(batch)],capture_output=True,timeout=60)
            (folder/'compile.log').write_bytes(compiled.stdout+compiled.stderr)
            if compiled.returncode:raise RuntimeError('Mutant must compile first: '+name)
            compiler=Path((folder/'compiler-path.txt').read_text().splitlines()[0])
            result=subprocess.run([str(executable),str(folder),'--quick'],capture_output=True,timeout=60)
            (folder/'run.log').write_bytes(result.stdout+result.stderr)
            if result.returncode!=1 or b'FAIL ' not in result.stderr:
                raise AssertionError('Mutant escaped runtime assertions: '+name)
            report['cases'].append(dict(name=name,rejected=True,exit_code=result.returncode,source_sha256=sha(changed),
                executable_sha256=sha(executable),compiler_sha256=sha(compiler),
                assertion=result.stderr.decode('utf-8',errors='replace').strip()))
            print('REJECTED journal mutant:',name,flush=True)
        report['passed']=len(report['cases'])==len(mutants)
    finally:
        report['inputs_unchanged']=all(sha(Path(p))==h for p,h in report['inputs_sha256'].items())
        report['passed'] &= report['inputs_unchanged']
        (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':
    main()
