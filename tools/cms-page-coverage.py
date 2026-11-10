#!/usr/bin/env python3
"""Which CMS components on real pages have a Spartacus mapping?

usage: cms-page-coverage.py <keys.tsv from cms-mapping-keys.js> <OCC base, e.g. https://host/occ/v2/<site>> <page spec>...
page spec:  ContentPage:/cart   ProductPage:<code>   CategoryPage:<code>   ContentPage:homepage

The mapping key is resolved the same way as OccCmsPageNormalizer.getFlexTypeFromComponent:
CMSFlexComponent -> flexType, JspIncludeComponent -> uid, otherwise typeCode.
Components nested in a CMSTabParagraphContainer are fetched with cms/components.
"""
import json, sys, urllib.parse, urllib.request
from collections import defaultdict

keys_tsv, base, specs = sys.argv[1], sys.argv[2].rstrip('/'), sys.argv[3:]
mapped = {r.split('\t')[1] for r in open(keys_tsv) if r.startswith('map\t')}

def get(path, **q):
    url = f"{base}/{path}?{urllib.parse.urlencode(dict(q, fields='FULL'))}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)

def key(c):
    t = c.get('typeCode')
    return c.get('flexType') if t == 'CMSFlexComponent' else c.get('uid') if t == 'JspIncludeComponent' else t

seen = defaultdict(set)
for spec in specs:
    ptype, _, ident = spec.partition(':')
    q = {'pageType': ptype, ('pageLabelOrId' if ptype == 'ContentPage' else 'code'): ident}
    try:
        page = get('cms/pages', **q)
    except Exception as e:
        print(f"# {spec}: {e}", file=sys.stderr); continue
    comps = [c for s in page.get('contentSlots', {}).get('contentSlot', []) for c in s.get('components', {}).get('component', [])]
    nested = [u for c in comps if c.get('typeCode') == 'CMSTabParagraphContainer' for u in (c.get('components') or '').split()]
    if nested:
        comps += get('cms/components', componentIds=','.join(nested)).get('component', [])
    for c in comps:
        seen[(key(c), c.get('typeCode'))].add(spec)

print('mapped\tkey\ttypeCode\tpages')
for (k, t), pages in sorted(seen.items(), key=lambda x: (x[0][0] in mapped, x[0][1], x[0][0] or '')):
    print(f"{'yes' if k in mapped else 'NO'}\t{k}\t{t}\t{len(pages)}\t{' '.join(sorted(pages))}")
