# Introduction

CHIRP driver for UV-K5/K6/5R radios running [Egzumer firmware](https://github.com/egzumer/uv-k5-firmware-custom)

This is a modification of a driver created by:<br>
(c) 2023 Jacek Lipkowski <sq5bpf@lipkowski.org>

Licensed cc-by-sa-4.0

# How to use

At some point the driver will hopefully be added to official release of CHIRP.

Currently you can use modified version of CHIRP from [releases](https://github.com/egzumer/uvk5-chirp-driver/releases). You can also use development version of driver [uvk5_EGZUMER.py](uvk5_EGZUMER.py?raw=1) and load it to CHIRP manually.

## Loading with menu
1. go to menu `Help` and turn on `Developer mode`
1. Restart CHIRP
1. Go to menu `File`, `Load module...`
1. Choose downloaded `uvk5_EGZUMER.py`, new radio will appear in Quansheng section in download/upload function.
1. Important, go to menu `View` and turn ON `Show extra fields`, this will show more options in `Memories` tab

## Loading with CHIRP input argument
1. Create a shortcut to CHIRP program
1. Edit shortcut settings, in target field add at the end `--module PATH_TO_DRIVER` (replace `PATH_TO_DRIVER` with a real path) example : "C:\Program Files (x86)\CHIRP\chirpwx.exe" --module C:\chirp_egzumer\uvk5_EGZUMER.py![add to start shorcut](https://github.com/egzumer/uvk5-chirp-driver/assets/56229329/219043eb-631c-4d1d-905d-9e99953de7f5)

1. Run CHIRP with the shortcut, it will automatically load the driver.
2. ![when chirp start](https://github.com/egzumer/uvk5-chirp-driver/assets/56229329/5fa94f0f-a540-4bc0-bd27-633a04e67b41)
