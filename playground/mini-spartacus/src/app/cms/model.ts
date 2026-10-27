/**
 * データモデル。上半分が「API の形」(OCC が返す JSON)、下半分が「State の形」。
 * 本家: core-libs/core/src/occ/occ-models/occ.models.ts(Occ.CMSPage ほか)、
 *       core-libs/core/src/cms/model/page.model.ts(Page, ContentSlotData, ContentSlotComponentData)
 */
export type PageType = 'ContentPage' | 'ProductPage';

export interface PageContext {
  id: string;
  type: PageType;
}

/** 本家 cms-utils.ts の serializePageContext に相当(ここでは常に type-id) */
export function serializePageContext(ctx: PageContext): string {
  return `${ctx.type}-${ctx.id}`;
}

// ---- API の形(cms/pages の応答) -------------------------------------------
export interface OccCmsComponent {
  uid: string;
  typeCode: string;
  [key: string]: unknown;
}
export interface OccContentSlot {
  slotId: string;
  position: string;
  components: { component: OccCmsComponent[] };
}
export interface OccCmsPage {
  uid: string;
  typeCode: PageType;
  template: string;
  title?: string;
  contentSlots: { contentSlot: OccContentSlot[] }; // 配列。position はこの中
}

// ---- State の形 -------------------------------------------------------------
export interface ContentSlotComponentData {
  uid: string;
  typeCode: string;
  flexType: string; // 実際に描画クラスを引く鍵
}
export interface ContentSlotData {
  components: ContentSlotComponentData[];
}
export interface Page {
  pageId: string; // uid から改名
  type: PageType; // typeCode から改名
  template: string;
  title?: string;
  slots: Record<string, ContentSlotData>; // 配列 → position をキーにした map
}
export interface CmsComponent {
  uid: string;
  typeCode: string;
  [key: string]: unknown;
}

// ---- 商品(cms とは別の Store) -------------------------------------------------
export interface Product {
  code: string;
  name: string;
  price: number;
}
export interface SearchResults {
  sortCode: string;
  products: Product[];
}
