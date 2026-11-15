#!/usr/bin/env python3
"""Hide any file in the red-channel LSBs of a set of PNG images.

Protocol (bit stream, MSB first, read in the keyed pseudo-random pixel order)
---------------------------------------------------------------------------
    [flag: 1 bit] [file type] [file name] [message size] [tag: 16 bytes] [data]

File type
    flag = 0 (standard)      -> extension is exactly 3 bytes:        EEE
    flag = 1 (non-standard)  -> letter | ext length (ASCII digits) | letter | ext bytes
    (no extension at all is non-standard with length "0")

File name (without the extension, always present)
    letter | name length (ASCII digits) | letter | name bytes
    (length "0" if empty; the receiver then falls back to "out")

Message size (in bytes, always present)
    letter | size (ASCII digits) | letter

The delimiter letters are random [a-z]; digits are [0-9], so a field's end is
unambiguous. Tag = HMAC-SHA256(flag, ext, name, data) truncated to 16 bytes: it
tells a wrong key / altered images apart from valid data, and covers the type,
name and size too. Readers cap the number of digits so garbage can't run on
forever.

Keys and image order
    * scrypt(passphrase, salt = nonce) -> XChaCha20 key + HMAC key.
    * The XChaCha20 keystream drives a partial Fisher-Yates shuffle over *all*
      pixels of *all* images: unique, secret positions, one bit per pixel.
    * Images are put in a canonical order by the SHA-256 of their pixel data
      with the red LSBs cleared (embedding does not change it). File names and
      metadata order are irrelevant; renamed or shuffled files still work.
    * The 192-bit nonce is stored in a "Nonce" PNG text chunk. It is not secret
      (only unique). If a platform strips metadata, hide with
      --no-nonce-metadata, keep the printed nonce, and give it back with --nonce.

Usage
    python -m fog hide    secret.mp4 bank_dir out_dir
                          [--key K] [--name NAME] [--ext EXT] [--no-nonce-metadata]
    python -m fog extract out_dir result_dir
                          [--key K] [--nonce B64] [--output-name NAME]

LSB data does not survive JPEG conversion, resizing or lossy re-encoding.
"""
import argparse
import base64
import binascii
import bisect
import functools
import getpass
import glob
import hashlib
import hmac
import os
import secrets
import struct
import sys

from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngInfo

NONCE_LEN = 24            # 192-bit nonce -> XChaCha20
TAG_LEN = 16              # truncated HMAC-SHA256
STD_EXT_LEN = 3           # "standard" extension length in bytes
MAX_EXT_BYTES = 255       # file-name limit on common file systems
EXT_LEN_DIGITS = 3        # max digits in the extension-length field
SIZE_DIGITS = 15          # max digits in the message-size field
MAX_NAME_BYTES = 255      # max length of the stored file name (without extension)
NONCE_KEY = "Nonce"

_BAD_MSG = ("no valid hidden data found: wrong key, wrong image set, "
            "or the images were modified/re-encoded")
_BAD_EXT_CHARS = set('/\\:*?"<>|')


class HiddenDataError(ValueError):
    """Raised when nothing valid can be read with this key and image set."""


# Images of any size are accepted: Pillow's "decompression bomb" guard is turned
# off for the images given by the user. Very large images only get a warning
# (large_images): they need a lot of memory and time.
Image.MAX_IMAGE_PIXELS = None
LARGE_IMAGE_PIXELS = 89_478_485   # Pillow's default limit, about 9460 x 9460
BYTES_PER_PIXEL = 4               # RGBA in memory, for the memory estimate

# Input formats. PNG is the native one; the others can be used for hiding when
# they are allowed (`extensions`): they are decoded and the output is PNG.
NATIVE_EXTENSIONS = (".png",)
CONVERTIBLE_FORMATS = {
    "jpg": (".jpg", ".jpeg"),
    "tiff": (".tif", ".tiff"),
    "bmp": (".bmp",),
    "webp": (".webp",),
}

_MEMORY_MSG = ("not enough memory to process these images (some are very large): "
               "use smaller or fewer images")


def open_image(path: str) -> Image.Image:
    """Image.open (OSError / UnidentifiedImageError if the file is unreadable)."""
    return Image.open(path)


def image_size(path: str):
    """(width, height) of `path`, reading only the header."""
    with open_image(path) as im:
        return im.size


def check_image(path: str) -> int:
    """Number of pixels of `path` (header only); OSError if it cannot be read."""
    w, h = image_size(path)
    return w * h


def large_images(image_bank, extensions=NATIVE_EXTENSIONS):
    """[(file, (width, height))] of the images of `image_bank` that are very large
    (LARGE_IMAGE_PIXELS or more)."""
    found = []
    for f in collect_images(image_bank, extensions):
        w, h = image_size(f)
        if w * h >= LARGE_IMAGE_PIXELS:
            found.append((f, (w, h)))
    return found


def _memory_guard(func):
    """Turn a MemoryError (huge images) into a clear ValueError."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MemoryError:
            raise ValueError(_MEMORY_MSG) from None
    return wrapper


# --------------------------------------------------------------------------
# Keys and keystream-driven RNG
# --------------------------------------------------------------------------
def derive_keys(passphrase: str, nonce: bytes):
    """Return (cipher_key, mac_key), 32 bytes each."""
    dk = hashlib.scrypt(passphrase.encode("utf-8"), salt=nonce,
                        n=2 ** 14, r=8, p=1, dklen=64)
    return dk[:32], dk[32:]


class Keystream:
    """Deterministic RNG on top of the XChaCha20 keystream (buffered)."""

    CHUNK = 1 << 16

    def __init__(self, key: bytes, nonce: bytes):
        self._cipher = ChaCha20.new(key=key, nonce=nonce)
        self._buf = b""
        self._pos = 0

    def _take(self, n: int) -> bytes:
        if len(self._buf) - self._pos < n:
            self._buf = self._buf[self._pos:] + self._cipher.encrypt(bytes(self.CHUNK))
            self._pos = 0
        out = self._buf[self._pos:self._pos + n]
        self._pos += n
        return out

    def randbelow(self, n: int) -> int:
        """Uniform integer in [0, n) via rejection sampling (no modulo bias)."""
        if n < 1:
            raise ValueError("n must be >= 1")
        nbytes = (n.bit_length() + 7) // 8 + 1
        limit = (256 ** nbytes // n) * n
        while True:
            v = int.from_bytes(self._take(nbytes), "big")
            if v < limit:
                return v % n


def position_stream(rng: Keystream, total: int):
    """Yield distinct positions in [0, total) in secret random order.

    Lazy, sparse partial Fisher-Yates: the j-th output depends only on the key
    and j, never on the message length, so headers can be read first.
    """
    swapped = {}
    for j in range(total):
        r = j + rng.randbelow(total - j)
        vj = swapped.get(j, j)
        vr = swapped.get(r, r)
        swapped[r] = vj          # index j is never read again
        swapped.pop(j, None)
        yield vr


# --------------------------------------------------------------------------
# Images
# --------------------------------------------------------------------------
def _normalize(img: Image.Image) -> Image.Image:
    """Make sure pixels are RGB/RGBA tuples (palette / grey images get converted)."""
    if img.mode in ("RGB", "RGBA"):
        img.load()
        return img
    has_alpha = img.mode in ("LA", "PA") or "transparency" in img.info
    return img.convert("RGBA" if has_alpha else "RGB")


_CLEAR_LSB = bytes(v & 0xFE for v in range(256))


def _fingerprint(img: Image.Image) -> bytes:
    """SHA-256 of the pixel data with every red LSB cleared (embedding-invariant)."""
    n = len(img.getbands())
    buf = bytearray(img.tobytes())
    buf[0::n] = buf[0::n].translate(_CLEAR_LSB)
    h = hashlib.sha256()
    h.update(f"{img.mode}:{img.size[0]}x{img.size[1]}".encode("ascii"))
    h.update(buf)
    return h.digest()


def _canonical_order(images, on_image=None):
    """Indices of `images` sorted by fingerprint; identical images are rejected.
    `on_image(i)` is called after each fingerprint (progress)."""
    prints = []
    for i, im in enumerate(images):
        prints.append(_fingerprint(im))
        if on_image:
            on_image(i)
    if len(set(prints)) != len(prints):
        raise ValueError("two images are identical (ignoring the red LSB); "
                         "every image in the set must be unique")
    return sorted(range(len(images)), key=lambda i: prints[i])


class ImageSet:
    """Images viewed as one long run of pixels, 1 bit per pixel."""

    def __init__(self, images):
        self.images = images
        self.px = [im.load() for im in images]
        self.starts = []
        total = 0
        for im in images:
            self.starts.append(total)
            total += im.size[0] * im.size[1]
        self.total = total

    def locate(self, idx: int):
        k = bisect.bisect_right(self.starts, idx) - 1
        w = self.images[k].size[0]
        off = idx - self.starts[k]
        return k, off % w, off // w

    def write_bit(self, idx: int, bit: int):
        k, x, y = self.locate(idx)
        p = self.px[k][x, y]
        self.px[k][x, y] = ((p[0] & ~1) | bit,) + tuple(p[1:])

    def read_bit(self, idx: int) -> int:
        k, x, y = self.locate(idx)
        return self.px[k][x, y][0] & 1


# --------------------------------------------------------------------------
# Protocol: building and parsing the bit stream
# --------------------------------------------------------------------------
def _letter() -> bytes:
    return bytes([ord("a") + secrets.randbelow(26)])


def _is_letter(b: int) -> bool:
    return 0x61 <= b <= 0x7A


def _extension_bytes(ext: str) -> bytes:
    """Validate an extension (no dot) and return its UTF-8 bytes."""
    if any(c in _BAD_EXT_CHARS or ord(c) < 32 for c in ext):
        raise ValueError(f"invalid character in file extension {ext!r}")
    raw = ext.encode("utf-8")
    if len(raw) > MAX_EXT_BYTES:
        raise ValueError(f"file extension longer than {MAX_EXT_BYTES} bytes")
    return raw


def _clean_name(name: str) -> str:
    """Replace characters that are invalid in file names (used when hiding)."""
    return "".join("_" if (c in _BAD_EXT_CHARS or ord(c) < 32) else c for c in name)


def _name_bytes(name: str, ext_len: int) -> bytes:
    """Validate a file name (without extension) and return its UTF-8 bytes."""
    if name in (".", "..") or any(c in _BAD_EXT_CHARS or ord(c) < 32 for c in name):
        raise ValueError(f"invalid file name {name!r}")
    raw = name.encode("utf-8")
    if len(raw) + (ext_len + 1 if ext_len else 0) > MAX_NAME_BYTES:
        raise ValueError(f"file name longer than {MAX_NAME_BYTES} bytes")
    return raw


def _mac(mac_key: bytes, flag: int, ext: bytes, name: bytes, data: bytes) -> bytes:
    msg = struct.pack(">BHHQ", flag, len(ext), len(name), len(data)) + ext + name + data
    return hmac.new(mac_key, msg, hashlib.sha256).digest()[:TAG_LEN]


def build_payload(ext: str, name: str, data: bytes, mac_key: bytes):
    """Return (flag, body): flag is the 1-bit standard indicator, body the bytes after it."""
    ext_b = _extension_bytes(ext)
    name_b = _name_bytes(name, len(ext_b))
    flag = 0 if len(ext_b) == STD_EXT_LEN else 1
    tag = _mac(mac_key, flag, ext_b, name_b, data)
    parts = []
    if flag:
        parts += [_letter(), str(len(ext_b)).encode("ascii"), _letter()]
    parts += [ext_b,
              _letter(), str(len(name_b)).encode("ascii"), _letter(), name_b,
              _letter(), str(len(data)).encode("ascii"), _letter(), tag, data]
    return flag, b"".join(parts)


def required_bits(message: str, extension: str = None, name: str = None) -> int:
    """Number of bits fog() needs to hide the file `message` (same layout as
    build_payload, computed from the file size: the file is not read)."""
    stem, dot_ext = os.path.splitext(os.path.basename(message))
    ext_b = _extension_bytes((dot_ext[1:] if extension is None else extension).lstrip("."))
    name_b = _name_bytes(_clean_name(stem if name is None else name), len(ext_b))
    size = os.path.getsize(message)
    n = (len(ext_b)
         + 2 + len(str(len(name_b))) + len(name_b)
         + 2 + len(str(size)) + TAG_LEN + size)
    if len(ext_b) != STD_EXT_LEN:
        n += 2 + len(str(len(ext_b)))
    return 1 + 8 * n


def capacity_bits(image_bank, extensions=NATIVE_EXTENSIONS) -> int:
    """Number of bits the images of `image_bank` can hold (1 bit per pixel).
    Only the image headers are read."""
    total = 0
    for f in collect_images(image_bank, extensions):
        total += check_image(f)
    return total


def payload_bits(flag: int, body: bytes):
    yield flag
    for byte in body:
        for shift in range(7, -1, -1):
            yield (byte >> shift) & 1


class _BitReader:
    def __init__(self, imgset: ImageSet, positions, on_bytes=None):
        self._set = imgset
        self._on_bytes = on_bytes      # progress: called with the number of bytes read
        self._pos = positions
        self.remaining = imgset.total

    def bit(self) -> int:
        if self.remaining <= 0:
            raise HiddenDataError(_BAD_MSG)
        self.remaining -= 1
        return self._set.read_bit(next(self._pos))

    def byte(self) -> int:
        v = 0
        for _ in range(8):
            v = (v << 1) | self.bit()
        return v

    def take(self, n: int) -> bytes:
        if n * 8 > self.remaining:
            raise HiddenDataError(_BAD_MSG)
        out = bytearray()
        chunk = 4096
        while len(out) < n:
            k = min(chunk, n - len(out))
            out += bytes(self.byte() for _ in range(k))
            if self._on_bytes:
                self._on_bytes(k)
        return bytes(out)


def _read_field(r: _BitReader, max_digits: int) -> int:
    """letter | ASCII digits | letter  ->  the integer."""
    if not _is_letter(r.byte()):
        raise HiddenDataError(_BAD_MSG)
    digits = bytearray()
    while True:
        b = r.byte()
        if 0x30 <= b <= 0x39:
            digits.append(b)
            if len(digits) > max_digits:
                raise HiddenDataError(_BAD_MSG)
        elif _is_letter(b):
            break
        else:
            raise HiddenDataError(_BAD_MSG)
    if not digits:
        raise HiddenDataError(_BAD_MSG)
    return int(digits)


def parse_payload(r: _BitReader, mac_key: bytes, on_size=None):
    """Read and authenticate the payload. Returns (extension, name, data).
    `on_size(size)` is called once the size of the hidden data is known."""
    flag = r.bit()
    if flag:
        ext_len = _read_field(r, EXT_LEN_DIGITS)
        if ext_len > MAX_EXT_BYTES:
            raise HiddenDataError(_BAD_MSG)
    else:
        ext_len = STD_EXT_LEN
    ext_b = r.take(ext_len)
    name_len = _read_field(r, EXT_LEN_DIGITS)
    if name_len > MAX_NAME_BYTES:
        raise HiddenDataError(_BAD_MSG)
    name_b = r.take(name_len)
    size = _read_field(r, SIZE_DIGITS)
    if on_size:
        on_size(size)
    tag = r.take(TAG_LEN)
    data = r.take(size)
    if not hmac.compare_digest(tag, _mac(mac_key, flag, ext_b, name_b, data)):
        raise HiddenDataError(_BAD_MSG)
    try:
        ext = ext_b.decode("utf-8")
        _extension_bytes(ext)
        name = name_b.decode("utf-8")
        _name_bytes(name, len(ext_b))
    except ValueError:
        raise ValueError("the hidden file name or type contains invalid characters") from None
    return ext, name, data


# --------------------------------------------------------------------------
# Hide
# --------------------------------------------------------------------------
def _same_path(a: str, b: str) -> bool:
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))




_FORMAT_ALIASES = {"jpeg": "jpg", "tif": "tiff"}


def extensions_for(formats) -> tuple:
    """PNG + the extensions of the given convertible formats (e.g. ["jpg", "webp"]).
    Raises ValueError for an unknown format."""
    exts = list(NATIVE_EXTENSIONS)
    for fmt in formats:
        key = fmt.strip().lower().lstrip(".")
        key = _FORMAT_ALIASES.get(key, key)
        if key not in CONVERTIBLE_FORMATS:
            raise ValueError(f"unknown image format: {fmt!r} "
                             f"(possible: {', '.join(CONVERTIBLE_FORMATS)})")
        exts += CONVERTIBLE_FORMATS[key]
    return tuple(dict.fromkeys(exts))


def list_images(folder: str, extensions=NATIVE_EXTENSIONS):
    """Image files of `folder` (not recursive) whose extension is in `extensions`."""
    return sorted(f for f in glob.glob(os.path.join(folder, "*"))
                  if os.path.isfile(f) and os.path.splitext(f)[1].lower() in extensions)


def collect_images(sources, extensions=NATIVE_EXTENSIONS):
    """Image files of `sources`: a folder, or a list of folders and / or image files.

    Only the extensions in `extensions` are used (PNG by default). Folders give
    their images (not recursive). A file listed twice (directly or through its
    folder) is kept once.
    """
    if isinstance(sources, (str, os.PathLike)):
        sources = [sources]
    extensions = tuple(e.lower() for e in extensions)
    files, seen = [], set()
    for src in sources:
        src = os.fspath(src)
        if os.path.isdir(src):
            found = list_images(src, extensions)
        elif os.path.isfile(src) and os.path.splitext(src)[1].lower() in extensions:
            found = [src]
        elif os.path.isfile(src):
            raise FileNotFoundError(f"image format not allowed (not PNG): {src!r}")
        else:
            raise FileNotFoundError(f"not an image or a folder: {src!r}")
        for f in found:
            real = os.path.normcase(os.path.realpath(f))
            if real not in seen:
                seen.add(real)
                files.append(f)
    if not files:
        raise FileNotFoundError("no usable image in the image bank")
    return files


def _output_names(files):
    """Base names for the output images, always .png (a photo.jpg gives photo.png);
    duplicates (same name, different folders or formats) get a suffix:
    image.png, image_2.png..."""
    names, used = [], set()
    for f in files:
        stem = os.path.splitext(os.path.basename(f))[0]
        ext = ".png"
        out, i = stem + ext, 2
        while out.lower() in used:
            out, i = f"{stem}_{i}{ext}", i + 1
        used.add(out.lower())
        names.append(out)
    return names


class _Progress:
    """Progress of fog(), as a fraction of the estimated work.

    Weights measured on real runs (time per unit, relative to fingerprinting a
    pixel): loading 3 per pixel, fingerprinting 1, writing 14 (PNG compression),
    hiding 250 per bit (pure Python).
    The callback gets (stage, fraction); stages: "load", "prepare", "embed", "save".
    It may raise an exception to cancel (fog writes nothing before "save").
    """
    WEIGHTS = {"load": 3, "prepare": 1, "embed": 250, "save": 14}

    def __init__(self, callback, pixels, bits):
        self.callback = callback
        w = self.WEIGHTS
        self.total = max(1, pixels * (w["load"] + w["prepare"] + w["save"]) + bits * w["embed"])
        self.done = 0

    def advance(self, stage, units=0):
        self.done += units * self.WEIGHTS[stage]
        if self.callback:
            self.callback(stage, min(1.0, self.done / self.total))


@_memory_guard
def fog(key: str, message: str, image_bank, destination_folder: str,
        extension: str = None, store_nonce: bool = True, name: str = None,
        progress=None, extensions=NATIVE_EXTENSIONS):
    """Hide the file `message` in the PNGs of `image_bank`, write them to `destination_folder`.

    `image_bank` is a folder, or a list of folders and / or PNG files (see
    collect_images). The file name and extension are taken from `message` and
    stored in the hidden data. `extension` (without dot) and `name` (without
    extension) override them; characters invalid in file names are replaced by "_".
    `progress(stage, fraction)` is called along the way (see _Progress).
    `extensions`: input formats allowed (see extensions_for); non-PNG images are
    decoded (and turned upright from their EXIF orientation), the output is PNG.
    Returns (embedded_bytes, nonce_base64).
    """
    files = collect_images(image_bank, extensions)
    for f in files:
        if _same_path(os.path.dirname(os.path.abspath(f)), destination_folder):
            raise ValueError("destination folder must differ from the image bank "
                             "(it would overwrite the source images)")
    pixels = [check_image(f) for f in files]
    tracker = _Progress(progress, sum(pixels), required_bits(message, extension, name))
    tracker.advance("load")
    images = []
    for f, px in zip(files, pixels):
        img = open_image(f)
        if os.path.splitext(f)[1].lower() not in NATIVE_EXTENSIONS:
            img = ImageOps.exif_transpose(img)   # photos: same orientation as displayed
        images.append(_normalize(img))
        tracker.advance("load", px)
    order = _canonical_order(images, lambda i: tracker.advance("prepare", pixels[i]))
    imgset = ImageSet([images[i] for i in order])

    with open(message, "rb") as fh:
        data = fh.read()
    stem, dot_ext = os.path.splitext(os.path.basename(message))
    if extension is None:
        extension = dot_ext[1:]
    extension = extension.lstrip(".")
    name = _clean_name(stem if name is None else name)

    nonce = get_random_bytes(NONCE_LEN)
    cipher_key, mac_key = derive_keys(key, nonce)
    flag, body = build_payload(extension, name, data, mac_key)

    nbits = 1 + 8 * len(body)
    if nbits > imgset.total:
        raise ValueError(f"message needs {nbits} bits but the images only offer "
                         f"{imgset.total} pixels (1 bit per pixel)")

    positions = position_stream(Keystream(cipher_key, nonce), imgset.total)
    step = max(1, nbits // 200)          # about 200 progress updates
    for i, bit in enumerate(payload_bits(flag, body), 1):
        imgset.write_bit(next(positions), bit)
        if i % step == 0:
            tracker.advance("embed", step)
    tracker.advance("embed", nbits % step)

    tracker.advance("save")              # from here on, files are written
    os.makedirs(destination_folder, exist_ok=True)
    snonce = base64.b64encode(nonce).decode("ascii")
    for out_name, img, px in zip(_output_names(files), images, pixels):
        meta = None
        if store_nonce:
            meta = PngInfo()
            meta.add_text(NONCE_KEY, snonce)
        img.save(os.path.join(destination_folder, out_name), "PNG", pnginfo=meta)
        tracker.advance("save", px)

    return (nbits + 7) // 8, snonce


# --------------------------------------------------------------------------
# Extract
# --------------------------------------------------------------------------
def _write_unique(path: str, data: bytes) -> str:
    """Write `data` to `path`, or to `name (1).ext`, `name (2).ext`... if it exists.

    Never overwrites an existing file. Returns the path actually used.
    """
    root, ext = os.path.splitext(path)
    candidate, i = path, 0
    while True:
        try:
            with open(candidate, "xb") as fh:
                fh.write(data)
            return candidate
        except FileExistsError:
            i += 1
            candidate = f"{root} ({i}){ext}"


class _WindProgress:
    """Progress of wind(); stages: "load", "prepare", "read", "write".

    The size of the hidden file is only known after its header is read (all the
    images must be loaded first), so the bar starts with an estimate (loading
    and ordering = PIXEL_SHARE of the work) and is re-scaled on the remaining part when
    the size is known: it never goes backwards. Same weights as _Progress
    (reading a bit costs about as much as hiding one).
    """
    WEIGHTS = {"load": 3, "prepare": 1, "read": 250 * 8, "write": 0}   # read: per byte
    PIXEL_SHARE = 0.15   # if the hidden file is small, the bar simply jumps forward

    def __init__(self, callback, pixels):
        self.callback = callback
        pixel_work = pixels * (self.WEIGHTS["load"] + self.WEIGHTS["prepare"])
        self.total = max(1, int(pixel_work / self.PIXEL_SHARE))
        self.done = 0
        self.base, self.base_done = 0.0, 0

    def fraction(self):
        rest = max(1, self.total - self.base_done)
        return min(1.0, self.base + (1 - self.base) * (self.done - self.base_done) / rest)

    def advance(self, stage, units=0):
        self.done += units * self.WEIGHTS[stage]
        if self.callback:
            self.callback(stage, self.fraction())

    def set_data_size(self, nbytes):
        self.base, self.base_done = self.fraction(), self.done
        self.total = self.done + max(1, nbytes * self.WEIGHTS["read"])

    def finish(self, stage):
        if self.callback:
            self.callback(stage, 1.0)


@_memory_guard
def wind(key: str, directory, outputdirectory: str,
         output_name: str = None, nonce: str = None, progress=None) -> str:
    """Recover the hidden file from the PNGs of `directory`: a folder, or a list of
    folders and / or PNG files (see collect_images).

    The file is written with its original name and extension. `output_name`
    (without extension) replaces the original name; if no name was stored, "out"
    is used. An existing file is never overwritten: a number is added instead.
    `nonce` (base64) is only needed when the metadata was stripped or not stored.
    `progress(stage, fraction)` is called along the way (see _WindProgress); it
    may raise an exception to cancel (nothing is written before "write").
    Returns the output path.
    """
    files = collect_images(directory)
    pixels = [check_image(f) for f in files]
    tracker = _WindProgress(progress, sum(pixels))
    tracker.advance("load")
    opened = [open_image(f) for f in files]   # lazy: only the headers are read here
    found = {getattr(im, "text", {}).get(NONCE_KEY) for im in opened} - {None}
    if nonce is None:
        if not found:
            raise ValueError("no nonce in the image metadata; pass it explicitly (--nonce)")
        if len(found) > 1:
            raise ValueError("images carry different nonces (not from the same hiding run)")
        nonce = found.pop()
    try:
        nonce_b = base64.b64decode(nonce, validate=True)
    except (binascii.Error, ValueError):
        raise ValueError("nonce is not valid base64") from None
    if len(nonce_b) != NONCE_LEN:
        raise ValueError(f"nonce must be {NONCE_LEN} bytes")

    images = []
    for im, px in zip(opened, pixels):
        images.append(_normalize(im))
        tracker.advance("load", px)
    order = _canonical_order(images, lambda i: tracker.advance("prepare", pixels[i]))
    imgset = ImageSet([images[i] for i in order])

    cipher_key, mac_key = derive_keys(key, nonce_b)
    positions = position_stream(Keystream(cipher_key, nonce_b), imgset.total)
    reader = _BitReader(imgset, positions, on_bytes=lambda n: tracker.advance("read", n))
    ext, name, data = parse_payload(reader, mac_key, on_size=tracker.set_data_size)

    tracker.advance("write")             # from here on, the file is written
    os.makedirs(outputdirectory, exist_ok=True)
    base = output_name if output_name is not None else (name or "out")
    filename = base + ("." + ext if ext else "")
    path = _write_unique(os.path.join(outputdirectory, filename), data)
    tracker.finish("write")
    return path


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m fog", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("hide", help="hide a file in a set of PNGs")
    h.add_argument("message")
    h.add_argument("image_bank", help="folder of PNG images, or one PNG image")
    h.add_argument("--add", action="append", default=[], metavar="SOURCE",
                   help="another folder or PNG image for the bank (repeatable)")
    h.add_argument("--convert", default="", metavar="FORMATS",
                   help="also use these image formats, converted to PNG: "
                        + ",".join(CONVERTIBLE_FORMATS) + " (e.g. --convert jpg,webp)")
    h.add_argument("destination")
    h.add_argument("--key")
    h.add_argument("--name", help="file name (without extension) to record (default: from the file)")
    h.add_argument("--ext", help="file extension to record (default: from the file name)")
    h.add_argument("--no-nonce-metadata", action="store_true",
                   help="do not write the nonce into the PNGs (it is printed instead)")

    e = sub.add_parser("extract", help="recover the hidden file")
    e.add_argument("directory", help="folder of the produced PNG images, or one PNG image")
    e.add_argument("--add", action="append", default=[], metavar="SOURCE",
                   help="another folder or PNG image of the set (repeatable)")
    e.add_argument("output_directory")
    e.add_argument("--output-name",
                   help="name (without extension) to use instead of the original file name")
    e.add_argument("--nonce", help="base64 nonce, if the metadata was stripped")
    e.add_argument("--key")

    args = ap.parse_args(argv)
    key = args.key or getpass.getpass("Key: ")

    try:
        if args.cmd == "hide":
            exts = extensions_for(f for f in args.convert.split(",") if f.strip())
            for f, (w, h) in large_images([args.image_bank, *args.add], exts):
                print(f"Warning: {os.path.basename(f)} is very large ({w} x {h} pixels): "
                      f"it needs at least {w * h * BYTES_PER_PIXEL / 2**30:.1f} GB of memory "
                      f"and can be slow.", file=sys.stderr)
            n, snonce = fog(key, args.message, [args.image_bank, *args.add], args.destination,
                            extensions=exts,
                            extension=args.ext, store_nonce=not args.no_nonce_metadata,
                            name=args.name)
            print(f"Hidden {n} bytes (including header) in {args.destination}/")
            if args.no_nonce_metadata:
                print(f"Nonce (keep it, needed to extract): {snonce}")
        else:
            path = wind(key, [args.directory, *args.add], args.output_directory,
                        args.output_name, args.nonce)
            print(f"Recovered file written to {path}")
    except (ValueError, OSError) as exc:   # OSError: missing or unreadable file
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
