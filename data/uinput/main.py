#!/usr/bin/env python3


import uinput

with uinput.Device([uinput.KEY_E, uinput.KEY_H,
                    uinput.KEY_L, uinput.KEY_O]) as device:
    device.emit_click(uinput.KEY_H)
    device.emit_click(uinput.KEY_E)
    device.emit_click(uinput.KEY_L)
    device.emit_click(uinput.KEY_L)
    device.emit_click(uinput.KEY_O)

with uinput.Device([uinput.REL_X, uinput.REL_Y,
                    uinput.BTN_LEFT, uinput.BTN_RIGHT]) as device:
    for i in range(20):
        device.emit(uinput.REL_X, 5)
        device.emit(uinput.REL_Y, 5)
