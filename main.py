#!/usr/bin/python3
import csv
import os
import shutil
import sys

with open("unwanted_dirs.csv", newline='') as f:
    reader = csv.reader(f)
    UNWANTED_DIRS = list(reader)[0]

with open("user_dirs.csv", newline='') as f:
    reader = csv.reader(f)
    UNWANTED_DIRS.extend(list(reader)[0])


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

    return total_size


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

    print("Estimated total removed size: %d MB" % (calculate_size(cdirs) / 1000 / 1000))

    user_in = input("Are you sure you want to remove ALL cache? (yes/no) ")

    if user_in.lower() == "yes":
        remove_cache(cdirs)
        print("Done.")
    else:
        print("ok")
