# fluff - 64bit

The exploit for the 64bit version is almost completely identical, where the only change is the 64bit registers that the binary uses.

The base gadget is displayed below:

```
mov qword ptr [r10], r11; pop r13; pop r12; xor byte ptr [r10], r12b; ret; 
```

The same process for the 32bit binary was used to construct the exploit.

One thing of note is that I could not find the gadget above using `ROPgadget` and could only see it when using `ropper`.