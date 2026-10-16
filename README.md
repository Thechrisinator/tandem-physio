# tandem-physio

Run the offline baseline with Python 3.9+ (standard library only):

```sh
python3 -B scripts/check_site.py
python3 -B scripts/test_check_site.py
python3 -B scripts/check_home_images.py
python3 -B scripts/check_visuals.py
python3 -B scripts/check_clinical_pages.py
python3 -B scripts/check_service_areas.py
```

The checker exits nonzero for missing local HTML links/assets (`href`, `src`,
`poster`, Open Graph images and literal CSS `url()` references), missing HTML
fragment IDs, duplicate IDs, or invalid JSON-LD. It checks root HTML files,
inline CSS and stylesheets under `assets/`. Local path spelling is case-sensitive
to match GitHub Pages; external URLs are not fetched.

The twenty-one substantive pages listed in `PAGES` must each have exactly one nonempty
title, description, canonical URL and Open Graph title, description, type and
URL. Canonical and Open Graph URLs must match the page's HTTPS apex URL.
Each substantive page must reference the shared HTTPS apex Open Graph image
(`assets/og-image.png`).
The sitemap must list exactly those twenty-one URLs, and robots.txt must reference
the HTTPS sitemap exactly once. `thanks.html` and `404.html` require
`noindex, follow` and receive the structural checks; they are exempt from the
substantive metadata contract and excluded from the sitemap. New root
HTML pages must be classified explicitly.

This is not an HTML/CSS validator, accessibility audit, schema semantics check,
browser/visual test, prose snapshot, or live HTTPS/external-link check. It does
not execute JavaScript, submit forms, or inspect dynamically generated assets,
`srcset`, CSS imports/escapes, or nested HTML pages as a complete page inventory.
The second command proves representative failures in temporary copies and
leaves the working site untouched.

Clinical/referral pages cover stroke, MND, spinal cord injury, ABI/TBI, multiple
sclerosis, Parkinson’s disease/parkinsonism, falls risk and complex chronic pain.
The NDIS “Who we support” tags link to all eight pages. The clinical-page check
verifies those destinations, exact titles, unique matching description/Open Graph
metadata, canonical URLs, and core/related links on the seven new pages.
When adding a substantive page, update `PAGES`, `sitemap.xml` and this inventory.
Shared presentation remains in `assets/site.css`; no build step is required.

The image and visual checks cover the homepage assets, reusable visual
conventions, the PracSuite embed and fallback link, retained referral anchors and
privacy links, and the absence of old form URLs and multi-step referral flows.
The referral page embeds the existing referral-specific PracSuite URL using the
official resizing script and stylesheet, with a secondary new-tab link. The
PracSuite root URL asks for a form code and is not the referral destination.
Embedding may require the approved parent domain, tandemphysio.com.au; a
localhost restriction is not evidence that the form fails on that domain.
Browser checks are separate: use a local HTTP server and
review mobile, tablet and desktop layouts, menu behaviour, links and console
errors before release. GitHub Pages deploys the repository root from `main`. `_config.yml` excludes
repository documentation and maintenance scripts from the public site.
Keep review changes local until the user explicitly approves remote changes.


## Service-area maintenance

`service-areas.html` contains the complete alphabetical directory in ordinary HTML.
This is the only editable directory source; JavaScript only filters existing entries.
No CMS, API, generated list or build command is required. Search accepts suburb
names, not postcodes. Entries use this format:

```html
<li data-suburb><span class="suburb-name">Box Hill NSW</span></li>
<li data-suburb data-boundary><span class="suburb-name">Glenorie NSW</span><small>Boundary area — confirm exact-address travel</small></li>
```

The owner confirmed the broad Glenorie (north), Penrith (west), Liverpool (south)
and Parramatta (east) limits on 17 October 2026 and authorised labelled boundary
suburbs with exact-address travel confirmation. All visits remain subject to
clinical suitability, funding, availability and travel feasibility.

The initial 202 entries (147 interior and 55 boundary) use NSW Spatial Services'
[official suburb polygons](https://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Administrative_Boundaries/MapServer/0).
A rectangle through the four named localities' area-weighted polygon centroids
was used to interpret the general limits: longitude 150.693608 to 151.006878,
latitude -33.923637 to -33.571310. Entire polygons inside are interior; positive-area
intersections are labelled boundary. This is a documented geographic approximation,
not an owner-supplied precise boundary, travel-time map or promise of whole-suburb
coverage. Even a small intersection receives the boundary label. The owner should
refine individual entries as actual travel decisions become known.

To change coverage: obtain the owner's confirmation, check the official suburb
name, edit one HTML list item in alphabetical order, and keep the boundary label
where needed. Retain the availability qualification and enquiry option. Review
any matching guide copy if its named coverage changes. Run all checks above,
then test search, reset and a JavaScript-disabled browser before deploying.
The three regional guides are linked from content, not the primary navigation.

The homepage's address-free Organization, WebSite and Service identities use
stable IDs; page descriptions and guide breadcrumbs refer to them. Do not add a
residential address, unsupported credentials, ratings or unconditional funding
claims. Existing condition metadata remains unchanged. The permissive robots
file already allows Googlebot, Bingbot and OAI-SearchBot; GPTBot's prior access is
also unchanged. Search visibility and inclusion are not guaranteed.
