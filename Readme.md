# Fog-project

Hide **any file** (zip, txt, mp4, ...) inside a bank of PNG images, at secret, key-dependent pseudo-random positions.

## Installation

```
pip install pillow pycryptodome
```

## Usage

### Hide a file

```
python fast-fog.py hide message.zip bank/ output/
```

- `message.zip`: the file to hide (any type, no need to zip it).
- `bank/`: folder containing the `.png` images used as cover. Every image must be different from the others.
- `output/`: folder where the new images are written (it must differ from the bank).
- The key (password) is asked at the prompt, or given with `--key`.

Then send **all the images of the output folder** to the receiver, and give them the key through another channel. The message length no longer needs to be sent: it is stored inside the hidden data.

Options:

| Option | Effect |
|-|-|
| `--key KEY` | Give the key on the command line instead of the prompt |
| `--ext EXT` | Record this extension instead of the one in the file name |
| `--no-nonce-metadata` | Do not write the nonce in the PNG metadata; it is printed instead (see below) |

### Recover a file

```
python fast-fog.py extract output/ result/
```

The file is written as `result/out.<extension>` (for example `out.zip`, `out.mp4`, or just `out` if the original had no extension).

Options:

| Option | Effect |
|-|-|
| `--key KEY` | Give the key on the command line instead of the prompt |
| `--nonce B64` | Nonce to use when the metadata was stripped or not stored |
| `--output-name NAME` | Base name of the recovered file (default: `out`) |

### Python

The hyphen in `fast-fog.py` prevents a plain `import`, so load the file explicitly (or rename it `fast_fog.py` and use `from fast_fog import fog, wind`):

```python
import importlib.util

spec = importlib.util.spec_from_file_location("fast_fog", "fast-fog.py")
fast_fog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fast_fog)

nbytes, nonce = fast_fog.fog("my key", "message.zip", "bank", "output")   # hide
path = fast_fog.wind("my key", "output", "result")                        # recover
```

`fog(key, message, image_bank, destination, extension=None, store_nonce=True)` returns the number of embedded bytes and the nonce (base64).
`wind(key, directory, outputdirectory, output_name="out", nonce=None)` returns the path of the recovered file.

## Warnings

- **Use exactly the images that were produced.** The folder given to `extract` must contain only those PNGs. A missing or extra image gives an error (`no valid hidden data found`). File names and listing order do not matter, so renaming files is fine.
- **Images must stay lossless PNG and unmodified.** JPEG conversion, resizing, screenshots, filters or re-compression destroy the data. The program detects it and refuses to output a corrupted file.
- **Metadata can be stripped by some platforms** (messengers, social networks). If that is a risk, hide with `--no-nonce-metadata`, keep the printed nonce, and give it to `extract` with `--nonce`. Without the nonce the message cannot be recovered.
- **Capacity is 1 bit per pixel**, minus a fixed overhead of a little over 22 bytes (type, size, authentication tag). The program stops with an error if the message does not fit.
- **Choose a long passphrase.** The key is the only secret.

## Objectives

The goal of this project is to hide a file of any type into a bank of images, so that it can only be found with the key.

The program has two main functions:
- `fog`: hide the message
- `wind`: uncover the message

## How does it work?

### 1. Keys

A random 24-byte nonce is drawn. The key is stretched with scrypt (salt = nonce) into 64 bytes: 32 bytes for XChaCha20 and 32 bytes for an HMAC.

### 2. Image order

Images are sorted by the SHA-256 of their pixel data with the red least-significant bits cleared. Embedding does not change this value, so the receiver gets the same order without needing file names or metadata. All images are then seen as one long run of pixels.

### 3. What is hidden

The hidden data is a bit stream:

```
[flag: 1 bit] [file type] [message size] [tag: 16 bytes] [data]
```

| Field | Content |
|-|-|
| Flag | `0` = standard (extension is exactly 3 bytes), `1` = non-standard |
| File type, standard | The 3 extension bytes |
| File type, non-standard | letter, extension length (ASCII digits), letter, then the extension bytes |
| Message size | letter, size in bytes (ASCII digits), letter |
| Tag | HMAC-SHA256 of flag, extension and data, truncated to 16 bytes |
| Data | The file content |

The delimiter letters are random `a-z`, digits are `0-9`, so each field ends unambiguously. A file with no extension is non-standard with length `0`. The extension is the text after the last dot (`a.tar.gz` is stored as `gz`), at most 255 bytes.

### 4. Where it is hidden

The XChaCha20 keystream drives a partial Fisher-Yates shuffle over all the pixels of all the images. This gives a secret sequence of distinct positions, so no two bits ever share a pixel. Bit number *i* of the stream goes into the red least-significant bit of the pixel at position number *i*. Nothing else in the images changes.

The j-th position does not depend on the message length, so the receiver can read the header first, learn the size, then read exactly the rest.

### 5. The nonce

By default the nonce is stored in each PNG as a `Nonce` text chunk. With `--no-nonce-metadata` it is only printed.

### 6. Recovering

The receiver rebuilds the same image order, the same keys and the same positions, reads the bits, then recomputes the HMAC. If it does not match (wrong key, wrong or incomplete images, modified images), the program stops with an error instead of writing a corrupted file.

## Why?

I think it is an interesting means of obfuscation: positions come from a cryptographically secure pseudo-random generator, so without the key the information is simply lost in the bank of images.

It sits between encryption and obfuscation: the message itself is not encrypted, but it is hidden at secret positions and authenticated.

What someone can see without the key:
- the nonce, if it is stored in the metadata (it is not secret and does not help without the key)
- the set of images

The size, the file type and the image order are not stored in the metadata any more; they are inside the hidden data or derived from the pixels.

The best way to recover the message is to find or guess the key. Otherwise it is out of reach.

### Limits

- This is classic LSB steganography: statistical analysis of the images can reveal that they were modified, even without knowing where.
- The hidden bits are not encrypted. Their confidentiality rests on the secrecy of the positions.
