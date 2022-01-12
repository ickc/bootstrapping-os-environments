from pathlib import Path
from unittest import TestCase

from bsos.core import normalize


class TestConfig(TestCase):
    def setUp(self) -> None:
        self.path = Path("common/conda/conda.csv")
        self.out_path = Path("tests/conda.csv")

    def test_roundtrip(self):
        normalize(self.path, self.out_path)
        with self.path.open("r") as f:
            ref = f.read()
        with self.out_path.open("r") as f:
            res = f.read()
        self.out_path.unlink(missing_ok=True)
        assert ref.strip() == res.strip()
