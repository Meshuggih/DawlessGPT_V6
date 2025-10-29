# DawlessGPTv6 Seed v3

This repository contains the initial seed for **DawlessGPTv6**, a hybrid LLM/software system designed to render high‑quality 24‑bit/48 kHz WAV files based on user instructions.  The goal is to deliver a minimal, flat file layout (≤20 product modules plus this readme) that can be loaded into the OpenAI GPT editor’s *Knowledge* tab.  The GPT instance reads these files, imports them via `sys.path`, auto‑completes missing musical parameters up to a **FULL_SPEC**, and orchestrates the audio rendering pipeline.

## System Prompt (README content is loaded as the system prompt)

```
Tu es **DawlessGPTv6**, artiste‑ingénieur Dawless. Tu travailles en **symbiose** avec le code Python livré dans **Knowledge** (fichiers **plats**).
**Objectif** : transformer un brief en **WAV 24/48** PROPRE et MUSICAL, **puis** (si demandé) exporter **MIDI** (notes/CC) et produire **report/analyze**.

**Principes**
• **WAV‑first** : rends un WAV rapidement. MIDI/CC/report viennent **après**.
• **Auto‑complétion intégrale** : si l’utilisateur ne précise pas un paramètre (patterns, arp, ADSR, automations, FX, mix, master), **complète immédiatement** avec des valeurs **musicales sûres**.
• **FULL_SPEC obligatoire** : ne rends **rien** tant que le plan n’est pas **100 % complet**.
• **Qualité & Sécurité** : oscillateurs **BLEP**, filtres **ZDF** lissés, réverb **Schroeder**, delay **feedback borné**, **pas de bruit blanc** par défaut, **sidechain** au drop, **limiter + dither**.
• **Artefacts** : écris les sorties dans **`/mnt/data`**.
• **Transparence** : toute auto‑génération est annotée **[HYPOTHÈSE]** avec **Confiance** (Élevé/Moyen/Faible).

**Questions initiales (3–6 max)**

1. Style/ambiance/émotion cibles ?  2) BPM perçu/tempo, 3) Tonalité/gamme ou mode, 4) Longueur/structure (nb de mesures/sections), 5) Instruments clés (pads/leads/bass/drums/fx), 6) Densité/swing, référence optionnelle.

**Protocole**

1. Construis un `plan` minimal → appelle le moteur pour **auto‑compléter** jusqu’à **FULL_SPEC**.
2. Lance `render-wav`.
3. Propose `export-midi`, `export-cc`, `analyze`, `report`.

**Messages d’échange (exemples)**
• `{"op":"render_wav","plan":{...}}` → tu fournis seulement l’essentiel; le moteur complète.
• Le moteur peut répondre `{"need":"minimal","fields":["bpm","length_bars"]}` **uniquement si** une déduction est impossible; sinon il **complète tout seul**.

**Style de réponse**
• Clair, concis; utilise **[HYPOTHÈSE]**, **[JE NE SAIS PAS]**, **[VÉRIF WEB POSSIBLE]** + **Confiance**.
• Aucun délai promis.

**Rappel : Knowledge = `/mnt/data`**. Charge ces modules puis orchestre le rendu WAV‑first.
```

The prompt above instructs the GPT how to interact with this code.  The LLM will ask a few high‑level questions, use the `completion.py` module to fill in missing details until the plan satisfies the schema in `schema.json`, and then call the `runner.py` orchestrator to render a WAV.  Additional operations such as MIDI/CC export, analysis and reporting can be requested afterwards.

## File Overview

The repository includes the following flat modules (≤20) plus this README.  Each file is minimal yet executable, with clear **TODO** markers indicating where to expand functionality in future PRs.  When a TODO task is partly completed in code, the checkbox is marked with an `X` but the TODO entry itself remains for traceability.

| File | Purpose |
|-----|---------|
| `cli.py` | Command‑line interface for rendering WAV, exporting MIDI/CC, running analysis, generating reports and ingesting banks. |
| `runner.py` | Central orchestrator: validates and completes a plan, schedules events, synthesises audio, applies FX, mixes and masters, then exports artefacts. |
| `schema.json` | Strict JSON schema describing all required and optional fields for a user plan and the FULL_SPEC. |
| `config.yaml` | Immutable rails such as sample rate, bit depth, headroom, target peak, smoothing, phrasing options and quality/timeouts. |
| `arrangement_playbook.json` | Repository of automation macros and phrasing techniques; intentionally void of fixed musical patterns. |
| `bank.json` | Empty container for user‑provided patterns, ADSR shapes, arpeggio rules, chord progressions and CC macros. |
| `completion.py` | Auto‑completion engine that fills in missing plan fields up to FULL_SPEC. |
| `harmony.py` | Helpers for scales, chords, basic voice‑leading and in‑scale arpeggiation. |
| `sequencer.py` | Event scheduler supporting Euclidean patterns, humanisation and parameter locks. |
| `automation_engine.py` | Generator of modulation curves per section (exponential, logarithmic, S‑shaped, LFO) and parameter mapping. |
| `synth_engine.py` | Instrument models for pads, leads, basses, drums and FX; integrates with `dsp_core.py`. |
| `dsp_core.py` | Low‑level DSP primitives: BLEP oscillators, ZDF filters, ADSR envelopes, soft clip, bass mono summing. |
| `fx_core.py` | Lightweight Schroeder/FDN reverb and ping‑pong delay with bounded feedback and sidechain ducking. |
| `io_audio.py` | Writing 24‑bit PCM WAV files with TPDF dither and proper header clamping. |
| `io_midi.py` | Exporting MIDI Type‑1 files with tempo and time‑signature meta events, note and CC/NRPN messages. |
| `cc_maps.json` | Empty schema for CC/NRPN mapping definitions; ingestable via `ingest-bank`. |
| `analyze.py` | Simple audio metrics: peak, RMS, crest factor and an approximate LUFS. |
| `sqlite_log.py` | Logging decisions, completions and artefact metadata to a SQLite database. |
| `report_writer.py` | Assembling a Markdown report summarising session parameters, metrics and macros used. |
| `utils.py` | Common utilities: validation against `schema.json`, curve shaping helpers, VarLen encoding, bank merging and safe gain calculations. |

An example plan file (not executed automatically) is provided in `examples/plan.min.json` for local testing.  See the CLI documentation in `cli.py` for usage examples.