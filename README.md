# tandem-physio

Run the offline baseline with Python 3.9+ (standard library only):

```sh
python3 scripts/check_site.py
python3 scripts/test_check_site.py
```

The checker exits nonzero for missing local HTML links/assets (`href`, `src`,
`poster`, Open Graph images and literal CSS `url()` references), missing HTML
fragment IDs, duplicate IDs, or invalid JSON-LD. It checks root HTML files,
inline CSS and stylesheets under `assets/`. Local path spelling is case-sensitive
to match GitHub Pages; external URLs are not fetched.

The ten substantive pages listed in `PAGES` must each have exactly one nonempty
title, description, canonical URL and Open Graph title, description, type and
URL. Canonical and Open Graph URLs must match the page's HTTPS apex URL.
The sitemap must list exactly those ten URLs, and robots.txt must reference
the HTTPS sitemap exactly once. `thanks.html` is explicitly exempt from
metadata/sitemap requirements, but receives the structural checks. New root
HTML pages must be classified explicitly.

This is not an HTML/CSS validator, accessibility audit, schema semantics check,
browser/visual test, prose snapshot, or live HTTPS/external-link check. It does
not execute JavaScript, submit forms, or inspect dynamically generated assets,
`srcset`, CSS imports/escapes, or nested HTML pages as a complete page inventory.
The second command proves representative failures in temporary copies and
leaves the working site untouched.
