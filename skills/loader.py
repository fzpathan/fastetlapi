"""
Skill loader — reads skill definitions from the skills/ directory.

Two formats are supported:

  1. Flat skill  (single file):
       skills/my-skill.md

  2. Directory skill  (with scripts):
       skills/my-skill/
           SKILL.md          ← required: prompt + frontmatter
           scripts/          ← optional: Python helper scripts
               analyse.py
               ...

Frontmatter fields (YAML-like, between --- delimiters):

    ---
    name: skill-name              # used as the /command name (required)
    description: One-line text    # shown in /help
    args: <required_arg>          # usage hint shown on missing args
    args_optional: true           # if set, skill runs without args
    ---

    Prompt body. Available substitutions:
      {args}       — replaced with whatever the user typed after the command
      {skill_dir}  — absolute path to the skill's directory (directory skills only)
                     useful for referencing bundled scripts, e.g.:
                     python {skill_dir}/scripts/analyse.py {args}
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path

_SKILLS_DIR = Path(__file__).parent
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_KV_RE = re.compile(r"^(\w+(?:_\w+)*):\s*(.+)$", re.MULTILINE)


@dataclass
class Skill:
    name: str
    description: str
    body: str
    args_hint: str = ""           # e.g. "<csv_file>"
    args_optional: bool = False   # if True, skill can run without args
    skill_dir: Path | None = None # set for directory-based skills

    @property
    def command(self) -> str:
        return f"/{self.name}"

    @property
    def has_scripts(self) -> bool:
        if self.skill_dir is None:
            return False
        return (self.skill_dir / "scripts").is_dir()

    def render(self, args: str) -> str:
        """Return the prompt with {args} and {skill_dir} substituted."""
        result = self.body.replace("{args}", args)
        if self.skill_dir is not None:
            result = result.replace("{skill_dir}", str(self.skill_dir))
        return result.strip()


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Split YAML-like frontmatter from body. Returns (meta, body)."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text.strip()

    meta_block = match.group(1)
    body = text[match.end():].strip()

    meta: dict[str, str] = {}
    for m in _KV_RE.finditer(meta_block):
        meta[m.group(1)] = m.group(2).strip()

    return meta, body


def _build_skill(path: Path, skill_dir: Path | None = None) -> Skill | None:
    """Parse a SKILL.md or flat .md file into a Skill. Returns None on error."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None

    meta, body = _parse_frontmatter(text)
    if not body:
        return None

    # derive name from frontmatter, then from directory name, then from file stem
    if skill_dir is not None:
        default_name = skill_dir.name
    else:
        default_name = path.stem

    name             = meta.get("name", default_name)
    description      = meta.get("description", "")
    args_hint        = meta.get("args", "")
    args_optional    = meta.get("args_optional", "false").lower() in {"true", "yes", "1"}

    return Skill(
        name=name,
        description=description,
        body=body,
        args_hint=args_hint,
        args_optional=args_optional,
        skill_dir=skill_dir,
    )


def load_skill_from_path(path: Path) -> Skill | None:
    """Load a skill from either a flat .md file or a directory containing SKILL.md."""
    if path.is_dir():
        skill_md = path / "SKILL.md"
        if skill_md.exists():
            return _build_skill(skill_md, skill_dir=path.resolve())
        return None
    if path.suffix == ".md":
        return _build_skill(path, skill_dir=None)
    return None


def load_all_skills() -> dict[str, Skill]:
    """
    Discover and load all skills from the skills/ directory.
    Returns a dict mapping command strings ("/name") to Skill objects.

    Discovery order (both are checked):
      1. Flat files:  skills/*.md
      2. Directories: skills/*/SKILL.md
    """
    skills: dict[str, Skill] = {}

    # flat .md files (skip loader.py itself and any non-skill md files)
    for path in sorted(_SKILLS_DIR.glob("*.md")):
        skill = load_skill_from_path(path)
        if skill:
            skills[skill.command] = skill

    # directory-based skills
    for path in sorted(_SKILLS_DIR.iterdir()):
        if path.is_dir() and (path / "SKILL.md").exists():
            skill = load_skill_from_path(path)
            if skill:
                skills[skill.command] = skill

    return skills
