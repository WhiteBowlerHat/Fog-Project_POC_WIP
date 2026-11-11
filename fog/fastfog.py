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
from PIL import Image
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


def _canonical_order(images):
    """Indices of `images` sorted by fingerprint; identical images are rejected."""
    prints = [_fingerprint(im) for im in images]
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


def payload_bits(flag: int, body: bytes):
    yield flag
    for byte in body:
        for shift in range(7, -1, -1):
            yield (byte >> shift) & 1


class _BitReader:
    def __init__(self, imgset: ImageSet, positions):
        self._set = imgset
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
        return bytes(self.byte() for _ in range(n))


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


def parse_payload(r: _BitReader, mac_key: bytes):
    """Read and authenticate the payload. Returns (extension, name, data)."""
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
def fog(key: str, message: str, image_bank: str, destination_folder: str,
        extension: str = None, store_nonce: bool = True, name: str = None):
    """Hide the file `message` in the PNGs of `image_bank`, write them to `destination_folder`.

    The file name and extension are taken from `message` and stored in the hidden
    data. `extension` (without dot) and `name` (without extension) override them;
    characters invalid in file names are replaced by "_".
    Returns (embedded_bytes, nonce_base64).
    """
    if os.path.realpath(image_bank) == os.path.realpath(destination_folder):
        raise ValueError("destination folder must differ from the image bank")

    files = sorted(glob.glob(os.path.join(image_bank, "*.png")))
    if not files:
        raise FileNotFoundError(f"no .png files in {image_bank!r}")
    images = [_normalize(Image.open(f)) for f in files]
    order = _canonical_order(images)
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
    for bit in payload_bits(flag, body):
        imgset.write_bit(next(positions), bit)

    os.makedirs(destination_folder, exist_ok=True)
    snonce = base64.b64encode(nonce).decode("ascii")
    for path, img in zip(files, images):
        meta = None
        if store_nonce:
            meta = PngInfo()
            meta.add_text(NONCE_KEY, snonce)
        img.save(os.path.join(destination_folder, os.path.basename(path)),
                 "PNG", pnginfo=meta)

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


def wind(key: str, directory: str, outputdirectory: str,
         output_name: str = None, nonce: str = None) -> str:
    """Recover the hidden file from the PNGs in `directory`.

    The file is written with its original name and extension. `output_name`
    (without extension) replaces the original name; if no name was stored, "out"
    is used. An existing file is never overwritten: a number is added instead.
    `nonce` (base64) is only needed when the metadata was stripped or not stored.
    Returns the output path.
    """
    files = sorted(glob.glob(os.path.join(directory, "*.png")))
    if not files:
        raise FileNotFoundError(f"no .png files in {directory!r}")

    opened = [Image.open(f) for f in files]
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

    images = [_normalize(im) for im in opened]
    order = _canonical_order(images)
    imgset = ImageSet([images[i] for i in order])

    cipher_key, mac_key = derive_keys(key, nonce_b)
    positions = position_stream(Keystream(cipher_key, nonce_b), imgset.total)
    ext, name, data = parse_payload(_BitReader(imgset, positions), mac_key)

    os.makedirs(outputdirectory, exist_ok=True)
    base = output_name if output_name is not None else (name or "out")
    filename = base + ("." + ext if ext else "")
    return _write_unique(os.path.join(outputdirectory, filename), data)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m fog", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("hide", help="hide a file in a set of PNGs")
    h.add_argument("message")
    h.add_argument("image_bank")
    h.add_argument("destination")
    h.add_argument("--key")
    h.add_argument("--name", help="file name (without extension) to record (default: from the file)")
    h.add_argument("--ext", help="file extension to record (default: from the file name)")
    h.add_argument("--no-nonce-metadata", action="store_true",
                   help="do not write the nonce into the PNGs (it is printed instead)")

    e = sub.add_parser("extract", help="recover the hidden file")
    e.add_argument("directory")
    e.add_argument("output_directory")
    e.add_argument("--output-name",
                   help="name (without extension) to use instead of the original file name")
    e.add_argument("--nonce", help="base64 nonce, if the metadata was stripped")
    e.add_argument("--key")

    args = ap.parse_args(argv)
    key = args.key or getpass.getpass("Key: ")

    try:
        if args.cmd == "hide":
            n, snonce = fog(key, args.message, args.image_bank, args.destination,
                            extension=args.ext, store_nonce=not args.no_nonce_metadata,
                            name=args.name)
            print(f"Hidden {n} bytes (including header) in {args.destination}/")
            if args.no_nonce_metadata:
                print(f"Nonce (keep it, needed to extract): {snonce}")
        else:
            path = wind(key, args.directory, args.output_directory,
                        args.output_name, args.nonce)
            print(f"Recovered file written to {path}")
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
