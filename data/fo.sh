#!/usr/bin/env bash

while true;
 openssl enc -aes-256-ctr -pass pass:"(dd if=/dev/urandom bs=128 count=1 2>/dev/null | base64)" -nosalt < /dev/zero > fo;
end;


