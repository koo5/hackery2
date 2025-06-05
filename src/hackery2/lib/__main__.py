#!/usr/bin/env python3
"""
Main entry point for hackery2 scripts when installed as a package.
This module is imported by each console script entry point.
"""

import sys
import importlib
import inspect

def __main__():
    """
    Main entry point for scripts. This will import the parent module 
    and execute it according to its structure.
    """
    # Get the caller module
    caller_frame = inspect.currentframe().f_back
    caller_module = inspect.getmodule(caller_frame)
    
    # Get the parent module (the actual script)
    if caller_module.__name__ == "__main__":
        # Running through python -m
        module_name = sys.argv[0]
    else:
        # Running as installed entry point
        module_name = caller_module.__name__
    
    # Import the module
    module = importlib.import_module(module_name)
    
    # Check if module has a main() function
    if hasattr(module, 'main') and callable(module.main):
        return module.main()
    
    # Check for common command-line interface functions
    for func_name in ['x', 'cli', 'run', 'main_cli']:
        if hasattr(module, func_name) and callable(getattr(module, func_name)):
            return getattr(module, func_name)()
    
    # If we got here, just let the module execute its top-level code
    # The module will have already been imported and executed
    return 0