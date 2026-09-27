"""Offline checks for the accessible, qualified V3 visual summaries."""
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ('refer', 'clinical-focus', 'mobile-physiotherapy', 'service-areas', 'index', 'about')


class Visuals(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tags = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def main():
    for name in PAGES:
        source = (ROOT / f'{name}.html').read_text()
        tags = Visuals(source).tags
        assert sum(tag == 'link' and attrs.get('href') == 'assets/visuals.css'
                   for tag, attrs in tags) == 1, name
        for tag, attrs in tags:
            if tag == 'svg':
                assert attrs.get('aria-hidden') == 'true', name
                assert attrs.get('focusable') == 'false', name
                assert attrs.get('viewbox') == '0 0 48 48', name
                assert int(attrs['width']) > 0 and int(attrs['height']) > 0, name

    referral = (ROOT / 'refer.html').read_text()
    journey = referral.split('id="journey-heading"', 1)[1].split('</section>', 1)[0]
    tags = Visuals(journey).tags
    assert [tag for tag, attrs in tags if attrs.get('class') == 'journey-entries'] == ['ul']
    assert [tag for tag, attrs in tags if attrs.get('class') == 'journey-common'] == ['ol']
    entries = journey.split('<ul class="journey-entries"', 1)[1].split('</ul>', 1)[0]
    common = journey.split('<ol class="journey-common"', 1)[1].split('</ol>', 1)[0]
    assert entries.count('<li') == 2 and common.count('<li') == 3
    assert 'journey-number' not in journey, 'Starting options must not be numbered steps'
    assert 'Choose either starting option.' in journey
    assert 'Optional preliminary enquiry' in entries and 'Formal referral' in entries
    assert 'Not sure about suitability?' in entries and 'Ready to refer?' in entries
    # Both links belong to the alternative entries, not the ordered common steps.
    assert 'href="#check-suitability"' in entries and 'href="#referral-form"' in entries
    assert 'Check suitability' in entries and 'Make a referral' in entries
    assert 'No formal referral is needed to check suitability.' in entries
    assert 'Provide only the information reasonably necessary to assess or progress this formal referral.' in entries
    assert 'href="#check-suitability"' not in common and 'href="#referral-form"' not in common
    stages = ('We aim to respond within 1 business day.', 'Initial assessment', 'Ongoing plan / review')
    positions = [common.index(stage) for stage in stages]
    assert positions == sorted(positions)
    assert 'Where appropriate' in common and 'As appropriate' in common
    assert 'Submitting a referral does not guarantee acceptance or an appointment.' in journey

    area = (ROOT / 'service-areas.html').read_text()
    assert 'Area guide — schematic, not a coverage boundary.' in area
    assert 'A listed suburb does not guarantee availability' in area
    print('PASS: visual SVG accessibility/dimensions; two-entry, qualified referral pathway; schematic area disclaimer')


if __name__ == '__main__':
    main()
