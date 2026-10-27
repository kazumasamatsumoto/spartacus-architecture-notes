import { CmsComponent, OccCmsPage, Page } from './model';

/**
 * API の形 → State の形。本家 occ-cms-page-normalizer.ts と同じ 4 つの作り変え:
 *  1. uid → pageId、typeCode → type に改名
 *  2. contentSlots.contentSlot[](配列)→ slots[position](map)
 *  3. スロット内コンポーネントは uid / typeCode / flexType の 3 項目に削る
 *  4. コンポーネント本体(headline, content ...)は別の表(components)へ分離する
 * 「DevTools の State が API の JSON と違う」のはここが原因。
 */
export function normalizeCmsPage(occ: OccCmsPage): { page: Page; components: CmsComponent[] } {
  const page: Page = {
    pageId: occ.uid,
    type: occ.typeCode,
    template: occ.template,
    title: occ.title,
    slots: {},
  };
  const components: CmsComponent[] = [];

  for (const s of occ.contentSlots.contentSlot) {
    page.slots[s.position] = {
      components: s.components.component.map((c) => {
        components.push({ ...c }); // 本体は components 表へ
        return { uid: c.uid, typeCode: c.typeCode, flexType: c.typeCode }; // 構造には鍵だけ残す
      }),
    };
  }
  return { page, components };
}
