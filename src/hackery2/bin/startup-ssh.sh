#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
{
bash -v "$DIR/startup2.sh" && 
ssh   editable-log@51.140.155.227 -p 44 -t "tmux attach"
ping 8.8.8.8
}


