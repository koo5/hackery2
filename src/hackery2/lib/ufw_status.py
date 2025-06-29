#!/usr/bin/env python3
"""
UFW Status Parser - Parse UFW firewall status into structured data
"""

import argparse
import subprocess
import sys
import json
import re
from typing import List, Dict, Optional, Tuple


def parse_ufw_rule(rule_line: str) -> Optional[Dict[str, str]]:
	"""Parse a single UFW rule line into structured data."""
	# Skip non-rule lines
	if not rule_line.strip() or rule_line.startswith('-'):
		return None
	
	# Match rule format: [ 1] 22/tcp                     ALLOW IN    Anywhere
	# Or with destination: [ 3] 192.168.8.24 22            ALLOW IN    192.168.8.8
	rule_pattern = r'\[\s*(\d+)\]\s+(.+?)\s+(ALLOW|DENY|REJECT)\s+(IN|OUT)\s+(.+)'
	match = re.match(rule_pattern, rule_line)
	
	if not match:
		return None
	
	number, to_field, action, direction, from_field = match.groups()
	
	# Parse the 'To' field which can contain:
	# - Just a port: "80"
	# - Port with protocol: "80/tcp"
	# - Port range: "1714:1764/tcp"
	# - Named service: "syncthing"
	# - Destination and port: "192.168.8.24 22"
	# - IPv6 destination and port: "200:27c9:eb53:77ba:1ce4:1c9b:f9b3:2906 2222"
	# - Just destination: "192.168.8.24"
	# - "Anywhere" or "Anywhere (v6)"
	
	to_field = to_field.strip()
	destination = None
	port = None
	protocol = None
	
	# Check if it's "Anywhere" (with optional v6)
	if to_field.lower().startswith('anywhere'):
		destination = to_field
		port = None
	else:
		# Handle IPv6 port format like "80 (v6)" or "10102 (v6)"
		if to_field.endswith(' (v6)'):
			# Remove the (v6) suffix and parse the rest
			to_field_clean = to_field[:-5].strip()
			# Now parse as normal
			parts = to_field_clean.rsplit(' ', 1)
			if len(parts) == 2:
				# Has destination and port/service
				destination = parts[0] + " (v6)"
				port_part = parts[1]
			else:
				# No destination, just port/service
				destination = "Anywhere (v6)"
				port_part = to_field_clean
		else:
			# Try to parse as "destination port" or "destination port/protocol"
			# First check if there's a space (indicating destination + port)
			parts = to_field.rsplit(' ', 1)
			if len(parts) == 2:
				# Has destination and port/service
				destination = parts[0]
				port_part = parts[1]
			else:
				# No destination, just port/service
				destination = "Anywhere"
				port_part = to_field
		
		# Parse port_part which can be:
		# - Port number: "22"
		# - Port range: "1714:1764"
		# - Port/protocol: "22/tcp"
		# - Port range/protocol: "1714:1764/tcp"
		# - Named service: "syncthing"
		if '/' in port_part:
			port, protocol = port_part.split('/', 1)
		else:
			port = port_part
			protocol = None
	
	return {
		'number': int(number),
		'destination': destination,
		'port': port,
		'protocol': protocol,
		'action': action,
		'direction': direction,
		'source': from_field.strip()
	}


def get_ufw_status() -> Tuple[bool, str, List[Dict[str, str]]]:
	"""
	Run 'sudo ufw status numbered' and parse the output.
	
	Returns:
		Tuple of (is_active, status_message, rules_list)
	"""
	try:
		result = subprocess.run(
			['sudo', 'ufw', 'status', 'numbered'],
			capture_output=True,
			text=True,
			check=True
		)
		
		output = result.stdout.strip()
		lines = output.split('\n')
		
		# Check if UFW is active
		is_active = False
		status_message = ""
		rules = []
		
		for line in lines:
			if line.startswith('Status:'):
				status_message = line.strip()
				is_active = 'active' in line.lower()
			else:
				rule = parse_ufw_rule(line)
				if rule:
					rules.append(rule)
		
		return is_active, status_message, rules
		
	except subprocess.CalledProcessError as e:
		print(f"Error running ufw command: {e}", file=sys.stderr)
		print(f"Error output: {e.stderr}", file=sys.stderr)
		sys.exit(1)
	except Exception as e:
		print(f"Unexpected error: {e}", file=sys.stderr)
		sys.exit(1)


def format_rule(rule: Dict[str, str]) -> str:
	"""Format a single rule for display."""
	# Build the To field
	to_field = rule['destination']
	if rule['port']:
		if rule['destination'] != "Anywhere" and not rule['destination'].startswith("Anywhere"):
			to_field += f" {rule['port']}"
		else:
			to_field = rule['port']
		
		if rule['protocol']:
			to_field += f"/{rule['protocol']}"
	
	return f"[{rule['number']:3d}] {to_field:<30} {rule['action']:<10} {rule['direction']:<5} {rule['source']}"


def main():
	parser = argparse.ArgumentParser(
		description='Parse UFW firewall status into structured data'
	)
	parser.add_argument(
		'--json', '-j',
		action='store_true',
		help='Output in JSON format'
	)
	parser.add_argument(
		'--pretty', '-p',
		action='store_true',
		help='Pretty print JSON output'
	)
	
	args = parser.parse_args()
	
	# Get UFW status
	is_active, status_message, rules = get_ufw_status()
	
	if args.json:
		output = {
			'active': is_active,
			'status': status_message,
			'rules': rules
		}
		if args.pretty:
			print(json.dumps(output, indent=2))
		else:
			print(json.dumps(output))
	else:
		# Text output
		print(status_message)
		print()
		
		if not is_active:
			print("UFW is inactive")
		elif not rules:
			print("No rules configured")
		else:
			print("Rules:")
			print("-" * 70)
			for rule in rules:
				print(format_rule(rule))


if __name__ == '__main__':
	main()