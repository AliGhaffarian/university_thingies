import struct
import zlib
import jpeglib
import argparse

EXPECTED_DCT_SIZE = 8
EXPECTED_QT_SIZE = 2

conf = {
    "input_path" : None,
    "output_path" : None,
    "channel" : "cb",
    "channel_obj" : None,
    "freq-positions" : None
}

img = None
valid_channels = ["y", "cr", "cb"]



import logging
import logging.config
import colorlog
import sys


log_format = '%(asctime)s [%(levelname)s] %(name)s [%(funcName)s]: %(message)s'
log_colors = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
        }


console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s' + log_format,
        log_colors = log_colors
        )
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(console_formatter)

logger.addHandler(stdout_handler)

def checksum32(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF

def split_blocks(data: bytes):
    blocks = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        if len(chunk) < 16:
            chunk = chunk.ljust(16, b'\x00')
        blocks.append(chunk)
    return blocks

def build_payload(raw: bytes):
    blocks = split_blocks(raw)

    serialized_blocks = b""
    for block in blocks:
        csum = checksum32(block)
        serialized_blocks += block + struct.pack("<I", csum)

    data_len = len(raw)
    checksum_input = struct.pack("<I", data_len) + serialized_blocks 
    full_checksum = checksum32(checksum_input)
    logger.debug(f"{checksum_input=}")

    header = struct.pack("<II", data_len, full_checksum)

    final_payload = header + serialized_blocks
    return final_payload


def payload_to_bits(payload: bytes):
    for byte in payload:
        for i in range(8):
            yield (byte >> (7 - i)) & 1


high_freq_positions = [60, 61, 62, 63]
def encode_bits_into_dct(dct_block, qtables, bitstream):
    """
    dct: list of 8x8 blocks for Cb channel
    qtables: list of quantization tables (8x8)
    bitstream: iterator of bits
    """

    for pos in conf["freq-positions"]:
        try:
            bit = next(bitstream)
        except StopIteration:
            return  False 

        debug_dct_old_value = dct_block[pos // 8][pos % 8]
        if bit == 1:
            dct_block[pos // 8][pos % 8] = 1 
        else:
            dct_block[pos // 8][pos % 8] = 0
        logger.debug(f"[{pos}]: {debug_dct_old_value} --> {1 if bit else 0}")
    return True


def verify_image(img):
    """
    verifies that the image contains:
        - 8*8 dct blocks
        - 2 quantization tables, and assumes the second one is both for both Cr and Cb
    """
    is_valid = True
    single_dct_entry = img.Cb[0][0]
    if(len(single_dct_entry) != EXPECTED_DCT_SIZE):
        logger.error(f"invalid length of dct collums. got {len(single_dct_entry)}, expected {EXPECTED_DCT_SIZE}")
        is_valid = False
    if(len(single_dct_entry[0]) != EXPECTED_DCT_SIZE):
        logger.error(f"invalid length of dct rows. got {len(single_dct_entry[0])}, expected {EXPECTED_DCT_SIZE}")
        is_valid = False
    if(len(img.qt) != EXPECTED_QT_SIZE):
        logger.error(f"invalid qtables, got {len(img.qt)}, expected {EXPECTED_QT_SIZE}")
        is_valid = False
    return is_valid 

def compute_image_capacity(image_resolution):
    return

def stego_encode(data: bytes):
    global img
    payload = build_payload(data)
    bitstream = payload_to_bits(payload)
    logger.debug("payload:")
    logger.debug(payload)
    logger.debug(len(payload))
    input()


    dct = conf["channel_obj"]
    qtables = img.qt

    do_continue = True
    encode_times = 0
    for i,row in enumerate(dct):
        for j,block in enumerate(row):
            logger.debug(f"selecting block[{i}][{j}]")
            do_continue = encode_bits_into_dct(block, qtables, bitstream)
            if not do_continue:
                bitstream = payload_to_bits(payload)
                do_continue = True
                logger.info(f"reseting the encoding in row {i} block {j}")
                encode_times += 1
                break

    logger.info(f"encoded {encode_times} times")
    img.write_dct(conf["output_path"])
    print("Stego JPEG written:", conf["output_path"])


def handle_args():
    global args
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input_path", help="input file", required=True)
    ap.add_argument("-o", "--output_path", help="output file", required=True)
    ap.add_argument("-m", "--message", help="message to be encoded", required=True)
    ap.add_argument("-c", "--channel", help="channel to encote to", default="cb")
    ap.add_argument("-f", "--freqs", help="freqs to encode to, seperated by commas", default = high_freq_positions)

    args = ap.parse_args()

    conf["input_path"] = args.input_path
    conf["output_path"] = args.output_path
    conf["channel"] = args.channel
    conf["freq-positions"] = [ int(x) for x in args.freqs.split(',') ]

def open_and_verify_img():
    global img
    img = jpeglib.read_dct(conf["input_path"])
    if verify_image(img) == False:
        logger.error("invalid image")
        return

def place_channel_into_conf():
    global img
    if conf["channel"] is None:
        return

    if conf["channel"] not in valid_channels:
        raise Exception("invalid channel")

    if conf["channel"] == "cr":
        conf["channel_obj"] = img.Cr
    if conf["channel"] == "cb":
        conf["channel_obj"] = img.Cb
    if conf["channel"] == "y":
        conf["channel_obj"] = img.Y

if __name__ == "__main__":
    global args
    handle_args()
    open_and_verify_img()
    place_channel_into_conf()
    stego_encode(args.message.encode())

