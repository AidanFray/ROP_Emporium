# pivot - 32bit

http://www.radiofreerobotron.net/blog/2017/11/23/ropemporium-pivot-ctf-walkthrough/

Attack strategy

1st stage
- Stack smash
- Stack pivot (Overwrite ESP?)
- libpivot32 address leak

2nd stage
- Stack smash to call ret2win()