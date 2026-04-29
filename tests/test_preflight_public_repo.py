from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "preflight_public_repo", ROOT / "scripts" / "preflight_public_repo.py"
)
preflight = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(preflight)


class PublicRepoPreflightTests(unittest.TestCase):
    def test_placeholder_keys_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n",
                encoding="utf-8",
            )
            self.assertEqual(preflight.run(root), 0)

    def test_real_looking_secret_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "OPENAI_API_KEY=sk-" + ("a" * 30) + "\n",
                encoding="utf-8",
            )
            self.assertEqual(preflight.run(root), 1)

    def test_raw_material_path_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / "wiki" / "raw"
            raw.mkdir(parents=True)
            (raw / "private-source.md").write_text("draft\n", encoding="utf-8")
            self.assertEqual(preflight.run(root), 1)


if __name__ == "__main__":
    unittest.main()
