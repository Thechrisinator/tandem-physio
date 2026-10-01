"""Check condition discovery, metadata and core/related links; standard library only."""
import re
from html.parser import HTMLParser

from check_site import DOMAIN, ROOT, Page

CONDITIONS = {
    "Stroke": ("stroke-physiotherapy.html", "Stroke"),
    "MND": ("mnd-physiotherapy.html", "MND"),
    "SCI": ("spinal-cord-injury-physiotherapy.html", "Spinal Cord Injury"),
    "ABI / TBI": ("abi-tbi-physiotherapy.html", "ABI & TBI"),
    "MS": ("multiple-sclerosis-physiotherapy.html", "Multiple Sclerosis"),
    "Parkinsonism": ("parkinsons-physiotherapy.html", "Parkinson's"),
    "Falls risk": ("falls-prevention-physiotherapy.html", "Falls Prevention"),
    "Complex chronic pain": ("complex-chronic-pain-physiotherapy.html", "Complex Chronic Pain"),
}


class Tags(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links = []
        self.current = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "tp-tag" in attrs.get("class", "").split():
            assert tag == "a", "Every NDIS condition tag must be a link"
            self.current = ["", attrs.get("href")]

    def handle_data(self, data):
        if self.current is not None:
            self.current[0] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.links.append(tuple(self.current))
            self.current = None


def main():
    ndis = (ROOT / "ndis-physiotherapy.html").read_text()
    assert Tags(ndis).links == [(tag, path) for tag, (path, _) in CONDITIONS.items()]
    descriptions = set()
    urls = {path for path, _ in CONDITIONS.values()}
    core = {"clinical-focus.html", "mobile-physiotherapy.html", "about.html",
            "service-areas.html", "refer.html"}
    for tag, (path, label) in CONDITIONS.items():
        source = (ROOT / path).read_text()
        page = Page(source)
        expected_title = f"{label} Physiotherapy Western Sydney | Tandem Physio"
        assert page.titles == [expected_title], path
        assert page.meta["og:title"] == page.titles, path
        assert page.meta["og:description"] == page.meta["description"], path
        description = page.meta["description"][0]
        assert description not in descriptions, f"Duplicate description: {path}"
        descriptions.add(description)
        assert page.canonicals == page.meta["og:url"] == [DOMAIN + path], path
        assert 'lang="en-AU"' in source and source.count("<h1>") == 1, path
        if tag == "MND":  # Existing published content is deliberately unchanged.
            continue
        body = source.split('<main id="main">', 1)[1].split("</main>", 1)[0]
        refs = set(Page(body).refs)
        assert core <= refs, f"Missing core links: {path}: {core - refs}"
        assert refs & {"ndis-physiotherapy.html", "icare-ltcs-physiotherapy.html"}, path
        assert "Penrith" in body and "Western Sydney" in body and "The Hills" in body, path
        related = body.split('id="related-services-heading"', 1)[1].split("</section>", 1)[0]
        related_links = set(Page(related).refs)
        assert 2 <= len(related_links) <= 3 and related_links <= urls - {path}, path
        assert not re.search(r'\b(expert|specialist)\b(?= physiotherap)', body, re.I), path
    print("PASS: eight linked NDIS tags, exact titles, unique matching metadata, seven core/related link sets")


if __name__ == "__main__":
    main()
