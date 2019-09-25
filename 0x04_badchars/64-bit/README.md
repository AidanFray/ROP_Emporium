# badchars - 64bit

The concept of exploitation is very similar to the [32-bit exploit](../32-bit/README.md) except the consideration of calling convention.

Gadgets for writing data:
```
mov qword ptr [r13], r12 ; ret
pop r12 ; pop r13 ; ret
```

XORing string back to normal
```
xor byte ptr [r15], r14b ; ret
pop r14 ; pop r15 ; ret
```

Calling system with the correct address:
```
pop rdi ; ret
```

The 64-bit architecture makes it easier to write the command string into memory as it can be done in one chain.

One aspect to note in 64-bit exploits the start of the `.data` section will normally be written to or altered. Therefore, using data a little further into the `.data` section is advised.

Putting these aspects together allows us to spawn a shell!