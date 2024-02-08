# pip install systemd-python

import time

from systemd import journal

# Open the journal for reading logs
j = journal.Reader()

# Filter logs by specific unit
j.this_boot()
j.add_match(_SYSTEMD_UNIT="systemd-logind.service")

# Move to the end of the journal, effectively emulating 'tail -f'
j.seek_tail()
j.get_previous()  # Necessary to actually get to the end


while True:
    # Wait for new journal entries; this is a blocking call
    if j.wait(timeout=1) == journal.APPEND:
        # There are new entries to read
        for entry in j:
            timestamp = entry['__REALTIME_TIMESTAMP']
            message = entry.get('MESSAGE', 'No message')
            print(f"{timestamp}: {message}")
    else:
        # No new entries, you can perform some other tasks, or just sleep for a while
        time.sleep(1)

