#!/usr/bin/env python3
"""Where does each CMS component on a page sit, and will Spartacus render it as an Angular component?

usage: cms-component-placement.py <OCC base, e.g. https://host/occ/v2/<site>> <page spec>... [--uid <uid>]
page spec:  ContentPage:homepage   ContentPage:/cart   ProductPage:<code>   CategoryPage:<code>

Placement (29-2 章):
  slot     … directly in a content slot. cx-page-slot passes it to cxComponentWrapper (page-slot.component.html:14),
             so cmsComponents mappings and the flexType outlet apply.
  wrapper  … listed by a parent that passes children to cxComponentWrapper itself:
             CMSTabParagraphContainer.components (tab-paragraph-container.component.html:10),
             RotatingImagesComponent.banners (banner-carousel.component.html:11). Mappings apply.
  data     … an entry of a navigation node. NavigationService reads it as data (navigation.service.ts:166-193);
             it is never created as an Angular component, so mappings and outlets do not apply.
"""
import json, sys, urllib.parse, urllib.request

args = sys.argv[1:]
only = None
if '--uid' in args:
    i = args.index('--uid'); only = args[i + 1]; del args[i:i + 2]
base, specs = args[0].rstrip('/'), args[1:]
WRAPPER_PARENTS = {'CMSTabParagraphContainer': 'components', 'RotatingImagesComponent': 'banners'}

def get(path, **q):
    url = f"{base}/{path}?{urllib.parse.urlencode(dict(q, fields='FULL'))}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)

def walk_nodes(node, path):
    for e in node.get('entries') or []:
        yield e, path + [node.get('uid', '?')]
    for ch in node.get('children') or []:
        yield from walk_nodes(ch, path + [node.get('uid', '?')])

rows = []
for spec in specs:
    ptype, _, ident = spec.partition(':')
    q = {'pageType': ptype, ('pageLabelOrId' if ptype == 'ContentPage' else 'code'): ident}
    page = get('cms/pages', **q)
    for slot in page.get('contentSlots', {}).get('contentSlot', []):
        for c in slot.get('components', {}).get('component', []):
            rows.append((spec, 'slot', c['uid'], c.get('typeCode'), slot.get('position')))
            attr = WRAPPER_PARENTS.get(c.get('typeCode'))
            if attr and c.get(attr):
                for uid in c[attr].split():
                    rows.append((spec, 'wrapper', uid, '?', f"{c['uid']}.{attr}"))
            if c.get('navigationNode'):
                for e, path in walk_nodes(c['navigationNode'], [c['uid']]):
                    rows.append((spec, 'data', e.get('itemId'), e.get('itemType'), ' > '.join(path)))

for spec, place, uid, t, where in rows:
    if only and uid != only:
        continue
    print(f"{spec}\t{place}\t{uid}\t{t}\t{where}")
if not only:
    from collections import Counter
    print('#', dict(Counter(r[1] for r in rows)), file=sys.stderr)
