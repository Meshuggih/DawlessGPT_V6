"""Orchestrator for DawlessGPTv6.

This module coordinates the high‑level rendering pipeline.  It validates the
user’s plan against the schema, completes missing fields to reach a
FULL_SPEC via `completion.py`, schedules musical events using
`sequencer.py`, synthesises audio through `synth_engine.py`, applies
effects and mixing, writes the WAV to disk, logs decisions and returns the
path to the rendered file.  Additional operations (MIDI export, analysis,
reporting) are invoked via other CLI commands.

High‑level flow:

1. Validate and auto‑complete the input plan.
2. Generate harmonic structures (progressions, arpeggios) using `harmony.py`.
3. Schedule note and automation events via `sequencer.py` and
   `automation_engine.py`.
4. Render individual tracks via `synth_engine.py` using low‑level DSP
   primitives in `dsp_core.py`.
5. Apply FX (`fx_core.py`), mix and master (limiter, dither) using config rails.
6. Write the output WAV via `io_audio.py` and return the file path.

TODOs:
    [ ] Integrate REAL BLEP oscillators and ZDF filters for sound quality.
    [ ] Implement a proper scheduler with Euclidean rhythms and humanisation.
    [ ] Add logging of completions and decisions to SQLite via `sqlite_log.py`.

"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Any, List

# Local imports will be available when this file is loaded via sys.path by the GPT.
from completion import complete_plan
from harmony import generate_progression, generate_arp
from sequencer import schedule_events
from synth_engine import render_tracks
from fx_core import apply_fx
from io_audio import write_wav
from utils import validate_plan, load_schema, load_config


def run(plan: Dict[str, Any]) -> Path:
    """Validate, complete and render a plan to a WAV file.

    Parameters
    ----------
    plan : dict
        A potentially incomplete user plan.  Missing fields are filled
        automatically to reach FULL_SPEC before rendering.

    Returns
    -------
    Path
        Path to the rendered WAV file in `/mnt/data`.
    """
    # Load schema and config rails
    schema = load_schema()
    config = load_config()
    # Complete the plan to FULL_SPEC
    full_plan, completions = complete_plan(plan, schema, config)
    # Validate the completed plan
    validate_plan(full_plan, schema)
    # Generate harmony and arp sequences
    generate_progression(full_plan)
    generate_arp(full_plan)
    # Schedule events (notes, drums, automation)
    events: List[Dict[str, Any]] = schedule_events(full_plan)
    # Render audio for each track
    tracks_audio = render_tracks(full_plan, events, config)
    # Apply FX and mix/master
    mixed_audio = apply_fx(tracks_audio, full_plan, config)
    # Export WAV
    output_name = f"render_{full_plan.get('seed', 0)}.wav"
    output_path = Path("/mnt/data") / output_name
    write_wav(mixed_audio, config["sample_rate"], output_path)
    # TODO: log completions and decisions via sqlite_log
    return output_path