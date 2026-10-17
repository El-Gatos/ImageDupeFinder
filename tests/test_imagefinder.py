import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from imagefinder import main, quarantine, scan


class FinderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "a.jpg").write_bytes(b"same")
        (self.root / "b.png").write_bytes(b"same")
        (self.root / "c.jpg").write_bytes(b"different")

    def test_exact_and_report_only(self):
        report = scan(self.root)
        self.assertEqual(len(report["exact_groups"]), 1)
        self.assertEqual(report["exact_groups"][0]["keeper"], str(self.root / "a.jpg"))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.root)]), 0)
        self.assertTrue((self.root / "b.png").exists())

    def test_quarantine_is_recoverable_and_excluded(self):
        manifest = quarantine(scan(self.root))
        entry = json.loads(manifest.read_text())[0]
        self.assertTrue((self.root / "a.jpg").exists())
        self.assertFalse((self.root / "b.png").exists())
        self.assertEqual(Path(entry["quarantined"]).read_bytes(), b"same")
        self.assertEqual(scan(self.root)["exact_groups"], [])
        Path(entry["quarantined"]).rename(entry["original"])
        self.assertEqual(len(scan(self.root)["exact_groups"]), 1)

    def test_reject_changed_source_and_keeper(self):
        for name in ("a.jpg", "b.png"):
            report = scan(self.root)
            path = self.root / name
            path.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                quarantine(report)
            self.assertTrue((self.root / "b.png").exists())
            path.write_bytes(b"same")

    def test_invalid_cli(self):
        for args in ([str(self.root), "--threshold", "-1"],
                     [str(self.root / "missing")], [str(self.root), "--auto"]):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main(args)

    def test_report_does_not_overwrite(self):
        report = self.root / "report.json"
        report.write_text("existing")
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main([str(self.root), "--report", str(report)])
        self.assertEqual(report.read_text(), "existing")


if __name__ == "__main__":
    unittest.main()
