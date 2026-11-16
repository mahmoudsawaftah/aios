"""No network / no model usage; validate gate, durability, and retry basics."""
import argparse
from contextlib import redirect_stdout
import io
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from factory import cli


class FactoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'control'
        self.state = self.root / '.factory-runtime'
        self.project = Path(self.tmp.name) / 'client-repo'
        self.project.mkdir()
        self.root.mkdir()
        subprocess.run(['git','init',str(self.project)],capture_output=True,check=True)
        self.oldroot, self.oldstate, self.olddb = cli.ROOT,cli.STATE,cli.DB
        cli.ROOT,cli.STATE,cli.DB = self.root,self.state,self.state/'state.sqlite3'
        (self.root/'agents'/'roles').mkdir(parents=True)
        for stage in cli.STAGES:
            (self.root/'agents'/'roles'/f'{stage}.md').write_text(f'Role {stage}',encoding='utf-8')
        self.db = cli.connect()
        self.id = 'demo123'
        self.db.execute('''INSERT INTO tasks (id,project,goal,methodology,status,created_at,updated_at)
             VALUES(?,?,?,?,?,?,?)''',(self.id,str(self.project),'Build a demo','hybrid','PENDING',cli.utcnow(),cli.utcnow()))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        cli.ROOT,cli.STATE,cli.DB = self.oldroot,self.oldstate,self.olddb
        self.tmp.cleanup()

    def runner(self,max_attempts=2):
        with redirect_stdout(io.StringIO()):
            cli.run_pipeline(self.db,argparse.Namespace(id=self.id, timeout=1,max_attempts=max_attempts))

    def test_build_gate_and_release_gate(self):
        with patch.object(cli,'codex_stage',return_value='OK') as mock:
            self.runner()
            row=cli.task(self.db,self.id)
            self.assertEqual((row['stage_idx'],row['status']),(4,'WAITING_APPROVAL'))
            self.assertEqual(mock.call_count,4)
            cli.approve(self.db,argparse.Namespace(id=self.id,gate='build'))
            self.runner()
            row=cli.task(self.db,self.id)
            self.assertEqual((row['stage_idx'],row['status']),(8,'WAITING_APPROVAL'))
            self.assertEqual(mock.call_count,8)
            cli.approve(self.db,argparse.Namespace(id=self.id,gate='release'))
            self.runner()
            self.assertEqual(cli.task(self.db,self.id)['status'],'DONE')
            self.assertTrue(cli.log_path(self.id,'qa').exists())

    def test_restart_retries_stage_then_requires_owner_reset(self):
        with patch.object(cli,'codex_stage',side_effect=RuntimeError('simulated failure')):
            self.runner()
            self.assertEqual(cli.task(self.db,self.id)['status'],'INTERRUPTED')
            self.runner()
            self.runner()
            self.assertEqual(cli.task(self.db,self.id)['status'],'FAILED')
            with redirect_stdout(io.StringIO()):
                cli.reset_stage(self.db,argparse.Namespace(id=self.id))
            self.assertEqual(cli.task(self.db,self.id)['attempt'],0)

    def test_project_root_is_independent(self):
        self.assertEqual(cli.project_path(str(self.project)),self.project.resolve())
        with self.assertRaises(ValueError):
            cli.project_path(str(self.root))

    def test_worktree_isolated_from_original(self):
        subprocess.run(['git','-C',str(self.project),'-c','user.name=AIOS Test',
                        '-c','user.email=test@example.invalid','commit','--allow-empty',
                        '-m','baseline'],capture_output=True,check=True)
        row=cli.task(self.db,self.id)
        worktree=cli.ensure_worktree(row)
        self.assertNotEqual(worktree,self.project)
        self.assertEqual(cli.ensure_worktree(row),worktree)
        self.assertTrue(cli.is_git_repository(worktree))
        (worktree/'sample.txt').write_text('only inside task worktree',encoding='utf-8')
        self.assertFalse((self.project/'sample.txt').exists())

    def test_no_early_approval(self):
        with self.assertRaises(ValueError):
            cli.approve(self.db,argparse.Namespace(id=self.id,gate='release'))


if __name__=='__main__':
    unittest.main()
