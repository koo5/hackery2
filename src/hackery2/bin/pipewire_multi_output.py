#!/usr/bin/env python3
"""Configure PipeWire to output to multiple devices simultaneously."""

import subprocess
import json
import argparse
import sys

def get_sinks():
    """Get list of available audio sinks."""
    result = subprocess.run(['pactl', 'list', 'short', 'sinks'], 
                          capture_output=True, text=True)
    sinks = []
    for line in result.stdout.strip().split('\n'):
        if line:
            parts = line.split('\t')
            sinks.append({
                'id': parts[0],
                'name': parts[1],
                'status': parts[4] if len(parts) > 4 else 'IDLE'
            })
    return sinks

def create_combined_sink(sink_names, name="combined"):
    """Create a combined sink from multiple sinks."""
    cmd = [
        'pactl', 'load-module', 'module-combine-sink',
        f'sink_name={name}',
        f'slaves={",".join(sink_names)}',
        f'sink_properties=device.description="{name.title()} Output"'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return int(result.stdout.strip())
    else:
        raise Exception(f"Failed to create combined sink: {result.stderr}")

def main():
    parser = argparse.ArgumentParser(description='Setup multi-output audio with PipeWire')
    parser.add_argument('--list', action='store_true', help='List available sinks')
    parser.add_argument('--combine', nargs='+', help='Sink names to combine')
    parser.add_argument('--name', default='combined', help='Name for combined sink')
    parser.add_argument('--set-default', action='store_true', help='Set as default sink')
    
    args = parser.parse_args()
    
    if args.list:
        sinks = get_sinks()
        print("Available audio sinks:")
        for sink in sinks:
            print(f"  {sink['name']} ({sink['status']})")
        return
    
    if args.combine:
        try:
            module_id = create_combined_sink(args.combine, args.name)
            print(f"Combined sink created (module ID: {module_id})")
            
            if args.set_default:
                subprocess.run(['pactl', 'set-default-sink', args.name])
                print(f"Set '{args.name}' as default sink")
                
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()