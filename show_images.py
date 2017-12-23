import argparse
import tkinter

import sys

import os

import PIL.ExifTags
from PIL import Image, ImageTk


class ProgressWindow:

    def __init__(self, root, image_list):
        self.frame = tkinter.Frame(root)
        self.frame.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        pad = 3
        root.geometry("{0}x{1}+0+0".format(
            root.winfo_screenwidth() - pad, root.winfo_screenheight() - pad))

        self.frame.bind("<Key>", self.key_pressed)
        root.bind("<Escape>", lambda e: e.widget.quit())
        self.frame.focus_set()

        self._image = None
        self._sprite = None
        self.canvas = tkinter.Canvas(
            self.frame,
            width=850,
            height=400
        )
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        self.current_image = -1
        with open(image_list) as images:
            self.image_list = [image.strip() for image in images]
        # self.show_next_image()
        self.excluded_images = []
        self.deg = 0

    def key_pressed(self, event):
        if event.keycode == 114:
            self.show_next_image()
        elif event.keycode == 113:
            self.show_last_image()
        elif event.char == 'e':
            self.exclude()
        elif event.char == 'r':
            self.rotate(-90)
        elif event.char == 't':
            self.rotate(90)

    def exclude(self):
        self.excluded_images.append(self.image_list[self.current_image])
        self.show_next_image()

    def rotate(self, angle):
        image_path = self.image_list[self.current_image]
        image = Image.open(image_path)
        self.deg -= angle
        image = image.rotate(self.deg, expand=True, resample=Image.LANCZOS)
        self.image = image

    def show_current_image(self):
        self.deg = 0
        image_path = self.image_list[self.current_image]
        image = Image.open(image_path)
        exif = {
            PIL.ExifTags.TAGS[k]: v
            for k, v in image._getexif().items()
            if k in PIL.ExifTags.TAGS
        }
        orientation = exif.get('Orientation', 1)
        if orientation != 1:
            self.deg -= 90
            image = image.rotate(self.deg, expand=True, resample=Image.LANCZOS)

        self.image = image

    def show_last_image(self):
        self.current_image -= 1
        if self.current_image < 0:
            self.current_image = len(self.image_list) - 1
        self.show_current_image()

    def show_next_image(self):
        self.current_image += 1
        if self.current_image >= len(self.image_list):
            self.current_image = 0
        self.show_current_image()

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        window_width = self.frame.winfo_width()
        window_height = self.frame.winfo_height()
        value.thumbnail((window_width, window_height), Image.LANCZOS)
        image = ImageTk.PhotoImage(value)
        self._image = image
        self._sprite = self.canvas.create_image(window_width // 2, window_height // 2, image=self._image)

    def quit(self, event):
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show your lovely photos presorted in a textfile")
    parser.add_argument("textfile", help='path to file containing all images to show in the correct order')

    args = parser.parse_args()

    root = tkinter.Tk()
    window = ProgressWindow(root, args.textfile)
    root.mainloop()

    # filter images
    with open(args.textfile) as the_file:
        lines = [l.strip() for l in the_file]
        files_to_keep = list(filter(lambda x: x not in window.excluded_images, lines))

    file_path, ext = os.path.splitext(args.textfile)
    new_file_name = "{}_reworked{}".format(file_path, ext)
    with open(new_file_name, "w") as new_file:
        for file_name in files_to_keep:
            print(file_name, file=new_file)
