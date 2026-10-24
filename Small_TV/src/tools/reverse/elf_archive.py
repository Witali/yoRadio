"""Read bounded GNU ar members without extracting archive-controlled paths."""


def members(data):
    """Yield member names and bytes; reject truncated headers, payloads and name offsets."""
    if data[:8]!=b'!<arch>\n':raise ValueError('Expected a regular ar archive')
    at=8;names=b''
    while at<len(data):
        header=data[at:at+60]
        if len(header)!=60 or header[58:60]!=b'`\n':raise ValueError('Invalid ar header')
        size=int(header[48:58]);start=at+60;stop=start+size
        if size<0 or stop>len(data):raise ValueError('Truncated ar member')
        payload=data[start:stop];name=header[:16].decode('ascii').strip();at=stop+(size&1)
        if at>len(data):raise ValueError('Missing ar padding')
        if name=='//':names=payload;continue
        if name in ('/','/SYM64/'):continue
        if name.startswith('/') and name[1:].isdigit():
            offset=int(name[1:])
            if not 0<=offset<len(names):raise ValueError('Invalid ar long name')
            end=names.find(b'/\n',offset)
            if end<0:raise ValueError('Unterminated ar long name')
            name=names[offset:end].decode('utf-8')
        elif name.startswith('#1/'):
            length=int(name[3:])
            if not 0<length<=len(payload):raise ValueError('Invalid BSD ar name')
            name=payload[:length].rstrip(b'\0').decode('utf-8');payload=payload[length:]
        else:name=name.rstrip('/')
        yield name,payload
