
```
sudo apt install intltool libepoxy-dev libgtk-3-dev libstartup-notification0-dev libwnck-3-dev libxcomposite-dev libxdamage-dev libxfce4ui-2-dev libxfce4util-dev libxfconf-0-dev libxft-dev libxpresent-dev libxres-dev xfce4-dev-tools


apt source xfwm4

cd ..../src

git apply ~/hackery2/data/setup/data/xfwm4/0001-patch.patch

cd ..

dpkg-source --commit

dpkg-buildpackage -us -uc

cd ..

sudo dpkg -i xfwm4_4.18.0-1build3_amd64.deb



```






these are multiple versions differing only in the version of xfwm4 source code that they're applicable to. Both files contain two set of changes: 
* commenting out clientAdjustFullscreenLayer (three lines) causes reasonable behavior with fullscreen windows
* cursorInMonitor stuff causes the window switcher to only show windows that are on the screen that the cursor is on


crash fix:
```
@@ -400,37 +373,7 @@ clientPassFocus (ScreenInfo *screen_info, Client *c, GList *exclude_list)
     if (!(screen_info->params->click_to_focus) &&
         XQueryPointer (myScreenGetXDisplay (screen_info), screen_info->xroot, &dr, &window, &rx, &ry, &wx, &wy, &mask))
     {
-        /*
-commenting this out due to a crash that happens when closing windows and goes like this:
-
-#0  0x00007ffff7240647 in g_log_writer_default () at /lib/x86_64-linux-gnu/libglib-2.0.so.0                                    
-#1  0x00007ffff723c407 in g_log_structured_array () at /lib/x86_64-linux-gnu/libglib-2.0.so.0                                  
-#2  0x00007ffff723c603 in g_log_structured_standard () at /lib/x86_64-linux-gnu/libglib-2.0.so.0                               
-#3  0x00007ffff75d1e04 in  () at /lib/x86_64-linux-gnu/libgdk-3.so.0                                                           
-#4  0x00007ffff70c7a24 in _XError () at /lib/x86_64-linux-gnu/libX11.so.6                                                      
-#5  0x00007ffff70c7b27 in  () at /lib/x86_64-linux-gnu/libX11.so.6                                                             
-#6  0x00007ffff70c9657 in _XReply () at /lib/x86_64-linux-gnu/libX11.so.6                                                      
-#7  0x00007ffff71d61f9 in XRRGetMonitors () at /lib/x86_64-linux-gnu/libXrandr.so.2
-#8  0x00005555555827d9 in clientSelectMask (c=0x5555558f43c0, other=<optimized out>, mask=<optimized out>, type=153) at focus.c:296
-#9  0x000055555559f07f in clientAtPosition.isra.0 (x=2023, y=1017, exclude_list=exclude_list@entry=0x55555574fe40 = {...}, screen_info=<optimized out>, screen_info=<optimized out>) at stacking.c:272
-#10 0x00005555555871e4 in clientPassFocus (screen_info=0x555555892000, c=<optimized out>, exclude_list=0x55555574fe40 = {...}) at focus.c:403
-#11 0x000055555557edda in handleUnmapNotify (ev=<optimized out>, display_info=<optimized out>) at events.c:1265
-#12 handleEvent (event=<optimized out>, display_info=0x55555578f850) at events.c:2238
-#13 xfwm4_event_filter (event=0x5555559964f0, data=0x55555578f850) at events.c:2322
-#14 0x00005555555797e8 in eventXfwmFilter (gdk_xevent=<optimized out>, gevent=<optimized out>, data=<optimized out>) at event_filter.c:175
-#15 0x00007ffff75c2d2f in  () at /lib/x86_64-linux-gnu/libgdk-3.so.0                                                           
-#16 0x00007ffff75cbbbf in  () at /lib/x86_64-linux-gnu/libgdk-3.so.0                                                           
-#17 0x00007ffff7591a69 in gdk_display_get_event () at /lib/x86_64-linux-gnu/libgdk-3.so.0
-#18 0x00007ffff75cbe26 in  () at /lib/x86_64-linux-gnu/libgdk-3.so.0                                                           
-#19 0x00007ffff72358eb in g_main_context_dispatch () at /lib/x86_64-linux-gnu/libglib-2.0.so.0
-#20 0x00007ffff7288d28 in  () at /lib/x86_64-linux-gnu/libglib-2.0.so.0                                                        
-#21 0x00007ffff7234e53 in g_main_loop_run () at /lib/x86_64-linux-gnu/libglib-2.0.so.0
-#22 0x00007ffff78a97fd in gtk_main () at /lib/x86_64-linux-gnu/libgtk-3.so.0                                                   
-
-arguably, i may not even want to pass focus to next window *under cursor*, so...
-
-*/
-        //new_focus = clientAtPosition (screen_info, rx, ry, exclude_list);
+        new_focus = clientAtPosition (screen_info, rx, ry, exclude_list);
     }
     if (!new_focus)
     {
:

```
todo:
 use https://www.debian.org/doc/manuals/maint-guide/modify.en.html next time and generate a proper patch


latest version is 0001-patch.patch
