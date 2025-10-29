"""Auto‑completion engine for DawlessGPTv6.

This module is responsible for filling in any missing fields of a user plan
until it matches the FULL_SPEC defined in `schema.json`.  It also returns a
record of what fields were auto‑generated so that the GPT can annotate
responses appropriately.  The current implementation is deliberately simple
and should be expanded in future PRs to include musical heuristics and
playbook macros.

TODOs:
    [X] Implement basic auto‑completion for mandatory fields (bpm, time signature,
        length_bars, tracks, quality).
    [ ] Implement harmonic progression generation using musical theory.
    [ ] Auto‑generate drum patterns and automation curves based on style and energy.
    [ ] Persist completions to a log via `sqlite_log.py`.

"""

from __future__ import annotations

import random
from typing import Dict, Any, Tuple

def complete_plan(plan: Dict[str, Any], schema: Dict[str, Any], config: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Fill missing fields in the plan according to the schema and config.

    Parameters
    ----------
    plan : dict
        The original user plan, possibly incomplete.
    schema : dict
        Loaded JSON schema describing required and optional fields.
    config : dict
        Immutable rails from `config.yaml` used for defaults.

    Returns
    -------
    tuple
        A tuple containing the completed plan and a dictionary of
        completions where each key indicates a field that was filled in.
    """
    completions: Dict[str, Any] = {}

    # Basic defaults
    if "bpm" not in plan:
        plan["bpm"] = 120
        completions["bpm"] = 120
    if "time_signature" not in plan:
        plan["time_signature"] = "4/4"
        completions["time_signature"] = "4/4"
    if "length_bars" not in plan:
        plan["length_bars"] = 32
        completions["length_bars"] = 32
    if "quality" not in plan:
        plan["quality"] = "hq"
        completions["quality"] = "hq"

    # Ensure at least one track exists
    if "tracks" not in plan or not plan["tracks"]:
        plan.setdefault("tracks", {})
        plan["tracks"]["track1"] = {
            "instrument_type": "pad",
            "events": []
        }
        completions["tracks"] = "added default pad track"

    # Harmony defaults
    if "root_midi" not in plan:
        plan["root_midi"] = 60  # C4
        completions["root_midi"] = 60
    if "scale" not in plan:
        plan["scale"] = "minor"
        completions["scale"] = "minor"
    if "mode" not in plan:
        plan["mode"] = "ionian"
        completions["mode"] = "ionian"

    # Placeholder for progression and arp rules
    if "progression" not in plan:
        plan["progression"] = [1, 5, 6, 4]
        completions["progression"] = "default I‑V‑vi‑IV progression"
    if "arp_rules" not in plan:
        plan["arp_rules"] = {"range": 1, "direction": "up", "gate": 0.8}
        completions["arp_rules"] = "default arp rules"

    # Default drum patterns (very basic four‑on‑the‑floor)
    if "drums" not in plan:
        length = plan.get("length_bars", 32) * 16  # 16 steps per bar
        kick = [1 if i % 16 == 0 else 0 for i in range(length)]
        snare = [1 if i % 16 == 8 else 0 for i in range(length)]
        hats = [1 if i % 4 == 0 else 0 for i in range(length)]
        plan["drums"] = {"kick": kick, "snare": snare, "hats": hats}
        completions["drums"] = "default four‑on‑the‑floor patterns"

    # Return completed plan and completion log
    return plan, completions