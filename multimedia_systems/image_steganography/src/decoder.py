import struct
import zlib
import logging
import logging.config
import colorlog
import sys
import math

import jpeglib

args = None
dct = None
conf = {
    "freq-positions" : None
}

EXPECTED_DCT_SIZE = 8
EXPECTED_QT_SIZE = 2

log_format = '%(asctime)s [%(levelname)s] %(name)s [%(funcName)s]: %(message)s'
log_colors = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}
console_formatter = colorlog.ColoredFormatter('%(log_color)s' + log_format, log_colors=log_colors)
logger = logging.getLogger("stego_decoder")
logger.setLevel(logging.DEBUG)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(console_formatter)
logger.addHandler(stdout_handler)

def checksum32(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF


def verify_image(img):
    """
    Verify structure is what encoder expects:
      - Cb DCT blocks are 8x8
      - 2 quantization tables
    """
    is_valid = True
    try:
        single_dct_entry = img.Cb[0][0]
    except Exception as e:
        logger.error("Image structure unexpected or missing Cb channel: %s", e)
        return False

    if len(single_dct_entry) != EXPECTED_DCT_SIZE:
        logger.error(f"invalid length of dct columns. got {len(single_dct_entry)}, expected {EXPECTED_DCT_SIZE}")
        is_valid = False
    if len(single_dct_entry[0]) != EXPECTED_DCT_SIZE:
        logger.error(f"invalid length of dct rows. got {len(single_dct_entry[0])}, expected {EXPECTED_DCT_SIZE}")
        is_valid = False
    if len(img.qt) != EXPECTED_QT_SIZE:
        logger.error(f"invalid qtables, got {len(img.qt)}, expected {EXPECTED_QT_SIZE}")
        is_valid = False
    return is_valid

valid_channels = ["y", "cr", "cb"]
def resolve_channel(img):
    global dct
    if args.channel is None:
        raise Exception("reached unreachable code")

    if args.channel not in valid_channels:
        raise Exception("invalid channel")

    if args.channel == "cr":
        dct = img.Cr
    if args.channel == "cb":
        dct = img.Cb
    if args.channel == "y":
        dct = img.Y


high_freq_positions = [60, 61, 62, 63]
def bits_from_dct(img):
    """
    Generator that yields embedded bits in the same order used by the encoder.
    For each Cb 8x8 block, reads positions [60,61,62,63] (zig-zag end).
    Non-zero -> 1, zero -> 0 (matches encoder: set to 0 or 1).
    """
    global dct


    for i, row in enumerate(dct):
        for j, block in enumerate(row):
            for pos in conf["freq-positions"]:
                val = block[pos // 8][pos % 8]
                yield 1 if val != 0 else 0


def read_n_bytes_from_bitgen(bitgen, n_bytes):
    """
    Read exactly n_bytes from bit generator. Assemble bits MSB-first to bytes.
    Raises ValueError if not enough bits available.
    """
    out = bytearray()
    try:
        for _ in range(n_bytes):
            b = 0
            for bit_index in range(8):
                bit = next(bitgen)
                b = (b << 1) | bit & 1
            out.append(b)
    except StopIteration:
        raise ValueError("Ran out of embedded bits before reading required bytes")
    return bytes(out)


def stego_decode(input_jpeg_path: str, output_path: str = None) -> bytes:
    """
    Decode payload from input_jpeg_path and optionally write the recovered data to output_path.
    Returns the recovered raw data (trimmed to original data length).
    """
    img = jpeglib.read_dct(input_jpeg_path)
    if not verify_image(img):
        raise RuntimeError("Invalid/unsupported JPEG structure for this decoder")

    resolve_channel(img)
    bitgen = bits_from_dct(img)

    header_bytes = read_n_bytes_from_bitgen(bitgen, 8)
    data_len, embedded_full_checksum = struct.unpack("<II", header_bytes)
    logger.info(f"decoded header: data_len={data_len}, embedded_full_checksum=0x{embedded_full_checksum:08x}")

    num_blocks = (data_len + 15) // 16
    serialized_blocks_size = num_blocks * (16 + 4)  
    expected_total_payload_size = 8 + serialized_blocks_size

    logger.debug(f"expecting {num_blocks} blocks; serialized blocks size = {serialized_blocks_size} bytes; total payload = {expected_total_payload_size} bytes")

    remaining_bytes = serialized_blocks_size
    serialized_blocks = read_n_bytes_from_bitgen(bitgen, remaining_bytes)

    checksum_input = struct.pack("<I", data_len) + serialized_blocks
    computed_full_checksum = checksum32(checksum_input)
    if computed_full_checksum != embedded_full_checksum:
        logger.error(f"global checksum mismatch: embedded=0x{embedded_full_checksum:08x} computed=0x{computed_full_checksum:08x}")
    else:
        logger.info("global checksum OK")

    recovered_raw = bytearray()
    problems = 0
    for k in range(0, len(serialized_blocks), 20):
        block_data = serialized_blocks[k:k+16]
        block_csum_bytes = serialized_blocks[k+16:k+20]
        if len(block_data) < 16 or len(block_csum_bytes) < 4:
            logger.error("unexpected truncated serialized block")
            problems += 1
            break
        (block_csum,) = struct.unpack("<I", block_csum_bytes)
        computed_block_csum = checksum32(block_data)
        if block_csum != computed_block_csum:
            logger.error(f"block {k//20}: checksum mismatch embedded=0x{block_csum:08x} computed=0x{computed_block_csum:08x}")
            problems += 1
        else:
            logger.debug(f"block {k//20}: checksum OK")
        recovered_raw.extend(block_data)

    recovered_raw = bytes(recovered_raw[:data_len])
    logger.info(f"Recovered {len(recovered_raw)} bytes (original length announced: {data_len}). problems={problems}")

    if output_path:
        with open(output_path, "wb") as f:
            f.write(recovered_raw)
        logger.info(f"Wrote recovered payload to {output_path}")

    return recovered_raw


def handle_args():
    global args
    import argparse
    ap = argparse.ArgumentParser(description="Decode payload previously embedded by the encoder into JPEG DCT (Cb high-freq positions).")
    ap.add_argument("-i", "--input_jpeg", help="stego JPEG file (input)")
    ap.add_argument("-o", "--output", help="where to write recovered payload (default: extracted.bin)", default="extracted.bin")
    ap.add_argument("-c", "--channel", help="channel to decode from", default="cb")
    ap.add_argument("-f", "--freqs", help="freqs to encode to, seperated by commas", default = high_freq_positions)

    args = ap.parse_args()

    conf["freq-positions"] = [ int(x) for x in args.freqs.split(',') ]


if __name__ == "__main__":
    handle_args()
    try:
        data = stego_decode(args.input_jpeg, args.output)
        logger.info("Decoding finished.")
    except Exception as e:
        logger.exception("Decoding failed: %s", e)
        sys.exit(1)

