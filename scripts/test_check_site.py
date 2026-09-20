"""Exercise the baseline checker in disposable copies, never in production files."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix="tandem-baseline-") as temporary:
        site = Path(temporary) / "site"
        shutil.copytree(ROOT, site, ignore=shutil.ignore_patterns(".git", "__pycache__"))

        def run():
            return subprocess.run([sys.executable, str(site / "scripts/check_site.py")],
                                  capture_output=True, text=True)

        baseline = run()
        assert baseline.returncode == 0, baseline.stderr
        cases = [
            ("about.html", '<a href="missing.html">test</a>', "missing local target"),
            ("about.html", '<a href="#missing-id">test</a>', "missing fragment target"),
            ("about.html", '<a href="index.html#missing-id">test</a>', "missing fragment target"),
            ("about.html", '<img src="assets/missing.png">', "missing local target"),
            ("about.html", '<link rel="stylesheet" href="assets/SITE.CSS">', "missing local target"),
            ("about.html", '<i id="test-id"></i><i id="test-id"></i>', "duplicate ID"),
            ("about.html", '<script type="application/ld+json">{broken}</script>', "invalid JSON-LD"),
        ]
        for file, addition, message in cases:
            path = site / file
            original = path.read_text()
            path.write_text(original + addition)
            result = run()
            assert result.returncode == 1 and message in result.stderr, result
            path.write_text(original)
        replacements = [
            ("about.html", '<title>', '<!--<title>', "metadata title"),
            ("sitemap.xml", "https://tandemphysio.com.au/", "http://tandemphysio.com.au/", "sitemap.xml"),
            ("robots.txt", "https://", "http://", "robots.txt"),
        ]
        for file, old, new, message in replacements:
            path = site / file
            original = path.read_text()
            assert old in original
            path.write_text(original.replace(old, new, 1))
            result = run()
            assert result.returncode == 1 and message in result.stderr, result
            path.write_text(original)
        assert run().returncode == 0
        print(f"PASS: clean temporary baseline and {len(cases) + len(replacements)} negative checks")


if __name__ == "__main__":
    main()
