#!/bin/bash

# https://stackoverflow.com/questions/6949546/an-rng-faster-than-dev-random-but-cryptographically-useful


head -c 10000000000 /dev/zero | openssl enc \
    -aes-256-ctr \
    -pass file:<(dd if=/dev/urandom bs=128 count=1 2>/dev/null | base64) \
    -nosalt 

