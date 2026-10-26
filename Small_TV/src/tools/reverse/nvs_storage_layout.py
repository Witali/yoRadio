"""Validate private Storage/Partition layouts from resolved DWARF in both SDK profiles."""
import io
from elftools.elf.elffile import ELFFile
from elftools.dwarf.dwarf_expr import DWARFExprParser

EXPECTED = {
 'Page': dict(size=84, fields=dict(mBaseAddress=8, mState=12, mSeqNumber=16, mVersion=20,
     mEntryTable=24, mNextFreeEntry=56, mFirstUsedEntry=60, mUsedEntryCount=64, mErasedEntryCount=66, mHashList=68, mPartition=80)),
 'PageManager': dict(size=40, fields=dict(mPageList=0, mFreePageList=12, mPages=24, mBaseSector=28, mPageCount=32, mSeqNumber=36)),
 'Storage': dict(size=104, fields=dict(mPartition=8, mPageCount=12, mPageManager=16, mNamespaces=56, mNamespaceUsage=68, mState=100)),
 'NamespaceEntry': dict(size=28, fields=dict(mName=8, mIndex=24)),
 'BlobIndexNode': dict(size=40, fields=dict(key=8, nsIndex=24, chunkCount=25, chunkStart=26, dataSize=28, observedDataSize=32, observedChunkCount=36)),
}
SLOTS = dict(read_raw=12, read=16, write_raw=20, write=24, erase_range=28, get_readonly=40)


def layout(raw):
    """Reject missing/inconsistent complete class DIEs instead of assuming vtable ordinals."""
    dwarf = ELFFile(io.BytesIO(raw)).get_dwarf_info(); result = {}; slots = {}
    parser = DWARFExprParser(dwarf.structs)
    for cu in dwarf.iter_CUs():
        for die in cu.iter_DIEs():
            attrs = die.attributes; name = attrs.get('DW_AT_name')
            if not name or 'DW_AT_byte_size' not in attrs: continue
            name = name.value.decode()
            if name in EXPECTED:
                fields = {}
                for child in die.iter_children():
                    a = child.attributes
                    if child.tag == 'DW_TAG_member' and 'DW_AT_data_member_location' in a:
                        fields[a['DW_AT_name'].value.decode()] = a['DW_AT_data_member_location'].value
                row = dict(size=attrs['DW_AT_byte_size'].value, fields=fields)
                if name in result and result[name] != row: raise ValueError('Conflicting Storage class DIEs')
                result[name] = row
            if name != 'Partition': continue
            for child in die.iter_children():
                a = child.attributes; method = a.get('DW_AT_name')
                if not method or method.value.decode() not in SLOTS: continue
                method = method.value.decode()
                expression = parser.parse_expr(a['DW_AT_vtable_elem_location'].value)
                if len(expression) != 1 or expression[0].op_name != 'DW_OP_constu':
                    raise ValueError('Requalify Storage virtual slot expression')
                slot = expression[0].args[0]*4
                if method in slots and slots[method] != slot: raise ValueError('Conflicting Storage virtual slot')
                slots[method] = slot
    if result != EXPECTED or slots != SLOTS: raise ValueError('Private NVS Storage ABI differs')
    return dict(passed=True, classes=result, virtual_slots=slots)
