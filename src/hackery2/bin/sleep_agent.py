#!/usr/bin/env python3

import logging
import os
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def get_lid_state():
    lid_paths = ['/proc/acpi/button/lid/LID/state', '/proc/acpi/button/lid/LID0/state']
    
    for path in lid_paths:
        try:
            with open(path, 'r') as f:
                state = f.read().strip().lower()
                if "closed" in state:
                    return "closed"
                elif "open" in state:
                    return "open"
                return "unknown"
        except FileNotFoundError:
            continue
    
    return "cannot detect state"

lid_state = get_lid_state()

state_messages = {
    "closed": "The lid is closed.",
    "open": "The lid is open.",
    "unknown": "The lid state is unknown.",
    "cannot detect state": "Cannot detect the lid state."
}

#print(state_messages[lid_state])

if lid_state == "closed":
		log.debug("The lid is closed.")
		log.debug("Going to sleep.")
		import os
		os.system("systemctl --check-inhibitors=no suspend")
elif lid_state == "open":
		log.debug("The lid is open.")
		log.debug("Not going to sleep.")
else:
		log.debug("Cannot detect the lid state.")
		log.debug("Not going to sleep.")
		