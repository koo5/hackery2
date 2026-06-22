# hp.internal — HP EliteBook 8570w notes

Hardware: HP EliteBook 8570w. NVIDIA Quadro K1000M (GK107, **Kepler**), Intel
Centrino Advanced-N 6205 wifi, Intel 82579LM ethernet. Ubuntu 24.04 (noble).

Storage: root `/` is ext4 on LVM (`vgubuntu-root`); `/boot` ext4 on `/dev/sda2`.
The data SSD `mx500data` (Crucial MX500, ~1.79 TiB, near full) is **btrfs** and
carries `/home`, `/d`, `/mx500data` (zlib compress, subvolumes). btrfs safety
therefore drives kernel choice — see "Kernel choice" below.

---

## Issue 1: Wi-Fi not detected on the old (5.x) kernels

**Symptom:** No `wlan`/`wlo` interface; NetworkManager shows `WIFI-HW: missing`.
The `iwlwifi` module loads and the PCI device (Intel 6205, `8086:0082`) is present.

**Root cause:** firmware load fails:

```
iwlwifi 0000:04:00.0: Direct firmware load for iwlwifi-6000g2a-6.ucode failed with error -2
iwlwifi 0000:04:00.0: no suitable firmware found!
```

Ubuntu 24.04's `linux-firmware` ships every blob in `/lib/firmware` as
**zstd-compressed `.zst` only** (no plain or `.xz` copies). Kernel zstd firmware
decompression (`CONFIG_FW_LOADER_COMPRESS_ZSTD`) only exists in **Linux ≥ 5.19**.
The old kernels here (5.8 / 5.11 / 5.15) only have the XZ-era
`CONFIG_FW_LOADER_COMPRESS=y`, so they cannot read any `.zst` firmware → every
firmware-dependent device (wifi included) fails on those kernels.

**Fix (for staying on a pre-5.19 kernel):** decompress the blob to a plain name
the old kernel can load; the kernel tries `.ucode` before `.ucode.zst`:

```sh
sudo unzstd -k /lib/firmware/iwlwifi-6000g2a-6.ucode.zst -o /lib/firmware/iwlwifi-6000g2a-6.ucode
sudo modprobe -r iwlwifi && sudo modprobe iwlwifi    # -> wlo1 appears
```

This only covers the wifi blob; any other device needing firmware on an old
kernel hits the same wall (decompress each as needed). **Better:** just boot a
≥ 5.19 kernel (6.8 — see below), which loads `.zst` natively and makes this
workaround unnecessary.

---

## Issue 2: Display manager doesn't come up on "newer" kernels

**Symptom:** booting certain 6.x kernels lands with no graphical login.

**It is NOT failing before the display manager.** sddm is reached and starts
every time. On a kernel that lacks an nvidia driver, X then dies immediately:

```
sddm: Failed to read display number from pipe
sddm: Attempt 3 starting the Display server on vt 2 failed
sddm: Could not start Display server on vt 2
```

**Root cause:** the GPU is a Kepler Quadro K1000M, supported only by the legacy
**nvidia-470** (or 390) driver. The nvidia kernel module is installed as
**per-kernel prebuilt packages** (`linux-modules-nvidia-470-<version>`), NOT via
dkms (dkms only carries `evdi` here). Modules existed for `6.8.0-31` and
`6.11.0-25` (those booted fine, straight into Plasma) but **not** for the
default `6.8.0-64`. With no nvidia module there is no usable fallback — Kepler
nouveau is not viable and `nvidiafb` is blacklisted — so X cannot start.

Per-kernel nvidia module presence is the whole story:

| Kernel        | nvidia-470 module | Result          |
|---------------|-------------------|-----------------|
| 6.8.0-31      | present           | works (Plasma)  |
| 6.8.0-64      | was missing       | X failed → fixed|
| 6.11.0-25     | present           | works (Plasma)  |
| 6.14.0-24     | none (EOL 470)    | avoid           |

**Fix applied:** install the tracking metapackage, which builds the module for
the current GA kernel and keeps future GA kernels covered automatically:

```sh
sudo apt install linux-modules-nvidia-470-generic
# pulls linux-modules-nvidia-470-6.8.0-64-generic; nvidia.ko now present for 6.8.0-64
```

(Per-kernel alternative: `sudo apt install linux-modules-nvidia-470-6.8.0-64-generic`.)

---

## Kernel choice — why pinned to 6.8.0-64

Two constraints decide which kernel to run:

1. **GPU:** must have an nvidia-470 prebuilt module (Kepler is 470/390 only).
2. **btrfs safety** (the data SSD): per the bees btrfs-kernel doc
   (<https://github.com/Zygo/bees/blob/master/docs/btrfs-kernel.md>), **6.11.x
   has a delayed-refs bug ("adding refs to an existing tree ref") that flips the
   filesystem read-only, fixed only in 6.11.10 / 6.12.** Ubuntu's `6.11.0-25` is
   upstream 6.11.0 + Canonical backports; whether that specific fix is included
   is unclear. 6.8 is the 24.04 **GA** kernel — best btrfs stable backports,
   longest support window, not flagged by the doc. It is also ≥ 5.19, so it
   loads the zstd wifi firmware natively (Issue 1 workaround not needed).

**Conclusion:** **6.8.0-64-generic** is the safe choice — it satisfies both
constraints. Avoid the 6.11/6.14 HWE kernels (btrfs risk + 470 is EOL and may
never get a build for them).

**GRUB pin applied** (so a future kernel install can't silently become a
non-bootable-to-desktop default):

```sh
# /etc/default/grub
GRUB_DEFAULT="gnulinux-advanced-6c2f33aa-0c23-4c86-93e8-daff8e356e50>gnulinux-6.8.0-64-generic-advanced-6c2f33aa-0c23-4c86-93e8-daff8e356e50"
sudo update-grub
```

Backup of the original config: `/etc/default/grub.bak-20260620-164901`
(the UUID `6c2f33aa-...` is the `/boot` filesystem; regenerate the pin string
from `/boot/grub/grub.cfg` if the disk/UUID ever changes).

---

## Gotchas / watch-list

- **nvidia-470 is EOL upstream.** HWE kernels (6.11, 6.14) may never get a 470
  build. The explicit GRUB pin is the guard against drifting onto one.
- The `linux-modules-nvidia-470-generic` metapackage tracks the **GA** flavour
  only. If the HWE stack is ever installed, it would need a different metapackage
  (which likely won't exist for 470) — stay on GA.
- After any kernel update, before rebooting, confirm the target kernel has a
  module: `find /lib/modules/<ver> -name nvidia.ko`.
- Verifying the display fix requires an actual reboot into 6.8.0-64; the module
  being present is necessary but the real proof is the next boot.

_Last updated: 2026-06-20._
