"""Report writer for DawlessGPTv6.

This module assembles a Markdown report describing the session.  The report
includes the manifest (seed, duration, quality), metrics from analysis,
macros used from the arrangement playbook and a summary of auto‑completed
fields.  The current implementation writes a basic report; future PRs
should enrich it with more detailed charts and visuals.

TODOs:
    [X] Implement a simple Markdown report generator.
    [ ] Embed charts of automation curves and spectral content.
    [ ] Reference user banks and macros utilised during rendering.

"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


def write_report(plan: Dict[str, Any], output_path: Path) -> None:
    """Generate a Markdown report for the session.

    Parameters
    ----------
    plan : dict
        The completed plan including analysis metrics and completions.
    output_path : Path
        Where to write the Markdown report.
    """
    seed = plan.get("seed", "n/a")
    quality = plan.get("quality", "n/a")
    length_bars = plan.get("length_bars", "n/a")
    metrics = plan.get("metrics", {})
    completions = plan.get("completions", {})
    # Compose Markdown
    lines = []
    lines.append(f"# DawlessGPTv6 Session Report\n")
    lines.append(f"**Seed:** {seed}  ")
    lines.append(f"**Quality:** {quality}  ")
    lines.append(f"**Length (bars):** {length_bars}\n")
    lines.append("## Metrics\n")
    for k, v in metrics.items():
        lines.append(f"- **{k}:** {v}")
    lines.append("\n## Auto‑completed Fields\n")
    if completions:
        for k, v in completions.items():
            lines.append(f"- **{k}:** {v} [HYPOTHÈSE] (Confiance: Élevé)")
    else:
        lines.append("No fields were auto‑completed.")
    lines.append("\n## Notes\n")
    lines.append("Ce rapport est généré automatiquement par DawlessGPTv6. Les valeurs auto‑complétées sont notées comme des hypothèses.\n")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))