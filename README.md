# tools
Some little tools I make for my system

# Tools list
## DUG
Dug is a pseudographical du interface

## HEXD
It's another hex dumper (written in Python) with some features that I needed.
It can dump just hex digits (no ASCII translation), change line width (i.e. 93 bytes), suppress address and so on.
It is not supposed to be Ultimate Hex Dumper, but just an extensible hex dumper with the features I need time by time.

## KeybDiskLed
Short form: uses scroll lock led to indicate disk acrtivity

Long form: needed an off-screen indicator of disk activity for internal disks, and my notebooks lack of this led.

Hence I wrote a small (very small) program taylored on my disk configuration (sda and sdb) that watches about 10 times/sec the disk activity
and lights or shuts the scroll lock led by means of xset command.

Feel free to use/modify/whatever you want

## More to come
