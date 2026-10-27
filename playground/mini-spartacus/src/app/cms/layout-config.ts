/**
 * 表②: 「どの枠に、どのスロットを、どの順番で」。フロント側の設定。
 * 本家 core-libs/storefront/recipes/config/layout-config.ts:33-64
 * header / footer は外枠のセクション名、それ以外はページテンプレート名。
 * ★ 実験: Section2A と Section1 を入れ替える、Tabs を消す、をやってみる。
 */
export const layoutConfig: Record<string, string[]> = {
  header: ['SiteLogo', 'SearchBox'],
  footer: ['Footer'],
  LandingPage2Template: ['Section1', 'Section2A'],
  SearchResultsListPageTemplate: ['ProductListSlot'],
  ProductDetailsPageTemplate: ['Summary', 'Tabs'],
  ErrorPageTemplate: ['MiddleContent'],
};
