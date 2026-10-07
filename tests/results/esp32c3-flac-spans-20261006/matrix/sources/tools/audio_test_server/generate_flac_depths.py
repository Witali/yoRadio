"""Deterministic FLAC depth/stereo/predictor fixtures, independently checked by FFmpeg.

Small RFC 9639 encoder for tests only. Produces STREAMINFO, frame CRCs and PCM
MD5; residuals use the legal Rice escape coding. No target-board assumptions.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import struct


class Bits:
    def __init__(self): self.bits = []
    def put(self, value, width):
        self.bits.extend((value >> bit) & 1 for bit in range(width-1, -1, -1))
    def bytes(self):
        self.bits.extend([0] * (-len(self.bits) % 8))
        return bytes(sum(self.bits[i+j] << (7-j) for j in range(8))
                     for i in range(0, len(self.bits), 8))


def crc(data, width, polynomial):
    value = 0
    for byte in data:
        value ^= byte << (width-8)
        for _ in range(8):
            value = ((value << 1) ^ (polynomial if value & (1 << (width-1)) else 0)) & ((1 << width)-1)
    return value


def subframe(writer, samples, depth, kind, wasted):
    samples = [v >> wasted for v in samples]
    depth -= wasted
    order = {'fixed4':4, 'lpc32':32, 'lpc32dense':32}.get(kind, 0)
    subtype = {'constant':0, 'verbatim':1, 'fixed4':12, 'lpc32':63, 'lpc32dense':63}[kind]
    writer.put(subtype << 1 | bool(wasted), 8)
    if wasted: writer.put(1, wasted)
    if kind == 'constant':
        assert len(set(samples)) == 1
        writer.put(samples[0], depth)
        return
    if kind == 'verbatim':
        for sample in samples: writer.put(sample, depth)
        return
    for sample in samples[:order]: writer.put(sample, depth)
    if kind == 'fixed4':
        coefficients, shift = [4, -6, 4, -1], 0
    else:
        # Large coefficients/shift exercise >32-bit LPC accumulation while
        # preserving a bounded residual for every 24-bit stereo side sample.
        coefficients, shift = [16383] + [0]*31, 14
        if kind == 'lpc32dense':
            coefficients = [16383 if j % 2 == 0 else -16383 for j in range(order)]
        writer.put(14, 4)  # coefficient precision minus one: 15 bits
        writer.put(shift, 5)
        for coefficient in coefficients: writer.put(coefficient, 15)
    residuals = [samples[i] - (sum(samples[i-1-j]*c for j,c in enumerate(coefficients)) >> shift)
                 for i in range(order, len(samples))]
    width = max((v if v >= 0 else ~v).bit_length()+1 for v in residuals)
    assert width <= 31
    writer.put(1, 2)   # Rice2, one partition, escaped signed residuals
    writer.put(0, 4)
    writer.put(31, 5)
    writer.put(width, 5)
    for value in residuals: writer.put(value, width)


def encode(left, right, depth, mode, kind, wasted=0, rate=48000, block=1024):
    channels = 1 if mode == 'mono' else 2
    assignment = {'mono':0, 'stereo':1, 'left':8, 'right':9, 'mid':10}[mode]
    frames = []
    for first in range(0, len(left), block):
        l, r = left[first:first+block], right[first:first+block]
        if mode == 'mono': data = [(l, depth)]
        elif mode == 'stereo': data = [(l, depth), (r, depth)]
        elif mode == 'left': data = [(l,depth), ([a-b for a,b in zip(l,r)],depth+1)]
        elif mode == 'right': data = [([a-b for a,b in zip(l,r)],depth+1), (r,depth)]
        else: data = [([(a+b)//2 for a,b in zip(l,r)],depth), ([a-b for a,b in zip(l,r)],depth+1)]
        frame_number = first // block
        number = chr(frame_number).encode('utf-8')
        # Block size follows number; sample rate and depth inherit STREAMINFO.
        header = b'\xff\xf8\x70' + bytes([assignment << 4]) + number + struct.pack('>H',len(l)-1)
        header += bytes([crc(header,8,0x07)])
        writer = Bits()
        for values, bits in data:
            # Mid/side may introduce a low bit even when L/R have wasted bits.
            actual_wasted = min(wasted, min((abs(v) & -abs(v)).bit_length()-1 for v in values if v)) if any(values) else wasted
            subframe(writer, values, bits, kind, actual_wasted)
        frame = header + writer.bytes()
        frames.append(frame + struct.pack('>H',crc(frame,16,0x8005)))
    width = (depth+7)//8
    raw = b''.join(v.to_bytes(width,'little',signed=True)
                   for pair in zip(left,right) for v in pair[:channels])
    packed = (rate << 44) | ((channels-1) << 41) | ((depth-1) << 36) | len(left)
    info = (struct.pack('>HH',block,block) + min(map(len,frames)).to_bytes(3,'big') +
            max(map(len,frames)).to_bytes(3,'big') + packed.to_bytes(8,'big') + hashlib.md5(raw).digest())
    return b'fLaC\x80\x00\x00\x22' + info + b''.join(frames)


def samples(depth, count, constant=False, wasted=0):
    rng = random.Random(9639 + depth)
    limit = 1 << (depth-1)
    if constant: return [-limit]*count, [limit-(1 << wasted)]*count
    boundaries = [-limit,limit-1,0,1,-1,limit//2,-limit//2]
    def channel():
        return [((boundaries[i] if i < len(boundaries) else rng.randrange(-limit,limit)) >> wasted) << wasted
                for i in range(count)]
    return channel(), channel()


def generate(output, *, physical=False, large_blocks=False, dense_lpc=False,
             seconds=12, selected_depths=None):
    if seconds < 1 or selected_depths and not set(selected_depths) <= {4,8,12,16,20,24}:
        raise ValueError('Invalid fixture duration/depth')
    output.mkdir(parents=True,exist_ok=False)
    manifest = dict(generator='RFC 9639 deterministic test encoder v1', fixtures=[])
    depths = (8,12,20,24) if physical else (4,8,12,16,20,24)
    if selected_depths: depths = tuple(selected_depths)
    modes = ('stereo',) if physical else ('mono','stereo','left','right','mid')
    kinds = ('lpc32',) if physical else ('constant','verbatim','fixed4','lpc32')
    if large_blocks: depths,kinds=(24,),('verbatim','lpc32')
    if dense_lpc: kinds = ('lpc32dense',)
    for depth in depths:
        for mode in modes:
            for kind in kinds:
                wasted = 1 if kind == 'verbatim' else 0
                count = 48000*seconds if physical else (8192+137 if large_blocks else 1024)
                left,right = samples(depth,count,kind=='constant',wasted)
                if physical:
                    # Listen-safe, independent tones; host matrix retains full
                    # scale random/boundary values for arithmetic stress.
                    left = [int(((1<<(depth-1))-1)*.18*math.sin(2*math.pi*997*i/48000)) for i in range(count)]
                    right = [int(((1<<(depth-1))-1)*.18*math.sin(2*math.pi*1601*i/48000)) for i in range(count)]
                data = encode(left,right,depth,mode,kind,wasted,block=8192 if large_blocks else 1024)
                name = f'flac-{depth}bit-{mode}-{kind}'+('-block8192' if large_blocks else '')
                path = output/(name+'.flac');path.write_bytes(data)
                channels = 1 if mode=='mono' else 2
                expected = b''.join(struct.pack('<h',v >> (depth-16) if depth > 16 else v * (1 << (16-depth)))
                                    for pair in zip(left,right) for v in pair[:channels])
                manifest['fixtures'].append(dict(name=name,file=path.name,codec='flac',mime='audio/flac',
                    rate=48000,channels=channels,bits=depth,seconds=count/48000,profile='flac',
                    sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),mode=mode,subframe=kind,
                    wasted_bits=wasted,pcm_bytes=len(expected),pcm_sha256=hashlib.sha256(expected).hexdigest()))
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--physical',action='store_true',help='Low-level tones, 8/12/20/24 bits, default twelve seconds')
    parser.add_argument('--large-blocks',action='store_true',help='8192-frame blocks and a short tail at 24 bits')
    parser.add_argument('--dense-lpc',action='store_true',help='Use 32 nonzero LPC coefficients instead of sparse LPC')
    parser.add_argument('--seconds',type=int,default=12,help='Duration of physical tone fixtures')
    parser.add_argument('--depth',type=int,action='append',choices=(4,8,12,16,20,24),help='Restrict source depths')
    args=parser.parse_args();generate(args.output,physical=args.physical,large_blocks=args.large_blocks,
        dense_lpc=args.dense_lpc,seconds=args.seconds,selected_depths=args.depth)
