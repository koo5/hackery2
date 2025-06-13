#!/usr/bin/env python
from setuptools import setup, find_packages
import os
import glob
import re

def get_python_scripts():
    """Get all Python scripts from src/hackery2/lib directory"""
    return glob.glob('src/hackery2/lib/*.py')

def create_console_scripts():
    """Create console_scripts entries for bin scripts based on their structure"""
    console_scripts = []
    
    for script_path in get_python_scripts():
        script_name = os.path.basename(script_path)[:-3]  # Remove .py extension
        
        # Skip __init__.py and utility modules
        if script_name in ['__init__', 'script_wrapper']:
            continue
            
        # Create function name by replacing hyphens with underscores
        function_name = f"run_{script_name.replace('-', '_')}"
        
        # Use original script name as command name
        console_scripts.append(
            f"{script_name}=hackery2.lib.script_wrapper:{function_name}"
        )
    
    return console_scripts

setup(
    name="hackery2",
    version="0.1.0",
    author="koom",
    description="Personal hackery utilities and scripts",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    install_requires=[
        # Command line and process utilities
        "click",                  # Command line interface creation
        "fire",                   # Automatic CLI generation
        "psycopg2",
        "ptyprocess",             # Pseudo-terminal utilities
        "prompt_toolkit==1.0.14", # Interactive command-line toolkit (specific version)
        
        # Network and web
        "requests",               # HTTP requests
        
        # Formatting and display
        "termcolor",              # Terminal color output
        
        # Date and time
        "python-dateutil",        # Date utilities
        
        # GUI/X11
        "python-xlib",            # X Window System interface
        
        # Version control
        "gitpython",              # Git repository interaction
        
        # Optional dependencies (uncomment as needed for specific scripts)
        # "av",                     # Audio/video processing
        # "numpy",                  # Scientific computing
        # "opencv-python",          # Computer vision
        # "sounddevice",            # Audio I/O
        # "openai-whisper",         # Speech recognition
    ],
    extras_require={
        # Define optional dependencies that can be installed with pip install hackery2[audio]
        "audio": ["av", "sounddevice", "openai-whisper"],
        "vision": ["numpy", "opencv-python"],
        "all": ["av", "numpy", "opencv-python", "sounddevice", "openai-whisper"],
    },
    # System dependencies noted in scripts:
    # - sudo apt install python3-xlib
    entry_points={
        "console_scripts": create_console_scripts(),
    },
)