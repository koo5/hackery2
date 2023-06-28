#!/usr/bin/env fish
grep -h security -R /etc/apt/sources.list /etc/apt/sources.list.d/ | sudo tee /etc/apt/sec
and sudo apt-get update -o Dir::Etc::SourceParts='' -o Dir::Etc::SourceList=/etc/apt/sec
and sudo apt-get upgrade -o Dir::Etc::SourceParts='' -o Dir::Etc::SourceList=/etc/apt/sec

# https://serverfault.com/a/282518/98242
# https://youtu.be/fo8zpBm05Dc
