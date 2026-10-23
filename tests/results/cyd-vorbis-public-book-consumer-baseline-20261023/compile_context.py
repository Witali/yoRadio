"""Exact extracted pure archived compile/dependency metadata readers."""
from pathlib import PureWindowsPath

def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def windows_args(command):
    """Pure Windows quoting parser, adapted from the reviewed rate verifier."""
    out, i = [], 0
    while i < len(command):
        while i < len(command) and command[i] in ' \t':
            i += 1
        if i == len(command):
            break
        word, quoted = '', False
        while i < len(command) and (quoted or command[i] not in ' \t'):
            count = 0
            while i < len(command) and command[i] == '\\':
                count += 1; i += 1
            if i < len(command) and command[i] == '"':
                word += '\\' * (count // 2)
                if count % 2:
                    word += '"'
                elif quoted and i + 1 < len(command) and command[i + 1] == '"':
                    word += '"'; i += 1
                else:
                    quoted = not quoted
                i += 1
            else:
                word += '\\' * count
                if i < len(command) and (quoted or command[i] not in ' \t'):
                    word += command[i]; i += 1
        need(not quoted, 'Unclosed actual compilation quote')
        out.append(word)
    return out


def dependency_rows(raw, cwd):
    raw = raw.replace('\\\r\n', '').replace('\\\n', '')
    need(': ' in raw and '$' not in raw and '\x00' not in raw, 'Unsupported actual GCC dependency spelling')
    body, parts, word, i = raw.split(': ', 1)[1], [], [], 0
    while i < len(body):
        char = body[i]
        if char == '\\' and i + 1 < len(body) and body[i + 1] in ' \t\\#:':
            word.append(body[i + 1]); i += 2
        elif char.isspace():
            if word:
                parts.append(''.join(word)); word = []
            i += 1
        else:
            word.append(char); i += 1
    if word:
        parts.append(''.join(word))
    need(parts, 'Empty dependency evidence')
    return [PureWindowsPath(cwd) / path for path in parts]


