# fluff - 32bit

This challenge is very similar to that of `write4`, but we have some restrictions in terms of the gadgets we can use.

This exploit was very satisfying and was great fun to construct.

The websites prompt suggests:

```
A solid approach is to work backwards; we'll need a mov [reg], reg or something equivalent to make the actual write so we can start there.
```

We'll follow the advice and take a look for a gadget we want.

The only suitable chain is the one below:

```
0x08048693 : mov dword ptr [ecx], edx ; pop ebp ; pop ebx ; xor byte ptr [ecx], bl ; ret
```

It's messy as it includes commands we do not need, but we can work around by providing padding in our payload.

This gadgets means we need to put data in `ecx` and `edx`. As you may have predicted, there're not `pop` commands available so we need to get a little creative.

This is where some clever XORing comes in handy, we have available two `xor` gadgets that allows us to simulate a pop command:


The gadget below allows us to clear the `edx` pointer.
```
xor edx, edx ; pop esi ; mov ebp, 0xcafebabe ; ret
```

This means as `edx` will be zero an XOR will place the contents on `ebx` in `edx`.
```
xor edx, ebx ; pop ebp ; mov edi, 0xdeadbabe ; ret
```

This is useful as there is a `pop ebx` gadget available!

This is our core `get-data-into-edx` rop chain sorted. 

We can then get it into `ecx` via an `xchg` call with the gadget below:

```
xchg edx, ecx ; pop ebp ; mov edx, 0xdefaced0 ; ret
```

Stringing two of the `get-data-into-edx` chains with the first followed by an exchange allows us to place 4 bytes of data into memory! We have created our write primitive.

This then can be used to write our full `/bin/sh\0` payload into memory.

This is followed by a call to `system` to spawn a shell!
