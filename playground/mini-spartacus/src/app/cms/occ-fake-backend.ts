import { Injectable, inject } from '@angular/core';
import { Observable, defer, of } from 'rxjs';
import { delay, tap } from 'rxjs/operators';
import { DebugLogService } from '../debug/debug-log.service';
import { OccCmsPage, PageContext, Product, SearchResults } from './model';

/**
 * SAP Commerce の OCC の代わり。HTTP の代わりに delay で待たせる。
 * ここに書いてある JSON が「CMS の管理画面で組んだページ」そのもの。
 * 本家の Adapter: core-libs/core/src/occ/adapters/cms/occ-cms-page.adapter.ts
 *
 * ★ 実験: スロットの順番を入れ替える、コンポーネントを別スロットへ動かす、
 *   typeCode を存在しない名前にする、新しい position を足す、をやってみる。
 *   フロントのコードを 1 行も触らずに画面が変わる(または変わらない)のが分かる。
 */
const PAGES: Record<string, OccCmsPage> = {
  homepage: {
    uid: 'homepage',
    typeCode: 'ContentPage',
    template: 'LandingPage2Template',
    title: 'Home',
    contentSlots: {
      contentSlot: [
        slot('SiteLogo', [{ uid: 'SiteLogoComponent', typeCode: 'SiteLogoComponent' }]),
        slot('SearchBox', [{ uid: 'SearchBoxComponent', typeCode: 'SearchBoxComponent' }]),
        slot('Section1', [
          {
            uid: 'HomepageSplashBanner',
            typeCode: 'SimpleBannerComponent',
            headline: 'Mini Spartacus',
            content: 'CMS のデータがページを組み立てる。クリックで商品ページへ。',
            productCode: '1934793',
          },
        ]),
        slot('Section2A', [
          {
            uid: 'HomepageParagraph',
            typeCode: 'CMSParagraphComponent',
            content:
              '<p>この段落は <code>cms/pages</code> 応答の <code>Section2A</code> スロットに入っている <code>CMSParagraphComponent</code> です。</p>',
          },
        ]),
        slot('Footer', [{ uid: 'FooterNavigationComponent', typeCode: 'FooterNavigationComponent' }]),
      ],
    },
  },
  search: {
    uid: 'search',
    typeCode: 'ContentPage',
    template: 'SearchResultsListPageTemplate',
    title: 'Search',
    contentSlots: {
      contentSlot: [
        slot('SiteLogo', [{ uid: 'SiteLogoComponent', typeCode: 'SiteLogoComponent' }]),
        slot('SearchBox', [{ uid: 'SearchBoxComponent', typeCode: 'SearchBoxComponent' }]),
        slot('ProductListSlot', [
          { uid: 'SearchResultsListComponent', typeCode: 'CMSProductListComponent' },
        ]),
        slot('Footer', [{ uid: 'FooterNavigationComponent', typeCode: 'FooterNavigationComponent' }]),
      ],
    },
  },
  // 商品ページは全商品で 1 枚。どの商品かは URL(:code)から各コンポーネントが読む
  productDetails: {
    uid: 'productDetails',
    typeCode: 'ProductPage',
    template: 'ProductDetailsPageTemplate',
    title: 'Product Details',
    contentSlots: {
      contentSlot: [
        slot('SiteLogo', [{ uid: 'SiteLogoComponent', typeCode: 'SiteLogoComponent' }]),
        slot('SearchBox', [{ uid: 'SearchBoxComponent', typeCode: 'SearchBoxComponent' }]),
        slot('Summary', [{ uid: 'ProductSummaryComponent', typeCode: 'ProductSummaryComponent' }]),
        slot('Tabs', [
          {
            uid: 'ProductDetailsParagraph',
            typeCode: 'CMSParagraphComponent',
            content: '<p>商品ページ共通の段落。どの商品でも同じ uid なので作り直されない。</p>',
          },
        ]),
        slot('Footer', [{ uid: 'FooterNavigationComponent', typeCode: 'FooterNavigationComponent' }]),
      ],
    },
  },
  notFound: {
    uid: 'notFound',
    typeCode: 'ContentPage',
    template: 'ErrorPageTemplate',
    title: 'Not Found',
    contentSlots: {
      contentSlot: [
        slot('SiteLogo', [{ uid: 'SiteLogoComponent', typeCode: 'SiteLogoComponent' }]),
        slot('MiddleContent', [
          {
            uid: 'NotFoundParagraph',
            typeCode: 'CMSParagraphComponent',
            content: '<p>CMS にこの URL のページはありません(notFound ページを表示中)。</p>',
          },
        ]),
        slot('Footer', [{ uid: 'FooterNavigationComponent', typeCode: 'FooterNavigationComponent' }]),
      ],
    },
  },
};

const PRODUCTS: Product[] = [
  { code: '1934793', name: 'PowerShot A480', price: 99.85 },
  { code: '300938', name: 'Photosmart E317 Digital Camera', price: 114.12 },
  { code: '3557133', name: 'Cyber-shot DSC-W55', price: 150.0 },
  { code: '816802', name: 'EasyShare M1033', price: 232.0 },
  { code: '1382080', name: 'PowerShot G9', price: 442.25 },
];

const LATENCY = 400;

@Injectable({ providedIn: 'root' })
export class OccFakeBackend {
  private log = inject(DebugLogService);

  /** GET cms/pages?pageType=...&pageLabelOrId=... / &code=... */
  loadPage(ctx: PageContext): Observable<OccCmsPage | null> {
    const key = ctx.type === 'ProductPage' ? 'productDetails' : ctx.id;
    const query =
      ctx.type === 'ProductPage'
        ? `pageType=ProductPage&code=${ctx.id}`
        : `pageType=ContentPage&pageLabelOrId=${ctx.id}`;
    return this.http(`cms/pages?${query}`, PAGES[key] ?? null);
  }

  /** GET products/search?sort=... */
  searchProducts(sortCode: string): Observable<SearchResults> {
    const products = [...PRODUCTS].sort((a, b) =>
      sortCode === 'price-asc' ? a.price - b.price
      : sortCode === 'price-desc' ? b.price - a.price
      : sortCode === 'name-asc' ? a.name.localeCompare(b.name)
      : 0
    );
    return this.http(`products/search?sort=${sortCode}`, { sortCode, products });
  }

  /** GET products/{code} */
  getProduct(code: string): Observable<Product | null> {
    return this.http(`products/${code}`, PRODUCTS.find((p) => p.code === code) ?? null);
  }

  private http<T>(url: string, body: T): Observable<T> {
    return defer(() => {
      this.log.http(`→ GET ${url}`);
      // 本物の HttpClient と同じく、応答は別のマクロタスクで届く
      return of(structuredClone(body)).pipe(
        delay(LATENCY),
        tap(() => this.log.http(`← 200 ${url}${body === null ? '(該当なし)' : ''}`))
      );
    });
  }
}

function slot(position: string, components: Array<Record<string, unknown> & { uid: string; typeCode: string }>): import('./model').OccContentSlot {
  return { slotId: position + 'Slot', position, components: { component: components } };
}
