---
name: deps
description: Audit project dependencies for outdated or missing packages
args_optional: true
---

Audit the dependencies for this project.

## Steps

1. **Find dependency files** using `glob` — look for:
   - `requirements*.txt`, `requirements/*.txt`
   - `pyproject.toml`, `setup.py`, `setup.cfg`
   - `package.json`, `package-lock.json`
   - `Gemfile`, `Cargo.toml`, `go.mod`

2. **Check installed vs declared** — for Python projects, run:
   ```bash
   pip list --outdated --format=json
   ```
   For Node.js:
   ```bash
   npm outdated --json
   ```

3. **Check for security issues** — for Python, run:
   ```bash
   pip-audit --format=json 2>/dev/null || safety check --json 2>/dev/null || echo "No security scanner available"
   ```

4. **Report results**:

## Dependency Audit

### Outdated Packages
| Package | Current | Latest | Type |
|---------|---------|--------|------|
| … | … | … | direct/transitive |

### Security Issues
List any CVEs or known vulnerabilities found. If none found or scanner unavailable, say so clearly.

### Missing from requirements
List any packages that are imported in the codebase but not declared in dependency files. Use `grep -r "^import\|^from" --include="*.py"` to find imports.

### Recommendations
- Prioritised list of updates to make (security fixes first, then major breaking changes, then minor updates)
- Note any packages that appear abandoned or unmaintained
