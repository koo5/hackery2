#!/usr/bin/env python3
"""
Helper module to create wrapper functions for scripts with different entry points
"""
import importlib
import sys
import inspect
import os
import glob

# Dictionary to hold all the run_* functions
_run_functions = {}

def _make_runner(script_name):
    """
    Create a wrapper function for a script that handles different entry point patterns
    
    Args:
        script_name: The name of the script without .py extension
    
    Returns:
        A function that will run the script
    """
    module_name = f"hackery2.bin.{script_name}"
    
    def wrapper():
        # Import the module
        module = importlib.import_module(module_name)
        
        # Check if module has a main() function
        if hasattr(module, 'main') and callable(module.main):
            return module.main()
        
        # Check for common command-line interface functions
        for func_name in ['x', 'cli', 'run']:
            if hasattr(module, func_name) and callable(getattr(module, func_name)):
                return getattr(module, func_name)()
                
        # If we got here, the script might be using __name__ == '__main__' guard
        # We need to trick it by setting __name__ to '__main__'
        old_name = module.__name__
        sys_argv = sys.argv
        module.__name__ = '__main__'
        sys.argv[0] = script_name
        
        # Run the module again
        try:
            importlib.reload(module)
        finally:
            # Restore the original state
            module.__name__ = old_name
            sys.argv = sys_argv
    
    return wrapper

# Get all script files
script_files = glob.glob(os.path.join(os.path.dirname(__file__), '*.py'))

# Create a runner function for each script
for script_path in script_files:
    script_name = os.path.basename(script_path)[:-3]  # Remove .py extension
    
    # Skip __init__.py and this utility module
    if script_name in ['__init__', 'script_wrapper']:
        continue
        
    # Create a function with the name run_script_name, replacing hyphens with underscores
    func_name = f"run_{script_name.replace('-', '_')}"
    _run_functions[func_name] = _make_runner(script_name)
    
    # Add the function to the module's globals
    globals()[func_name] = _run_functions[func_name]