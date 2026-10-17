"""Observe scalar weather outcomes only when the paused guest worker is idle."""
from runtime_memory import RAM


class WeatherSnapshot:
    """Bind numeric cache fields to the exact ELF and the producer's DWARF layout."""
    def __init__(self, memory, layout, objects, elf_sha256):
        self.memory, self.layout = memory, layout
        if layout['elf_sha256'] != elf_sha256:
            raise ValueError('Weather observation ELF differs')
        cache, worker = objects['cached_weather'], objects['request_state']
        if (cache != {'address': layout['address'], 'size': layout['size']} or
                worker != {'address': layout['request_state_address'], 'size': 4}):
            raise ValueError('Weather observation object ABI differs')
        for row in (cache, worker):
            if (type(row['address']) is not int or type(row['size']) is not int or
                    not 0 < row['size'] <= 1024 or
                    not any(lo <= row['address'] < row['address'] + row['size'] <= hi for lo, hi in RAM)):
                raise ValueError('Weather observation object outside bounded SRAM')
        if worker['address'] % 4 or not (worker['address'] + 4 <= cache['address'] or
                                        cache['address'] + cache['size'] <= worker['address']):
            raise ValueError('Overlapping or unaligned weather objects')
        spans = []
        for name, size in [('valid', 1), ('humidity', 4), ('generation', 4)]:
            offset = layout['fields'][name]
            if type(offset) is not int or offset < 0 or offset + size > cache['size']:
                raise ValueError('Weather observation field outside cache')
            if size == 4 and (cache['address'] + offset) % 4:
                raise ValueError('Unaligned weather scalar')
            if any(offset < end and start < offset + size for start, end in spans):
                raise ValueError('Overlapping weather fields')
            spans.append((offset, offset + size))
        self.snapshots = self.quiet = self.valid = 0
        self.generations = set()
        self.previous_generation = None
        self.first_fresh = self.last_fresh = None
        self.maximum_fresh_gap = 0

    def number(self, address, size, signed=False):
        """Read one scalar, never a city, description, URL, key or buffer payload."""
        data = self.memory(address, size)
        if len(data) != size:
            raise ValueError('Short weather scalar read')
        return int.from_bytes(data, 'little', signed=signed)

    def sample(self, when):
        """Skip cache reads while RUNNING/PENDING can cover a partial struct copy."""
        state = self.number(self.layout['request_state_address'], 4)
        if state not in (0, 1, 2, 3):
            raise ValueError('Invalid weather worker state')
        self.snapshots += 1
        result = {'worker_state': state}
        if state:
            return result
        self.quiet += 1
        fields, address = self.layout['fields'], self.layout['address']
        valid = self.number(address + fields['valid'], 1)
        generation = self.number(address + fields['generation'], 4)
        if valid not in (0, 1):
            raise ValueError('Invalid weather valid flag')
        if self.previous_generation is not None and generation < self.previous_generation:
            raise ValueError('Weather generation regressed')
        self.previous_generation = generation
        result.update(valid=bool(valid), generation=generation)
        if valid:
            humidity = self.number(address + fields['humidity'], 4, signed=True)
            if humidity != 67 or generation == 0:
                raise ValueError('Synthetic weather was not parsed correctly')
            result['humidity'] = humidity
            self.valid += 1
            if generation not in self.generations:
                self.generations.add(generation)
                if self.first_fresh is None:
                    self.first_fresh = when
                if self.last_fresh is not None:
                    self.maximum_fresh_gap = max(self.maximum_fresh_gap, when - self.last_fresh)
                self.last_fresh = when
        return result

    def summary(self):
        """Distinguish valid old cache samples from new successful publications."""
        return {'snapshots': self.snapshots, 'quiescent_samples': self.quiet, 'valid_samples': self.valid,
                'distinct_valid_generations': len(self.generations),
                'first_fresh_guest_seconds': self.first_fresh, 'last_fresh_guest_seconds': self.last_fresh,
                'maximum_fresh_gap_guest_seconds': self.maximum_fresh_gap}
