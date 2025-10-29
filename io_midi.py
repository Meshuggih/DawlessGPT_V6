"""MIDI file I/O for DawlessGPTv6.

This module exports Standard MIDI Files (SMF) of Type‑1.  It writes meta
events for tempo (0x51) and time signature (0x58), note on/off events and
generic control change (CC) or NRPN messages.  Only a minimal subset of the
MIDI specification is implemented here.  For more complete support,
consider using the `mido` package (not allowed in this project) or
implementing the full SMF format manually.

TODOs:
    [X] Implement basic SMF Type‑1 writer with tempo and time signature.
    [ ] Support CC/NRPN export based on `cc_maps.json`.
    [ ] Write multiple tracks and proper channel assignment.
    [ ] Implement delta time calculation with running status optimisation.

"""

from __future__ import annotations

import struct
import math
from pathlib import Path
from typing import Dict, Any, List


def _varlen(value: int) -> bytes:
    """Encode an integer as a variable‑length quantity (7 bits per byte)."""
    buffer = value & 0x7F
    result = bytearray([buffer])
    value >>= 7
    while value:
        buffer = (value & 0x7F) | 0x80
        result.insert(0, buffer)
        value >>= 7
    return bytes(result)


def _write_meta_event(delta: int, meta_type: int, data: bytes) -> bytes:
    return _varlen(delta) + bytes([0xFF, meta_type]) + _varlen(len(data)) + data


def _note_on(delta: int, channel: int, note: int, velocity: int) -> bytes:
    return _varlen(delta) + bytes([0x90 | (channel & 0x0F), note & 0x7F, velocity & 0x7F])


def _note_off(delta: int, channel: int, note: int, velocity: int) -> bytes:
    return _varlen(delta) + bytes([0x80 | (channel & 0x0F), note & 0x7F, velocity & 0x7F])


def export_midi(plan: Dict[str, Any], path: Path) -> None:
    """Export a MIDI Type‑1 file from a fully specified plan.

    The current implementation writes a single track containing tempo and
    time signature meta events plus note events extracted from the plan
    events.  Future work should separate tracks and channels.
    """
    bpm = plan.get("bpm", 120)
    time_signature = plan.get("time_signature", "4/4").split('/')
    numerator = int(time_signature[0])
    denominator = int(time_signature[1])
    ticks_per_beat = 480  # PPQN (pulses per quarter note)
    events = plan.get("events", [])
    # Sort events by time for correct ordering
    events_sorted = sorted(events, key=lambda e: e["time"])
    # Convert time in seconds to ticks
    seconds_per_beat = 60.0 / bpm
    def sec_to_ticks(sec: float) -> int:
        return int(sec / seconds_per_beat * ticks_per_beat)
    # Build track data
    track_data = bytearray()
    # Tempo meta event (microseconds per quarter note)
    mpqn = int(60_000_000 / bpm)
    track_data += _write_meta_event(0, 0x51, struct.pack('>I', mpqn)[1:])
    # Time signature meta event
    track_data += _write_meta_event(0, 0x58, bytes([numerator, int(math.log2(denominator)), 24, 8]))
    # Note events
    last_tick = 0
    for event in events_sorted:
        start_tick = sec_to_ticks(event["time"])
        delta = start_tick - last_tick
        note = event.get("note", 60)
        velocity = int(event.get("velocity", 1.0) * 127)
        duration_tick = sec_to_ticks(event.get("duration", 1.0))
        # Note on
        track_data += _note_on(delta, 0, note, velocity)
        # Note off
        track_data += _note_off(duration_tick, 0, note, 0)
        last_tick = start_tick + duration_tick
    # End of track meta event
    track_data += _write_meta_event(0, 0x2F, b"")
    # Build MIDI file structure
    with open(path, 'wb') as f:
        # Header chunk
        f.write(b"MThd")
        f.write(struct.pack('>I', 6))  # header length
        f.write(struct.pack('>H', 1))  # format type 1
        f.write(struct.pack('>H', 1))  # one track
        f.write(struct.pack('>H', ticks_per_beat))  # division
        # Track chunk
        f.write(b"MTrk")
        f.write(struct.pack('>I', len(track_data)))
        f.write(track_data)