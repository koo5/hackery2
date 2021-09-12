#!/bin/bash

# https://gist.github.com/joeharr4/c7599c52f9fad9e53f62e9c8ae690e6b

# ssh-cipher-benchmark.sh - Assesses speed of SSH encryption between specific hosts.
# Usage:
# ssh-cipher-benchmark.sh <remotehost> [ciphers]
# Default ciphers: all we can find...
#
# Note: In some cases, the first cipher tested runs faster than the others, regardless of order.
# Cause of this is not known, but changing the order of testing shows it to be true.  Run the
# first one twice if you suspect this.  Perhaps it is due to buffering?
#
# Hosted at:
# https://gist.github.com/dlenski/e42a08fa27e97b0dbb0c0024c99a8bc4#file-ssh-cipher-benchmark-sh
# Which was based on:
# Based on: http://www.systutorials.com/5450/improving-sshscp-performance-by-choosing-ciphers/#comment-28725
#
# You should set up PublicKey authentication so that you don't have to type your
# password for every cipher tested.

# parse command line
remote=${1:-localhost} # machine to test
shift

set -o pipefail

ciphers="$@"
if [[ -n "$ciphers" ]]; then echo "User-supplied ciphers: $ciphers"; fi

if [[ -z "$ciphers" ]]; then
  ciphers=$(egrep '^\s*Ciphers' /etc/ssh/sshd_config|sed 's/Ciphers//; s/,/ /g')
  if [[ -n "$ciphers" ]]; then echo "/etc/ssh/sshd_config allows these ciphers: $ciphers"; fi
fi

if [[ -z "$ciphers" ]]; then
  ciphers=$(echo $(ssh -Q cipher))
  if [[ -n "$ciphers" ]]; then echo "ssh -Q cipher reports these ciphers: $ciphers"; fi
fi

if [[ -z "$ciphers" ]]; then
  read -rd '' ciphers <<EOF
3des-cbc aes128-cbc aes128-ctr aes128-gcm@openssh.com aes192-cbc aes192-ctr
aes256-cbc aes256-ctr aes256-gcm@openssh.com arcfour arcfour128 arcfour256
blowfish-cbc cast128-cbc chacha20-poly1305@openssh.com rijndael-cbc@lysator.liu.se
EOF
  echo "Default cipher test list: $ciphers"
fi

echo
echo "For each cipher, will transfer 1000 MB of zeros to/from ${remote}."
echo

tmp=$(mktemp)
for i in $ciphers
do
  echo -n "$i: "
  dd if=/dev/zero bs=1000000 count=1000 2> /dev/null |
  ssh -p 44 -c $i -o Compression=no ${remote} "/bin/bash -c \"(/usr/bin/time -p cat) > /dev/null\"" > $tmp 2>&1
  
  if [[ $? == 0 ]]; then
      grep real $tmp | awk '{print 1000 / $2" MB/s" }'
  else
      echo "failed, for why run: ssh -vc $i ${remote}"
  fi
done
