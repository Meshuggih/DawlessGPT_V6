"""Command‑line interface for DawlessGPTv6.

This module exposes a simple CLI that allows users to render WAV files, export
MIDI/CC data, analyze audio and generate reports.  It is intentionally kept
minimal to avoid heavy dependencies; argument parsing uses the standard
`argparse` library.  Each command delegates to the corresponding function
within the `runner.py` orchestrator or other modules.  Additional
functionality (e.g. Euclidean sequencing, bank ingestion) can be expanded in
future PRs.

TODOs:
    [ ] Add proper help and example sections to CLI documentation.
    [ ] Support asynchronous rendering via a job queue.
    [ ] Implement `export-cc` once CC mapping is supported.

"""

import argparse
import json
import sys
from pathlib import Path

# Import modules dynamically; these will be available when `/mnt/data` is added
try:
    import runner
    from io_midi import export_midi
    from analyze import analyze_audio
    from report_writer import write_report
    from utils import load_plan
except Exception:
    # Modules may not exist on first import when run outside of the GPT
    pass


def _load_plan(path: Path) -> dict:
    """Load a JSON plan from disk.

    Parameters
    ----------
    path : Path
        Location of the JSON plan file.

    Returns
    -------
    dict
        Parsed plan dictionary.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def render_wav(args: argparse.Namespace) -> None:
    """Render a WAV file from a user plan.

    This function reads a minimal plan from disk, completes it to a FULL_SPEC
    using `runner`, renders the audio and writes the resulting WAV file to
    `/mnt/data`.  The output path is printed to stdout for convenience.
    """
    plan = _load_plan(Path(args.plan))
    output_path = runner.run(plan)
    print(str(output_path))


def export_midi_cmd(args: argparse.Namespace) -> None:
    """Export a MIDI file from a fully specified plan.

    The user must provide a plan that has already been completed and rendered.
    The function writes a Type‑1 MIDI file to the specified output path.
    TODO: Determine the correct plan format for CC/NRPN export.
    """
    plan = _load_plan(Path(args.plan))
    out_path = Path(args.output)
    export_midi(plan, out_path)
    print(str(out_path))


def analyze_cmd(args: argparse.Namespace) -> None:
    """Run audio analysis on a previously rendered WAV file.

    This reads the WAV file, computes simple metrics (peak, RMS, crest factor,
    approximate LUFS) and writes them to a JSON file.  The path to the
    metrics file is printed for reference.
    """
    plan = _load_plan(Path(args.plan))
    metrics_path = Path(args.output)
    analyze_audio(plan, metrics_path)
    print(str(metrics_path))


def report_cmd(args: argparse.Namespace) -> None:
    """Generate a Markdown report summarising the session.

    This function calls the report writer to assemble a report from the plan
    and its corresponding analysis metrics.  The report is written to the
    specified output path.
    """
    plan = _load_plan(Path(args.plan))
    report_path = Path(args.output)
    write_report(plan, report_path)
    print(str(report_path))


def ingest_bank_cmd(args: argparse.Namespace) -> None:
    """Ingest a user bank (patterns/adsr/arp/progressions) into `bank.json`.

    The provided file must be a JSON or CSV describing additional patterns or
    CC mappings.  The bank is merged with the existing empty `bank.json` and
    stored back to disk.  This command is a placeholder for future work.
    """
    # TODO: implement ingestion logic (merge with existing bank.json)
    print("Bank ingestion is not yet implemented.")


def selftest_cmd(args: argparse.Namespace) -> None:
    """Run built‑in self‑tests to validate the engine.

    Self‑tests check WAV header correctness, ensure dither and peak limits are
    applied, verify MIDI VarLen encoding, confirm ZDF filter stability and
    confirm that no NaN/Inf values are produced.  For now only a placeholder
    implementation exists.
    """
    # TODO: call test functions once implemented
    print("Self‑tests are not yet implemented.")


def main(argv: list[str] | None = None) -> None:
    """Entry point for the command line interface.

    Parse command line arguments and dispatch to the appropriate handler.
    """
    parser = argparse.ArgumentParser(description="DawlessGPTv6 CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # render-wav
    render_parser = subparsers.add_parser("render-wav", help="Render a WAV from a plan")
    render_parser.add_argument("--plan", required=True, help="Path to JSON plan file")
    render_parser.set_defaults(func=render_wav)

    # export-midi
    midi_parser = subparsers.add_parser("export-midi", help="Export a MIDI file from a plan")
    midi_parser.add_argument("--plan", required=True, help="Path to JSON plan file")
    midi_parser.add_argument("--output", required=True, help="Path for the MIDI output file")
    midi_parser.set_defaults(func=export_midi_cmd)

    # analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a rendered WAV")
    analyze_parser.add_argument("--plan", required=True, help="Path to JSON plan file")
    analyze_parser.add_argument("--output", required=True, help="Path for the metrics JSON file")
    analyze_parser.set_defaults(func=analyze_cmd)

    # report
    report_parser = subparsers.add_parser("report", help="Generate a session report")
    report_parser.add_argument("--plan", required=True, help="Path to JSON plan file")
    report_parser.add_argument("--output", required=True, help="Path for the report Markdown file")
    report_parser.set_defaults(func=report_cmd)

    # ingest-bank
    ingest_parser = subparsers.add_parser("ingest-bank", help="Ingest a user bank file")
    ingest_parser.add_argument("--file", required=True, help="Path to the bank JSON/CSV file to ingest")
    ingest_parser.set_defaults(func=ingest_bank_cmd)

    # selftest
    selftest_parser = subparsers.add_parser("selftest", help="Run engine self‑tests")
    selftest_parser.set_defaults(func=selftest_cmd)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()