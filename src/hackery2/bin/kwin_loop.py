#!/usr/bin/env python3

import logging
import os
import time

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def main():
	time.sleep(4)
	while True:
		try:
			os.system("""QML_XHR_ALLOW_FILE_READ=1 QT_LOGGING_RULES="kwin_tabbox=true;qml=true;qml.debug=true" kwin_x11 --replace""")
		except e:
			pass

if __name__ == "__main__":
	main()