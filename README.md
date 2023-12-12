# Introduction

CHIRP driver for UV-K5/K6/5R radios running [Egzumer firmware](https://github.com/egzumer/uv-k5-firmware-custom)

This is a modification of a driver created by:<br>
(c) 2023 Jacek Lipkowski <sq5bpf@lipkowski.org>

Licensed cc-by-sa-4.0

# How to use

At some point the driver will hopefully be added to official release of CHIRP.

Right now you have to:
1. Download [uvk5_EGZUMER.py](uvk5_EGZUMER.py?raw=1)
1. go to menu `Help` and turn on `Developer mode`
1. Restart CHIRP
1. Go to menu `File`, `Load module...`
1. Choose downloaded `uvk5_EGZUMER.py`, new radio will appear in Quansheng section in download/upload function.

# Current status

***This driver is work in progress... not finished yet...***

know isue : RXMODE that modify dualwatch and cross band not working

some menu not uses has been remove

some menu has been add in for chirp:
in basic setting : s-meter s0 and s9, 
                   backligkt min, 
                   backlight max,
                   backlight tx rx,
                   battery texte,
                   rxmode,
                   
in driver information :  all the option of the firmware are display their status.
in unlock : the battery type 1600/2200mah
in programable key : the M key has been add

struct put bitfield in reverse bit 0 to 7  as bit0 is on the left... 
normaly it bit0 on the right, so inverse struct bitfield,
stay to test the compiler version bitfield ... not yet implement in my firmware version in radio... 
