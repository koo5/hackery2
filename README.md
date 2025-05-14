bits of code and configuration for my machines. 
- ./data containes miscellaneous or less used functionalities and experiments
- ./src/hackery2/bin/ are functions that i often use on command line
- ./setup - data for setting up new machines, some of it is directly referenced by env vars, in /etc, etc
- ./notes - notes, research

## Installation as a Python Package

You can install this repository as a Python package to make all scripts from `src/hackery2/bin/` available in your PATH:

```bash
# Clone the repository if you haven't already
cd /home/koom/hackery2

# Install in development mode
pip install -e .
```

This will make all Python scripts from `src/hackery2/bin/` available as commands in your PATH.

### Optional Dependencies

Some scripts require additional dependencies. You can install them as needed:

```bash
# For audio-related scripts
pip install -e ".[audio]"

# For computer vision scripts
pip install -e ".[vision]"

# For all optional dependencies
pip install -e ".[all]"
```

### System Dependencies

Some scripts may require system packages:

```bash
# X11 support
sudo apt install python3-xlib
```

## Development

When adding new scripts to `src/hackery2/bin/`, reinstall the package to make them available:

```bash
pip install -e .
```