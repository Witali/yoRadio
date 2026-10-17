"""Encode the factory multipart upload format without changing JPEG bytes."""
import uuid


def multipart_chunk(slot, index, total, block, boundary=None):
    """Return one bounded binary chunk body and its Content-Type header."""
    if (type(slot) is not int or not 1 <= slot <= 5 or type(index) is not int or
            type(total) is not int or not 0 <= index < total <= 25 or
            not isinstance(block, bytes) or not 1 <= len(block) <= 4096):
        raise ValueError('Invalid factory photo chunk coordinates or payload')
    boundary = boundary or 'small-tv-' + uuid.uuid4().hex
    if (not 1 <= len(boundary) <= 70 or
            any(not (char.isascii() and (char.isalnum() or char in '-_.')) for char in boundary) or
            boundary.encode() in block):
        raise ValueError('Unsafe or colliding multipart boundary')
    fields = [('chunk', block), ('file_number', str(slot).encode()),
              ('chunk_index', str(index).encode()), ('total_chunks', str(total).encode())]
    body = b''.join(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
                    + value + b'\r\n' for name, value in fields)
    body += f'--{boundary}--\r\n'.encode()
    return body, 'multipart/form-data; boundary=' + boundary
