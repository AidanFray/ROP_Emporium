# ret2win

Locate a method within the binary that you want to call and do so by overwriting a saved return address on the stack.

## No spoilers here

Take the time to read these challenge pages, there aren't any spoilers and they contain important information that could save you some frustration. If you're unfamiliar with ROP tools of the trade then check out the beginner's guide. As it states; you'll feed each binary with a quantity of garbage followed by your ROP chain. In this case there is a magic method we want to call and we'll do so by overwriting a saved return address on the stack. Certainly nothing that could be called a 'chain' by any stretch of the imagination but we've got to start somewhere. We'll do a little RE to confirm some information but nothing serious.

## What am I doing

These challenges use the usual CTF objective of retrieving the contents of a file named "flag.txt" from a remote machine by exploiting a given binary. The two most common courses of action are to somehow read flag.txt back to us directly or drop a shell and read it yourself. Let's see if ret2win has an easy way to do either of these. We'll use the following nm one-liner to check method names. 

`nm ret2win | grep t` will tell us that the suspiciously named function `ret2win` is present and r2 confirms that it will cat the flag back to us: 

![](_images/r2.png)

## Double check

For a quick and dirty confirmation of how many bytes are needed to cause an overflow in the 64bit binary you can use `sudo dmesg -C` to clear the kernel ring buffer, run the program and type 40 characters followed by 5 capital Xs (why let the As have all the fun) then type `dmesg -t` to see output that hopefully looks similar to the sample below: 


```
ret2win[14987]: segfault at a5858585858 ip 00000a5858585858 sp 00007ffe8c93d4e0 error 14 in libc-2.24.so[7fef0e075000+195000]
```

## Let's do this

You can solve this challenge with a variety of tools, even the echo command will work, although pwntools is suggested. If you decided to go for a more complex exploit than a ret2win then be aware that input is truncated for these simpler challenges. Find out how many bytes you have to construct your chain in each challenge using `ltrace <binary>` and looking at the call to fgets(). If your ROP chain seems perfect but the binary is crashing before printing the flag see the [common pitfalls](https://ropemporium.com/guide.html#Common%20pitfalls) section of the beginner's guide, especially if you're using Ubuntu 18.04.