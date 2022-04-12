#!/usr/bin/python3
import csv
import os
import shutil
import sys

HOME_DIRECTORY = os.path.expanduser('~')

UNWANTED_DIRS = [
    "/cores",
    "/dev",
    "/etc",
    "/opt",
    "/private",
    "/sbin",
    "/System",
    "/tmp",
    "/usr",
    "/var",
    "/Volumes",
    "/.Trashes",
    "/Applications/Safari.app",
    "/Library/Developer"
]

with open("user_dirs.csv", newline='') as f:
    reader = csv.reader(f)
    user_dirs = list(reader)[0]

    for dir in user_dirs:
        if "$HOME" in dir:
            UNWANTED_DIRS.append(dir.replace("$HOME", HOME_DIRECTORY))
        elif "~" in dir:
            UNWANTED_DIRS.append(dir.replace("~", HOME_DIRECTORY))
        else:
            UNWANTED_DIRS.extend(dir)


def scan_dirs(dirname):
    subfolders = []
    for f in os.scandir(dirname):
        if f.is_dir() is True and f.is_symlink() is False and "apple" not in f.path.lower():
            subfolders.append(f.path)

    for dirname in list(subfolders):
        if dirname not in UNWANTED_DIRS and "apple" not in dirname.lower():
            subfolders.extend(scan_dirs(dirname))

    return subfolders


def filter_dir(dir_list):
    cache_dirs = []

    for dir in dir_list:
        if "cache" in dir.lower() and "apple" not in dir.lower():
            cache_dirs.append(dir)

    return cache_dirs


def calculate_size(dir_list):
    total_size = 0

    for dir in dir_list:
        try:
            for f in os.listdir(dir):
                total_size += os.path.getsize(os.path.join(dir, f))
        except:
            pass

    return total_size       # Returns size in bytes

def get_size_with_unit(dir_list):
    size = calculate_size(dir_list)
    unit = "bytes"

    if 1000 < size < 1000**2:
        size = size / 1000
        unit = "kB"
    elif 1000**2 < size < 1000**3:
        size = size / ( 1000**2 )
        unit = "MB"
    else:
        size = size / ( 1000**3 )
        unit = "GB"

    return str(int(size)) + " "  + unit


def remove_cache(dir_list):
    for dir in dir_list:
        if "apple" not in dir.lower():
            shutil.rmtree(dir, ignore_errors=True)


if __name__ == '__main__':
    print("List of ignored directories:")
    for dir in UNWANTED_DIRS:
        print(dir)
    print("To edit this list, modify unwanted_dirs.csv")

    print("\nScanning...")
    cdirs = filter_dir(scan_dirs("/"))
    print("Found %d cache directories." % len(cdirs))

    if "-d" in sys.argv:
        print("\n")
        for dir in cdirs:
            print(dir)

    # print("Estimated total removed size: %d MB" % (calculate_size(cdirs) / 1000 / 1000))
    print("Esitmated total removed size: %s" % get_size_with_unit(cdirs) )

    user_in = input("Are you sure you want to remove ALL cache? (yes/no) ")

    if user_in.lower() == "yes":
        remove_cache(cdirs)
        print("Done.")
    else:
        print("ok")
