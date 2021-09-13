these are multiple versions differing only in the version of xfwm4 source code that they're applicable to. Both files contain two set of changes: 
* commenting out clientAdjustFullscreenLayer (three lines) causes reasonable behavior with fullscreen windows
* cursorInMonitor stuff causes the window switcher to only show windows that are on the screen that the cursor is on

