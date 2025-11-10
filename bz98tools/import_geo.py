import os
import bpy
import importlib
import struct
import zlib
from io import BytesIO

from . import geo_classes
from .bzmap import BZMap, BZMapFormat
from .bzmap_serializer import BZMapSerializer
from .bzact_serializer import BZActSerializer


importlib.reload(geo_classes)

# Use built-in ACT palette by name (must exist in BUILTIN_ACT_PALETTES)
BZ_FORCE_ACT_NAME = "moon.act"


BUILTIN_ACT_PALETTES = {
    'moon.act': [
        (0, 0, 0),
        (17, 16, 16),
        (26, 24, 24),
        (31, 26, 25),
        (36, 35, 31),
        (50, 42, 36),
        (52, 49, 48),
        (60, 56, 56),
        (68, 64, 64),
        (77, 72, 72),
        (85, 80, 80),
        (84, 79, 76),
        (112, 108, 104),
        (116, 129, 125),
        (133, 138, 133),
        (178, 174, 174),
        (191, 188, 188),
        (204, 201, 201),
        (217, 215, 215),
        (229, 228, 228),
        (255, 255, 255),
        (20, 3, 2),
        (40, 6, 3),
        (59, 10, 5),
        (79, 13, 6),
        (99, 16, 8),
        (107, 0, 8),
        (148, 8, 0),
        (140, 33, 8),
        (148, 16, 0),
        (156, 24, 0),
        (173, 57, 0),
        (189, 82, 8),
        (206, 99, 16),
        (200, 94, 11),
        (214, 101, 0),
        (214, 132, 33),
        (222, 123, 24),
        (231, 140, 33),
        (231, 156, 41),
        (239, 173, 57),
        (222, 156, 49),
        (222, 165, 57),
        (222, 165, 74),
        (231, 173, 99),
        (239, 189, 90),
        (247, 198, 82),
        (239, 206, 115),
        (249, 249, 149),
        (235, 230, 97),
        (183, 180, 81),
        (169, 133, 50),
        (131, 124, 45),
        (123, 99, 39),
        (149, 101, 17),
        (87, 59, 2),
        (80, 67, 28),
        (78, 48, 3),
        (53, 40, 12),
        (36, 24, 5),
        (171, 72, 69),
        (169, 168, 158),
        (153, 150, 139),
        (249, 249, 195),
        (223, 216, 188),
        (200, 189, 151),
        (194, 186, 139),
        (186, 172, 145),
        (167, 164, 145),
        (160, 151, 127),
        (175, 168, 134),
        (160, 145, 106),
        (157, 145, 109),
        (136, 130, 107),
        (132, 125, 80),
        (116, 104, 81),
        (96, 94, 83),
        (84, 73, 55),
        (115, 72, 1),
        (106, 81, 30),
        (109, 118, 109),
        (93, 106, 102),
        (79, 96, 90),
        (68, 91, 86),
        (63, 76, 73),
        (62, 63, 57),
        (48, 70, 67),
        (46, 61, 56),
        (37, 59, 54),
        (34, 50, 45),
        (31, 42, 41),
        (24, 36, 32),
        (19, 23, 21),
        (16, 14, 14),
        (15, 10, 6),
        (7, 11, 9),
        (181, 191, 204),
        (150, 156, 172),
        (139, 149, 164),
        (134, 143, 156),
        (125, 134, 150),
        (120, 130, 143),
        (115, 124, 139),
        (112, 129, 150),
        (111, 120, 135),
        (107, 116, 131),
        (106, 124, 145),
        (101, 117, 141),
        (100, 111, 128),
        (100, 108, 123),
        (96, 108, 123),
        (96, 104, 120),
        (95, 112, 135),
        (92, 104, 119),
        (92, 100, 116),
        (91, 108, 131),
        (88, 100, 115),
        (88, 96, 112),
        (85, 104, 127),
        (84, 96, 111),
        (84, 92, 108),
        (83, 100, 123),
        (80, 96, 119),
        (80, 92, 108),
        (80, 88, 104),
        (76, 96, 119),
        (76, 92, 116),
        (76, 92, 110),
        (76, 84, 100),
        (75, 88, 103),
        (74, 88, 108),
        (72, 92, 115),
        (72, 88, 112),
        (72, 84, 104),
        (72, 84, 99),
        (72, 80, 95),
        (68, 88, 112),
        (68, 84, 108),
        (68, 80, 100),
        (68, 76, 92),
        (67, 84, 102),
        (67, 80, 95),
        (64, 84, 108),
        (64, 80, 104),
        (64, 76, 96),
        (64, 72, 87),
        (63, 80, 100),
        (63, 76, 91),
        (60, 80, 104),
        (60, 76, 104),
        (60, 76, 100),
        (60, 72, 92),
        (60, 68, 83),
        (59, 76, 96),
        (59, 72, 87),
        (56, 76, 100),
        (56, 72, 100),
        (56, 72, 96),
        (56, 64, 79),
        (55, 72, 92),
        (55, 68, 83),
        (53, 68, 88),
        (52, 72, 96),
        (52, 68, 96),
        (52, 68, 92),
        (52, 64, 88),
        (52, 60, 75),
        (51, 64, 79),
        (49, 64, 84),
        (48, 68, 92),
        (48, 64, 92),
        (48, 60, 84),
        (47, 64, 88),
        (47, 60, 75),
        (47, 56, 72),
        (46, 56, 68),
        (45, 60, 88),
        (45, 60, 80),
        (44, 56, 79),
        (44, 52, 68),
        (44, 51, 64),
        (43, 60, 84),
        (40, 56, 80),
        (40, 56, 76),
        (40, 52, 76),
        (40, 48, 64),
        (40, 48, 60),
        (40, 44, 60),
        (36, 52, 72),
        (36, 51, 76),
        (36, 48, 72),
        (36, 40, 56),
        (35, 44, 60),
        (33, 41, 56),
        (31, 38, 53),
        (28, 36, 49),
        (26, 33, 45),
        (24, 30, 41),
        (22, 27, 38),
        (20, 24, 34),
        (17, 22, 30),
        (15, 19, 26),
        (13, 16, 23),
        (11, 13, 19),
        (9, 10, 15),
        (6, 8, 11),
        (4, 5, 8),
        (2, 2, 4),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
        (0, 255, 255),
        (0, 127, 127),
        (0, 63, 63),
        (78, 194, 242),
        (14, 153, 240),
        (7, 109, 222),
        (12, 149, 203),
        (6, 102, 171),
        (6, 93, 136),
        (3, 56, 124),
        (26, 35, 80),
        (0, 127, 255),
        (0, 99, 199),
        (0, 70, 141),
        (0, 34, 69),
        (0, 21, 42),
        (0, 255, 0),
        (0, 127, 0),
        (0, 63, 0),
        (0, 31, 0),
        (0, 15, 0),
        (255, 0, 0),
        (127, 0, 0),
        (63, 0, 0),
        (31, 0, 0),
        (15, 0, 0),
        (255, 255, 0),
        (164, 164, 0),
        (127, 127, 0),
        (80, 80, 0),
        (64, 64, 0),
        (255, 0, 255),
    ],
}



_palette_cache = {}


# ---------------------------------------------------------------------------
# File / palette helpers
# ---------------------------------------------------------------------------

def _find_map_file(map_name, base_dir):
    """
    Try to find a .map file for the given name (without extension)
    starting from base_dir. Case-insensitive, searches subfolders.
    """
    if not map_name:
        return None

    map_name = map_name.strip()
    if not map_name:
        return None

    # Direct hit first
    candidate = os.path.join(base_dir, map_name + ".map")
    if os.path.exists(candidate):
        return candidate

    target_lower = (map_name + ".map").lower()
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.lower() == target_lower:
                return os.path.join(root, f)

    return None


def _load_palette_from_act(path):
    """
    Load a BZ .act palette.

    For Battlezone objects.act, this is 256 * 3 bytes (RGB, no alpha).
    Returns a list of 256 [r, g, b] entries (0-255).
    """
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError as e:
        print(f"[BZ ACT] Failed to read palette file '{path}': {e}")
        return None

    if len(data) != 256 * 3:
        print(f"[BZ ACT] Unexpected palette size {len(data)} (expected 768 bytes) in '{path}'.")
        return None

    palette = []
    for i in range(256):
        r = data[i * 3 + 0]
        g = data[i * 3 + 1]
        b = data[i * 3 + 2]
        palette.append((r, g, b))
    return palette


_palette_cache = {}


def _find_act_file(start_dir):
    """
    Very simple search for any .act file under start_dir.
    Only used if we don't have a forced/built-in palette name.
    """
    start_dir = os.fspath(start_dir)
    for root, dirs, files in os.walk(start_dir):
        for fname in files:
            if fname.lower().endswith(".act"):
                return os.path.join(root, fname)
    return None


def _get_palette_for_dir(start_dir):
    """
    Get a 256x(R,G,B) palette for the given directory.

    Preference order:
      1) Forced built-in palette name (BZ_FORCE_ACT_NAME) if present.
      2) Forced built-in name + ACT file in addon 'data' folder (optional).
      3) Any .act under start_dir (use built-in data if we have it, or load file).
    """
    # 1) Forced built-in palette by name
    if BZ_FORCE_ACT_NAME:
        name = BZ_FORCE_ACT_NAME
        if name in _palette_cache:
            return _palette_cache[name]

        # Built-in data baked into the addon
        if name in BUILTIN_ACT_PALETTES:
            pal = BUILTIN_ACT_PALETTES[name]
            _palette_cache[name] = pal
            print(f"[BZ ACT] Using built-in palette '{name}'.")
            return pal

        # Optional: if you *also* ship a binary .act in addon/data, you can still load it:
        forced_path = os.path.join(os.path.dirname(__file__), "data", name)
        if os.path.exists(forced_path):
            pal = _load_palette_from_act(forced_path)
            if pal:
                _palette_cache[name] = pal
                print(f"[BZ ACT] Loaded palette from '{forced_path}'.")
                return pal

    # 2) No forced name or it failed: look for any .act near the map
    act_path = _find_act_file(start_dir)
    if not act_path:
        print(f"[BZ ACT] No .act palette found near '{start_dir}'.")
        return None

    act_name = os.path.basename(act_path)

    if act_name in _palette_cache:
        return _palette_cache[act_name]

    # If we have built-in data for this filename, use it instead of reading from disk
    if act_name in BUILTIN_ACT_PALETTES:
        pal = BUILTIN_ACT_PALETTES[act_name]
        _palette_cache[act_name] = pal
        print(f"[BZ ACT] Using built-in palette '{act_name}'.")
        return pal

    # Otherwise, load from the .act file on disk
    pal = _load_palette_from_act(act_path)
    if pal:
        _palette_cache[act_path] = pal
        print(f"[BZ ACT] Loaded palette from '{act_path}'.")
        return pal

    return None


def _write_indexed_map_to_png(map_path, palette, out_path=None):
    """
    Pure-Python writer for INDEXED (fmt=0) .MAP files.

    Uses the same logic as your NumPy/PIL version:
      - header: <row_bytes, pixel_format, height, unknown> (4 x uint16 LE)
      - data: row_bytes * height bytes of palette indices
      - palette: list of 256 (r,g,b) tuples, 0..255
    Writes an 8-bit RGB PNG with no dependencies beyond the stdlib.
    """
    map_path = os.fspath(map_path)

    if out_path is None:
        out_path = os.path.splitext(map_path)[0] + ".png"
    else:
        out_path = os.fspath(out_path)

    # Read the whole .map file
    try:
        with open(map_path, "rb") as f:
            data = f.read()
    except OSError as e:
        print(f"[BZ MAP] Failed to read .map file '{map_path}': {e}")
        return None

    if len(data) < 8:
        print(f"[BZ MAP] File too small to be a valid .map: '{map_path}'")
        return None

    row_bytes, pixel_format, height, unknown = struct.unpack("<4H", data[:8])

    if pixel_format != BZMapFormat.INDEXED:
        print(f"[BZ MAP] _write_indexed_map_to_png called for non-indexed fmt={pixel_format} in '{map_path}'")
        return None

    buf = data[8:]
    width = row_bytes  # for INDEXED, bpp == 1

    expected = width * height
    if len(buf) < expected:
        print(f"[BZ MAP] Buffer too small: {len(buf)} bytes, expected {expected} in '{map_path}'")
        return None

    # Build scanlines with PNG filter type 0 (no filter)
    pixels = bytearray()
    for y in range(height):
        pixels.append(0)  # filter type 0
        row_start = y * width
        row = buf[row_start:row_start + width]
        for idx in row:
            r, g, b = palette[idx]
            pixels.extend((r, g, b))

    # Minimal PNG writer (8-bit RGB, no interlace, no extras)
    def _png_chunk(tag, payload):
        return (struct.pack(">I", len(payload)) +
                tag +
                payload +
                struct.pack(">I", zlib.crc32(tag + payload) & 0xffffffff))

    bio = BytesIO()
    # PNG signature
    bio.write(b"\x89PNG\r\n\x1a\n")

    # IHDR: width, height, bit depth=8, color type=2 (RGB), no interlace
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    bio.write(_png_chunk(b"IHDR", ihdr))

    # IDAT: compressed image data
    compressed = zlib.compress(bytes(pixels), 9)
    bio.write(_png_chunk(b"IDAT", compressed))

    # IEND
    bio.write(_png_chunk(b"IEND", b""))

    try:
        with open(out_path, "wb") as f:
            f.write(bio.getvalue())
        print(f"[BZ MAP] Wrote PNG '{out_path}'")
        return out_path
    except OSError as e:
        print(f"[BZ MAP] Failed to write PNG '{out_path}': {e}")
        return None


# ---------------------------------------------------------------------------
# Pixel format decoders (mirror your NumPy/PIL logic)
# ---------------------------------------------------------------------------

def _decode_indexed(buf, width, height, row_bytes, palette=None):
    use_palette = palette is not None and len(palette) >= 256
    pixels = [0.0] * (width * height * 4)
    i = 0

    # Top-to-bottom, same as bzmap_to_pilimage
    for y in range(height):
        row_start = y * row_bytes
        for x in range(width):
            off = row_start + x
            idx = buf[off]

            if use_palette and 0 <= idx < len(palette):
                pr, pg, pb = palette[idx]
                r = pr / 255.0
                g = pg / 255.0
                b = pb / 255.0
                a = 1.0
            else:
                v = idx / 255.0
                r = g = b = v
                a = 1.0

            pixels[i + 0] = r
            pixels[i + 1] = g
            pixels[i + 2] = b
            pixels[i + 3] = a
            i += 4

    return pixels




def _decode_argb4444(buf, width, height, row_bytes):
    """
    Decode ARGB4444 (16-bit) to RGBA.
    Matches the bit math from your NumPy implementation.
    """
    pixels = [0.0] * (width * height * 4)
    i = 0
    for y in range(height):
        row_start = y * row_bytes
        for x in range(width):
            off = row_start + x * 2
            v = buf[off] | (buf[off + 1] << 8)
            a = ((v >> 12) & 0xF) / 15.0
            r = ((v >> 8) & 0xF) / 15.0
            g = ((v >> 4) & 0xF) / 15.0
            b = (v & 0xF) / 15.0
            pixels[i + 0] = r
            pixels[i + 1] = g
            pixels[i + 2] = b
            pixels[i + 3] = a
            i += 4
    return pixels


def _decode_rgb565(buf, width, height, row_bytes):
    """
    Decode RGB565 (16-bit) to RGBA (alpha=1).
    Matches your NumPy interp version.
    """
    pixels = [0.0] * (width * height * 4)
    i = 0
    for y in range(height):
        row_start = y * row_bytes
        for x in range(width):
            off = row_start + x * 2
            v = buf[off] | (buf[off + 1] << 8)
            r = ((v >> 11) & 0x1F) / 31.0
            g = ((v >> 5) & 0x3F) / 63.0
            b = (v & 0x1F) / 31.0
            pixels[i + 0] = r
            pixels[i + 1] = g
            pixels[i + 2] = b
            pixels[i + 3] = 1.0
            i += 4
    return pixels


def _decode_argb8888(buf, width, height, row_bytes, xrgb=False):
    """
    Decode ARGB8888 / XRGB8888 to RGBA.

    From your PIL code:
        ar = np.frombuffer(..., dtype="B")
        ar.shape = (h, w, 4)
        ar = ar[:, :, [2, 1, 0, 3]]   # -> RGBA
    So the underlying layout is BGRA.

    For XRGB8888:
        ar = ar[:, :, [2, 1, 0]]      # -> RGB, ignore alpha.
    """
    pixels = [0.0] * (width * height * 4)
    i = 0
    for y in range(height):
        row_start = y * row_bytes
        for x in range(width):
            off = row_start + x * 4
            b = buf[off + 0]
            g = buf[off + 1]
            r = buf[off + 2]
            a = buf[off + 3]
            if xrgb:
                a = 255
            pixels[i + 0] = r / 255.0
            pixels[i + 1] = g / 255.0
            pixels[i + 2] = b / 255.0
            pixels[i + 3] = a / 255.0
            i += 4
    return pixels


def _load_bzmap_to_image(filepath, image_name, palette_search_dir):
    """
    Load a Battlezone .map file into a Blender Image.

    For INDEXED (fmt=0):
      - Use ACT palette via _get_palette_for_dir
      - Convert .map -> .png with _write_indexed_map_to_png (pure Python)
      - Load the PNG into Blender as a normal file-backed image.

    For other formats (ARGB4444, RGB565, ARGB8888, XRGB8888):
      - Fall back to the existing BZMap/BZMapSerializer + pixel decoder path.
    """
    import bpy

    # Always normalize the path
    filepath = os.fspath(filepath)
    png_path = os.path.splitext(filepath)[0] + ".png"

    # If there's already a PNG for this MAP, just use it
    if os.path.exists(png_path):
        try:
            img = bpy.data.images.load(png_path, check_existing=True)
            try:
                img.colorspace_settings.name = "sRGB"
            except Exception:
                pass
            print(f"[BZ MAP] Using existing PNG '{png_path}' for '{os.path.basename(filepath)}'.")
            return img
        except Exception as e:
            print(f"[BZ MAP] Failed to load existing PNG '{png_path}': {e}")

    # Peek at the MAP header to figure out pixel_format
    try:
        with open(filepath, "rb") as f:
            header = f.read(8)
    except OSError as e:
        print(f"[BZ MAP] Failed to open .map file '{filepath}': {e}")
        return None

    if len(header) < 8:
        print(f"[BZ MAP] File too small to be a valid .map: '{filepath}'")
        return None

    row_bytes, pixel_format, height, unknown = struct.unpack("<4H", header)

    # ------------------------------------------------------------------
    # INDEXED (fmt=0): use ACT + pure-Python MAP->PNG path
    # ------------------------------------------------------------------
    if pixel_format == BZMapFormat.INDEXED:
        width = row_bytes
        print(f"[BZ MAP] {os.path.basename(filepath)}: fmt={pixel_format}, size={width}x{height}, row_bytes={row_bytes}")

        palette = _get_palette_for_dir(palette_search_dir)
        if not palette:
            print(f"[BZ MAP] No valid ACT palette found near '{palette_search_dir}'. Cannot decode indexed .map.")
            return None

        print(f"[BZ MAP] Using palette from ACT; first 4 entries: {palette[:4]}")

        # Write PNG using pure-Python writer
        out_png = _write_indexed_map_to_png(filepath, palette, png_path)
        if not out_png:
            return None

        # Load the resulting PNG into Blender
        try:
            img = bpy.data.images.load(out_png, check_existing=True)
            try:
                img.colorspace_settings.name = "sRGB"
            except Exception:
                pass
            return img
        except Exception as e:
            print(f"[BZ MAP] Failed to load PNG '{out_png}' after writing: {e}")
            return None

    # ------------------------------------------------------------------
    # Non-indexed formats: fall back to your existing decoder path
    # ------------------------------------------------------------------
    print(f"[BZ MAP] {os.path.basename(filepath)}: non-indexed fmt={pixel_format}, using direct decode path.")

    try:
        bz = BZMap()
        ser = BZMapSerializer()
        with open(filepath, "rb") as f:
            ser.deserialize(f, bz)
    except Exception as e:
        print(f"[BZ MAP] Failed to read .map file '{filepath}': {e}")
        return None

    width, height = bz.get_size()
    buf = bz.get_buffer()
    if buf is None:
        print(f"[BZ MAP] No pixel buffer in '{filepath}'.")
        return None

    row_bytes = bz.row_byte_size
    print(f"[BZ MAP] {os.path.basename(filepath)}: fmt={bz.pixel_format}, size={width}x{height}, row_bytes={row_bytes}")

    # Decode to RGBA list (0..1) using your existing decoders
    if bz.pixel_format == BZMapFormat.ARGB4444:
        pixels = _decode_argb4444(buf, width, height, row_bytes)
    elif bz.pixel_format == BZMapFormat.RGB565:
        pixels = _decode_rgb565(buf, width, height, row_bytes)
    elif bz.pixel_format == BZMapFormat.ARGB8888:
        pixels = _decode_argb8888(buf, width, height, row_bytes, xrgb=False)
    elif bz.pixel_format == BZMapFormat.XRGB8888:
        pixels = _decode_argb8888(buf, width, height, row_bytes, xrgb=True)
    else:
        print(f"[BZ MAP] Unsupported format={bz.pixel_format}, file='{filepath}'.")
        return None

    # Create a GENERATED image and fill pixels
    img = bpy.data.images.new(image_name, width=width, height=height, alpha=True)
    expected_len = width * height * 4
    if len(pixels) != expected_len:
        print(
            f"[BZ MAP] WARNING: pixel buffer size mismatch for '{filepath}' "
            f"(len={len(pixels)}, expected={expected_len})"
        )
    else:
        img.pixels[:] = pixels

    try:
        img.colorspace_settings.name = "sRGB"
    except Exception:
        pass

    img.source = 'GENERATED'
    img.filepath = ""
    return img




def _ensure_map_texture_on_material(mat, map_name, base_dir):
    """
    Given a Blender material and a Battlezone map name, try to load the
    corresponding .map file as an image and hook it up to the material's
    Principled BSDF.
    """
    if not map_name:
        return

    map_path = _find_map_file(map_name, base_dir)
    if not map_path:
        print(f"[BZ MAP] Could not find .map file for '{map_name}' under '{base_dir}'.")
        return

    image_name = f"{map_name}.map"
    palette_dir = os.path.dirname(map_path)
    img = _load_bzmap_to_image(map_path, image_name, palette_dir)
    if img is None:
        return

    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links

    # Find or create Principled BSDF
    bsdf = None
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            bsdf = node
            break
    if bsdf is None:
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)

    # Find or create Material Output
    output = None
    for node in nodes:
        if node.type == 'OUTPUT_MATERIAL':
            output = node
            break
    if output is None:
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300, 0)

    # Image Texture node
    tex_node = nodes.new(type='ShaderNodeTexImage')
    tex_node.image = img
    tex_node.label = map_name
    tex_node.location = (-300, 0)

    # Link color + alpha
    if tex_node.outputs.get('Color') is not None and bsdf.inputs.get('Base Color') is not None:
        links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
    if tex_node.outputs.get('Alpha') is not None and bsdf.inputs.get('Alpha') is not None:
        links.new(tex_node.outputs['Alpha'], bsdf.inputs['Alpha'])

    # Ensure BSDF is connected to output
    if not any(link.to_node == output for link in bsdf.outputs['BSDF'].links):
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])


# ---------------------------------------------------------------------------
# GEO loader
# ---------------------------------------------------------------------------

def geoload(context, geofilepath, *, name=None, flip=True,
            PreserveFaceColors=False, ImportMapTextures=False,
            map_base_dir=None):
    position = 0
    header = None
    verticeslist = []
    normalslist = []
    uvslist = []
    facelist = []

    if not os.path.exists(geofilepath):
        raise Exception(geofilepath + ' was not found!')
        return None

    if map_base_dir is None:
        map_base_dir = os.path.dirname(geofilepath)

    with open(geofilepath, mode='rb') as file:
        fileContent = file.read()
        import struct

        header = geo_classes.GEOHeader(struct.unpack("=4si16siii", fileContent[position:position+36]))
        uvslist = [None] * header.Vertices
        position += 36

        # Vertices
        for _ in range(header.Vertices):
            newvertex = geo_classes.GEOVertex(struct.unpack("=fff", fileContent[position:position+12]))
            position += 12
            verticeslist.append(newvertex)

        # Normals
        for _ in range(header.Vertices):
            newnormal = geo_classes.GEONormal(struct.unpack("=fff", fileContent[position:position+12]))
            position += 12
            normalslist.append(newnormal)

        # Faces
        for _ in range(header.Faces):
            newface = geo_classes.GEOFace(struct.unpack("=iiBBBffffi3s13sii", fileContent[position:position+55]))
            position += 55
            for _ in range(newface.Vertices):
                newvert = geo_classes.PolygonVert(struct.unpack("iiff", fileContent[position:position+16]))
                position += 16
                newface.VertList.append(newvert)
            facelist.append(newface)

        OBJName = header.GEOName if name is None else name

        mesh = bpy.data.meshes.new("mesh")
        obj = bpy.data.objects.new(OBJName, mesh)
        bpy.context.collection.objects.link(obj)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        import bmesh
        bm = bmesh.new()
        for i in range(header.Vertices):
            if flip:
                vert = bm.verts.new((verticeslist[i].x, verticeslist[i].z, verticeslist[i].y))
            else:
                vert = bm.verts.new((verticeslist[i].x, verticeslist[i].y, verticeslist[i].z))
            vert.normal = (normalslist[i].x, normalslist[i].y, normalslist[i].z)

        used_faces = []
        bm.verts.ensure_lookup_table()
        for face in facelist:
            verts = []
            for vert in face.VertList:
                verts.append(bm.verts[vert.vertID])
                uv = geo_classes.GEOUV([vert.u, 1.0 - vert.v])
                uvslist[vert.vertID] = uv
            try:
                bm_face = bm.faces.new(verts)
                used_faces.append(face)
            except Exception:
                # duplicate/invalid face
                pass

        bm.to_mesh(mesh)
        bm.free()

        mesh.uv_layers.new()
        uv_layer = mesh.uv_layers.active.data
        for poly in mesh.polygons:
            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                uv = uvslist[mesh.loops[loop_index].vertex_index]
                if uv is not None:
                    uv_layer[loop_index].uv = (uv.u, uv.v)
                else:
                    uv_layer[loop_index].uv = (0.0, 0.0)

        Slots = {}
        for i, face in enumerate(used_faces):
            if i >= len(mesh.polygons):
                break

            if len(face.MapName) > 0:
                if PreserveFaceColors:
                    PreservedName = f"{face.MapName}-Color({face.r},{face.g},{face.b})"
                    mat = bpy.data.materials.get(PreservedName)
                    if mat is None:
                        mat = bpy.data.materials.new(name=PreservedName)
                        mat.diffuse_color = (face.r/255, face.g/255, face.b/255, 1.0)
                        mat.MaterialPropertyGroup.MapTexture = face.MapName
                    if obj.data.materials.get(PreservedName) is None:
                        Slots[PreservedName] = len(Slots)
                        obj.data.materials.append(mat)
                    mesh.polygons[i].material_index = Slots[PreservedName]
                else:
                    mat = bpy.data.materials.get(face.MapName)
                    if mat is None:
                        mat = bpy.data.materials.new(name=face.MapName)
                        mat.diffuse_color = (face.r/255, face.g/255, face.b/255, 1.0)
                        mat.MaterialPropertyGroup.MapTexture = face.MapName
                    if obj.data.materials.get(face.MapName) is None:
                        Slots[face.MapName] = len(Slots)
                        obj.data.materials.append(mat)
                    mesh.polygons[i].material_index = Slots[face.MapName]

        if ImportMapTextures:
            for mat in obj.data.materials:
                if not hasattr(mat, "MaterialPropertyGroup"):
                    continue
                map_name = (mat.MaterialPropertyGroup.MapTexture or "").strip()
                if not map_name:
                    continue
                _ensure_map_texture_on_material(mat, map_name, map_base_dir)

        return obj


def load(context, filepath, *, PreserveFaceColors=True, ImportMapTextures=False):
    if not os.path.exists(filepath):
        raise Exception(filepath + ' was not found!')
        return {'FINISHED'}

    geoload(
        context,
        filepath,
        PreserveFaceColors=PreserveFaceColors,
        ImportMapTextures=ImportMapTextures,
        map_base_dir=os.path.dirname(filepath),
    )

    return {'FINISHED'}
