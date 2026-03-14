#!/usr/bin/env python3
"""
Diagnostic tool to find and examine all Firefox storage databases in a profile.
"""

import sqlite3
import os
import sys
from pathlib import Path
import json


def check_database(db_path):
	"""Check a SQLite database for tables and data."""
	print(f"\n{'='*60}")
	print(f"Database: {db_path.name}")
	print(f"Path: {db_path}")
	print(f"Size: {db_path.stat().st_size:,} bytes")
	
	try:
		conn = sqlite3.connect(str(db_path))
		cursor = conn.cursor()
		
		# Get all tables
		cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
		tables = cursor.fetchall()
		
		if not tables:
			print("  No tables found")
			conn.close()
			return
		
		print(f"  Tables found: {len(tables)}")
		
		for table in tables:
			table_name = table[0]
			
			# Get row count
			try:
				cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
				count = cursor.fetchone()[0]
				
				# Get column info
				cursor.execute(f"PRAGMA table_info({table_name})")
				columns = cursor.fetchall()
				col_names = [c[1] for c in columns]
				
				print(f"\n  Table: {table_name}")
				print(f"    Rows: {count}")
				print(f"    Columns: {', '.join(col_names)}")
				
				# If it looks like a storage table, show sample data
				if count > 0 and any(keyword in table_name.lower() for keyword in ['storage', 'store', 'local', 'session']):
					cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
					samples = cursor.fetchall()
					print(f"    Sample data:")
					for i, row in enumerate(samples, 1):
						# Truncate long values
						row_display = []
						for val in row:
							val_str = str(val) if val else "NULL"
							if len(val_str) > 50:
								val_str = val_str[:50] + "..."
							row_display.append(val_str)
						print(f"      Row {i}: {row_display}")
						
			except sqlite3.Error as e:
				print(f"    Error reading table: {e}")
		
		conn.close()
		
	except sqlite3.Error as e:
		print(f"  Error opening database: {e}")


def find_storage_files(profile_path="."):
	"""Find all potential storage files in Firefox profile."""
	profile = Path(profile_path)
	
	print(f"Scanning Firefox profile: {profile.absolute()}")
	print("="*60)
	
	# Check for common Firefox storage databases
	storage_files = {
		"webappsstore.sqlite": "localStorage",
		"storage.sqlite": "IndexedDB metadata",
		"cookies.sqlite": "Cookies",
		"places.sqlite": "History and bookmarks",
		"formhistory.sqlite": "Form data",
		"permissions.sqlite": "Site permissions",
		"content-prefs.sqlite": "Site preferences",
		"protections.sqlite": "Tracking protection",
	}
	
	found_any = False
	
	# Check each known storage file
	for filename, description in storage_files.items():
		file_path = profile / filename
		if file_path.exists():
			found_any = True
			print(f"\n✓ Found: {filename} ({description})")
			check_database(file_path)
		else:
			print(f"\n✗ Not found: {filename}")
	
	# Check storage/default directory for IndexedDB
	storage_dir = profile / "storage" / "default"
	if storage_dir.exists():
		print(f"\n{'='*60}")
		print(f"IndexedDB Storage Directory: {storage_dir}")
		print("="*60)
		
		# List all origin directories
		origins = list(storage_dir.iterdir())
		if origins:
			print(f"Found {len(origins)} origin directories:")
			for origin_dir in origins[:10]:  # Show first 10
				if origin_dir.is_dir():
					print(f"  - {origin_dir.name}")
					
					# Check for .sqlite files in each origin
					idb_files = list(origin_dir.glob("*.sqlite"))
					if idb_files:
						print(f"    IndexedDB files: {[f.name for f in idb_files]}")
						for idb_file in idb_files[:2]:  # Check first 2
							check_database(idb_file)
			
			if len(origins) > 10:
				print(f"  ... and {len(origins) - 10} more")
	
	# Check for localStorage in storage/default directories
	print(f"\n{'='*60}")
	print("Checking for localStorage in storage/default/*/ls/")
	print("="*60)
	
	ls_found = False
	if storage_dir.exists():
		for origin_dir in storage_dir.iterdir():
			ls_dir = origin_dir / "ls"
			if ls_dir.exists():
				ls_found = True
				print(f"\nFound localStorage directory: {origin_dir.name}/ls/")
				
				# Check for data.sqlite
				data_sqlite = ls_dir / "data.sqlite"
				if data_sqlite.exists():
					print(f"  Found: data.sqlite")
					check_database(data_sqlite)
				
				# List any other files
				other_files = list(ls_dir.iterdir())
				if other_files:
					print(f"  Other files: {[f.name for f in other_files]}")
	
	if not ls_found:
		print("No localStorage directories found in storage/default/*/ls/")
	
	# Look for any other .sqlite files
	print(f"\n{'='*60}")
	print("Other SQLite databases in profile:")
	print("="*60)
	
	all_sqlite = list(profile.glob("*.sqlite"))
	other_sqlite = [f for f in all_sqlite if f.name not in storage_files.keys()]
	
	if other_sqlite:
		for db_file in other_sqlite:
			print(f"\nFound: {db_file.name}")
			check_database(db_file)
	else:
		print("No other SQLite databases found")
	
	if not found_any and not ls_found:
		print("\n" + "="*60)
		print("WARNING: No storage databases found!")
		print("This might not be a Firefox profile directory.")
		print("Firefox profiles are typically located at:")
		print("  Linux: ~/.mozilla/firefox/[profile-name]/")
		print("  macOS: ~/Library/Application Support/Firefox/Profiles/[profile-name]/")
		print("  Windows: %APPDATA%\\Mozilla\\Firefox\\Profiles\\[profile-name]\\")


def main():
	if len(sys.argv) > 1:
		profile_path = sys.argv[1]
	else:
		profile_path = "."
	
	find_storage_files(profile_path)


if __name__ == "__main__":
	main()