#!/usr/bin/env python3
"""
UFW Cleanup - Compare UFW rules with actual open ports and generate delete commands
"""

zzzimport argparse
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
		'--dry-run', '-n',
		action='store_true',
		help='Show what would be deleted without generating commands'
	)
	parser.add_argument(
		'--verbose', '-v',
		action='store_true',
		help='Show detailed information'
	)
	
	args = parser.parse_args()
	
	# Get UFW rules and open ports
	ufw_rules = get_ufw_rules()
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
	
	if args.dry_run:
		print("Unused UFW rules:")
		for rule in unused_rules:
			port_info = f"{rule['port']}"
			if rule['protocol']:
				port_info += f"/{rule['protocol']}"
			dest_info = f"to {rule['destination']}" if rule['destination'] != "Anywhere" else ""
			print(f"  Rule {rule['number']}: {port_info} {dest_info} from {rule['source']}")
	else:
		# Generate delete commands, starting from highest rule number
		# This ensures rule numbers don't change as we delete
		unused_rules.sort(key=lambda r: r['number'], reverse=True)
		
		print("# UFW cleanup commands:")
		for rule in unused_rules:
			# Build rule description
			port_info = f"{rule['port']}"
			if rule['protocol']:
				port_info += f"/{rule['protocol']}"
			
			desc_parts = []
			desc_parts.append(f"{rule['action']} {rule['direction']}")
			desc_parts.append(port_info)
			if rule['destination'] != "Anywhere":
				desc_parts.append(f"to {rule['destination']}")
			desc_parts.append(f"from {rule['source']}")
			
			description = " ".join(desc_parts)
			print(f"echo y | sudo ufw delete {rule['number']}  # {description}")


if __name__ == '__main__':
	main()