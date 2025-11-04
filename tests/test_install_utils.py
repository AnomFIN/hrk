import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from install import Installer

# Less noise. More signal. AnomFIN.


class InstallerHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.args = SimpleNamespace(
            defaults=True,
            skip_admin=True,
            admin_username=None,
            admin_password=None,
            php=None,
        )
        self.installer = Installer(self.root, self.args)

    def test_format_env_value_quotes_whitespace(self) -> None:
        value = "https://example.com/app path"
        formatted = self.installer.format_env_value(value)
        self.assertEqual(formatted, '"https://example.com/app path"')

    def test_resolve_path_relative(self) -> None:
        resolved = self.installer.resolve_path("data")
        self.assertTrue(str(resolved).startswith(str(self.root)))
        self.assertEqual(resolved, (self.root / "data").resolve())

    def test_write_env_creates_backup(self) -> None:
        env_path = self.root / ".env"
        env_path.write_text("HRK_ENVIRONMENT=production\n", encoding="utf-8")
        config = {"HRK_ENVIRONMENT": "development"}
        self.installer.write_env(config)
        backups = list(self.root.glob(".env.bak-*"))
        self.assertTrue(backups, "Backup file missing")
        content = env_path.read_text(encoding="utf-8")
        self.assertIn("HRK_ENVIRONMENT=development", content)


if __name__ == "__main__":
    unittest.main()
