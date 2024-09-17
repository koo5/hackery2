#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/input.h>
#include <libevdev.h>
#include <X11/Xlib.h>
#include <X11/keysym.h>
#include <X11/extensions/XTest.h>

// xinput list
#define TOUCHPAD_DEVICE "/dev/input/eventX"

void send_key(Display *display, int keycode) {
    XTestFakeKeyEvent(display, keycode, True, CurrentTime);
    XTestFakeKeyEvent(display, keycode, False, CurrentTime);
    XFlush(display);
}

int main() {
    struct libevdev *dev = NULL;
    int fd = open(TOUCHPAD_DEVICE, O_RDONLY);
    if (fd < 0) {
        perror("Failed to open device");
        return 1;
    }

    int rc = libevdev_new_from_fd(fd, &dev);
    if (rc < 0) {
        fprintf(stderr, "Failed to create evdev device: %s\n", strerror(-rc));
        return 1;
    }

    Display *display = XOpenDisplay(NULL);
    if (display == NULL) {
        fprintf(stderr, "Failed to open X display\n");
        return 1;
    }

    printf("Touchpad to Numpad program started. Press Ctrl+C to exit.\n");

    struct input_event ev;
    while (1) {
        rc = libevdev_next_event(dev, LIBEVDEV_READ_FLAG_NORMAL, &ev);
        if (rc == 0) {
            if (ev.type == EV_ABS && ev.code == ABS_X) {
                int x = ev.value;
                int y = libevdev_get_event_value(dev, EV_ABS, ABS_Y);

                int keycode = 0;
                if (x < 1000 && y < 1000) keycode = XKeysymToKeycode(display, XK_KP_7);
                else if (x < 1000 && y < 2000) keycode = XKeysymToKeycode(display, XK_KP_4);
                else if (x < 1000 && y < 3000) keycode = XKeysymToKeycode(display, XK_KP_1);
                else if (x < 2000 && y < 1000) keycode = XKeysymToKeycode(display, XK_KP_8);
                else if (x < 2000 && y < 2000) keycode = XKeysymToKeycode(display, XK_KP_5);
                else if (x < 2000 && y < 3000) keycode = XKeysymToKeycode(display, XK_KP_2);
                else if (x < 3000 && y < 1000) keycode = XKeysymToKeycode(display, XK_KP_9);
                else if (x < 3000 && y < 2000) keycode = XKeysymToKeycode(display, XK_KP_6);
                else if (x < 3000 && y < 3000) keycode = XKeysymToKeycode(display, XK_KP_3);

                if (keycode != 0) {
                    send_key(display, keycode);
                }
            }
        }
    }

    libevdev_free(dev);
    close(fd);
    XCloseDisplay(display);
    return 0;
}
