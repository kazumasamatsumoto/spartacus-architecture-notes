# 11. バックエンドでカスタム CMS コンポーネントを作るとき、フロントへ渡す仕様

> **図**: 03 カスタムコンポーネントのデータ経路(`diagrams/spartacus-architecture.drawio`)。本章が扱うのは左の経路 A(CMS 属性)。経路 B(業務データ)は 15 章

![03 カスタムコンポーネントのデータ経路](diagrams/page3.png)

> **この章が答える問い**: バックエンドでカスタム CMS コンポーネントを作ったとき、フロントに何を渡せば表示されるか(①→依頼書)
>
> **位置づけ**: 9〜10 章を踏まえて、CMS コンポーネントを 1 つ作るとき依頼書に何を書くか


### 先に話し言葉で: 依頼書に書くのは 3 つ、フロントの作業は 1 行

カスタム CMS コンポーネントを 1 つ作ったとき、フロントに渡す情報は 3 つです。**`typeCode`**(どの Angular コンポーネントを選ぶかのキー)、**属性の一覧と型**(`cms/pages` に同梱されて届く中身)、**業務データを見せるならその参照 ID**(商品コードや店舗 ID。本体ではなく ID)。フロント側の作業は原則、`provideConfig` に `typeCode` とコンポーネントの対応を 1 行足し、`CmsComponentData` から `data$` を受け取って描くことだけです(11.3)。

8.0 の規則で言うと、属性だけで完結するコンポーネントは `cms/pages` の応答に収まるので API は 1 本も増えません。参照 ID を持つコンポーネントは、その ID のリソースを「購読した瞬間」に初回だけ API が増えます(7.1 の階層 3、11.6)。依頼書を書く前に、自分のコンポーネントがどちらかを決めておくと、フロントとの会話が短くなります。

### 11.1 鍵になる 3 つの値

| 値 | バックエンドでの定義 | フロントでの使われ方 |
|---|---|---|
| `typeCode` | `*-items.xml` の ItemType 名(例: `MyPromoBannerComponent extends SimpleCMSComponent`) | `cmsComponents` のキー(3.4 の表)。**この文字列の一致がすべて** |
| `flexType` | `CMSFlexComponent` を使う場合のみ、その属性値 | `CMSFlexComponent` のときはこちらがキー |
| `uid` | コンポーネントインスタンスの uid | `CmsComponentData.uid` とデータ取得キー。`JspIncludeComponent` のときのみマッピングキー |

新しい ItemType を作る(= typeCode が新しい)のであれば、フロントに新しいマッピングが必要。**既存 typeCode のインスタンスを増やすだけなら、フロント作業は不要**(例: `SimpleResponsiveBannerComponent` をもう 1 つ置く)。

### 11.2 OCC が返す JSON の形(デモ実物)

`GET .../cms/pages` 内の 1 コンポーネント(`CMSParagraphComponent`):
```json
{
  "uid": "NoticeTextParagraph",
  "uuid": "eyJpdGVtSWQiOi...",
  "typeCode": "CMSParagraphComponent",
  "modifiedtime": "2026-02-13T22:41:44.318Z",
  "name": "Notice Text Paragraph",
  "container": "false",
  "synchronizationBlocked": "false",
  "content": "<div class=\"cx-notice\">Copyright © 2020 SAP SE ...</div>"
}
```
`CMSFlexComponent`(`flexType` がキーになる例):
```json
{
  "uid": "PageTitleComponent",
  "typeCode": "CMSFlexComponent",
  "name": "Page Header Component",
  "container": "false",
  "flexType": "PageTitleComponent",
  "synchronizationBlocked": "false"
}
```
`ProductCarouselComponent`(複数値はスペース区切りの **1 つの文字列**):
```json
{
  "uid": "ElectronicsHomepageProductCarouselComponent",
  "typeCode": "ProductCarouselComponent",
  "container": "false",
  "popup": "false",
  "scroll": "ALLVISIBLE",
  "productCodes": "300938 358639 553637 816802 1934793 1382080 1981415 816780 1934406 1986316 592506",
  "title": "Our Bestselling Products"
}
```
フロント側のモデルはこの JSON をそのまま TypeScript インターフェースにしたもの(`spartacus/core-libs/core/src/model/cms.model.ts:7-32, 88-92, 137-144`):
```ts
export interface CmsComponent {
  modifiedTime?: Date;
  name?: string;
  otherProperties?: any;
  typeCode?: string;
  uid?: string;
  composition?: { inner?: string[] };
  ...
  styleClasses?: string;
}
export interface CmsParagraphComponent extends CmsComponent {
  content?: string;
  container?: string;
  title?: string;
}
export interface CmsProductCarouselComponent extends CmsComponent {
  categoryCodes?: string;
  title?: string;
  productCodes?: string;
  container?: string;
  popup?: string;
  scroll?: string;
}
```
**注意点**: OCC の CMS コンポーネント DTO は属性を文字列化する(`"container": "false"`、`productCodes` はスペース区切り)。真偽値・複数値・参照(商品コード、メディア)をどう表現するかを依頼書に明記すること。メディアは `media: { desktop:{url,altText,mime,code}, tablet, mobile, widescreen }` 形式(`cms.model.ts:99-117`、11.2 冒頭のバナー JSON 参照)。

### 11.3 フロント側の実装雛形(Angular)

リポジトリの既存コンポーネントと同じ書き方。例: 段落(`spartacus/core-libs/storefront/cms-components/content/paragraph/`)。

**(1) モデル** — OCC JSON と同じ属性名で `CmsComponent` を拡張
```ts
// my-promo-banner.model.ts
import { CmsComponent } from '@spartacus/core';
export interface CmsMyPromoBannerComponent extends CmsComponent {
  headline?: string;
  content?: string;       // HTML 可
  productCode?: string;   // 参照は code 文字列
  backgroundColor?: string;
}
```

**(2) コンポーネント** — `CmsComponentData<T>` を注入し `data$` を `async` パイプで描画(参照: `paragraph.component.ts:20-47`, `paragraph.component.html:1-4`)
```ts
// my-promo-banner.component.ts
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { AsyncPipe, NgIf } from '@angular/common';
import { CmsComponentData } from '@spartacus/storefront';
import { CmsMyPromoBannerComponent } from './my-promo-banner.model';

@Component({
  selector: 'cx-my-promo-banner',
  template: `
    <section *ngIf="data$ | async as data" [style.background]="data.backgroundColor">
      <h2>{{ data.headline }}</h2>
      <div [innerHTML]="data.content"></div>
    </section>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NgIf, AsyncPipe],
})
export class MyPromoBannerComponent {
  protected componentData = inject<CmsComponentData<CmsMyPromoBannerComponent>>(CmsComponentData);
  data$ = this.componentData.data$;
}
```

**(3) マッピング登録** — typeCode をキーに `provideConfig`(参照: `paragraph.module.ts:21-31` は `provideDefaultConfig` だが、アプリ側は `provideConfig` を使う)
```ts
// my-promo-banner.module.ts
import { NgModule } from '@angular/core';
import { CmsConfig, provideConfig } from '@spartacus/core';
import { MyPromoBannerComponent } from './my-promo-banner.component';

@NgModule({
  imports: [MyPromoBannerComponent],
  providers: [
    provideConfig(<CmsConfig>{
      cmsComponents: {
        MyPromoBannerComponent: {          // ← バックエンドの typeCode と完全一致
          component: MyPromoBannerComponent,
        },
      },
    }),
  ],
})
export class MyPromoBannerModule {}
```
このモジュールをアプリの `SpartacusFeaturesModule`(または `AppModule`)の `imports` に追加する。参照アプリでは `spartacus/projects/storefrontapp/src/app/spartacus/spartacus-features.module.ts` / `spartacus-configuration.module.ts` に相当。

**(4) 遅延ロードさせたい場合** — 機能名を決め、`featureModules` で `cmsComponents` の typeCode 一覧と `import()` を結びつける(参照: `feature-libs/cart/quick-order/root/quick-order-root.module.ts:23-34`, `projects/storefrontapp/src/app/spartacus/features/cart/cart-quick-order-feature.module.ts:21-32`)
```ts
provideConfig(<CmsConfig>{
  featureModules: {
    myPromo: {
      cmsComponents: ['MyPromoBannerComponent'],
      module: () => import('./my-promo-banner.module').then((m) => m.MyPromoBannerModule),
    },
  },
}),
```
この場合、`cmsComponents` マッピング自体は遅延モジュール側の `providers` に置く(`cms-features.service.ts:188-204` が遅延モジュールの `ConfigChunk` を読む)。ページにその typeCode が現れたときだけチャンクがロードされる(`cms-page-guard.service.ts:71-74` の `determineMappings`)。

### 11.4 マッピングで指定できるオプション

`spartacus/core-libs/core/src/cms/config/cms-config.ts:60-93`
```ts
export interface CmsComponentMapping<T = CmsComponent> {
  component?: any;
  providers?: StaticProvider[];
  childRoutes?: Route[] | CmsComponentChildRoutesConfig;
  disableSSR?: boolean;
  i18nKeys?: string[];
  guards?: any[];
  data?: T;
  deferLoading?: DeferLoadingStrategy;
}
```

| オプション | 用途 | 実例 |
|---|---|---|
| `component` | Angular コンポーネントクラス、`() => import()`、または Web Component `'script.js#tag'` | `banner.module.ts:30-47`(3 typeCode → 1 コンポーネント) |
| `providers` | そのコンポーネント専用 DI(`CmsComponentData` を deps にできる) | `site-context-selector.module.ts:34-45`(属性 `context` が `LANGUAGE`/`CURRENCY` で挙動切替) |
| `guards` | 認証などの `canActivate` | `address-book.module.ts:34-41`(`guards: [AuthGuard]`) |
| `childRoutes` | そのコンポーネントがページに置かれたときだけ有効になる子ルート | `store-finder-components.module.ts:67-99`、`budget.config.ts:30-79` |
| `data` | API に無い UI 専用プロパティや初期値 | `category-navigation.module.ts:21-30`、`product-list.module.ts:68-75`(`composition.inner`) |
| `deferLoading` | ビューポート外でも即描画(`INSTANT`) | `anonymous-consent-management.module.ts:31-42` |
| `i18nKeys` / `disableSSR` | 翻訳チャンク / SSR では描画しない | 型定義のみ。標準ライブラリ内に使用例なし |

### 11.5 新しいスロットやページテンプレートを作る場合

バックエンドで**新しいページテンプレートやスロット位置**を定義した場合、フロントの `LayoutConfig.layoutSlots` に追加しないとそのスロットは描画されない(3.5)。依頼書にテンプレート名とスロット位置名、望む描画順を書くこと。
```ts
provideConfig(<LayoutConfig>{
  layoutSlots: {
    MyCampaignPageTemplate: {
      slots: ['HeroSlot', 'Section1', 'Section2', 'FooterCtaSlot'],
    },
  },
}),
```
型: `spartacus/core-libs/storefront/layout/config/layout-config.ts:36-61, 94-102`。既存テンプレートに既存スロットを使い回すなら設定変更は不要。

### 11.6 コンポーネントが追加データを必要とする場合

CMS 属性に「商品コード」「カテゴリコード」のような参照だけを持たせ、実体はフロントが Facade 経由で取りに行くのが標準パターン。商品カルーセルの実装(`spartacus/core-libs/storefront/cms-components/product/carousel/product-carousel/product-carousel.component.ts:69-83`):
```ts
  items$: Observable<Observable<Product | undefined>[]> =
    this.componentData$.pipe(
      switchMap((data) => this.handleCategoryCodes(data)),
      map((data) => {
        const componentMappingExist = !!data.composition?.inner?.length;
        const codes = data.productCodes?.trim().split(' ') ?? [];
        return { componentMappingExist, codes };
      }),
      map(({ componentMappingExist, codes }) => {
        const scope = componentMappingExist ? 'carousel' : 'carouselMinimal';
        return codes.map((code: string) =>
          this.productSearchByCodeService.get({ code, scope })
        );
      })
    );
```
`ProductSearchByCodeService.get` はストアに無いときだけロードを dispatch し(`product-search-by-code.service.ts:46-53`)、Effect が同時要求をまとめて `products/search?filters=code:...` 1 本にする(8.2 (h))。**バックエンドが CMS 属性に商品データをコピーして持つ必要はない**。逆に、OCC に無い情報が必要なら「商品 API 側の拡張」か「CMS 属性として持たせる」かを依頼書で決める。

### 11.7 既存コンポーネントの差し替え・部分差し替え

- **同じ typeCode に別コンポーネントを `provideConfig` で上書き**: アプリ側の設定が標準ライブラリの `provideDefaultConfig` より優先される(`cms-components.service.ts:126-133` の `deepMerge(featureMapping, staticConfig)` でアプリ設定が後勝ち)。バックエンド変更は不要。
- **アウトレット**で既存レイアウトの前後に差し込む(`provideOutlet({ id: 'AddToCart', position: OutletPosition.AFTER, component })`)。スロット内の各コンポーネントは `flexType` 名のアウトレットに包まれている(3.6)。
- **静的 `cmsStructure`**: バックエンド変更前にフロントだけで動作確認する手段(`spartacus/core-libs/storefront/cms-structure/utils/cms-structure.util.ts:31-66`, `cms-structure.config.ts:79-85`)。

使い分けはリポジトリ同梱の `spartacus/core-libs/skills/skills/spartacus-developer/references/placement-mechanisms.md` にも整理されている。

### 11.8 「FE への依頼書」に書くべき項目

1. **typeCode**(ItemType 名)。`CMSFlexComponent` 流用なら `flexType` の値
2. **OCC が返す属性の一覧**: 名前 / 型(すべて文字列化される点に注意) / 必須か / 例。真偽値・列挙・複数値・参照・メディア・ローカライズ属性の表現方法
3. **実際の `cms/pages` レスポンス JSON のサンプル**(開発環境の OCC から取得して添付)
4. **配置先**: ページテンプレート名、スロット位置名、既存か新規か(新規なら `layoutSlots` 追加が必要)
5. **追加で必要なデータ**: 商品・カテゴリ・在庫など、CMS 属性に持たせず参照だけ渡すもの
6. **振る舞い要件**: ログイン必須(`guards`)、子ルート、SSR 可否、遅延描画の可否、翻訳キー
7. **既存コンポーネントの流用可否**: 既存 typeCode(例: `SimpleResponsiveBannerComponent`, `CMSParagraphComponent`, `ProductCarouselComponent`)で済むならフロント作業はゼロ
8. **遅延ロードの希望**(機能単位でチャンク分割するか)


---

[目次](README.md) | ← [10. フロント側の呼び出し方法はリソースごとに違うのか](10-frontend-call-patterns.md) | [12. バックエンド(Java)側: 何を、どの単位で返すか](12-backend-api-granularity.md) →
