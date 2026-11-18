// 29-2 のサンプルで使う仮のアイコン。実在の会社のロゴは使わず、頭文字の丸を SVG で作る
// 本番では、バックエンドが CMSLinkComponent に足した属性(例: logoUrl)の URL を使う
const COLORS = ['#7b2cbf', '#2a9d8f', '#e76f51', '#264653', '#e9c46a'];

export function sampleBrandLogo(item: { categoryCode?: string; linkName?: string } | undefined): string | undefined {
  if (!item?.categoryCode?.startsWith('brand_') || !item.linkName) {
    return undefined;
  }
  const color = COLORS[Number(item.categoryCode.replace('brand_', '')) % COLORS.length];
  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">` +
    `<circle cx="10" cy="10" r="10" fill="${color}"/>` +
    `<text x="10" y="14" font-size="11" text-anchor="middle" fill="#fff" font-family="sans-serif">${item.linkName[0]}</text></svg>`;
  return 'data:image/svg+xml,' + encodeURIComponent(svg);
}
