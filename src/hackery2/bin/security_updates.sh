#!/usr/bin/env fish


sudo aptdcon --fix-install
and \
grep -h -e "security\|mozilla" -R /etc/apt/sources.list /etc/apt/sources.list.d/*.list \
| sudo tee /etc/apt/sec

and sudo apt-get update  -o Dir::Etc::SourceParts='' -o Dir::Etc::SourceList=/etc/apt/sec  --error-on=any 
and sudo apt-get upgrade -o Dir::Etc::SourceParts='' -o Dir::Etc::SourceList=/etc/apt/sec  -y --allow-downgrades


# https://serverfault.com/a/282518/98242
# https://youtu.be/fo8zpBm05Dc
