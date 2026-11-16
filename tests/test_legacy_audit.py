"""Classification and traversal regression checks; no external service calls."""
from contextlib import redirect_stdout, redirect_stderr
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import audit_legacy_projects as audit


class LegacyAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return path

    def test_all_names_and_variants_fail_active_guidance(self):
        self.write('AGENTS.md', 'AMG\nworkmerit\nHR Odoo\nhr_odoo\nHR-Odoo\nHRA\nOdoo\n')
        findings = audit.scan(self.root)
        self.assertEqual(len(findings), 7)
        self.assertTrue(all(f.category == 'obsolete' for f in findings))

    def test_exact_history_and_definition_exemptions(self):
        for path in (*audit.HISTORY, *audit.DEFINITIONS):
            self.write(path, 'AMG')
        self.write('docs/new-history.md', 'WorkMerit')
        findings = audit.scan(self.root)
        self.assertEqual(sum(f.category == 'history' for f in findings), len(audit.HISTORY))
        self.assertEqual(sum(f.category == 'definition' for f in findings), len(audit.DEFINITIONS))
        self.assertEqual([f.path for f in findings if f.category == 'obsolete'], ['docs/new-history.md'])

    def test_protected_directories_nested_repos_and_secrets_are_not_read(self):
        for name in audit.SKIP:
            self.write(f'{name}/private.md', 'AMG')
        self.write('projects/client/private.md', 'AMG')
        self.write('nested/.git/HEAD', 'ref: refs/heads/main')
        self.write('nested/private.md', 'AMG')
        self.write('.env.local', 'AMG')
        self.write('projects/_template/README.md', 'AMG')
        self.write('.env.example', 'AMG')
        self.assertEqual({f.path for f in audit.scan(self.root)},
                         {'.env.example', 'projects/_template/README.md'})

    def test_reparse_directory_pruned_before_read(self):
        junction = self.write('linked/private.md', 'AMG').parent
        original = audit.linked
        with patch.object(audit, 'linked', side_effect=lambda path: path == junction or original(path)):
            self.assertEqual(audit.scan(self.root), [])

    def test_exit_codes_and_no_source_content_in_output(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(audit.main([str(self.root)]), 0)
            self.write('README.md', 'AMG sensitive example')
            self.assertEqual(audit.main([str(self.root)]), 1)
        self.assertNotIn('sensitive example', output.getvalue())
        self.assertIn('obsolete=1', output.getvalue())
        self.write('bad.md', 'placeholder').write_bytes(b'\xff')
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(audit.main([str(self.root)]), 2)


if __name__ == '__main__':
    unittest.main()
