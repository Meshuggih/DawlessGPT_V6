"""Utility functions for DawlessGPTv6.

This module houses helper functions used across the codebase, including
plan validation against the JSON schema, configuration loading from YAML,
VarLen encoding for MIDI, bank merging and safe gain calculations.  The
validation implementation here is naive and should be replaced with a
proper JSON Schema validator when allowed.  YAML parsing uses the built‑in
`yaml` module if available; otherwise a minimal parser is provided.

TODOs:
    [X] Implement simple schema validation by checking required keys exist.
    [ ] Use a full JSON schema validator (e.g. `jsonschema`) when permitted.
    [ ] Implement bank merging and CC mapping ingestion.
    [ ] Add curve helpers (exponential/logarithmic/S) used in automation.
    [ ] Provide safe gain calculations to avoid clipping when mixing.

"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Any, List

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # YAML parsing will fall back to a simple parser


SCHEMA_PATH = Path(os.environ.get("SCHEMA_PATH", "schema.json"))
CONFIG_PATH = Path(os.environ.get("CONFIG_PATH", "config.yaml"))


def load_schema() -> Dict[str, Any]:
    """Load the JSON schema from disk."""
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_config() -> Dict[str, Any]:
    """Load the YAML configuration from disk.

    Falls back to a minimal parser if the `yaml` module is unavailable.
    """
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        if yaml is not None:
            return yaml.safe_load(f)
        # Minimal YAML parser: handle simple key: value pairs and nested
        config: Dict[str, Any] = {}
        current_dict = config
        stack: List[Dict[str, Any]] = []
        indent_levels: List[int] = []
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            indent = len(line) - len(line.lstrip(' '))
            key, _, value = stripped.partition(':')
            key = key.strip()
            value = value.strip()
            if not value:
                # Nested dict
                new_dict: Dict[str, Any] = {}
                current_dict[key] = new_dict
                stack.append(current_dict)
                indent_levels.append(indent)
                current_dict = new_dict
            else:
                # Parse simple types
                if value.lower() in ['true', 'false']:
                    parsed: Any = value.lower() == 'true'
                elif value.isdigit():
                    parsed = int(value)
                else:
                    try:
                        parsed = float(value)
                    except ValueError:
                        parsed = value
                current_dict[key] = parsed
            # Pop back when indent decreases
            while indent_levels and indent < indent_levels[-1]:
                current_dict = stack.pop()
                indent_levels.pop()
        return config


def validate_plan(plan: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """Validate a plan against the JSON schema.

    The validation is rudimentary: it checks that all required keys listed in
    the schema are present in the plan.  It does not perform type
    validation or nested checks.  Future versions should integrate a JSON
    Schema validator for full compliance.
    """
    required = schema.get("required", [])
    missing = [key for key in required if key not in plan]
    if missing:
        raise ValueError(f"Plan missing required fields: {', '.join(missing)}")


def load_plan(path: Path) -> Dict[str, Any]:
    """Load a plan JSON file from disk."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)