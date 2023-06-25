#!/usr/bin/env fish
grep -h security -R /etc/apt/sources.list /etc/apt/sources.list.d/ | sudo tee /etc/apt/sec
and sudo apt-get upgrade -o Dir::Etc::SourceParts='' -o Dir::Etc::SourceList=/etc/apt/sec
