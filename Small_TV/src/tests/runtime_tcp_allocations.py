"""Attribute typed network ranges to exact live ROM/TLSF allocations once."""
from bisect import bisect_right
from collections import Counter


class AllocationIndex:
    """Use callbacks of the actual walker, never reinterpret its header bits here."""
    def __init__(self, topology, snapshot):
        """Verify the same-stop heap transcript and index all actual live capacities."""
        topology.validate(snapshot)
        self.blocks, self.extents, self.claims = [], [], {}
        for part in snapshot['heap_topology']['heaps']:
            inventory = part['inventory']
            if topology.walker.replay(inventory['record']) != inventory:
                raise ValueError('Allocation source differs from exact instruction replay')
            overhead = inventory['allocation_header_bytes']
            self.extents.append(inventory['record']['extent'])
            for pointer, capacity, used in topology.walker.blocks:
                if used:
                    self.blocks.append({'pointer': pointer, 'capacity': capacity, 'header_bytes': overhead})
        self.blocks.sort(key=lambda row: row['pointer'])
        self.starts = [row['pointer'] for row in self.blocks]
        if any(a['pointer'] + a['capacity'] > b['pointer'] for a, b in zip(self.blocks, self.blocks[1:])):
            raise ValueError('Overlapping live allocation extents')

    def containing(self, address, size, optional=False):
        """Reject dangling/cross-boundary ranges; allow external payloads without reads."""
        if (type(address) is not int or type(size) is not int or not 0 < size <= 65535 or
                not 0 < address < address + size <= 2**32):
            raise ValueError('Invalid network object extent')
        index = bisect_right(self.starts, address) - 1
        if index >= 0:
            block = self.blocks[index]
            if block['pointer'] <= address < block['pointer'] + block['capacity']:
                if address + size > block['pointer'] + block['capacity']:
                    raise ValueError('Network object crosses its allocation')
                return block
        if optional and not any(address < hi and lo < address + size for lo, hi in self.extents):
            return None
        raise ValueError('Network object is not in a live observed allocation')

    def claim(self, kind, address, size, owner=None, metadata=True, optional=False):
        """Deduplicate shared allocations while rejecting metadata/payload aliasing."""
        block = self.containing(address, size, optional)
        if block is None:
            return None
        if metadata and address != block['pointer']:
            raise ValueError('TCP metadata is not at its qualified allocation start')
        key = (kind, address if owner is None else owner, address, size)
        for other_key, other in self.claims.get(block['pointer'], {}).items():
            overlap = address < other['address'] + other['size'] and other['address'] < address + size
            if overlap and key != other_key and (metadata or other['metadata']):
                raise ValueError('Network metadata aliases another object or packet payload')
        claims = self.claims.setdefault(block['pointer'], {})
        claims[key] = {'kind': kind, 'owner': key[1], 'address': address, 'size': size, 'metadata': metadata}
        return block['pointer']

    def summary(self):
        """Keep attributed and unclassified capacities additive without shared double counts."""
        attributed = [dict(block, claims=[claims[key] for key in sorted(claims)])
                      for block in self.blocks if (claims := self.claims.get(block['pointer']))]
        allocated_capacity = sum(row['capacity'] for row in self.blocks)
        capacity = sum(row['capacity'] for row in attributed)
        headers = sum(row['header_bytes'] for row in attributed)
        total_headers = sum(row['header_bytes'] for row in self.blocks)
        kinds = Counter(claim['kind'] for row in attributed for claim in row['claims'] if claim['metadata'])
        return {'allocated_blocks': len(self.blocks), 'allocated_capacity_bytes': allocated_capacity,
                'allocated_header_bytes': total_headers,
                'attributed_blocks': len(attributed), 'attributed_capacity_bytes': capacity,
                'attributed_header_bytes': headers,
                'unclassified_blocks': len(self.blocks) - len(attributed),
                'unclassified_capacity_bytes': allocated_capacity - capacity,
                'unclassified_header_bytes': total_headers - headers,
                'metadata_objects_by_kind': dict(sorted(kinds.items())), 'allocations': attributed}
