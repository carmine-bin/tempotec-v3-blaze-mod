#!/usr/bin/env python3
"""Summarize an A2DP LDAC reception capture made with measure.sh.

Usage: python3 analyze.py captures/<name>

Per 10-second window: received payload rate, dropped audio, number of
discontinuities, missing RTP sequence numbers and minimum HCI link quality.

Dropped audio is the RTP timestamp advance beyond the previous packet's own
duration (LDAC frames x 256 samples at a 96 kHz clock): audio the source
discarded before numbering packets. Missing sequence numbers are packets that
were numbered by the source but never reached the Blaze's HCI.
"""
import collections
import glob
import os
import struct
import sys

EPOCH = 0x00dcddb30f2f8000  # btsnoop timestamps: microseconds since year 0
CLOCK = 96000
SAMPLES_PER_FRAME = 256


def rtp_packets(path):
    """Return (time, seq, rtp_ts, payload_bytes, ldac_frames) for media packets."""
    d = open(path, 'rb').read()
    if len(d) < 16 or d[:8] != b'btsnoop\0':
        return []
    pos, buf, start, out = 16, None, 0.0, []
    while pos + 24 <= len(d):
        _, length, flags, _, ts = struct.unpack('>IIIIq', d[pos:pos + 24])
        acl = d[pos + 24:pos + 24 + length]
        pos += 24 + length
        if flags & 0xffff != 5 or len(acl) < 4:  # monitor opcode 5: ACL RX
            continue
        boundary = (struct.unpack('<H', acl[:2])[0] >> 12) & 3
        if boundary in (0, 2):
            buf, start = bytearray(acl[4:]), (ts - EPOCH) / 1e6
        elif buf is not None:
            buf += acl[4:]
        if buf is not None and len(buf) >= 4:
            size, cid = struct.unpack('<HH', buf[:4])
            if len(buf) >= 4 + size:
                pay = bytes(buf[4:4 + size])
                buf = None
                if cid >= 0x40 and size > 100 and pay[0] & 0xc0 == 0x80:
                    seq, rts = struct.unpack('>HI', pay[2:8])
                    out.append((start, seq, rts, size - 13, pay[12] & 0x0f))
    return out


def summarize(folder):
    quality, roles = {}, collections.Counter()
    log = os.path.join(folder, 'lq.log')
    if os.path.exists(log):
        for line in open(log):
            f = line.split()
            if len(f) >= 2 and f[1].isdigit():
                quality[int(f[0])] = int(f[1])
            if 'lm' in f:
                roles[f[-1]] += 1
    packets = []
    for capture in sorted(glob.glob(os.path.join(folder, 'seg*.btsnoop'))):
        packets += rtp_packets(capture)
    if not packets:
        return None
    t0 = packets[0][0]
    rows = collections.defaultdict(lambda: [0, 0.0, 0, 0])
    for a, b in zip(packets, packets[1:]):
        row = rows[int((b[0] - t0) // 10)]
        row[0] += b[3]
        advance = (b[2] - a[2]) & 0xffffffff
        duration = a[4] * SAMPLES_PER_FRAME
        if duration < advance < CLOCK * 10:
            row[1] += (advance - duration) / CLOCK
            row[2] += 1
        row[3] += ((b[1] - a[1]) & 0xffff) - 1
    windows = []
    for k in sorted(rows):
        q = [quality[t] for t in range(int(t0) + k * 10, int(t0) + k * 10 + 10)
             if t in quality]
        kbps, dropped, gaps, missing = rows[k]
        windows.append({'t': k * 10, 'kbps': round(kbps * 8 / 10000),
                        'dropped_s': round(dropped, 1), 'discontinuities': gaps,
                        'missing_seq': missing, 'link_quality_min': min(q) if q else None})
    seconds = packets[-1][0] - t0
    return {'seconds': round(seconds), 'packets': len(packets),
            'dropped_s': round(sum(w['dropped_s'] for w in windows), 1),
            'missing_seq': sum(w['missing_seq'] for w in windows),
            'role': sorted(roles), 'windows': windows}


def main(folder):
    s = summarize(folder)
    if not s:
        print('no A2DP media packets')
        return
    print(f'{"t":>4} {"kb/s":>5} {"dropped":>8} {"gaps":>5} {"lost":>5} {"LQmin":>5}')
    for w in s['windows']:
        lq = w['link_quality_min'] if w['link_quality_min'] is not None else '-'
        print(f'{w["t"]:>4} {w["kbps"]:>5} {w["dropped_s"]:>7.1f}s '
              f'{w["discontinuities"]:>5} {w["missing_seq"]:>5} {lq:>5}')
    pct = 100 * s['dropped_s'] / max(s['seconds'], 1)
    print(f'dropped audio {s["dropped_s"]} s of {s["seconds"]} s ({pct:.1f} %), '
          f'missing RTP packets {s["missing_seq"]}, Blaze role: {", ".join(s["role"]) or "?"}')


if __name__ == '__main__':
    main(sys.argv[1])
