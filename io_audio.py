"""Audio I/O for DawlessGPTv6.

This module handles writing 24‑bit little‑endian PCM WAV files with TPDF
dither and proper header fields.  Reading audio is not currently required
but could be added in future PRs for analysis or sample playback.

TODOs:
    [X] Implement WAV writing with 24‑bit conversion and TPDF dither.
    [ ] Implement optional dithering types and noise shaping.
    [ ] Add WAV reading for analysis or reuse.

"""

from __future__ import annotations

import os
import struct
import wave
import random
from pathlib import Path
from typing import List


def _tpdf_dither() -> float:
    """Generate a single TPDF dither sample in the range [-1, 1]."""
    return (random.random() - random.random())


def float_to_int24(sample: float) -> bytes:
    """Convert a floating point sample (-1 to 1) to 24‑bit signed little‑endian."""
    # Clamp sample to [-1, 1]
    clamped = max(-1.0, min(1.0, sample))
    # Scale to 24‑bit signed integer range
    int_sample = int(clamped * 0x7FFFFF)
    return struct.pack('<i', int_sample)[0:3]  # take lowest 3 bytes (little‑endian)


def write_wav(samples: List[float], sample_rate: int, path: Path, dither: bool = True) -> None:
    """Write a list of floating point samples to a 24‑bit PCM WAV file.

    Parameters
    ----------
    samples : list of float
        Normalised audio samples in the range [-1, 1].
    sample_rate : int
        Sample rate in Hz.
    path : Path
        Output file path (will be created or overwritten).
    dither : bool, optional
        Whether to apply TPDF dither when converting to 24‑bit.
    """
    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(1)  # mono for now; future work could support stereo
        wf.setsampwidth(3)  # 24 bits = 3 bytes
        wf.setframerate(sample_rate)
        frames = bytearray()
        for sample in samples:
            val = sample
            if dither:
                val += _tpdf_dither() / (2 ** 24)
            frames.extend(float_to_int24(val))
        wf.writeframes(frames)