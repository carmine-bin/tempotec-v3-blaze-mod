#!/usr/bin/env python3
"""Audita un rango de .text: cada llamada a un lookup de elemento por nombre
(0x46d340 find_element, 0x49c3a0 / 0x49b900 lookup global) e informa

  - el nombre buscado (resuelto del puntero a string en a1/a2)
  - si el resultado se guardea (beq/bne v0,zero) ANTES del primer deref de v0

Un deref sin guard = SIGSEGV si el .view no trae el elemento (el crash del PEQ
en device 2026-08-08 fue exactamente eso, escondido en un delay slot).

Uso: lookup-audit.py <elf> <start_hex> <end_hex>
"""
import struct, sys, subprocess, re

LOOKUPS = {0x46d340: "find_element(padre,nombre)",
           0x49c3a0: "lookup_global(nombre,tipo)",
           0x49b900: "lookup_global2(nombre,tipo)"}
WINDOW = 16  # instrucciones a mirar tras el jal


def sections(p):
    out = subprocess.run(["readelf", "-S", "-W", p], capture_output=True, text=True).stdout
    S = {}
    for m in re.finditer(r"\[\s*\d+\]\s+(\S+)\s+\S+\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)", out):
        S[m.group(1)] = (int(m.group(2), 16), int(m.group(3), 16), int(m.group(4), 16))
    return S


def cstr(data, S, va):
    for name, (addr, off, size) in S.items():
        if addr and addr <= va < addr + size and name != ".bss":
            i = off + (va - addr)
            end = data.find(b"\0", i, i + 128)
            if end < 0:
                return None
            s = data[i:end]
            return s.decode() if s and all(32 <= c < 127 for c in s) else None
    return None


def main(p, start, end):
    S = sections(p); data = open(p, 'rb').read()
    a, o, sz = S['.text']

    def word(pc):
        return struct.unpack_from("<I", data, o + (pc - a))[0]

    bad = 0
    for pc in range(start, end, 4):
        w = word(pc)
        if w >> 26 != 3:  # jal
            continue
        tgt = ((pc + 4) & 0xf0000000) | ((w & 0x3ffffff) << 2)
        if tgt not in LOOKUPS:
            continue
        # nombre: reconstruir lui+addiu/ori de los ~10 anteriores y del delay slot
        names, hi = [], {}
        for q in range(pc - 40, pc + 8, 4):
            v = word(q); op = v >> 26; rs = (v >> 21) & 31; rt = (v >> 16) & 31
            imm = struct.unpack("<h", struct.pack("<H", v & 0xffff))[0]
            if op == 0x0f:
                hi[rt] = v & 0xffff
            elif op in (0x09, 0x0d) and rs in hi:
                va = ((hi[rs] << 16) | (v & 0xffff)) if op == 0x0d else ((hi[rs] << 16) + imm) & 0xffffffff
                t = cstr(data, S, va)
                if t:
                    names.append(t)
        # guard vs deref: recorrer hasta encontrar branch sobre v0(=2) o lw off v0
        verdict = "SIN-GUARD-NI-DEREF"
        q = pc + 8
        stop = pc + 8 + WINDOW * 4
        while q < stop:
            v = word(q); op = v >> 26; rs = (v >> 21) & 31; rt = (v >> 16) & 31
            is_call = op == 3 or (op == 0 and (v & 63) == 9)
            if is_call:  # el delay slot del jal siguiente cuenta (ahí se escondía el crash)
                d = word(q + 4)
                if (d >> 26) in (0x20, 0x21, 0x23, 0x24, 0x25) and ((d >> 21) & 31) == 2:
                    verdict = f"*** DEREF SIN GUARD @0x{q+4:08x} (delay slot) ***"
                    bad += 1
                break
            if op in (4, 5) and (rs == 2 or rt == 2) and (rs == 0 or rt == 0):
                verdict = f"guard @0x{q:08x}"
                break
            if op in (0x20, 0x21, 0x23, 0x24, 0x25) and rs == 2:
                verdict = f"*** DEREF SIN GUARD @0x{q:08x} ***"
                bad += 1
                break
            q += 4
        print(f"0x{pc:08x}  {LOOKUPS[tgt]:28s} {str(names[-2:]):46s} {verdict}")
    print(f"\n{bad} deref(s) sin guard")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)) else 0)
