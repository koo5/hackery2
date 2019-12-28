#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
bash -v "$DIR/startup2.sh"
ping 8.8.8.8
cat


# echo "koom ALL=(ALL) NOPASSWD:/home/koom/hackery2/src/hackery2/bin/update-yum" | sudo tee  /etc/sudoers.d/hackery


