import argparse
import os
import subprocess
import time

import exifread
from datetime import timedelta, datetime
from tqdm import tqdm

IMAGE_TYPES = [".jpg", ".png", ".gif", ".jpeg"]


def extract_time(root_path, files):
    file_and_date = []
    for file in tqdm(files):
        file_path = os.path.abspath(os.path.join(root_path, file))
        with open(file_path, 'rb') as image_file:
            data = exifread.process_file(image_file, details=False)
            try:
                date = time.strptime(data["Image DateTime"].values, "%Y:%m:%d %H:%M:%S")
            except KeyError:
                args = [
                    "identify",
                    "-format '%[EXIF:DateTime]'",
                    "\"{}\"".format(file_path)
                ]
                try:
                    date = subprocess.check_output(args)
                except subprocess.CalledProcessError:
                    date = time.localtime()


            date = datetime.fromtimestamp(time.mktime(date))

            if file.startswith("IMGP"):
                # adjust date
                date = date + timedelta(hours=7)
        file_and_date.append((file_path, date))
    return file_and_date


def traverse_directory_tree(root_path):
    for dirpath, _, files in os.walk(root_path):
        image_files = filter(lambda x: os.path.splitext(x)[-1].lower() in IMAGE_TYPES, files)
        for image_file in image_files:
            yield os.path.join(dirpath, image_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="tool that walks direcgtories, sorts all images according by date and creates a list file")
    parser.add_argument("dir", help="root directory with pictures")
    parser.add_argument("dest_file", help="path to destination image list, that can be used with viewer")

    args = parser.parse_args()

    image_files = sorted(extract_time(args.dir, traverse_directory_tree(args.dir)), key=lambda x: x[1])

    with open(args.dest_file, "w") as destination:
        for file, _ in tqdm(image_files):
            print(file, file=destination)
