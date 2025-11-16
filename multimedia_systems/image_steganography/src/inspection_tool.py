import jpeglib
import sys
import argparse
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input-jpeg", help="stego JPEG file (input)", required = True)
ap.add_argument("-d", "--diff-file", help="jpeg file to compare", default = None)
ap.add_argument("-e", "--check-equal", help="show which elements are not equal", default=False, action='store_true')
ap.add_argument("-c", "--channel", help="channel to show", type=str, default="cb")
args = ap.parse_args()

conf = {
    "diff_img" : None,
    "diff_path" : None,
    "input_channel" : None,
    "diff_channel" : None,
}

if args.check_equal and not args.diff_file:
    raise Exception("invalid args")

def check_diffable(one, other):
    return one.Cb.shape == other.Cb.shape and \
        one.Cr.shape == other.Cr.shape and \
        one.Y.shape == other.Y.shape and \
        one.qt.shape == other.qt.shape
def print_jpeg_stats(img):
    print(f"{img.Y.shape=}")
    print(f"{img.Cr.shape=}")
    print(f"{img.Cb.shape=}")
    print(f"{img.qt.shape=}")

valid_channels = ["y", "cr", "cb"]
def resolve_channel(img):
    if args.channel is None:
        raise Exception("reached unreachable code")

    if args.channel not in valid_channels:
        raise Exception("invalid channel")

    if args.channel == "cr":
        return img.Cr
    if args.channel == "cb":
        return img.Cb
    if args.channel == "y":
        return img.Y

if len(sys.argv) < 2:
    print("usage: inputfile [--do-diff diff_path] [--check_eq]")
    exit(1)

img = jpeglib.read_dct(args.input_jpeg)
if args.diff_file:
    conf["diff_img"] = jpeglib.read_dct(args.diff_file)
    if not check_diffable(img, conf["diff_img"]):
        print("warning: images are not compatible")
        print(f"{img.Cb.shape == conf["diff_img"].Cb.shape=}")
        print(f"{img.Cr.shape == conf["diff_img"].Cr.shape=}")
        print(f"{img.Y.shape == conf["diff_img"].Y.shape=}")
        print(f"{img.qt.shape == conf["diff_img"].qt.shape=}")
        input("enter to continue...")

conf["input_channel"] = resolve_channel(img)
if conf["diff_img"]:
    conf["diff_channel"] = resolve_channel(conf["diff_img"])

print("input file stats:")
print(print_jpeg_stats(img))
if args.diff_file:
    print("diff file stats:")
    print_jpeg_stats(conf["diff_img"])

def print_dct(x, y):
    print(f"img.{args.channel}[{y}][{x}]")
    if(args.diff_file):
        print(args.input_jpeg)

    print(conf["input_channel"][y][x])

    if(args.diff_file):
        print(args.diff_file)
        print(conf["diff_channel"][y][x])

    if args.check_equal:
        print(f"{conf["input_channel"][y][x] == conf["diff_channel"][y][x]}")

if conf["diff_img"]:
    print(args.input_jpeg)
print(
    img.qt
)
if conf["diff_img"]:
    print(args.diff_file)
    print(conf["diff_img"].qt)

if args.check_equal:
    print(f"{img.qt == conf["diff_img"].qt}")

x = 0
y = 0

def next_dct_entry():
        global x, y
        x += 1
        if x == len(conf["input_channel"][0]):
            x = 0
            y += 1

def continue_until_not_equal():
    next_dct_entry()
    while(np.all(conf["input_channel"][y][x] == conf["diff_channel"][y][x])):
        next_dct_entry()

while True:
    print_dct(x, y)
    cmd = input().strip()

    if len(cmd) == 0:
        next_dct_entry()
        continue

    if(cmd == "u"):
        continue_until_not_equal()
        continue

    try:
        y, x = [ int(elem) for elem in cmd.split() ]
        continue
    except:
        pass

