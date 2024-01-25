#!/usr/bin/env python3
import subprocess
import os
import signal
import time

# Specify the directory containing the executables
directory_path = "/usr/libexec/xscreensaver/"

# Function to get the active window ID using xprop
def get_active_window_id():
    try:
        output = subprocess.check_output(['xprop', '-root', '_NET_ACTIVE_WINDOW'])
        window_id = output.decode().split()[-1].strip(',')
        return window_id
    except subprocess.CalledProcessError:
        return None

# Function to run each executable in the directory for 10 seconds
def run_executables(window_id):
    for file in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file)
        # Check if the file is executable
        if os.access(file_path, os.X_OK):
            print(f"Running {file} for 10 seconds...")
            process = subprocess.Popen([file_path, '-window-id', window_id])
            time.sleep(10)
            process.terminate()

# Function to handle exit signals
def handle_exit_signal(signum, frame):
    print("Terminating...")
    subprocess.run(['killall', 'abstractile'])

# Set signal handlers
signal.signal(signal.SIGWINCH, handle_exit_signal)
signal.signal(signal.SIGTERM, handle_exit_signal)

# Get the active window ID and run the executables
active_window_id = get_active_window_id()
if active_window_id:
    run_executables(active_window_id)
