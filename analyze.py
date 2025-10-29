"""Audio analysis for DawlessGPTv6.

This module computes simple loudness and dynamic range metrics for a rendered
audio buffer.  The current implementation calculates peak amplitude, root
mean square (RMS), crest factor and a rough approximation of LUFS using a
static K‑weighting filter approximation.  Future PRs should implement a
more accurate LUFS calculation per EBU R 128.

TODOs:
    [X] Implement basic peak, RMS and crest factor analysis.
    [ ] Implement a proper K‑weighting filter for LUFS approximation.
    [ ] Output additional metrics such as dynamic range and spectral centroid.

"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, Any, List


def _rms(samples: List[float]) -> float:
    return math.sqrt(sum(x * x for x in samples) / max(1, len(samples)))


def _crest_factor(samples: List[float]) -> float:
    rms_val = _rms(samples)
    if rms_val == 0:
        return 0.0
    peak = max(abs(x) for x in samples)
    return peak / rms_val


def _approx_lufs(samples: List[float]) -> float:
    """Approximate LUFS by applying a simple K‑weighting.  Not accurate."""
    # Simple weighting: emphasise mid frequencies; ignore proper filter
    weighted = [x * 0.85 for x in samples]
    rms_val = _rms(weighted)
    if rms_val <= 0:
        return -float('inf')
    return 20 * math.log10(rms_val)


def analyze_audio(plan: Dict[str, Any], output_path: Path) -> None:
    """Analyze the rendered WAV and write metrics to a JSON file.

    Parameters
    ----------
    plan : dict
        Completed plan containing the path to the rendered WAV (under key
        `rendered_wav_path` or in the return value of `runner.run`).
    output_path : Path
        Where to store the resulting metrics JSON file.
    """
    # Locate WAV file
    wav_path = plan.get("rendered_wav_path")
    if wav_path is None:
        # Attempt default naming
        wav_path = Path("/mnt/data") / f"render_{plan.get('seed', 0)}.wav"
    # Read PCM samples as floats; fallback if file missing
    samples: List[float] = []
    try:
        import wave
        with wave.open(str(wav_path), 'rb') as wf:
            n_frames = wf.getnframes()
            raw = wf.readframes(n_frames)
            # Assume 24‑bit mono; convert to floats
            for i in range(0, len(raw), 3):
                int_sample = int.from_bytes(raw[i:i+3] + (b'\x00' if raw[i+2] < 0x80 else b'\xff'), byteorder='little', signed=True)
                samples.append(int_sample / 0x7FFFFF)
    except Exception:
        # If reading fails, return empty metrics
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        return
    # Compute metrics
    peak = max(abs(x) for x in samples) if samples else 0.0
    rms_val = _rms(samples)
    crest = _crest_factor(samples)
    lufs = _approx_lufs(samples)
    metrics = {
        "peak": peak,
        "rms": rms_val,
        "crest_factor": crest,
        "lufs_approx": lufs
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)