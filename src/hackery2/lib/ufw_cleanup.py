#!/usr/bin/env python3
"""
UFW Cleanup - Compare UFW rules with actual open ports and generate delete commands
"""

import argparse
import subprocess
import sys
import json
import re
from typing import List, Dict, Set, Tuple


def get_ufw_rules() -> List[Dict]:
	"""Get UFW rules using ufw_status.py."""
	try:
		result = subprocess.run(
			['ufw_status', '--json'],
			capture_output=True,
			text=True,
			check=True
		)
		data = json.loads(result.stdout)
		return data['rules']
	except subprocess.CalledProcessError as e:
		print(f"Error getting UFW rules: {e}", file=sys.stderr)
		sys.exit(1)
	except json.JSONDecodeError as e:
		print(f"Error parsing UFW status JSON: {e}", file=sys.stderr)
		sys.exit(1)


def get_open_ports() -> Set[Tuple[str, str]]:
	"""Get open ports from netstat."""
	try:
		result = subprocess.run(
			['sudo', 'netstat', '-nlpt'],
			capture_output=True,
			text=True,
			check=True
		)
		
		open_ports = set()
		lines = result.stdout.strip().split('\n')
		
		# Skip header lines
		for line in lines[2:]:  # Skip "Active Internet connections" and headers
			if not line.strip():
				continue
			
			# Parse netstat output
			# Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
			parts = line.split()
			if len(parts) >= 6 and parts[0] in ['tcp', 'tcp6']:
				proto = 'tcp'
				local_addr = parts[3]
				
				# Extract port from address
				if ':::' in local_addr:
					# IPv6 format like :::22
					port = local_addr.split(':::')[1]
					open_ports.add((port, proto))
				elif ':' in local_addr:
					# IPv4 format like "0.0.0.0:22" or specific IP
					port = local_addr.rsplit(':', 1)[1]
					open_ports.add((port, proto))
		
		return open_ports
		
	except subprocess.CalledProcessError as e:
		print(f"Error running netstat: {e}", file=sys.stderr)
		print("Make sure to run with sudo", file=sys.stderr)
		sys.exit(1)


def find_unused_rules(ufw_rules: List[Dict], open_ports: Set[Tuple[str, str]]) -> List[Dict]:
	"""Find UFW rules that don't match any open ports."""
	unused_rules = []
	
	for rule in ufw_rules:
		# Only check ALLOW IN rules (outgoing and deny rules are different use case)
		if rule['action'] != 'ALLOW' or rule['direction'] != 'IN':
			continue
		
		# Skip rules without specific ports (general allow rules)
		if not rule['port']:
			continue
		
		# Handle port ranges
		port_str = rule['port']
		protocol = rule['protocol'] or 'tcp'  # Default to tcp if not specified
		
		# Skip port ranges entirely
		if ':' in port_str:
			continue
		
		# Check if single port is in use
		is_used = (port_str, protocol) in open_ports
		
		if not is_used:
			unused_rules.append(rule)
	
	return unused_rules


def main():
	parser = argparse.ArgumentParser(
		description='Compare UFW rules with actual open ports and generate cleanup commands'
	)
	parser.add_argument(
		'--verbose', '-v',
		action='store_true',
		help='Show detailed information'
	)
	parser.add_argument(
		'--comment', '-c',
		type=str,
		help='Delete all rules with this comment (skips port checking)'
	)
	
	args = parser.parse_args()
	
	# Get UFW rules
	ufw_rules = get_ufw_rules()
	
	if args.comment:
		# Filter rules by comment
		matching_rules = []
		for rule in ufw_rules:
			# Check if the source field contains a comment
			if '#' in rule['source']:
				# Extract the comment part
				comment_part = rule['source'].split('#', 1)[1].strip()
				if comment_part == args.comment:
					matching_rules.append(rule)
		unused_rules = matching_rules
		
		if args.verbose:
			print(f"Found {len(unused_rules)} rules with comment '{args.comment}'")
			print()
	else:
		# Normal operation - find unused ports
		open_ports = get_open_ports()
		
		if args.verbose:
			print("Open ports detected:")
			for port, proto in sorted(open_ports):
				print(f"  {port}/{proto}")
			print()
		
		# Find unused rules
		unused_rules = find_unused_rules(ufw_rules, open_ports)
	
	if not unused_rules:
		print("No unused UFW rules found.")
		return
	
	# Generate delete commands, starting from highest rule number
	# This ensures rule numbers don't change as we delete
	unused_rules.sort(key=lambda r: r['number'], reverse=True)
	
	print("# UFW cleanup commands:")
	for rule in unused_rules:
			# Build rule description
			port_info = f"{rule['port']}" if rule['port'] else "any"
			if rule['protocol']:
				port_info += f"/{rule['protocol']}"
			
			desc_parts = []
			desc_parts.append(f"{rule['action']} {rule['direction']}")
			desc_parts.append(port_info)
			if rule['destination'] != "Anywhere" and rule['destination'] != "Anywhere (v6)":
				desc_parts.append(f"to {rule['destination']}")
			
			# For the source, include the full text (with comment if present)
			desc_parts.append(f"from {rule['source']}")
			
			description = " ".join(desc_parts)
			print(f"echo y | sudo ufw delete {rule['number']}  # {description}")


if __name__ == '__main__':
	main()