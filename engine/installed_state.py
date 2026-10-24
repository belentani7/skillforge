"""Reconcile CLI inventory after a conservative skill uninstall.

A retained, edited or legacy file is still tracked by ``skill_files`` and
must keep its parent skill visible to users. No files are touched here.
"""
from __future__ import annotations

import json
import sqlite3
from typing import List


def reconcile_after_uninstall(db: sqlite3.Connection, name: str) -> List[str]:
    """Keep a skill record while any tracked installation still exists.

    Returns the tool identifiers whose files were retained. The caller has
    already invoked Installer.uninstall(), which refuses to delete changed,
    symlinked, or unverified files.
    """
    remaining = [row[0] for row in db.execute(
        "SELECT tool FROM skill_files WHERE skill_name = ? ORDER BY tool", (name,)
    ).fetchall()]
    if remaining:
        db.execute(
            "UPDATE installed_skills SET tools_installed = ? WHERE name = ?",
            (json.dumps(remaining), name),
        )
    else:
        db.execute("DELETE FROM installed_skills WHERE name = ?", (name,))
    db.commit()
    return remaining
