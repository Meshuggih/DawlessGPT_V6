"""Harmony utilities for DawlessGPTv6.

This module exposes helper functions for working with musical scales,
chords and arpeggios.  It provides basic major/minor scale definitions
and simple progression and arpeggiation generators.  In future PRs
additional modes, borrowed chords and voice leading should be added.

TODOs:
    [ ] Support additional scales/modes (Dorian, Phrygian, Lydian, etc.).
    [ ] Implement a more sophisticated chord progression generator.
    [ ] Consider voice‑leading rules for smoother transitions.

"""

from __future__ import annotations

from typing import List, Dict, Any

# Simple scale definitions: semitone offsets from the root
SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10]
}


def generate_progression(plan: Dict[str, Any]) -> None:
    """Generate a chord progression for the plan in‑place.

    If the plan already contains a progression, nothing is changed.  Future
    versions should create progressions based on style, emotion and
    structure.  Currently this function simply attaches the chosen scale
    semitone offsets to each degree of the provided progression.
    """
    if "progression_semitones" in plan:
        return
    root = plan.get("root_midi", 60)
    scale_name = plan.get("scale", "minor")
    scale = SCALES.get(scale_name, SCALES["minor"])
    progression = plan.get("progression", [1, 5, 6, 4])
    progression_semitones: List[int] = []
    for degree in progression:
        index = (degree - 1) % len(scale)
        semitone = scale[index]
        progression_semitones.append(root + semitone)
    plan["progression_semitones"] = progression_semitones


def generate_arp(plan: Dict[str, Any]) -> None:
    """Generate arpeggiation rules for each track.

    The current implementation does nothing beyond attaching the provided
    `arp_rules` to tracks if no explicit events exist.  In future versions
    this function will create note events based on arp rules.
    """
    # Placeholder: attach arp rules to tracks if events list is empty
    arp_rules = plan.get("arp_rules", {"range": 1, "direction": "up", "gate": 0.8})
    for track in plan.get("tracks", {}).values():
        if not track.get("events"):
            track["arp_rules"] = arp_rules.copy()