#!/usr/bin/env python3
"""Make a Ghidra-friendly ARM64 ELF from the exact DCO-AL00 boot image.
All output is offline research data, NOT a flashable image or executable exploit.
Usage: python3 mate50_make_sym_elf.py boot_42.img kernel-symbolized.elf
"""
import struct
import sys
from pathlib import Path
from mate50_kallsyms_extract import recover, IMAGE_OFFSET, IMAGE_LENGTH, BASE

def aligned(x, n):
    return (x + n - 1) // n * n

def section(name_off, kind, flags, address, offset, size,
            link=0, info=0, alignment=1, entsize=0):
    return struct.pack("<IIQQQQIIQQ", name_off, kind, flags, address, offset,
                       size, link, info, alignment, entsize)

def symbolize(boot, output):
    symbols = recover(boot)
    kernel = boot[IMAGE_OFFSET:IMAGE_OFFSET + IMAGE_LENGTH]
    names_by_symbol = {name: address for address, kind, name in symbols}
    stops = [names_by_symbol[n] - BASE for n in (
        "_etext", "__end_rodata", "__bss_start", "_end")]
    text_end, rodata_end, bss_start, bss_end = stops
    if not (0 < text_end < rodata_end < bss_start < bss_end < len(kernel)):
        raise ValueError("Invalid kernel ELF section boundaries")
    if any(kernel[bss_start:bss_end]):
        raise ValueError("Expected zero-filled raw image .bss")

    names = [".text",".rodata",".data",".bss",".tail",".strtab",".symtab",".shstrtab"]
    shstr = b"\0" + b"\0".join(n.encode() for n in names) + b"\0"
    idx = {n: shstr.index(n.encode()) for n in names}
    strings = bytearray(b"\0")
    symtab = bytearray(bytes(24))
    for address, letter, name in symbols:
        string_index = len(strings)
        strings.extend(name.encode("ascii") + b"\0")
        delta = address - BASE
        if delta < text_end: shndx=1
        elif delta < rodata_end: shndx=2
        elif delta < bss_start: shndx=3
        elif delta <= bss_end: shndx=4
        else: shndx=5
        elf_type = 2 if letter in ("T","t","W","w") else 1
        symtab.extend(struct.pack("<IBBHQQ",string_index,0x10|elf_type,
                                  0,shndx,address,0))

    image_offset=4096
    str_offset=aligned(image_offset+len(kernel),8)
    sym_offset=aligned(str_offset+len(strings),8)
    shstr_offset=aligned(sym_offset+len(symtab),8)
    sections_offset=aligned(shstr_offset+len(shstr),8)
    secs=[
        bytes(64),
        section(idx[".text"],1,6,BASE,image_offset,text_end,alignment=4096),
        section(idx[".rodata"],1,2,BASE+text_end,image_offset+text_end,
                rodata_end-text_end,alignment=4096),
        section(idx[".data"],1,3,BASE+rodata_end,image_offset+rodata_end,
                bss_start-rodata_end,alignment=4096),
        section(idx[".bss"],8,3,BASE+bss_start,image_offset+bss_start,
                bss_end-bss_start,alignment=4096),
        section(idx[".tail"],1,0,0,image_offset+bss_end,len(kernel)-bss_end),
        section(idx[".strtab"],3,0,0,str_offset,len(strings)),
        section(idx[".symtab"],2,0,0,sym_offset,len(symtab),
                link=6,info=1,alignment=8,entsize=24),
        section(idx[".shstrtab"],3,0,0,shstr_offset,len(shstr)),
    ]
    ident=b"\x7fELF"+bytes([2,1,1,0])+bytes(8)
    ehdr=struct.pack("<16sHHIQQQIHHHHHH",ident,2,183,1,BASE,
                     64,sections_offset,0,64,56,3,64,len(secs),8)
    phfmt="<IIQQQQQQ"
    pheaders=[
        struct.pack(phfmt,1,5,image_offset,BASE,0,text_end,text_end,4096),
        struct.pack(phfmt,1,4,image_offset+text_end,BASE+text_end,0,
                    rodata_end-text_end,rodata_end-text_end,4096),
        struct.pack(phfmt,1,6,image_offset+rodata_end,BASE+rodata_end,0,
                    bss_start-rodata_end,bss_end-rodata_end,4096),
    ]
    with Path(output).open("wb") as f:
        f.write(ehdr+b"".join(pheaders))
        f.seek(image_offset);f.write(kernel)
        f.seek(str_offset);f.write(strings)
        f.seek(sym_offset);f.write(symtab)
        f.seek(shstr_offset);f.write(shstr)
        f.seek(sections_offset)
        for record in secs:f.write(record)
    return len(symbols)

if __name__ == "__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: mate50_make_sym_elf.py boot_42.img output.elf")
    count=symbolize(Path(sys.argv[1]).read_bytes(),sys.argv[2])
    print(f"Created ELF64/AArch64 with {count} symbols: {sys.argv[2]}")
