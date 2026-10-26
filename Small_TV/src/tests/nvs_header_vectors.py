"""Exercise real Item header validation at format, span, version and CRC boundaries."""
from audit_factory_xrefs import Image
from reverse.nothrow_linkage import LinkedRuntime
from reverse.runtime_metadata import instructions
from runtime_call_instructions import HEAP
from nvs_record_vectors import item
from nvs_records_cpu import RecordCpu, HEADER_CHECK


def run(factory, native, app, linkage, crc):
    """Use independent wire vectors rather than replacing any header-validation branch."""
    cases = []
    for datatype in (1, 0x11, 2, 0x12, 4, 0x14, 8, 0x18):
        for span in (0, 1, 2, 255): cases.append((datatype, span, 0, 255, 0, 0, False, span == 1))
    for datatype in (0x21, 0x41, 0x42):
        for index in (0, 124, 125):
            for size in (0, 1, 32, 33, 4000, 4001, 65535):
                span = (size+31)//32+1
                if span > 255: span = 255
                for chunk in (0, 128, 255):
                    wanted = size <= (125-index)*32 and span <= 126-index and (datatype != 0x42 or chunk != 255)
                    cases.append((datatype, span, size, chunk, index, 0, False, wanted))
    for size in (0, 508000, 508001, 0xffffffff):
        for span in (0, 1, 2):
            for chunk in (0, 255): cases.append((0x48, span, 0, chunk, 0, size, False, span == 1 and chunk == 255 and size <= 508000))
    for datatype in (0, 3, 0x22, 0x99, 0xff): cases.append((datatype, 1, 0, 255, 0, 7, False, False))
    for datatype in (0x21, 0x41, 0x42):
        for span in (0, 1, 3, 127): cases.append((datatype, span, 1, 0, 0, 0, False, False))
    cases += [(1, 1, 0, 255, 0, 7, True, False), (0x21, 2, 1, 255, 0, 0, True, False)]
    readers = {'factory': Image(factory).read, 'native': LinkedRuntime(native, app).read}; result = {}; coverage = {}
    for variant, definition in linkage['variants'].items():
        rows = []; f = RecordCpu(variant+'-headers', definition, readers[variant], crc)
        for datatype, span, size, chunk, index, value, bad_crc, wanted in cases:
            raw = item(datatype=datatype, span=span, size=size, chunk=chunk, value=value, bad_crc=bad_crc)
            f.cpu.mem_write(HEAP+1280, raw); f.reg(10, HEAP+1280); f.reg(11, index)
            observed = f.invoke(HEADER_CHECK); assert bool(observed) == wanted, (variant, datatype, span, size, chunk, index, observed)
            rows.append(dict(datatype=datatype, span=span, size=size, chunk=chunk, index=index,
                             value=value, bad_crc=bad_crc, valid=bool(observed)))
        result[variant] = rows
        body = next(row for row in definition['functions'] if row['name'] == HEADER_CHECK); start = int(body['start'], 0)
        starts = {int(row['pc'], 0) for row in instructions(readers[variant](start, body['linked_bytes'], True), start)}
        assert starts <= f.visited, (variant, [hex(pc) for pc in sorted(starts-f.visited)])
        coverage[variant] = dict(instruction_starts=len(starts), visited=sorted(starts))
    assert result['factory'] == result['native']
    return dict(passed=True, cases_per_variant=len(cases), total_cases=len(cases)*2, results=result, coverage=coverage,
                header_algorithm_executed=True, crc_rom_executed=True, physical_hardware_tested=False)
