# jj: spectacle (and other KDE/Qt apps) take ~25s+ to start

**Investigated:** 2026-06-27 · **Status:** root cause found, fix NOT yet applied (deferred to avoid session restart)

## TL;DR

`spectacle` taking "minutes to start" is **not** a spectacle/X11/GPU/screenshot problem.
**`org.kde.plasmashell` is wedged** — alive on the bus but its main thread doesn't service
D-Bus calls. Spectacle makes a *blocking* D-Bus call into plasmashell during startup and eats
the full **25-second D-Bus default timeout**, then proceeds. Any Qt/KDE app that makes a
blocking call into plasmashell at launch is affected.

**Fix (when ready to accept a Plasma restart):**
```fish
systemctl --user restart plasma-plasmashell.service
# or, if not systemd-managed:
# kquitapp5 plasmashell; and kstart5 plasmashell
```
Restarting plasmashell clears the wedge; spectacle should then start in ~2–3 s.
Plasma had **5+ days uptime** when it wedged — likely a stuck plasmoid / nested blocking call
on plasmashell's main thread. If it recurs, suspect a specific widget.

## Decisive evidence

Direct `org.freedesktop.DBus.Peer Ping` to each service spectacle hits at startup:

| Service | Ping response |
|---|---|
| org.kde.kglobalaccel | 0.00 s ✅ |
| org.kde.KWin | 0.00 s ✅ |
| org.kde.ActivityManager | 0.00 s ✅ |
| org.kde.kded5 | 0.00 s ✅ |
| **org.kde.plasmashell** | **25.00 s → TIMEOUT** ❌ |

Reproduce in one line:
```fish
time busctl --user call org.kde.plasmashell /org/freedesktop/DBus org.freedesktop.DBus.Peer Ping
# hangs ~25s and fails while plasmashell is wedged; ~instant once healthy
```

plasmashell process at time of investigation: pid 8191, `STAT=Ssl`, `0% CPU`,
`wchan=do_poll`, `ELAPSED=5-06:53:21`. So: not crashed, not CPU-spinning — main thread
blocked (probably on its own sub-call) and never gets to dispatch incoming D-Bus.

## How it was traced (strace of `spectacle -b -n -f -o shot.png`)

- Full run ≈ **28 s**, reproducible (one run spiked to 46 s under load).
- The **actual screenshot is fast**: bulk 253 MB pixel readback happened at `+25.83s → +25.98s`
  (~0.15 s) and the PNG saved at `+26.3s`. So the screenshot work is ~sub-second.
- The first **~25.8 s is pure idle wait** before any pixels are grabbed:
  - thread polls the session-bus fd with a **25000 ms timeout** and **times out at +25.55s**
    (`poll(...) = 0 (Timeout) <25.267425>`); main thread parked on a futex the whole time.
  - 25 s == the libdbus/QtDBus **default method-call timeout**.
  - the small X events trickling in during the wait (PropertyNotify=28, XKB=85) are just
    ambient noise that periodically wakes the event loop — red herrings.
- D-Bus messages on the session bus just before the stall reference `org.kde.plasmashell`
  (and heavy but *healthy* kglobalaccel traffic). The per-service ping table above isolated
  plasmashell as the one that hangs.

## Ruled out (so we don't chase these again)

- **X11 vs Wayland** — irrelevant. Always X11; X11 is fine.
- **MIT-SHM / "is there an shm config option"** — no spectacle SHM toggle, and SHM is not the
  lever. On X11 spectacle's PlatformXcb uses plain `xcb_get_image` (the 1-byte `shmget` in the
  trace is just an XCB capability probe). Doesn't matter — see next point.
- **GPU / framebuffer readback** — fine. `xwd -root` copies the entire 253 MB framebuffer in
  **2 s**, `import -window root` in 3.7 s. AMD RX 580 (radeonsi), direct rendering. The
  NVIDIA GT 1030 (nouveau) drives a connected-but-inactive DVI output; not in the layout.
- **Monitor layout / bounding box** — irrelevant to the slowness. The staircase layout
  (HDMI @ 0,0; three DPs stacked at x=3840 down to y=8640) makes the X screen a
  7680×8640 bbox = **253 MB** at 32bpp (= exactly 8 screen-tiles of area; 4 real panels +
  ~4 tiles of empty void). But since the grab itself is sub-second, the staircase costs
  nothing meaningful and is kept intentionally (mouse ergonomics).

## Side change already applied (`~/.config/spectaclerc`)

Backup: `~/.config/spectaclerc.bak.20260627-000117`

```ini
[General]
onLaunchAction=DoNotTakeScreenshot   # was UseLastUsedCapturemode — open window, don't auto-grab
[GuiConfig]
captureMode=1                        # was 0 (AllScreens) — default to CurrentScreen (1 monitor)
```

**Caveat:** these only reduce screenshot *work*; they do **not** fix the startup delay, because
the 25 s plasmashell timeout is hit during app init on every launch regardless of capture mode.
The real cure is un-wedging plasmashell (restart, above). Revert with the backup if undesired.

## Re-verify after the eventual plasmashell restart

```fish
time busctl --user call org.kde.plasmashell /org/freedesktop/DBus org.freedesktop.DBus.Peer Ping   # expect ~instant
time spectacle -b -n -f -o /tmp/s.png                                                              # expect ~2-3s
```
