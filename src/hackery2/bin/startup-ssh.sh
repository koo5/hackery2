#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
{
bash -v "$DIR/startup2.sh" && 
ssh -v  editable-log@loworbit.now.im  -p 44 -t "tmux attach-session"
}

