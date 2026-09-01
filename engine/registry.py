"""
Registry client — searches GitHub repos, fetches skill metadata, manages versions.
Uses GitHub API (no auth required for public repos) and a local curated JSON fallback.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional


class Registry:
    """Client for the SkillForge community registry."""

    GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
    GITHUB_RAW_URL = "https://raw.githubusercontent.com"

    def __init__(self, db: sqlite3.Connection, config: dict):
        self.db = db
        self.config = config
        self.forge_dir = Path(__file__).resolve().parent.parent
        self.popular_path = self.forge_dir / "registry" / "popular.json"

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for skills by query string.
        Tries GitHub API first, falls back to local popular.json.
        """
        results = []

        # Try GitHub search for repos with topic:ai-skill
        github_results = self._search_github(query)
        results.extend(github_results)

        # Supplement with local popular skills
        local_results = self._search_local(query)
        # Deduplicate by name
        seen_names = {r["name"] for r in results}
        for r in local_results:
            if r["name"] not in seen_names:
                results.append(r)
                seen_names.add(r["name"])

        return results[:20]  # Cap at 20 results

    def fetch(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch full skill data by name.
        Tries local cache, then GitHub, then popular.json.
        """
        # Check local popular registry first
        skill = self._fetch_from_popular(name)
        if skill:
            return skill

        # Try to find via GitHub search
        results = self._search_github(name)
        for r in results:
            if r["name"] == name:
                # Try to fetch the actual skill.yaml from the repo
                remote = self._fetch_remote_skill(r.get("repo_url", ""), r.get("default_branch", "main"))
                if remote:
                    return remote
                return r

        return None

    def check_version(self, name: str) -> Optional[str]:
        """Check the latest version of a skill from the registry."""
        skill = self.fetch(name)
        if skill:
            return skill.get("version")
        return None

    def record_install(self, name: str, version: str):
        """Record a skill installation in the local database."""
        import datetime
        now = datetime.datetime.utcnow().isoformat()
        try:
            self.db.execute(
                "INSERT OR REPLACE INTO installed_skills (name, version, installed_at, tools_installed) "
                "VALUES (?, ?, ?, ?)",
                (name, version, now, "[]"),
            )
            self.db.commit()
        except Exception:
            pass

    # ── Private methods ───────────────────────────────────────

    def _search_github(self, query: str) -> List[Dict[str, Any]]:
        """Search GitHub for repos with topic:ai-skill matching query."""
        results = []
        try:
            url = (
                f"{self.GITHUB_SEARCH_URL}"
                f"?q={_url_encode(query)}+topic:ai-skill"
                f"&sort=stars&order=desc&per_page=10"
            )
            data = _fetch_json(url)
            for item in data.get("items", []):
                results.append({
                    "name": item["name"],
                    "description": item.get("description", ""),
                    "author": item["owner"]["login"],
                    "stars": item.get("stargazers_count", 0),
                    "downloads": 0,
                    "version": "1.0.0",
                    "tags": [t["name"] for t in item.get("topics", []) if t["name"] != "ai-skill"],
                    "repo_url": item.get("html_url", ""),
                    "default_branch": item.get("default_branch", "main"),
                })
        except Exception:
            pass  # GitHub API may be unavailable or rate-limited
        return results

    def _search_local(self, query: str) -> List[Dict[str, Any]]:
        """Search the local popular.json for matching skills."""
        if not self.popular_path.exists():
            return []
        try:
            data = json.loads(self.popular_path.read_text(encoding="utf-8"))
        except Exception:
            return []

        query_lower = query.lower()
        # Normalize query for matching
        results = []
        for skill in data.get("skills", []):
            name = skill.get("name", "")
            desc = skill.get("description", "")
            tags = skill.get("tags", [])
            if (query_lower in name.lower()
                    or query_lower in desc.lower()
                    or any(query_lower in t.lower() for t in tags)):
                results.append(skill)
        return results

    def _fetch_from_popular(self, name: str) -> Optional[Dict[str, Any]]:
        """Fetch a skill from local popular.json."""
        if not self.popular_path.exists():
            return None
        try:
            data = json.loads(self.popular_path.read_text(encoding="utf-8"))
        except Exception:
            return None

        for skill in data.get("skills", []):
            if skill.get("name") == name:
                return skill
        return None

    def _fetch_remote_skill(self, repo_url: str, branch: str = "main") -> Optional[Dict[str, Any]]:
        """Try to fetch skill.yaml from a GitHub repo."""
        if not repo_url:
            return None

        # Extract owner/repo from URL
        parts = repo_url.rstrip("/").split("/")
        if len(parts) < 2:
            return None
        owner, repo = parts[-2], parts[-1]

        url = f"{self.GITHUB_RAW_URL}/{owner}/{repo}/{branch}/skill.yaml"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SkillForge/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8")
                return _parse_simple_yaml(raw)
        except Exception:
            return None


# ── Utility functions ─────────────────────────────────────────

def validate_skill_yaml(path: Path) -> List[str]:
    """
    Validate a skill.yaml file.
    Returns a list of error strings (empty if valid).
    """
    errors = []

    if not path.exists():
        return [f"File not found: {path}"]

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Cannot read file: {e}"]

    data = _parse_simple_yaml(content)

    required_fields = ["name", "version", "description"]
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")

    # Check content.prompt exists
    content_block = data.get("content", {})
    if isinstance(content_block, dict):
        if not content_block.get("prompt"):
            errors.append("Missing content.prompt")
    else:
        errors.append("content must be a mapping with at least a 'prompt' key")

    return errors


def _fetch_json(url: str) -> dict:
    """Fetch JSON from a URL using stdlib urllib."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "SkillForge/1.0",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _url_encode(s: str) -> str:
    """Minimal URL encoding."""
    return s.replace(" ", "+").replace("/", "%2F").replace("#", "%23")


def _parse_simple_yaml(text: str) -> Dict[str, Any]:
    """
    Minimal YAML parser for flat skill definitions (stdlib only).
    Handles basic key: value, lists, and one level of nesting.
    """
    result: Dict[str, Any] = {}
    current_section = None
    in_multiline = False
    multiline_key = None
    multiline_indent = 0
    multiline_lines: List[str] = []

    for line in text.splitlines():
        # Handle multiline strings (prompt: |)
        if in_multiline:
            stripped = line.rstrip()
            if stripped and len(line) - len(line.lstrip()) > multiline_indent:
                multiline_lines.append(line.lstrip())
                continue
            elif stripped == "" or len(line) - len(line.lstrip()) > multiline_indent:
                multiline_lines.append("")
                continue
            else:
                result[multiline_key] = "\n".join(multiline_lines).strip()
                in_multiline = False

        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()

            if val == "|":
                # Start of multiline
                in_multiline = True
                multiline_key = key
                multiline_indent = len(line) - len(line.lstrip())
                multiline_lines = []
                current_section = None
                continue

            if val:
                # Handle inline lists [a, b, c]
                if val.startswith("[") and val.endswith("]"):
                    items = val[1:-1].split(",")
                    result[key] = [i.strip() for i in items if i.strip()]
                else:
                    result[key] = val
                current_section = None
            else:
                current_section = key
                result[key] = {}
        elif current_section and stripped.startswith("- "):
            if not isinstance(result.get(current_section), list):
                result[current_section] = []
            result[current_section].append(stripped[2:].strip())

    # Flush any remaining multiline
    if in_multiline and multiline_key:
        result[multiline_key] = "\n".join(multiline_lines).strip()

    return result
