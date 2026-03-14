#!/usr/bin/env python3
"""
Read localStorage data from Firefox profile in current directory.
Firefox stores localStorage in webappsstore.sqlite database.
"""

import sqlite3
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse
import argparse


def find_firefox_profiles(base_path="."):
	"""Find Firefox profiles in the given directory."""
	profiles = []
	base = Path(base_path)
	
	# Look for webappsstore.sqlite files
	for sqlite_file in base.rglob("webappsstore.sqlite"):
		profile_dir = sqlite_file.parent
		profiles.append(profile_dir)
	
	# Also check for typical Firefox profile patterns
	for item in base.iterdir():
		if item.is_dir():
			# Check if it contains webappsstore.sqlite
			webapp_store = item / "webappsstore.sqlite"
			if webapp_store.exists() and item not in profiles:
				profiles.append(item)
	
	return profiles


def reverse_origin_key(origin_key):
	"""
	Firefox stores origins in reverse notation.
	e.g., "moc.elgoog.:https:443" -> "https://google.com"
	"""
	parts = origin_key.split(":")
	
	if len(parts) >= 2:
		# Reverse the domain part
		domain_parts = parts[0].split(".")
		domain = ".".join(reversed(domain_parts))
		
		# Reconstruct the URL
		if len(parts) == 3:
			protocol = parts[1]
			port = parts[2]
			if (protocol == "https" and port == "443") or (protocol == "http" and port == "80"):
				return f"{protocol}://{domain}"
			else:
				return f"{protocol}://{domain}:{port}"
		elif len(parts) == 2:
			protocol = parts[1]
			return f"{protocol}://{domain}"
	
	return origin_key


def read_localstorage(profile_path):
	"""Read localStorage data from Firefox profile."""
	webapp_store = Path(profile_path) / "webappsstore.sqlite"
	
	if not webapp_store.exists():
		print(f"Error: webappsstore.sqlite not found in {profile_path}")
		return None
	
	storage_data = {}
	
	try:
		# Connect to the SQLite database
		conn = sqlite3.connect(str(webapp_store))
		cursor = conn.cursor()
		
		# First, let's check what tables exist
		cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
		tables = cursor.fetchall()
		print(f"Debug: Found tables: {[t[0] for t in tables]}")
		
		# Try different possible table names
		table_name = None
		for possible_table in ['webappsstore2', 'webappsstore', 'data']:
			cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{possible_table}'")
			if cursor.fetchone()[0] > 0:
				table_name = possible_table
				break
		
		if not table_name:
			print("Error: Could not find localStorage table in database")
			print(f"Available tables: {[t[0] for t in tables]}")
			conn.close()
			return None
		
		print(f"Debug: Using table: {table_name}")
		
		# Check the schema of the table
		cursor.execute(f"PRAGMA table_info({table_name})")
		columns = cursor.fetchall()
		print(f"Debug: Table columns: {[(c[1], c[2]) for c in columns]}")
		
		# Query the table - get total count first
		cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
		total_count = cursor.fetchone()[0]
		print(f"Debug: Total rows in table: {total_count}")
		
		if total_count == 0:
			print("The webappsstore.sqlite database exists but contains no localStorage data.")
			print("This can happen if:")
			print("  1. This is a new/unused profile")
			print("  2. The profile has been cleaned/cleared")
			print("  3. No websites have stored localStorage data yet")
			conn.close()
			return storage_data  # Return empty dict instead of None
		
		# Get column info to determine structure
		has_scope = any(c[1] == 'scope' for c in columns)
		has_origin_attributes = any(c[1] == 'originAttributes' for c in columns)
		
		# Build the appropriate query based on available columns
		if has_scope:
			# Newer Firefox versions with scope column
			cursor.execute(f"""
				SELECT originAttributes, originKey, scope, key, value 
				FROM {table_name}
				ORDER BY originKey, key
			""")
			rows = cursor.fetchall()
			
			for origin_attrs, origin_key, scope, key, value in rows:
				# Convert the reversed origin to normal format
				origin = reverse_origin_key(origin_key)
				
				# Add scope info if present
				if scope and scope != origin_key:
					origin = f"{origin} (scope: {scope})"
				
				if origin not in storage_data:
					storage_data[origin] = {}
				
				# Try to parse JSON values
				try:
					parsed_value = json.loads(value)
					storage_data[origin][key] = parsed_value
				except (json.JSONDecodeError, TypeError):
					storage_data[origin][key] = value
		else:
			# Older Firefox versions without scope
			cursor.execute(f"""
				SELECT originKey, key, value 
				FROM {table_name}
				ORDER BY originKey, key
			""")
			rows = cursor.fetchall()
			
			for origin_key, key, value in rows:
				# Convert the reversed origin to normal format
				origin = reverse_origin_key(origin_key)
				
				if origin not in storage_data:
					storage_data[origin] = {}
				
				# Try to parse JSON values
				try:
					parsed_value = json.loads(value)
					storage_data[origin][key] = parsed_value
				except (json.JSONDecodeError, TypeError):
					storage_data[origin][key] = value
		
		conn.close()
		
	except sqlite3.Error as e:
		print(f"SQLite error: {e}")
		import traceback
		traceback.print_exc()
		return None
	
	return storage_data


def display_storage_data(storage_data, filter_origin=None, filter_key=None):
	"""Display localStorage data with optional filtering."""
	if not storage_data:
		print("No localStorage data found.")
		return
	
	for origin, keys in storage_data.items():
		# Apply origin filter if specified
		if filter_origin and filter_origin.lower() not in origin.lower():
			continue
		
		print(f"\n{'='*60}")
		print(f"Origin: {origin}")
		print(f"{'='*60}")
		
		displayed_any = False
		for key, value in keys.items():
			# Apply key filter if specified
			if filter_key and filter_key.lower() not in key.lower():
				continue
			
			displayed_any = True
			print(f"\nKey: {key}")
			
			# Format the value for display
			if isinstance(value, (dict, list)):
				print(f"Value (JSON):\n{json.dumps(value, indent=2)}")
			else:
				value_str = str(value)
				if len(value_str) > 200:
					print(f"Value (truncated): {value_str[:200]}...")
				else:
					print(f"Value: {value_str}")
		
		if not displayed_any and filter_key:
			print(f"  (No keys matching '{filter_key}')")


def export_to_json(storage_data, output_file):
	"""Export localStorage data to JSON file."""
	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(storage_data, f, indent=2, ensure_ascii=False)
	print(f"Data exported to {output_file}")


def main():
	parser = argparse.ArgumentParser(
		description="Read localStorage data from Firefox profiles"
	)
	parser.add_argument(
		"--profile", "-p",
		help="Path to Firefox profile directory (default: search current directory)",
		default="."
	)
	parser.add_argument(
		"--origin", "-o",
		help="Filter results by origin (partial match)"
	)
	parser.add_argument(
		"--key", "-k",
		help="Filter results by key name (partial match)"
	)
	parser.add_argument(
		"--export", "-e",
		help="Export data to JSON file"
	)
	parser.add_argument(
		"--list-origins", "-l",
		action="store_true",
		help="Only list origins without showing data"
	)
	
	args = parser.parse_args()
	
	# Find Firefox profiles
	profiles = find_firefox_profiles(args.profile)
	
	if not profiles:
		print(f"No Firefox profiles found in {args.profile}")
		print("\nMake sure you're in a directory containing a Firefox profile,")
		print("or specify the profile path with --profile")
		sys.exit(1)
	
	# Use the first profile found
	profile_path = profiles[0]
	print(f"Using Firefox profile: {profile_path}")
	
	if len(profiles) > 1:
		print(f"Note: Found {len(profiles)} profiles, using the first one.")
		print("Other profiles found:")
		for p in profiles[1:]:
			print(f"  - {p}")
	
	# Read localStorage data
	storage_data = read_localstorage(profile_path)
	
	if storage_data is None:
		sys.exit(1)
	
	# List origins only
	if args.list_origins:
		print("\nOrigins with localStorage data:")
		for origin in sorted(storage_data.keys()):
			item_count = len(storage_data[origin])
			print(f"  {origin} ({item_count} items)")
		return
	
	# Export to JSON if requested
	if args.export:
		export_to_json(storage_data, args.export)
		return
	
	# Display the data
	display_storage_data(storage_data, args.origin, args.key)
	
	# Summary
	total_origins = len(storage_data)
	total_items = sum(len(items) for items in storage_data.values())
	print(f"\n{'='*60}")
	print(f"Total: {total_origins} origins, {total_items} localStorage items")


if __name__ == "__main__":
	main()