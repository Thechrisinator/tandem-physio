"""Protect crawlable coverage, regional discovery and truthful schema contracts."""
import json
from html.parser import HTMLParser

from check_site import ROOT, Page, PAGES, DOMAIN

GUIDES = ('hills-district-physiotherapy.html', 'blacktown-physiotherapy.html',
          'parramatta-physiotherapy.html')


class Directory(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.entries = []
        self.capture = False
        self.controls_hidden = False
        self.feed(source)

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if 'data-directory-controls' in attrs:
            self.controls_hidden = 'hidden' in attrs
        if tag == 'li' and 'data-suburb' in attrs:
            assert 'hidden' not in attrs, 'Suburbs must be in initial readable HTML'
            self.entries.append({'name': '', 'boundary': 'data-boundary' in attrs, 'text': ''})
        if 'suburb-name' in attrs.get('class', '').split():
            self.capture = True
        if tag == 'li':
            self.in_entry = 'data-suburb' in attrs

    def handle_data(self, data):
        if self.capture:
            self.entries[-1]['name'] += data
        if getattr(self, 'in_entry', False):
            self.entries[-1]['text'] += data

    def handle_endtag(self, tag):
        if tag == 'span':
            self.capture = False
        if tag == 'li':
            self.in_entry = False


def main():
    source = (ROOT / 'service-areas.html').read_text()
    directory = Directory(source)
    names = [entry['name'] for entry in directory.entries]
    assert len(names) >= 100 and len(names) == len(set(names)), 'Missing or duplicate suburbs'
    assert names == sorted(names, key=lambda name: name.removesuffix(" NSW").casefold()), 'Directory must stay alphabetical'
    assert {'Box Hill NSW', 'Glenorie NSW', 'Penrith NSW', 'Liverpool NSW',
            'Parramatta NSW', 'Dural NSW', 'Nirimba Fields NSW', 'Melonba NSW',
            'Grantham Farm NSW', 'Gables NSW', 'Bungarribee NSW'} <= set(names)
    assert directory.controls_hidden, 'Hide nonfunctional controls without JavaScript'
    assert any(entry['boundary'] for entry in directory.entries)
    for entry in directory.entries:
        assert bool('confirm exact-address travel' in entry['text']) == entry['boundary'], entry
    assert 'travel feasibility' in source and 'does not guarantee' in source
    page = Page(source)
    assert set(GUIDES) <= set(page.refs), 'Regional guides need ordinary HTML links'
    assert 'refer.html#check-suitability' in page.refs
    for file in PAGES:
        text = (ROOT / file).read_text()
        nav = text.split('<nav id="site-nav"', 1)[1].split('</nav>', 1)[0]
        assert not any(guide in nav for guide in GUIDES), 'Keep regional pages off primary navigation'
        for schema in Page(text).schemas:
            graph = json.loads(schema).get('@graph', [])
            assert all(node['@id'].startswith(DOMAIN) for node in graph)
            assert not any(key in schema for key in ['streetAddress', 'aggregateRating', 'reviewRating'])
    for file in GUIDES:
        text = (ROOT / file).read_text()
        assert text.count('<h1>') == 1
        main_content = text.split('<main id="main">', 1)[1].split('</main>', 1)[0]
        refs = Page(main_content).refs
        assert {'service-areas.html#suburb-directory', 'refer.html#check-suitability',
                'clinical-focus.html', 'mobile-physiotherapy.html'} <= set(refs), file
        assert 'referrals@tandemphysio.com.au' in main_content and 'availability' in main_content
    home = json.loads(Page((ROOT / 'index.html').read_text()).schemas[0])['@graph']
    organisation = next(node for node in home if node['@type'] == 'Organization')
    assert organisation['email'] == 'referrals@tandemphysio.com.au'
    assert organisation['telephone'] == '+61410048142' and 'address' not in organisation
    print(f'PASS: {len(names)} crawlable suburbs, boundary labels, three discoverable regional guides and schema safeguards')


if __name__ == '__main__':
    main()
