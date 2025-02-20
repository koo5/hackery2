#!/usr/bin/env python3

import os
import shutil
from pathlib import Path

import exifread

def has_geo_and_bearing_exif(filepath):
    """
    Check if the image at `filepath` contains both GPS (lat/long)
    and bearing (direction) EXIF data.
    """
    # Possible EXIF keys for bearing info (not all cameras use the same tags):
    # - 'GPS GPSImgDirection'
    # - 'GPS GPSTrack'
    # - 'GPS GPSDestBearing'
    # Some cameras might use different or additional tags,
    # but these are the common ones.

    try:
        with open(filepath, 'rb') as f:
            tags = exifread.process_file(f, details=False)

        # Check GPS data
        has_latitude = 'GPS GPSLatitude' in tags
        has_longitude = 'GPS GPSLongitude' in tags

        # Check bearing data (any one of the possible keys)
        bearing_keys = ['GPS GPSImgDirection', 'GPS GPSTrack', 'GPS GPSDestBearing']
        has_bearing = any(key in tags for key in bearing_keys)

        return has_latitude and has_longitude and has_bearing
    except:
        # If there's an error reading EXIF or opening the file
        return False

def copy_photos_with_bearing_and_gps(source_dir, dest_dir, extensions=None):
    """
    Recursively traverse `source_dir`, detect images with GPS and bearing EXIF data,
    and copy them to `dest_dir`.

    :param source_dir: Source directory to begin recursive search
    :param dest_dir: Destination directory to copy matching images
    :param extensions: List of file extensions to consider as images (e.g. ['.jpg', '.jpeg', '.png'])
                      If None, a default set of image extensions is used.
    """

    if extensions is None:
        # Common photo file extensions
        extensions = ['.jpg', '.jpeg', '.tiff', '.png', '.heic', '.heif']

    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    for root, dirs, files in os.walk(source_dir):
        for file in files:

            source_filepath = Path(os.path.join(root, file))
            if source_filepath.is_relative_to(dest_dir):
                continue

            file_lower = file.lower()
            # Check file extension
            if any(file_lower.endswith(ext) for ext in extensions):

                try:
                    src_size = os.path.getsize(source_filepath)
                except FileNotFoundError:
                    print(f"Skipping unreadable {source_filepath}")
                    continue
                if (src_size < 1000):
                    print(f"Skipping empty {source_filepath}")
                    continue
                if (src_size > 50000000):
                    print(f"Skipping large {source_filepath}")
                    continue

                # Check EXIF for GPS + bearing
                if has_geo_and_bearing_exif(source_filepath):
                    destination_filepath = os.path.join(dest_dir, file)

                    # if the source file is bigger than the destination file, copy it
                    try:
                        if src_size <= os.path.getsize(destination_filepath):
                            print(f"Skipping smaller {source_filepath}")
                            continue
                    except FileNotFoundError:
                        pass

                    print(f"Copying {source_filepath}")
                    shutil.copy2(source_filepath, destination_filepath)

def main():
    # Example usage:
    source_directory = "/d/sync"
    destination_directory = "/d/sync/jj/geo/pics"

    copy_photos_with_bearing_and_gps(source_directory, destination_directory)
    os.system('fdupes -S -r --delete --noprompt ' + destination_directory)

if __name__ == "__main__":
    main()
