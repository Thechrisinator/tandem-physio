"""Offline structural baseline for this static site; Python standard library only."""

import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://tandemphysio.com.au/"
PAGES = (
    "index.html", "about.html", "clinical-focus.html", "mobile-physiotherapy.html",
    "service-areas.html", "ndis-physiotherapy.html", "icare-ltcs-physiotherapy.html",
    "refer.html", "faq.html", "privacy.html",
)
UTILITY_PAGES = {"thanks.html", "404.html"}


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.refs = []
        self.meta = {}
        self.canonicals = []
        self.titles = []
        self.schemas = []
        self.styles = []
        self.in_head = False
        self.capture = None
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "head":
            self.in_head = True
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for key in ("href", "src", "poster"):
            if attrs.get(key):
                self.refs.append(attrs[key])
        if attrs.get("style"):
            self.styles.append(attrs["style"])
        if tag == "style":
            self.styles.append("")
            self.capture = (tag, self.styles)
        if tag == "script" and attrs.get("type", "").lower() == "application/ld+json":
            self.schemas.append("")
            self.capture = (tag, self.schemas)
        if self.in_head:
            if tag == "title":
                self.titles.append("")
                self.capture = (tag, self.titles)
            if tag == "meta":
                name = (attrs.get("name") or attrs.get("property") or "").lower()
                self.meta.setdefault(name, []).append(attrs.get("content", ""))
                if name == "og:image" and attrs.get("content"):
                    self.refs.append(attrs["content"])
            if tag == "link" and "canonical" in attrs.get("rel", "").lower().split():
                self.canonicals.append(attrs.get("href", ""))

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        if self.capture and self.capture[0] == tag:
            self.capture = None

    def handle_data(self, data):
        if self.capture:
            self.capture[1][-1] += data


def css_urls(source):
    # ponytail: literal url() only; use a CSS parser if imports/escaping become needed.
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    return [match[1].strip() for match in re.findall(
        r"url\(\s*(['\"]?)(.*?)\1\s*\)", source, flags=re.I | re.S
    )]


def reject_constant(value):
    raise ValueError(f"non-JSON constant {value}")


def main():
    errors = []

    def fail(file, message):
        errors.append(f"{file}: {message}")

    pages = {p.name: Page(p.read_text(encoding="utf-8")) for p in ROOT.glob("*.html")}
    # Compare spellings even on case-insensitive development filesystems.
    files = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*")
             if ".git" not in p.parts and p.is_file()}
    expected = set(PAGES) | UTILITY_PAGES
    for name in sorted(expected - pages.keys()):
        fail(name, "missing HTML page")
    for name in sorted(pages.keys() - expected):
        fail(name, "unclassified HTML page; declare substantive or utility")

    def check_ref(file, ref):
        url = urlsplit(urljoin(DOMAIN + file, ref))
        if url.scheme not in ("http", "https") or url.hostname not in (
            "tandemphysio.com.au", "www.tandemphysio.com.au"
        ):
            return
        path = unquote(url.path).lstrip("/")
        target = (ROOT / path).resolve()
        if not target.is_relative_to(ROOT):
            fail(file, f"local reference escapes site: {ref}")
            return
        if target.is_dir():
            target /= "index.html"
        if target.relative_to(ROOT).as_posix() not in files:
            fail(file, f"missing local target: {ref}")
        elif url.fragment and target.suffix.lower() == ".html":
            name = target.relative_to(ROOT).as_posix()
            page = pages.get(name)
            if page is None:
                page = Page(target.read_text(encoding="utf-8"))
            if unquote(url.fragment) not in page.ids:
                fail(file, f"missing fragment target: {ref}")

    canonical_urls = {DOMAIN + ("" if name == "index.html" else name) for name in PAGES}
    for name, page in sorted(pages.items()):
        for ident, count in Counter(page.ids).items():
            if count > 1:
                fail(name, f"duplicate ID: {ident}")
        for ref in page.refs:
            check_ref(name, ref)
        for style in page.styles:
            for ref in css_urls(style):
                check_ref(name, ref)
        for schema in page.schemas:
            try:
                json.loads(schema, parse_constant=reject_constant)
            except ValueError as exc:
                fail(name, f"invalid JSON-LD: {exc}")
        if name in UTILITY_PAGES:
            directives = page.meta.get("robots", [])
            if len(directives) != 1 or {value.strip().lower() for value in
                                        directives[0].split(",")} != {"noindex", "follow"}:
                fail(name, "metadata robots: require noindex, follow")
        if name not in PAGES:
            continue
        canonical = DOMAIN + ("" if name == "index.html" else name)
        fields = {"title": page.titles, "canonical": page.canonicals}
        fields.update({key: page.meta.get(key, []) for key in (
            "description", "og:title", "og:description", "og:type", "og:url", "og:image"
        )})
        for key, values in fields.items():
            if len(values) != 1 or not values[0].strip():
                fail(name, f"metadata {key}: require exactly one nonempty value")
        if fields["og:image"] != [DOMAIN + "assets/og-image.png"]:
            fail(name, "metadata og:image: expected shared HTTPS apex image")
        for key in ("canonical", "og:url"):
            if fields[key] != [canonical]:
                fail(name, f"metadata {key}: expected {canonical}")

    for css in sorted((ROOT / "assets").rglob("*.css")):
        name = css.relative_to(ROOT).as_posix()
        for ref in css_urls(css.read_text(encoding="utf-8")):
            check_ref(name, ref)

    try:
        sitemap = ElementTree.parse(ROOT / "sitemap.xml").getroot()
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        urls = [node.text for node in sitemap.findall(f"{ns}url/{ns}loc")]
        if sitemap.tag != ns + "urlset" or len(urls) != len(PAGES) or set(urls) != canonical_urls:
            fail("sitemap.xml", "must contain exactly the ten substantive canonical HTTPS URLs")
    except (OSError, ElementTree.ParseError) as exc:
        fail("sitemap.xml", str(exc))
    try:
        lines = (ROOT / "robots.txt").read_text(encoding="utf-8").splitlines()
        sitemaps = [line.split(":", 1)[1].strip() for raw in lines
                    if (line := raw.split("#", 1)[0].strip()).lower().startswith("sitemap:")]
        if sitemaps != [DOMAIN + "sitemap.xml"]:
            fail("robots.txt", "must reference the canonical HTTPS sitemap exactly once")
    except OSError as exc:
        fail("robots.txt", str(exc))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"PASS: {len(pages)} HTML pages; {len(PAGES)} substantive metadata contracts; links, "
          "fragments, assets, IDs, JSON-LD, sitemap and robots.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
