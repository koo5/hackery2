#!/usr/bin/env fish

set F (mktemp /tmp/commits.XXXXXX)
interleaved_git_history.py --reverse > $F;
libreoffice --norestore --calc $F --infilter='Text - txt - csv (StarCalc):9,34,76,1';

