#!/usr/bin/env python3
"""
Read localStorage data from modern Firefox profiles.
Modern Firefox stores localStorage in storage/default/*/ls/data.sqlite files.
"""

import sqlite3
import json
import os
import sys
from pathlib import Path
import argparse
from urllib.parse import unquote


def decode_origin(origin_dir_name):
	"""
	Decode Firefox origin directory name to readable URL.
	e.g., "https+++www.example.com" -> "https://www.example.com"
	e.g., "https+++apps.autodesk.com" -> "https://apps.autodesk.com"
	"""
	# Simply replace +++ with ://
	# The domain part doesn't need + replaced with . because Firefox doesn't encode dots as +
	origin = origin_dir_name.replace("+++", "://")
	
	# Unescape any URL-encoded characters
	origin = unquote(origin)
	
	return origin


def read_localstorage_file(data_sqlite_path, origin_name):
	"""Read localStorage data from a single data.sqlite file."""
	storage_data = {}
	
	try:
		conn = sqlite3.connect(str(data_sqlite_path))
		cursor = conn.cursor()
		
		# Check if data table exists and has content
		cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='data'")
		if cursor.fetchone()[0] == 0:
			conn.close()
			return storage_data
		
		# Get the data
		cursor.execute("""
			SELECT key, value, utf16_length, compression_type 
			FROM data
			ORDER BY key
		""")
		
		rows = cursor.fetchall()
		
		for row in rows:
			key = row[0]
			value = row[1]
			utf16_length = row[2] if len(row) > 2 else None
			compression_type = row[3] if len(row) > 3 else None
			
			# Handle different value types
			if value is None:
				storage_data[key] = None
			elif isinstance(value, bytes):
				# Check if it's compressed (compression_type 1 means snappy compression)
				if compression_type == 1:
					# Firefox uses snappy compression for large values
					# For now, just show it's compressed
					hex_preview = value.hex()
					# Check if it looks like UTF-16 (starts with specific bytes)
					if hex_preview.startswith('f8'):
						storage_data[key] = f"<compressed data, {len(value)} bytes>"
					else:
						# Try to decode as-is
						try:
							value_str = value.decode('utf-8')
							try:
								storage_data[key] = json.loads(value_str)
							except json.JSONDecodeError:
								storage_data[key] = value_str
						except UnicodeDecodeError:
							storage_data[key] = f"<binary: {value.hex()[:100]}...>"
				else:
					# Not compressed, try to decode
					try:
						value_str = value.decode('utf-8')
						# Try to parse as JSON
						try:
							storage_data[key] = json.loads(value_str)
						except json.JSONDecodeError:
							storage_data[key] = value_str
					except UnicodeDecodeError:
						# If can't decode, store as hex representation
						storage_data[key] = f"<binary: {value.hex()[:100]}...>"
			else:
				# Try to parse as JSON
				try:
					storage_data[key] = json.loads(value)
				except (json.JSONDecodeError, TypeError):
					storage_data[key] = value
		
		conn.close()
		
	except sqlite3.Error as e:
		print(f"SQLite error reading {data_sqlite_path}: {e}")
	
	return storage_data


def find_localstorage_data(profile_path="."):
	"""Find and read all localStorage data from a Firefox profile."""
	profile = Path(profile_path)
	storage_dir = profile / "storage" / "default"
	
	all_storage_data = {}
	
	if not storage_dir.exists():
		# Fall back to old webappsstore.sqlite if storage/default doesn't exist
		webapp_store = profile / "webappsstore.sqlite"
		if webapp_store.exists():
			print("Found legacy webappsstore.sqlite")
			# Would need to implement legacy reading here
		else:
			print(f"No storage/default directory found in {profile}")
		return all_storage_data
	
	# Iterate through all origin directories
	for origin_dir in storage_dir.iterdir():
		if not origin_dir.is_dir():
			continue
		
		ls_dir = origin_dir / "ls"
		if not ls_dir.exists():
			continue
		
		data_sqlite = ls_dir / "data.sqlite"
		if not data_sqlite.exists():
			continue
		
		# Decode the origin name
		origin = decode_origin(origin_dir.name)
		
		# Read the localStorage data
		storage_data = read_localstorage_file(data_sqlite, origin)
		
		if storage_data:
			all_storage_data[origin] = storage_data
	
	return all_storage_data


def display_storage_data(all_storage_data, filter_origin=None, filter_key=None, verbose=False):
	"""Display localStorage data with optional filtering."""
	if not all_storage_data:
		print("No localStorage data found.")
		return
	
	total_items = 0
	
	for origin, storage_data in sorted(all_storage_data.items()):
		# Apply origin filter if specified
		if filter_origin and filter_origin.lower() not in origin.lower():
			continue
		
		if not storage_data:
			continue
		
		print(f"\n{'='*60}")
		print(f"Origin: {origin}")
		print(f"Items: {len(storage_data)}")
		print(f"{'='*60}")
		
		displayed_any = False
		for key, value in sorted(storage_data.items()):
			# Apply key filter if specified
			if filter_key and filter_key.lower() not in key.lower():
				continue
			
			displayed_any = True
			total_items += 1
			
			print(f"\nKey: {key}")
			
			# Format the value for display
			if isinstance(value, (dict, list)):
				print(f"Value (JSON):\n{json.dumps(value, indent=2)}")
			else:
				value_str = str(value) if value is not None else "null"
				print(f"Value: {value_str}")
		
		if not displayed_any and filter_key:
			print(f"  (No keys matching '{filter_key}')")
	
	print(f"\n{'='*60}")
	print(f"Total: {len(all_storage_data)} origins, {total_items} items")


def export_to_json(all_storage_data, output_file):
	"""Export localStorage data to JSON file."""
	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(all_storage_data, f, indent=2, ensure_ascii=False)
	print(f"Data exported to {output_file}")


def main():
	parser = argparse.ArgumentParser(
		description="Read localStorage data from modern Firefox profiles"
	)
	parser.add_argument(
		"--profile", "-p",
		help="Path to Firefox profile directory (default: current directory)",
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
	parser.add_argument(
		"--verbose", "-v",
		action="store_true",
		help="Show full values instead of truncated"
	)
	
	args = parser.parse_args()
	
	profile_path = Path(args.profile)
	
	if not profile_path.exists():
		print(f"Error: Profile path does not exist: {profile_path}")
		sys.exit(1)
	
	print(f"Reading Firefox profile: {profile_path.absolute()}")
	
	# Read all localStorage data
	all_storage_data = find_localstorage_data(profile_path)
	
	if not all_storage_data:
		print("\nNo localStorage data found in this profile.")
		print("Make sure you're in a Firefox profile directory that contains")
		print("a 'storage/default' subdirectory.")
		sys.exit(1)
	
	# List origins only
	if args.list_origins:
		print("\nOrigins with localStorage data:")
		for origin in sorted(all_storage_data.keys()):
			item_count = len(all_storage_data[origin])
			print(f"  {origin} ({item_count} items)")
		return
	
	# Export to JSON if requested
	if args.export:
		export_to_json(all_storage_data, args.export)
		return
	
	# Display the data
	display_storage_data(all_storage_data, args.origin, args.key, args.verbose)


if __name__ == "__main__":
	main()