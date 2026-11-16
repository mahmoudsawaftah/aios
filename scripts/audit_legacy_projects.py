"""Read-only, classified legacy-reference audit of the AIOS control repository."""
import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import re
import stat
import sys

SKIP = {'.git', '.factory-runtime', '.aios-update-backups', 'vault', 'node_modules',
        '.venv', '__pycache__', 'dist', 'build', '.claude', '.agents', 'raw', 'comms'}
EXTS = {'.md', '.yaml', '.yml', '.json', '.toml', '.txt', '.py', '.ps1',
        '.js', '.ts', '.tsx', '.example'}
MATCH = re.compile(r'\bAMG\b|WorkMerit|\bHR[ _-]+Odoo\b|\bHRA\b|\bOdoo\b', re.I)
# Exact files only: new documents are never exempt by directory or marker.
HISTORY = {
    'mytasks/2026-09-18-environment-bootstrap.md': 'dated bootstrap evidence, not instructions',
    'docs/harvest.md': 'historical provenance with retirement notice',
}
DEFINITIONS = {
    'scripts/audit_legacy_projects.py': 'audit definitions',
    'tests/test_legacy_audit.py': 'audit regression fixtures',
}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    category: str
    reason: str


def linked(path):
    """Reject symlinks and Windows junctions, including on Python 3.11."""
    return path.is_symlink() or bool(
        getattr(path.lstat(), 'st_file_attributes', 0)
        & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400))


def scan(root: Path):
    if linked(root) or not root.is_dir():
        raise ValueError(f'Not a regular directory: {root}')
    findings = []

    def walk_error(error):
        raise error

    for directory, dirs, files in os.walk(root, topdown=True, followlinks=False, onerror=walk_error):
        base = Path(directory)
        dirs[:] = sorted(name for name in dirs if name not in SKIP
                         and not linked(base / name)
                         and not (base / name / '.git').exists()
                         and (base != root / 'projects' or name == '_template'))
        for name in sorted(files):
            path = base / name
            if linked(path) or path.suffix.lower() not in EXTS:
                continue
            if path.name.startswith('.env') and path.name != '.env.example':
                continue
            if path.stat().st_size > 2_000_000:
                raise ValueError(f'Eligible file too large to audit: {path.relative_to(root)}')
            relative = path.relative_to(root).as_posix()
            for number, line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
                if not MATCH.search(line):
                    continue
                if relative in HISTORY:
                    category, reason = 'history', HISTORY[relative]
                elif relative in DEFINITIONS:
                    category, reason = 'definition', DEFINITIONS[relative]
                else:
                    category, reason = 'obsolete', 'active or unreviewed legacy reference'
                findings.append(Finding(relative, number, category, reason))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo', nargs='?', default='.')
    args = parser.parse_args(argv)
    try:
        findings = scan(Path(args.repo).absolute())
    except (OSError, UnicodeError, ValueError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2
    for finding in findings:
        # Never echo potentially sensitive source lines.
        print(f'{finding.category.upper()} {finding.path}:{finding.line}: {finding.reason}')
    counts = {category: sum(f.category == category for f in findings)
              for category in ('obsolete', 'history', 'definition')}
    print('SUMMARY ' + ' '.join(f'{key}={value}' for key, value in counts.items()))
    print('FAIL' if counts['obsolete'] else 'PASS')
    return int(bool(counts['obsolete']))


if __name__=='__main__':
    sys.exit(main())
