"""Exact reviewed bounded Reader/prefix extraction; no generator or parser import."""
def need(condition, message):
    if not condition:
        raise ValueError(message)


class Reader:
    def __init__(self, data):
        self.data, self.position, self.fields = data, 0, {}

    def take(self, name, width):
        need(name not in self.fields and 0 <= width <= 64 and
             self.position + width <= len(self.data) * 8, "bit_read_bounds_or_name")
        start, result = self.position, 0
        for index in range(width):
            position = self.position + index
            result |= ((self.data[position // 8] >> (position % 8)) & 1) << index
        self.position += width
        self.fields[name] = dict(offset=start, width=width, value=result)
        return result

    def expected(self, name, width, value):
        result = self.take(name, width)
        need(result == value, "field_expectation:" + name)
        return result

    def finish(self):
        need(0 <= len(self.data) * 8 - self.position < 8, "unexpected_trailing_fields")
        need(all(((self.data[p // 8] >> (p % 8)) & 1) == 0
             for p in range(self.position, len(self.data) * 8)), "nonzero_padding")


def prefix(reader, packet_type):
    reader.expected("packet_type", 8, packet_type)
    for index, value in enumerate(b"vorbis"):
        reader.expected(f"signature[{index}]", 8, value)


