#!/usr/bin/env python3
"""Build a READ-ONLY, symbolized ELF64/AArch64 Ghidra import image from DCO boot.
Requires only Python 3 stdlib. This ELF is NOT FLASHABLE or executable as a phone app.
Usage: python3 mate50_make_sym_elf.py boot_42.img Mate50_symbols.elf
"""
import struct
import sys
from pathlib import Path
from mate50_kallsyms_extract import recover, IMAGE_OFFSET, IMAGE_LENGTH, BASE

def aligned(x, n):
    return ((x + n - 1) // n) * n

def pack_section(name_index, kind, flags, address, offset, size,
                 link=0, info=0, alignment=1, entry_size=0):
    return struct.pack("<IIQQQQIIQQ", name_index, kind, flags, address,
                       offset, size, link, info, alignment, entry_size)

def symbolize(boot, output):
    symbols = recover(boot)
    kernel = boot[IMAGE_OFFSET:IMAGE_OFFSET + IMAGE_LENGTH]
    names = bytearray(b"\0")
    entries = bytearray(bytes(24))
    for address, type_letter, symbol_name in symbols:
        string_index = len(names)
        names.extend(symbol_name.encode("ascii") + b"\0")
        kind = 2 if type_letter in ("T", "t", "W", "w") else 1
        entries.extend(struct.pack("<IBBHQQ", string_index, 0x10 | kind,
                                   0, 1, address, 0))
    shstr = b"\0.kernel\0.strtab\0.symtab\0.shstrtab\0"
    name_idx = lambda x: shstr.index(x.encode("ascii"))
    kernel_off = 4096
    strings_off = aligned(kernel_off + len(kernel), 8)
    symbols_off = aligned(strings_off + len(names), 8)
    shstr_off = aligned(symbols_off + len(entries), 8)
    table_off = aligned(shstr_off + len(shstr), 8)
    ident = b"\x7fELF" + bytes([2,1,1,0]) + bytes(8)
    ehdr = struct.pack("<16sHHIQQQIHHHHHH", ident, 2, 183, 1, BASE,
                       64, table_off, 0, 64, 56, 1, 64, 5, 4)
    phdr = struct.pack("<IIQQQQQQ", 1, 7, kernel_off, BASE, 0,
                       len(kernel), len(kernel), 4096)
    sections = [
        bytes(64),
        pack_section(name_idx(".kernel"),1,7,BASE,kernel_off,len(kernel),
                     alignment=4096),
        pack_section(name_idx(".strtab"),3,0,0,strings_off,len(names)),
        pack_section(name_idx(".symtab"),2,0,0,symbols_off,len(entries),
                     link=2,info=1,alignment=8,entry_size=24),
        pack_section(name_idx(".shstrtab"),3,0,0,shstr_off,len(shstr))
    ]
    with Path(output).open("wb") as f:
        f.write(ehdr + phdr)
        f.seek(kernel_off); f.write(kernel)
        f.seek(strings_off); f.write(names)
        f.seek(symbols_off); f.write(entries)
        f.seek(shstr_off); f.write(shstr)
        f.seek(table_off)
        for section in sections:
            f.write(section)
    return len(symbols)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: mate50_make_sym_elf.py boot_42.img out.elf")
    count = symbolize(Path(sys.argv[1]).read_bytes(),sys.argv[2])
    print(f"Symbolized ELF created: {sys.argv[2]}, {count} symbols")
