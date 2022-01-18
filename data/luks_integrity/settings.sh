
export WORKDIR=/run/luks_integrity_benchmark
# where to mount ramfs
export MNT=$WORKDIR/ramfs
mkdir -p $MNT
# image file path
export DEV=$MNT/image.raw
# crypto key
export KEY=$WORKDIR/key
# dev-mapper device name
export CRYPTDEV=luks_integrity_benchmark1
# dd
export DD="dd status=progress"

# block size that we will write/read
export BS=4096

# block count for image file
export BC=$(python3 -c "import os;print(int(round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / 2 / int(os.environ['BS']))))")
export BC=20000000

# how much data should we actually try to read and write, this is better to be lower than the image size
export BCDATA=$(python3 -c "import os;print(int(round(int(os.environ['BC']) / 5 * 4)))")


