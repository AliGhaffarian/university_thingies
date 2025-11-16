from PIL import Image
import jpeglib
import sys

def extract_qtables(jpeg_path):
    """
    Extract quantization tables from a JPEG file.
    Returns a dict like {0: [...64 entries...], 1: [...]}.
    """
    img = Image.open(jpeg_path)
    if not hasattr(img, "quantization") or img.quantization is None:
        raise ValueError("This JPEG does not contain quantization tables.")
    return img.quantization


def jpeg_to_png(jpeg_path, png_path):
    """
    Convert JPEG → PNG.
    """
    img = Image.open(jpeg_path)
    img.save(png_path, "PNG")


def png_to_jpeg_with_qt(png_path, out_jpeg_path, qtables):
    """
    Convert PNG → JPEG while applying the original JPEG quantization tables.
    """
    img = Image.open(png_path)

    ordered_tables = [qtables[k] for k in sorted(qtables.keys())]

    img.save(
        out_jpeg_path,
        format="JPEG",
        qtables=qtables,
        #subsampling=0
    )


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py input.jpg temp.png output.jpg")
        sys.exit(1)

    jpeg_in = sys.argv[1]
    png_tmp = sys.argv[2]
    jpeg_out = sys.argv[3]

    print("[*] Extracting quantization tables...")
    qtables = extract_qtables(jpeg_in)
    print(qtables)

    print("[*] Converting JPEG → PNG...")
    jpeg_to_png(jpeg_in, png_tmp)

    print("[*] Converting PNG → JPEG with original QTs...")
    png_to_jpeg_with_qt(png_tmp, jpeg_out, qtables)

    print("[✓] Done!")
    print(f"Saved new JPEG with original quantization tables to: {jpeg_out}")

