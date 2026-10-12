"""Offline checks for the accessible, qualified V3 visual summaries."""
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ('clinical-focus', 'mobile-physiotherapy', 'service-areas', 'index', 'about')


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
    tags = Visuals(referral).tags
    form_url = 'https://tandemphysio.forms.pracsuite.com/t/25QzUp7bP3gyywLILMefzepi'
    form_links = [attrs for tag, attrs in tags if tag == 'a' and attrs.get('href') == form_url]
    assert len(form_links) == 1, 'Referral page must offer one PracSuite fallback link'
    assert form_links[0].get('target') == '_blank'
    assert 'noopener' in form_links[0].get('rel', '').split()
    frames = [attrs for tag, attrs in tags if tag == 'iframe']
    assert len(frames) == 1, 'Referral page must embed one PracSuite form'
    assert frames[0].get('id') == 'psforms-iframe'
    assert frames[0].get('src') == form_url
    assert frames[0].get('title'), 'Embedded form needs an accessible title'
    assert frames[0].get('width') == '100%'
    assert 'scrolling' not in frames[0], 'Allow scrolling if the resize script is unavailable'
    assert sum(attrs.get('id') == 'psforms-iframe-container' for tag, attrs in tags) == 1
    assert sum(tag == 'script' and attrs.get('src') ==
               'https://tandemphysio.forms.pracsuite.com/static_js/embed-forms.js'
               for tag, attrs in tags) == 1
    assert sum(tag == 'link' and attrs.get('href') ==
               'https://tandemphysio.forms.pracsuite.com/css/embed-forms.css'
               for tag, attrs in tags) == 1
    ids = {attrs.get('id') for tag, attrs in tags}
    assert {'referral-form', 'check-suitability'} <= ids, 'Existing referral anchors must work'
    links = {attrs.get('href') for tag, attrs in tags if tag == 'a'}
    assert {'privacy.html#referral-collection-notice', 'privacy.html#privacy-policy',
            'mailto:referrals@tandemphysio.com.au', 'tel:0410048142'} <= links
    assert 'Submitting a referral does not guarantee acceptance or an appointment.' in referral

    for page in ROOT.glob('*.html'):
        source = page.read_text()
        assert 'docs.google.com/forms' not in source and 'forms.gle/' not in source, page.name
        assert 'tandemphysionsw@gmail.com' not in source, page.name
        tags = Visuals(source).tags
        assert not any(attrs.get('class') in ('journey-entries', 'journey-common', 'tp-path-list')
                       for tag, attrs in tags), page.name
    assert 'Google Forms' not in (ROOT / 'thanks.html').read_text()

    area = (ROOT / 'service-areas.html').read_text()
    assert 'Area guide — schematic, not a coverage boundary.' in area
    assert 'A listed suburb does not guarantee availability' in area
    print('PASS: visual accessibility; PracSuite embed, resizing assets and fallback; referral anchors/privacy links; no legacy forms or flows; area disclaimer')


if __name__ == '__main__':
    main()
