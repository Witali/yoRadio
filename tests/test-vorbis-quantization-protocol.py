"""Pure mixed VQ literal/event checks; execute no component, SDK, QEMU or oracle."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('quantization_capture', ROOT/'tests/run-vorbis-quantization-qemu.py')
subject = importlib.util.module_from_spec(spec); spec.loader.exec_module(subject)
DATA = 'a'*64
AFFINE = ('minimum_bits', 'delta_bits', 'minimum_multiplier', 'delta_multiplier')


def book_row(name, operation, lookup=2, dimensions=1, length=1, bridge=False):
    start, position, packed = 3, 3, 0
    for value, width in ((lookup,4),(0x60000000,32),(0x60100000,32),(15,4),(1,1),(65535,16)):
        packed |= value << position; position += width
    return dict(id=name, operation=operation, dimensions=dimensions, entries=1, start_bit=start,
        packet_bits=position, packet_hex=packed.to_bytes((position+7)//8,'little').hex(),
        entry_numbers=[0]*((length-1)//dimensions+1 if operation=='floor' else 1), length=length,
        component=65534 if operation=='scalar' else 0, affine=[], bridge=bridge, bin=1, map_size=3,
        raw_amplitude='9007199254740993', amplitude_bits=63, amplitude_offset=255)


ROWS = [book_row('vector','vector'),book_row('floor','floor',length=2,bridge=True),
        book_row('scalar','scalar',lookup=1,dimensions=65535),
        dict(id='direct',operation='affine',dimensions=0,entries=0,start_bit=0,packet_bits=0,packet_hex='',
             entry_numbers=[],length=1,component=0,affine=[dict(zip(AFFINE,(0xffffffff,0x60000001,65535,4294836225)))],
             bridge=True,bin=0,map_size=1,raw_amplitude='1',amplitude_bits=1,amplitude_offset=255)]
DOCUMENT = dict(schema='native-vorbis-quantization-cases-v1',cases=ROWS)


def header_for(rows):
    lines = ['#define QUANTIZATION_CASE_COUNT '+str(len(rows))]
    for i,row in enumerate(rows):
        if row['packet_hex']:
            lines.append('static const uint8_t quant_packet_%d[] = {%s};'%(i,','.join('UINT8_C(0x%02x)'%x for x in bytes.fromhex(row['packet_hex']))))
        if row['entry_numbers']:
            lines.append('static const uint32_t quant_entries_%d[] = {%s};'%(i,','.join('UINT32_C(%d)'%x for x in row['entry_numbers'])))
        if row['affine']:
            lines.append('static const native_vorbis_affine_t quant_affine_%d[] = {%s};'%(i,','.join('{'+','.join('UINT32_C(%d)'%x[k] for k in AFFINE)+'}' for x in row['affine'])))
    lines.append('static const quantization_case_t quantization_cases[QUANTIZATION_CASE_COUNT] = {')
    for i,row in enumerate(rows):
        pointer=lambda prefix,present: prefix+str(i) if present else 'NULL'
        fields=['"'+row['id']+'"',str({'vector':1,'floor':2,'affine':3,'scalar':4}[row['operation']]),str(row['dimensions']),str(row['entries']),
            'UINT64_C(%d)'%row['packet_bits'],'UINT64_C(%d)'%row['start_bit'],pointer('quant_packet_',row['packet_hex']),str(len(row['packet_hex'])//2),
            pointer('quant_entries_',row['entry_numbers']),str(len(row['entry_numbers'])),str(row['length']),str(row['component']),
            pointer('quant_affine_',row['affine']),str(len(row['affine'])),str(int(row['bridge'])),str(row['bin']),str(row['map_size']),
            'UINT64_C('+row['raw_amplitude']+')',str(row['amplitude_bits']),str(row['amplitude_offset'])]
        lines.append(' {'+','.join(fields)+'},')
    return '\n'.join(lines+['};'])+'\n'


HEADER=header_for(ROWS)


def log_for(target):
    core=1 if target=='esp32' else 0
    lines=[f'QUANTIZATION_BEGIN cases=4 coordinator=0 worker={core} data={DATA}',
           f'QUANTIZATION_WORKER core={core} priority=3 stack=16384',f'QUANTIZATION_CONTROLS checks=152 core={core}']
    for i,row in enumerate(ROWS):
        status=-99 if row['operation']=='affine' else 0
        lines.append(f'QUANTIZATION_CASE case={i} id={row["id"]} operation='+str({'vector':1,'floor':2,'affine':3,'scalar':4}[row['operation']])+f' length={row["length"]} bridge={int(row["bridge"])} measure_status={status} materialize_status={status} decode_status={status} core={core}')
        if row['operation']!='affine':
            lines += [f'QUANTIZATION_LAYOUT case={i} dimensions={row["dimensions"]} entries=1 lookup_type={1 if i==2 else 2} minimum_bits=60000000 delta_bits=60100000 value_bits=16 sequence_p=1 multiplicand_count=1 start_bit=3 multiplicand_bit=76 end_bit=92 core={core}',
                      f'QUANTIZATION_MULT case={i} count=1 hex=ffff core={core}']
        # Arbitrary well-formed values: only the separate independent checker qualifies them.
        values=''.join(''.join('%08x'%v[k] for k in AFFINE) for v in row['affine']) if i==3 else '6000000060100000000000010000ffff'*row['length']
        lines.append(f'QUANTIZATION_VALUES case={i} count={row["length"]} hex={values} core={core}')
        numbers='ds=0 denominator_bits=3fe0000000000000 denominator_exponent=123 gs=0 kind=0 log2_bits=bfe8000000000000 log2_exponent=1' if row['bridge'] else 'ds=-99 denominator_bits=0000000000000000 denominator_exponent=0 gs=-99 kind=-99 log2_bits=0000000000000000 log2_exponent=0'
        lines += [f'QUANTIZATION_MATH case={i} {numbers} core={core}',f'QUANTIZATION_END case={i} guards=1 unchanged=1 core={core}']
    return '\n'.join(lines+[f'QUANTIZATION_COMPLETE cases=4 controls=152 core={core}','QUANTIZATION_STOP status=CAPTURED'])+'\n'


class LiteralReadback(unittest.TestCase):
    def test_all_four_operations_and_exact_wide_fields(self):
        self.assertEqual(subject.validate_cases(copy.deepcopy(DOCUMENT),HEADER),ROWS)
        self.assertNotEqual(int(ROWS[0]['raw_amplitude']),int(float(ROWS[0]['raw_amplitude'])))
        self.assertEqual(ROWS[3]['affine'][0]['delta_multiplier'],4294836225)

    def test_missing_packet_entry_affine_and_descriptor_commas_fail(self):
        for before,after in (('),UINT8_C',')UINT8_C'),('UINT32_C(0),UINT32_C(0)','UINT32_C(0)UINT32_C(0)'),
                             ('4294836225)}','4294836225) UINT32_C(0)}'),('63,255},\n','63,255}\n')):
            changed=HEADER.replace(before,after,1);self.assertNotEqual(changed,HEADER)
            with self.subTest(before=before),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,changed)

    def test_changed_raw_pointer_scalar_component_and_affine_field_fail(self):
        for changed in (HEADER.replace('9007199254740993','9007199254740992'),HEADER.replace('quant_packet_0,12','quant_packet_1,12'),
                        HEADER.replace('1,1,65534,NULL','1,1,65533,NULL'),HEADER.replace('4294836225','4294836224')):
            self.assertNotEqual(changed,HEADER)
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,changed)

    def test_duplicate_inventory_and_nonliteral_expressions_fail(self):
        array=HEADER.splitlines()[1]+'\n'
        for changed in (array+HEADER,'#define QUANTIZATION_CASE_COUNT 4\n'+HEADER,
                        HEADER.replace('UINT64_C(9007199254740993)','UINT64_C(9007199254740992)+1'),HEADER.replace('63,255}','63,255+0}')):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,changed)

    def test_invalid_domains_extents_and_reserved_lookup_fail(self):
        for key,value in (('packet_bits',97),('start_bit',93),('dimensions',0),('dimensions',65536),('entries',0x1000000),
                          ('length',256),('amplitude_bits',True),('amplitude_bits',64),('raw_amplitude','9223372036854775808'),
                          ('packet_hex','zz'),('entry_numbers',[1]),('component',1),('bridge',1)):
            data=copy.deepcopy(DOCUMENT);data['cases'][0][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):subject.validate_cases(data,HEADER)
        data=copy.deepcopy(DOCUMENT);data['cases'][0]['packet_hex']='18'+data['cases'][0]['packet_hex'][2:]
        with self.assertRaises(ValueError):subject.validate_cases(data,header_for(data['cases']))

    def test_missing_reordered_extra_rows_schema_or_ids_fail(self):
        descriptors=[x for x in HEADER.splitlines() if x.startswith(' {')]
        for changed in (HEADER.replace(descriptors[0]+'\n',''),HEADER.replace(descriptors[0],descriptors[1]),HEADER.replace('CASE_COUNT 4','CASE_COUNT 5')):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_cases(DOCUMENT,changed)
        for change in ('schema','extra','id'):
            data=copy.deepcopy(DOCUMENT)
            if change=='schema':data['schema']='other'
            elif change=='extra':data['cases'][0]['unused']=0
            else:data['cases'][1]['id']='vector'
            with self.subTest(change=change),self.assertRaises(ValueError):subject.validate_cases(data,HEADER)


class EventCapture(unittest.TestCase):
    def test_both_native_core_profiles_and_all_mixed_shapes(self):
        for target in ('esp32','esp32c3'):
            parsed=subject.validate_log('I normal boot\n'+log_for(target),ROWS,target,DATA)
            self.assertEqual((parsed['cases'],parsed['protocol_lines'],parsed['metadata_controls']),(4,27,152))
            self.assertIsNone(parsed['rows'][3]['layout']);self.assertEqual(parsed['rows'][3]['measure_status'],-99)
            self.assertEqual(parsed['rows'][2]['multiplicands'],[65535])

    def test_well_formed_wrong_math_and_exact_values_are_retained_for_checker(self):
        changed=log_for('esp32').replace('denominator_exponent=123','denominator_exponent=124').replace('hex=ffff','hex=fffe')
        parsed=subject.validate_log(changed,ROWS,'esp32',DATA)
        self.assertEqual(parsed['rows'][0]['multiplicands'],[65534]);self.assertEqual(parsed['rows'][1]['denominator_exponent'],124)

    def test_missing_duplicate_reordered_foreign_or_torn_events_fail(self):
        lines=log_for('esp32').splitlines()
        for changed in (lines[:4]+lines[5:],lines[:4]+[lines[4]]+lines[4:],lines[:4]+[lines[5],lines[4]]+lines[6:],
                        lines+['QUANTIZATION_OTHER value=1'],['I noise: '+lines[0]]+lines[1:],lines[:-1]):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_log('\n'.join(changed),ROWS,'esp32',DATA)

    def test_core_controls_data_status_guard_and_duplicate_keys_fail(self):
        log=log_for('esp32')
        for changed in (log.replace('worker=1','worker=0'),log.replace('checks=152','checks=133'),log.replace(DATA,'b'*64),
                        log.replace('materialize_status=0','materialize_status=-4'),log.replace('guards=1','guards=0'),
                        log.replace('unchanged=1','unchanged=0'),log.replace('priority=3','priority=3 priority=3')):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_log(changed,ROWS,'esp32',DATA)

    def test_truncated_hex_counts_signed_fields_and_uncalled_math_fail(self):
        log=log_for('esp32')
        for changed in (log.replace('hex=ffff','hex=fff'),log.replace('count=1 hex=ffff','count=2 hex=ffff'),
                        log.replace('multiplicand_count=1','multiplicand_count=-1'),log.replace('minimum_bits=60000000','minimum_bits=6000000g'),
                        log.replace('ds=-99','ds=0'),log.replace('kind=-99','kind=0')):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_log(changed,ROWS,'esp32',DATA)

    def test_nonfinite_unnormalized_exponent_shape_and_panics_fail(self):
        log=log_for('esp32')
        for changed in (log.replace('3fe0000000000000','7ff0000000000000'),log.replace('3fe0000000000000','3ff0000000000000'),
                        log.replace('denominator_exponent=123','denominator_exponent=2147483648'),
                        log.replace('kind=0','kind=1'),log+'Guru Meditation\n'):
            with self.subTest(changed=changed),self.assertRaises(ValueError):subject.validate_log(changed,ROWS,'esp32',DATA)


if __name__=='__main__':unittest.main()
