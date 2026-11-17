"""The history policy must catch removed artifacts and shared-blob aliases."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_site import historical_artifacts


class SourcePolicyTest(unittest.TestCase):
    def test_artifacts_remain_rejected_after_removal(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.DEVNULL)
            git('init', '-b', 'main')
            git('config', 'user.email', 'test@example.invalid')
            git('config', 'user.name', 'Policy Test')
            (root / 'source.html.in').write_text('same content')
            git('add', '.')
            git('commit', '-m', 'Source template is allowed')
            self.assertEqual(historical_artifacts(root), [])
            # Same blob as the permitted template: an object-only scan misses it.
            (root / 'rendered.html').write_text('same content')
            (root / 'outputs').mkdir()
            (root / 'outputs' / 'catalog.json').write_text('{}')
            git('add', '.')
            git('commit', '-m', 'Accidental generated output')
            git('rm', 'rendered.html', 'outputs/catalog.json')
            git('commit', '-m', 'Remove output from current tree')
            self.assertEqual(historical_artifacts(root), ['outputs/catalog.json', 'rendered.html'])


if __name__ == '__main__':
    unittest.main()
