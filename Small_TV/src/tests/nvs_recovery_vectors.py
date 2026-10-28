"""Exercise exact identity past colliding candidates and type replacement in corrected recovery."""
from nvs_record_vectors import item, vectors, COLLISION_KEYS, WRITTEN, EMPTY, crc


def vectors_extra():
    """Keep all earlier failing-before vectors unchanged and add adversarial key ordering."""
    rows = list(vectors()); left, right = COLLISION_KEYS
    for updated, other in ((left, right), (right, left)):
        records = {0: item(left), 1: item(right, value=9), 2: item(updated, value=11)}
        remaining = [(1, updated, 255, 11), (1, other, 255, 9 if other == right else 7)]
        rows.append(dict(name='colliding-'+('left' if updated == left else 'right')+'-replacement',
                         states=[WRITTEN]*3+[EMPTY]*123, payloads=records, data_payloads={}, wanted=remaining))
    index_data = 1 | 1 << 32 | 0xffff << 48
    rows.append(dict(name='legacy-blob-to-index-replacement', states=[WRITTEN]*3+[EMPTY]*123,
                     payloads={0: item(b'blob', datatype=0x41, span=2, size=1, data_crc=crc(b'A')),
                               2: item(b'blob', datatype=0x48, value=index_data)},
                     data_payloads={1: b'A'+b'\xff'*31}, wanted=[(1, b'blob', 255, index_data, 0x48)]))
    # A damaged tail can cross a slot already counted as erased by the scan.
    rows.append(dict(name='partial-tail-before-erased-slot', states=[EMPTY, 0]+[EMPTY]*124,
                     payloads={}, data_payloads={0: b'A'+b'\xff'*31, 1: b'B'+b'\xff'*31}, wanted=[]))
    return rows
