#!/usr/bin/env python3

# sudo apt install jpegoptim imagemagick-6.q16

import os
import shutil
from pathlib import Path
import json
import fire
import exifread
import shlex
import subprocess


extensions = ['.jpg', '.jpeg', '.tiff', '.png', '.heic', '.heif']


def geo_and_bearing_exif(filepath):
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

        bearing = None
        latitude = tags.get('GPS GPSLatitude')
        longitude = tags.get('GPS GPSLongitude')

        # Check bearing data (any one of the possible keys)
        bearing_keys = ['GPS GPSImgDirection', 'GPS GPSTrack', 'GPS GPSDestBearing']
        has_bearing = any(key in tags for key in bearing_keys)
        if has_bearing:
            bearing = tags.get(bearing_keys[0])

        altitude = tags.get('GPS GPSAltitude')

        if latitude and longitude and bearing:
            return latitude, longitude, bearing, altitude
        else:
            return False
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


    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    for root, dirs, files in os.walk(source_dir):
        for file in files:

            source_filepath = Path(os.path.join(root, file))
            if source_filepath.is_relative_to(dest_dir):
                continue

            if is_pic(file):

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
                if geo_and_bearing_exif(source_filepath) != False:
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

def is_pic(file):
    """check if the file is a picture"""
    file_lower = file.lower()
    return any(file_lower.endswith(ext) for ext in extensions)

def compile_json_database(directory):
    """iterate all files and create a json file with the exif data"""

    database = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if is_pic(file):
                filepath = os.path.join(root, file)
                tags = geo_and_bearing_exif(filepath)
                if tags:
                    latitude, longitude, bearing, altitude = tags
                    database.append({
                        'file': file,
                        'latitude': str(latitude),
                        'longitude': str(longitude),
                        'bearing': str(bearing),
                        'altitude': str(altitude)
                    })
                else:
                    print(f"Skipping non-geo {file}")
            else:
                print(f"Skipping non-pic {file}")
    json_file = os.path.join(directory, 'files.json')
    with open(json_file, 'w') as f:
        json.dump(database, f, indent=4)


class Geo:
    @staticmethod
    def collect(source_directory = "/d/sync", destination_directory = "/d/sync/jj/geo/pics"):

        copy_photos_with_bearing_and_gps(source_directory, destination_directory)
        os.system('fdupes -S -r --delete --noprompt ' + destination_directory)
        compile_json_database(destination_directory)


    @staticmethod
    def optimize(directory):
        f = open(directory + '/files.json')
        files = json.load(f)
        f.close()

        for file in files:
            file['sizes'] = {}
            input_file_path = directory + '/' + file['file']

            print('file:', file['file'])
            # get the width of the image
            cmd = ['identify', '-format', '%w', input_file_path]
            print('cmd:', shlex.join(cmd))
            width = int(subprocess.check_output(cmd).decode('utf-8'))
            print('width:', width)

            for size in ['full', 320, 640, 1024, 1600, 2048, 2560, 3072]:

                size_path = str(size) + '/' + file['file']
                output_file_path = directory + '/' + size_path
                os.makedirs(directory + '/' + str(size), exist_ok=True)
                shutil.copy2(input_file_path, output_file_path)

                if size == 'full':
                    pass
                else:
                    if size > width:
                        break
                    else:
                        cmd = ['mogrify', '-resize', str(size), output_file_path]
                        print('cmd:', shlex.join(cmd))
                        subprocess.run(cmd)

                cmd = ['jpegoptim', '--all-progressive', '--overwrite', output_file_path]
                print('cmd:', shlex.join(cmd))
                subprocess.run(cmd)

                file['sizes'][size] = size_path

        f = open(directory + '/files.json', 'w')
        json.dump(files, f, indent=4)
        f.close()



if __name__ == "__main__":
    fire.Fire(Geo)

