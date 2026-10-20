"""Source-span extraction only; no target ABI claims."""
import re

def function(source, anchor):
    start = source.index(anchor)
    opening = source.index(b'{', start)
    # Lexing preserves source positions while excluding braces in comments or
    # string literals. The returned span itself remains byte-for-byte source.
    lexical = re.sub(rb'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                     lambda match: b' ' * len(match[0]), source, flags=re.S)
    depth = 0
    for index in range(opening, len(source)):
        if lexical[index] == 123:
            depth += 1
        elif lexical[index] == 125:
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise ValueError('Unterminated SDK function')

def macro(source, name):
    lines = source.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if re.match(rb'#define\s+' + name.encode() + rb'(?:\s|$)', line):
            output = line
            while lines[index].rstrip().endswith(b'\\'):
                index += 1
                output += lines[index]
            return output
    raise ValueError('Missing SDK capacity macro: ' + name)
