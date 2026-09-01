-- ═══════════════════════════════════════════════════════════════
-- ⚒️ SkillForge — SQLite Schema for Local Cache
-- ═══════════════════════════════════════════════════════════════
-- Tracks installed skills, versions, file locations, and search cache.

-- ── Installed skills ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS installed_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    version TEXT NOT NULL,
    installed_at TEXT NOT NULL,
    updated_at TEXT,
    tools_installed TEXT DEFAULT '[]',  -- JSON array of tool names
    source TEXT DEFAULT 'registry',     -- 'registry', 'local', 'url'
    metadata TEXT DEFAULT '{}'           -- JSON blob for extra data
);

-- ── Individual file installations ─────────────────────────────
-- Tracks which files were written where for each skill
CREATE TABLE IF NOT EXISTS skill_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    tool TEXT NOT NULL,
    file_path TEXT NOT NULL,
    installed_at TEXT NOT NULL,
    UNIQUE(skill_name, tool)
);

-- ── Registry search cache ─────────────────────────────────────
-- Caches GitHub API results to reduce rate-limit hits
CREATE TABLE IF NOT EXISTS search_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT UNIQUE NOT NULL,
    results TEXT NOT NULL,       -- JSON array of skill objects
    cached_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

-- ── Skill versions ────────────────────────────────────────────
-- Tracks known versions for update checking
CREATE TABLE IF NOT EXISTS skill_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    discovered_at TEXT NOT NULL,
    UNIQUE(name, version)
);

-- ── Dependencies ──────────────────────────────────────────────
-- Tracks skill-to-skill dependencies
CREATE TABLE IF NOT EXISTS dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    depends_on TEXT NOT NULL,
    version_constraint TEXT DEFAULT '*',
    UNIQUE(skill_name, depends_on)
);

-- ── Indexes for performance ───────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_installed_name ON installed_skills(name);
CREATE INDEX IF NOT EXISTS idx_files_skill ON skill_files(skill_name);
CREATE INDEX IF NOT EXISTS idx_files_tool ON skill_files(tool);
CREATE INDEX IF NOT EXISTS idx_cache_query ON search_cache(query);
CREATE INDEX IF NOT EXISTS idx_versions_name ON skill_versions(name);
CREATE INDEX IF NOT EXISTS idx_deps_skill ON dependencies(skill_name);
