"""Check homepage responsive artwork, which check_site.py does not inspect."""

from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.images.append(dict(attrs))


def main():
    page = Images()
    page.feed((ROOT / "index.html").read_text())
    for name, loading in (("home-visit-physiotherapy", "eager"), ("function-at-home", "lazy")):
        matches = [i for i in page.images if i.get("src") == f"assets/{name}.webp"]
        assert len(matches) == 1, f"Expected one {name} illustration"
        image = matches[0]
        assert image.get("alt", "").strip(), f"Missing {name} description"
        assert (image.get("width"), image.get("height")) == ("1536", "1024"), name
        assert image.get("loading") == loading, name
        assert image.get("sizes"), f"Missing {name} responsive sizes"
        candidates = [candidate.strip().split() for candidate in image.get("srcset", "").split(",")]
        assert candidates == [[f"assets/{name}-768.webp", "768w"], [f"assets/{name}.webp", "1536w"]], name
        for path, _ in candidates:
            assert (ROOT / path).is_file(), f"Missing responsive image: {path}"
        if loading == "eager":
            assert image.get("fetchpriority") == "high", "Hero must load with high priority"
    print("PASS: both homepage illustrations, responsive sources, dimensions, alt text and loading")


if __name__ == "__main__":
    main()
