these are multiple versions differing only in the version of xfwm4 source code that they're applicable to. Both files contain two set of changes: 
* commenting out clientAdjustFullscreenLayer (three lines) causes reasonable behavior with fullscreen windows
* cursorInMonitor stuff causes the window switcher to only show windows that are on the screen that the cursor is on

the more recent version - fullscreenfix+patch2-xfwm4.16.1 - crashes on every closing of probably any window, and it's necessary to keep spawning xfwm4 in an endless loop. I don't know if this is an instability just brought out by the patchset, or something wrong about it. I'd pay $30 for a fix.
