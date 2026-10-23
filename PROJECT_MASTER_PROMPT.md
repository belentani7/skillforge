# PROJECT MASTER PROMPT — SKILLFORGE

> Canonical repository: `belentani7/skillforge`.
> Product identity: **SkillForge — the universal package manager for AI coding skills**.
> Principle: *Write once. Install everywhere.*

## Source of truth

The existing executable `skillforge`, `engine/`, `format/`, `database/schema.sql`, `registry/`, `templates/` and `tests/` define this product. It is a Python CLI that discovers skills, converts universal skill definitions and installs them into supported AI coding tools. Do not conflate SkillForge with the wider Belentani Factory, do not create a replacement repository, and do not silently remove files under users' home directories.

## Finished product destination

- **Reliable skill lifecycle:** searchable registry and local fallback, explicit skill installation, listing, update, version history, safe uninstall, local skill creation and validation.
- **Universal conversion:** Claude Code, Codex, Aider, Qwen and Gemini adapters; preserve tool-native semantics and clean capability detection.
- **Safety by design:** reject path traversal, symlink tricks and unexpected writes; never replace manually edited or third-party files; track installed file paths and cryptographic checksums; treat unverified legacy installs conservatively.
- **Recoverability:** SQLite schema migrations that retain existing data; deterministic version state; clear error codes and meaningful terminal feedback; backup/rollback where appropriate.
- **Supply-chain discipline:** remote manifests validated before installation; pinned source integrity or checksums for remote downloads; no implicit `curl | bash` required for normal use; avoid installing arbitrary executable hooks without opt-in.
- **Professional CLI:** reproducible releases, install script, help, shell completion, accessibility-friendly output, integration tests and cross-platform smoke checks.
- **Quality gates:** tests in CI, Python compilation, safe temp-directory filesystem tests, dependency/security checks and verified package release before calling it complete.

## Architecture and evolution

Keep the standard-library-first Python CLI; avoid a frontend rewrite. Stage construction: (1) safe file lifecycle and schema migration; (2) registry and YAML validation; (3) accurate listing/update/uninstall UX; (4) cross-platform release and package integrity; (5) true CI + release verification. Every step requires a functional change and regression coverage, not a document-only deliverable.

## Agent operating procedure

Read current source and outstanding PRs first. Implement one coherent increment on a branch, add tests, run `python -m unittest discover -s tests -p 'test_*.py' -v` and `python -m compileall -q engine format tests`, then inspect checks before merging. Keep archived/private state unchanged unless explicitly authorized. Do not declare successful execution when the GitHub runner produced no steps. If no runner is available, report verification pending. Respect ownership of files and never remove data merely because its filename resembles a tracked skill.

## Delivery log

- 2026-10-23: branch `fix/299-skill-installer-path-safety-20261023` implements checksummed installation records, refusal of untracked overwrites, guarded updates, non-destructive uninstall, safe skill names and Python regression tests.
- **Verification status:** changes are committed on a branch but remote CI execution, merge and release have not been confirmed.
