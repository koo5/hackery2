
export MNT=$WORKDIR/ramfs
mkdir -p $MNT
export DEV=$MNT/image.raw


# block size that we will write/read
export BS=4096

# block count for image file
export BC=$(python3 -c "import os;print(int(round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / 2 / int(os.environ['BS']))))")
export BC=20000000

# how much data should we actually try to read and write, this is better to be lower than the image size
export BCDATA=$(python3 -c "import os;print(int(round(int(os.environ['BC']) / 5 * 4)))")

export MP=$WORKDIR/luks
mkdir -p MP
export CRYPTDEV=luks_integrity_benchmark1

export DD="dd status=progress"

