libvte_increased_contrast.patch seems to apply to libvte9 now, that is, gtk 2.


for gtk 3, do something like
```
apt source vte2.91-0.62.3; cd vte2.91-0.62.3
```
edit src/drawing-cairo.cc :
add:
```
vte::color::rgb dark;
dark.red = 65535 - color->red * 0.1;
dark.green = 65535 - color->green * 0.3;
dark.blue = 65535 - color->blue * 0.1;

//it says "dark" but those "65535 - "'s actually shift everything towards white (and invert)
dark.red = 65535 - dark.red;
dark.green = 65535 - dark.green;
dark.blue = 65535 - dark.green;
```

sudo apt build-dep .
dpkg-buildpackage  -rfakeroot -b --jobs=1000
sudo dpkg -i ../libvte-2.91-0_0.62.3-1ubuntu1_amd64.deb
