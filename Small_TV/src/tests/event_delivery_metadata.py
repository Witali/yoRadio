"""Bounded numeric event-loop geometry, excluding queue storage and event payloads."""


def decode(read, layout):
    """Follow only aligned SRAM object prefixes whose field accesses were qualified."""
    requests = 0
    def pointer(value, size):
        """Reject overflow, aliases outside C2 SRAM and incomplete object prefixes."""
        if value & 3 or not 0x3fca0000 <= value < value+size <= 0x3fce0000:
            raise ValueError('Invalid event metadata pointer')
        return value
    def word(address):
        """Allow at most nine exact scalar reads, without a general RAM export."""
        nonlocal requests
        requests += 1
        if requests > 9: raise ValueError('Event metadata request budget exceeded')
        pointer(address, 4); raw = read(address, 4)
        if len(raw) != 4: raise ValueError('Short event metadata read')
        return int.from_bytes(raw, 'little')
    loop = pointer(word(layout['default_loop']), layout['loop_prefix'])
    current = word(layout['current_task'])
    queue = pointer(word(loop+layout['queue_offset']), layout['queue_prefix'])
    task = word(loop+layout['task_offset']); running = word(loop+layout['running_offset'])
    mutex = word(loop+layout['mutex_offset'])
    for value in (current, task, mutex): pointer(value, 4)
    if running: pointer(running, 4)
    count = word(queue+layout['count_offset']); length = word(queue+layout['length_offset'])
    item = word(queue+layout['item_offset'])
    if not 0 <= count <= length <= 256 or not length or item != layout['post_bytes']:
        raise ValueError('Invalid event queue dimensions')
    return dict(loop=loop, current=current, queue=queue, task=task, running=running,
                mutex=mutex, count=count, length=length, item=item)
