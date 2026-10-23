# SAP Composable Storefront (Spartacus) アーキテクチャ解説

**目的**: バックエンド(SAP Commerce Cloud)でカスタム CMS コンポーネントを作る担当者が、フロントエンド(Spartacus)側に「何を・どう」依頼すればよいかを、ソースコードを根拠に理解する。

**調査対象**

| 項目 | 値 | 根拠 |
|---|---|---|
| リポジトリ | https://github.com/SAP/spartacus `develop` | クローン先 `spartacus/`(本リポジトリ直下) |
| コミット | `b7b028f22814412ccbd8be3c7f688d4119abdc5f`(2026-10-22) | `git log -1` |
| Spartacus バージョン | 2612.0.0 | `spartacus/package.json:3` |
| Angular | ~21.2.23 | `spartacus/package.json`(`@angular/core`) |
| NgRx / RxJS / i18next | ~21.0.1 / ~7.8.0 / ~25.7.4 | 同上 |
| デモサイト | https://composable-storefront-demo.eastus.cloudapp.azure.com/electronics-spa/en/USD/ | 2026-10-23 実測 |

本書のソース引用はすべて `spartacus/<パス>:<行>` 形式で、上記コミットのファイルを指す。

---

## 0. 要約

1. **Spartacus は Angular アプリ**である。SAP が提供するのは Angular ライブラリ群(`@spartacus/core`, `@spartacus/storefront`, 機能ライブラリ)で、利用者は Angular CLI プロジェクトにそれらを組み込む。
2. **描画の主導権は CMS バックエンドにある**。ルーティングは `**`(ワイルドカード)で全 URL を受け、OCC の `cms/pages` からページ構造(テンプレート → スロット → コンポーネント)を取得して描画する。Angular のルート定義にページを書くのではない。
3. **バックエンドの `typeCode`(CMSFlexComponent なら `flexType`)が、フロントの Angular コンポーネントを選ぶキー**になる。フロント側の作業は原則「`provideConfig({ cmsComponents: { <typeCode>: { component: XxxComponent } } })` を 1 つ追加し、`CmsComponentData<T>` を注入して `data$` を描く」だけ。
4. **API が少ないのは設計どおり**。`cms/pages` のレスポンスに全コンポーネントのデータが同梱され、NgRx ストアに入る。足りない分だけ `cms/components?componentIds=...` でまとめて取り、取得済みは再取得しない。商品カルーセルも `products/search?filters=code:...` で一括取得する。
5. デモサイトは **CSR 配信(SSR なし)**。それでもホーム初回表示の OCC GET は 9 本程度、商品詳細への SPA 遷移は 6 本だった。SSR を有効にすると TransferState でさらに減る。
6. **動的な業務データ**を表示するコンポーネントは、フロントに Facade / Connector / Adapter / Normalizer を追加し(7 章)、バックエンドは**コンポーネント単位ではなくリソース単位**の OCC エンドポイントを用意する(8 章)。

### 図(draw.io)

`docs/diagrams/spartacus-architecture.drawio`(4 ページ)。PNG / SVG 書き出し済み。

| ページ | 内容 | 画像 |
|---|---|---|
| 01 全体フロー URL→描画 | 3 章の 10 ステップと OCC 呼び出しの対応 | [page1.png](diagrams/page1.png) |
| 02 レイヤ構成 | アプリ → 機能ライブラリ → storefront → core → OCC → SAP Commerce | [page2.png](diagrams/page2.png) |
| 03 カスタムコンポーネントのデータ経路 | 経路 A(CMS 属性)と経路 B(業務データ: Facade〜Java Controller) | [page3.png](diagrams/page3.png) |
| 04 バックエンド判断フロー | 何を・どの単位で返すかの判断木 | [page4.png](diagrams/page4.png) |

![全体フロー](diagrams/page1.png)

---

## 1. Angular 入門(バックエンド担当者向け)と Spartacus への対応

> この章は、Angular を知らない読者が 2 章以降を読めるようにするための最小限の対応表です。各概念の「Spartacus ではここ」を実ファイルで示します。

### 1.1 技術スタック(根拠: `spartacus/package.json`)

| 技術 | バージョン | 役割 |
|---|---|---|
| Angular (`@angular/core`, `@angular/ssr`, `@angular/platform-server`) | ~21.2.23 | UI フレームワーク本体、SSR |
| NgRx (`@ngrx/store`, `@ngrx/effects`, `@ngrx/router-store`) | ~21.0.1 | 状態管理(Redux パターン) |
| RxJS | ~7.8.0 | 非同期ストリーム(`Observable`) |
| i18next (+ `i18next-http-backend`, `i18next-resources-to-backend`) | ~25.7.4 | 翻訳(Angular 標準 i18n ではない) |
| TypeScript / Node.js | ~5.9.3 / ^22.22.0 | `package.json:290`, `:11-13` |
| zone.js | ^0.16.0 | 変更検知(まだ zone ベース) |

利用者のアプリに `ng add @spartacus/schematics` で入る依存は `spartacus/core-libs/schematics/src/dependencies.json:10-23` に定義されている(`@angular/core ^21.2.23`, `@ngrx/store ^21.0.1`, `rxjs ^7.8.0` 等)。

### 1.2 Angular の基本概念 → Spartacus での実体

| Angular の概念 | 一言で | Spartacus での実体(ファイル) |
|---|---|---|
| **Component** | テンプレート(HTML)+クラス(TS)の UI 部品。`@Component` デコレータで定義 | 各 CMS コンポーネント。例 `core-libs/storefront/cms-components/content/paragraph/paragraph.component.ts:20-26` |
| **Standalone Component** | NgModule 無しで `imports: [...]` に依存を直接書く形式(Angular 19+ で既定) | storefront の 99 コンポーネント中 `standalone: false` は 0。`ParagraphComponent` も `imports: [NgIf, AsyncPipe, ...]` |
| **NgModule** | コンポーネント・プロバイダをまとめる単位。`forRoot()` は「アプリ全体に 1 回だけ」の慣用句 | `BaseStorefrontModule`(`core-libs/storefront/base-storefront.module.ts:26-49`)、`BaseCoreModule`(`core-libs/core/src/base-core.module.ts:26-46`)、各機能の `XxxModule` |
| **Directive** | 既存要素に振る舞いを足す | `[cxComponentWrapper]`(動的生成)、`[cxOutlet]`(差し替えポイント) |
| **Pipe** | テンプレート内の値変換 `{{ v \| pipe }}` | `async`(Observable を購読)、`cxTranslate`(`core-libs/core/src/i18n/translate.pipe.ts:25-29`)、`cxUrl`(`url.pipe.ts:11-18`) |
| **DI / Injector / InjectionToken** | 依存をコンストラクタや `inject()` で受け取る。`multi: true` で複数プロバイダを配列として集約 | `provideConfig` は `ConfigChunk` トークンへの `multi: true` プロバイダ(`config-providers.ts:18-27`)。`CmsComponentData` は子インジェクタで提供(3.8) |
| **Observable / RxJS** | 値が時間とともに流れるストリーム。テンプレートでは `\| async` で購読 | `CmsComponentData.data$`、Facade の戻り値はすべて Observable |
| **ChangeDetectionStrategy.OnPush** | 入力や Observable の変化時だけ再描画 | storefront 99 コンポーネント中 67 が OnPush(例 `paragraph.component.ts:23`) |
| **NgRx Store / Action / Effect / Reducer / Selector** | 単一ストア。Action を dispatch → Effect が HTTP → Success Action → Reducer が状態更新 → Selector で読む | `cms-store.module.ts:33-45`(`StoreModule.forFeature('cms')`)、`page.effect.ts`、`components.reducer.ts`、`components.selectors.ts` |
| **Facade** (Spartacus の慣習) | コンポーネントは Store を直接触らず Service 経由 | `CmsService`(`cms.service.ts:33-46`)、`ProductService`、`ProductSearchByCodeService` |
| **Router / Route / Guard** | URL → コンポーネント。`canActivate` ガードで遷移前処理 | `'**'` ルート + `CmsPageGuard`(3.1)。`@ngrx/router-store` でルーター状態もストアへ(`routing.module.ts:73-108`) |
| **Lazy loading `() => import()`** | 必要になった時にチャンクをダウンロード | `featureModules[...].module: () => import(...)`(5.3 (4)) |
| **APP_INITIALIZER** | 起動時に 1 回走る初期化フック | `'**'` ルート追加(`cms-route.module.ts:10-20`)、設定ルート適用、アウトレット登録 |
| **SSR / TransferState** | サーバで HTML を描画し、取得済みデータを HTML に埋めてブラウザへ渡す | `core-libs/setup/ssr/`、`transfer-state.reducer.ts:16`(`makeStateKey('cx-state')`) |
| **Angular CLI / schematics** | `ng add` などのコード生成 | `core-libs/schematics/src/add-spartacus/`(1.3) |

### 1.3 アプリの骨格(利用者が持つコード)

`ng add @spartacus/schematics` が生成する構造は、参照アプリ `spartacus/projects/storefrontapp/` と同じ形である。

**起動**: standalone ブートストラップ + 既存 NgModule ツリーの橋渡し
`spartacus/projects/storefrontapp/src/main.ts:17`
```ts
bootstrapApplication(AppComponent, appConfig)
```
`spartacus/projects/storefrontapp/src/app/app.config.ts:26-35`
```ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(withFetch(), withInterceptorsFromDi()),
    provideClientHydration(withEventReplay(), withNoHttpTransferCache()),
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideBrowserGlobalErrorListeners(),
    importProvidersFrom(AppModule),
  ],
};
```
`withNoHttpTransferCache()` は、Angular 標準の HTTP 転送キャッシュを切り、代わりに NgRx 経由で状態を転送するため(1.5)。

**ルートモジュール** `spartacus/projects/storefrontapp/src/app/app.module.ts:15-25`
```ts
@NgModule({
  imports: [
    BrowserModule,
    StoreModule.forRoot({}),      // NgRx ルートストア(空。各機能が forFeature で追加)
    AppRoutingModule,             // RouterModule.forRoot([]) のラッパ(core-libs/storefront/router/app-routing.module.ts:13-19)
    EffectsModule.forRoot([]),
    SpartacusModule,
  ],
})
export class AppModule {}
```
**ルートコンポーネント** `app.component.ts:14-19` — テンプレートは `<cx-storefront />` だけ。以降の DOM はすべて Spartacus が CMS データから生成する。

**Spartacus 組み込みの 3 モジュール**(schematics が `app/spartacus/` に生成: `core-libs/schematics/src/shared/utils/workspace-utils.ts:170-193`)

| ファイル | 役割 | 参照アプリ |
|---|---|---|
| `spartacus.module.ts` | `BaseStorefrontModule` + 下 2 つをまとめる | `spartacus.module.ts:12-20` |
| `spartacus-features.module.ts` | 使う機能モジュールを `imports` に列挙(`CmsParagraphModule`, `BannerModule`, `ProductCarouselModule`, 遅延ロード用の `*-feature.module.ts` …)。**カスタム CMS コンポーネントのモジュールを足す場所** | `spartacus-features.module.ts:7-60` |
| `spartacus-configuration.module.ts` | `provideConfig(...)` の列挙(OCC の `baseUrl`、`context`(baseSite/言語/通貨)、`layoutConfigFactory`、i18n)。**`cmsComponents` の上書きや `layoutSlots` 追加を書く場所** | `spartacus-configuration.module.ts:44-67` |

`BaseStorefrontModule`(`core-libs/storefront/base-storefront.module.ts:26-49`)が `BaseCoreModule.forRoot()`, `PageLayoutModule`, `PageSlotModule`, `PageComponentModule.forRoot()`, `OutletModule`, `RoutingModule.forRoot()` などを束ね、`BaseCoreModule`(`core-libs/core/src/base-core.module.ts:26-46`)が `StateModule`, `ConfigModule`, `CmsModule`, `BaseOccModule`, `I18nModule`, `SiteContextModule`, `LazyLoadingModule` などを束ねる。

ビルド設定は Nx ワークスペースのため `angular.json` ではなく `spartacus/projects/storefrontapp/project.json`(esbuild `application` ビルダー、`ssr.entry: server.ts`、`noSsr` 構成あり)。

### 1.4 設定の仕組み(`provideConfig` が効く理由)

Spartacus の設定はすべて Angular DI で集約される。`spartacus/core-libs/core/src/config/config-providers.ts:18-27, 55-61`
```ts
export function provideConfig(config: Config = {}, defaultConfig = false): ValueProvider {
  return {
    provide: defaultConfig ? DefaultConfigChunk : ConfigChunk,
    useValue: config,
    multi: true,
  };
}
export function provideDefaultConfig(config: Config = {}): ValueProvider {
  return { provide: DefaultConfigChunk, useValue: config, multi: true };
}
```
`spartacus/core-libs/core/src/config/config-tokens.ts:10-62`
```ts
export function configFactory() {
  return deepMerge({}, inject(DefaultConfig), inject(RootConfig));
}
@Injectable({ providedIn: 'root', useFactory: configFactory })
export abstract class Config {}
export function defaultConfigFactory() {
  return deepMerge({}, ...(inject(DefaultConfigChunk, { optional: true }) ?? []));
}
export function rootConfigFactory() {
  return deepMerge({}, ...(inject(ConfigChunk, { optional: true }) ?? []));
}
```
- ライブラリは `provideDefaultConfig`(既定値)、アプリは `provideConfig`(上書き)を使う。
- `deepMerge`(`utils/deep-merge.ts:31-48`)はオブジェクトを再帰的に合成し、後勝ち。配列は丸ごと置換。
- したがってアプリが `provideConfig({ cmsComponents: { CMSParagraphComponent: { component: MyParagraph } } })` と書けば、`paragraph.module.ts:22-31` の既定マッピングのその 1 キーだけが置き換わる。
- 遅延ロードモジュール内の設定は `ConfigurationService.emitUnifiedConfig`(`services/configuration.service.ts:92-105`)で `default → ambientDefault → ambient → root` の順に合成され、常にアプリ(root)が最後に勝つ。
- `CmsConfig`, `LayoutConfig`, `RoutingConfig`, `StateConfig` などは `@Injectable({ providedIn: 'root', useExisting: Config })` の抽象クラスで、同じ 1 つの合成済み設定を型付きで覗く窓にすぎない(例 `routing-config.ts:22-27`)。

### 1.5 状態管理(NgRx)と「取得済みなら取らない」の実装

- ルートストアはアプリ側 `StoreModule.forRoot({})`(1.3)。各機能が `StoreModule.forFeature(CMS_FEATURE, ...)` で自分のスライスを追加(`cms-store.module.ts:33-45`)。
- ローダー状態の共通形(`core-libs/core/src/state/utils/loader/loader-state.ts:7-12`):
```ts
export interface LoaderState<T> {
  loading?: boolean;
  error?: boolean;
  success?: boolean;
  value?: T;
}
```
- `entityLoaderReducer`(`entity-loader.reducer.ts:13-25`)が「ID ごとに loading/success/error を持つ」高階リデューサ。CMS の `LoadCmsComponent` は `EntityLoadAction` を継承(`components.action.ts:19, 28`)。
- Facade はこのフラグを見て、未試行のときだけ dispatch する(`cms.service.ts:112-133`、4.2 (b))。これが Angular/NgRx レベルでの API 削減の実装。
- 言語変更・ログイン・ログアウト時は CMS スライスを丸ごとクリアして再取得(`cms/store/reducers/index.ts:75-90` の `clearCmsState`、`page.effect.ts:34-52`)。

**SSR 時の状態転送**: サーバ側のメタリデューサが毎アクション後に設定済みスライスを `TransferState` のキー `'cx-state'` に書き(`transfer-state.reducer.ts:16, 51-61`)、ブラウザ側は NgRx `INIT` 時に読み戻して初期状態へ `deepMerge` する(同 `:74-95`、未ログイン時のみ)。転送対象は `cms`, `product`, `siteContext`, `siteTheme` の 4 スライス(各 `*-store.module.ts` の `ssrTransfer.keys`)。デモは CSR なのでこの経路は使われていない。

### 1.6 ルーティング

- `AppRoutingModule` は `RouterModule.forRoot([], { initialNavigation: 'enabledBlocking' })`(`core-libs/storefront/router/app-routing.module.ts:13-19`)。ルート配列は空。
- 機能ライブラリのルートは `data.cxRoute` 名だけを持ち、実パスは `RoutingConfig.routing.routes[name].paths` から `ConfigurableRoutesService` が起動時に埋める(`configurable-routes.service.ts:48-52, 77-97`)。既定は `core-libs/storefront/cms-structure/routing/default-routing-config.ts`(例 `product: { paths: ['product/:productCode/:name', 'product/:productCode'] }`)。
- 最後に `'**'` が追加され、残りはすべて CMS ページ(3.1)。
- ルーター状態は `@ngrx/router-store` + `CustomSerializer`(`router.reducer.ts:109-155`)でストアに入り、`PageContext` と `cmsRequired` を持つ。`CmsService` は `getNextPageContext` を見て、遷移先ページ応答で届く見込みのコンポーネント要求を抑止する(4.2 (c))。
- テンプレートからの URL 生成は `cxUrl` パイプ + `{ cxRoute: 'product', params: { code } }`(`url.pipe.ts:11-18`, `url-command.ts:7-10`)。

### 1.7 アウトレット(マッピングを変えずに差し込む仕組み)

`spartacus/core-libs/storefront/cms-structure/outlet/outlet.model.ts:9-13`
```ts
export enum OutletPosition {
  REPLACE = 'replace',
  BEFORE = 'before',
  AFTER = 'after',
}
```
`[cxOutlet]` ディレクティブは、登録されたテンプレート/コンポーネントを自身の前・置換・後に描画する(`outlet.directive.ts:121-139`)。ページテンプレート名(`page-layout.component.html:4`)、スロット位置、コンポーネントの `flexType`(`page-slot.component.html:1-15`)がそのままアウトレット ID になるため、**バックエンドの typeCode 名は、フロントにとってアウトレット名でもある**。登録は `provideOutlet({ id, position, component })`(`outlet.providers.ts:41-47`、既定 AFTER)または `<ng-template cxOutletRef="..." cxOutletPos="before">`。

### 1.8 i18n

Angular 標準 i18n ではなく i18next。`TranslationService` 抽象 → `I18nextTranslationService`(`i18n.module.ts:36-56`)。翻訳キーは `chunks` 設定で名前空間(チャンク)に割り当てられ、必要時にロードされる(`translation-chunk.service.ts:41-49`, `i18next-translation.service.ts:64-79`)。`CmsComponentMapping.i18nKeys` を設定すると、そのコンポーネントがページに現れたときにガード内でチャンクを先読みする(`cms-i18n.service.ts:21-28`, `cms-page-guard.service.ts:83`)。翻訳 JSON は `core-libs/assets/src/translations/<lang>/*.json`。

### 1.9 コンポーネントの書き方(標準ライブラリの実例)

`spartacus/core-libs/storefront/cms-components/content/paragraph/paragraph.component.ts:20-26, 44-47`
```ts
@Component({
  selector: 'cx-paragraph',
  templateUrl: './paragraph.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NgIf, AsyncPipe, SupplementHashAnchorsPipe],
})
export class ParagraphComponent {
  ...
  constructor(
    public component: CmsComponentData<CmsParagraphComponent>,
    protected router: Router
  ) {}
```
`paragraph.component.html:1-4`
```html
<div
  *ngIf="component.data$ | async as data"
  [innerHTML]="bypassSecurityTrustHtml(data.content | cxSupplementHashAnchors)"
></div>
```
特徴: standalone、OnPush、コンストラクタ DI と `inject()` の併用(`banner.component.ts:32-63`, `product-carousel.component.ts:41-46`)、`*ngIf="x$ | async as data"` でストリームを購読。Signal の使用は storefront 内で 1 ファイルのみ。カスタムコンポーネントもこの形に合わせれば良い(5.3)。

---

## 2. Spartacus のパッケージ構成

| パッケージ(npm 名) | リポジトリ内の場所 | 役割 |
|---|---|---|
| `@spartacus/core` | `spartacus/core-libs/core/` | 非 UI。モデル、NgRx ストア、OCC アダプタ(HTTP)、Facade サービス、設定の仕組み、ルーティング、i18n |
| `@spartacus/storefront` | `spartacus/core-libs/storefront/` | UI。CMS エンジン(ページレイアウト、スロット、コンポーネント動的生成)、レイアウト設定、標準 CMS コンポーネント群(バナー、段落、カルーセル等)、アウトレット |
| `@spartacus/styles` | `spartacus/core-libs/styles/` | SCSS |
| `@spartacus/setup` | `spartacus/core-libs/setup/` | SSR 用ユーティリティ |
| 機能ライブラリ(`@spartacus/cart`, `@spartacus/user`, `@spartacus/checkout`, …) | `spartacus/feature-libs/*` | 任意機能。`root` エントリ(常時ロード、軽量)と本体(遅延ロード)に分かれる |
| 連携ライブラリ | `spartacus/integration-libs/*` | CDC, CDS, OPF などバックエンドアドオンが必要なもの |
| 参照アプリ | `spartacus/projects/storefrontapp/` | SAP 自身が使う Angular アプリ。利用者のアプリの雛形として読める |

出典: `spartacus/.claude/CLAUDE.md`(リポジトリ同梱の構成説明)および各ディレクトリ。

依存方向は「アプリ → 機能ライブラリ → storefront → core」。バックエンド担当者が意識すべきなのは、**`cmsComponents` マッピングの型は core、動的生成とレイアウトは storefront** にあることと、**機能ライブラリは typeCode 単位で遅延ロードされる**ことの 2 点。

---

## 3. 全体像: URL からコンポーネント描画まで

```
ブラウザ URL  /electronics-spa/en/USD/product/300938/...
   │
   ▼ Angular Router
[1] ワイルドカード route '**' (canActivate: CmsPageGuard, component: PageLayoutComponent)
   │
   ▼ NgRx Router State (CustomSerializer)
[2] PageContext を導出  { type: 'ProductPage', id: '300938' } / { type:'ContentPage', id:'__HOMEPAGE__' }
   │
   ▼ CmsPageGuard → CmsService.getPage() → hasPage()
[3] ストアに無ければ LoadCmsPageData を dispatch
   │
   ▼ PageEffects → CmsPageConnector → OccCmsPageAdapter
[4] GET users/{userId}/cms/pages?pageType=ProductPage&code=300938   (1 本)
   │
   ▼ OccCmsPageNormalizer
[5] レスポンス → { page: {template, slots{position → components[{uid,typeCode,flexType}]}}, components:[全データ] }
   │        └─ CmsGetComponentFromPage で全コンポーネントデータをストアへ(追加 API なし)
   ▼ PageLayoutComponent
[6] page.template ('ProductDetailsPageTemplate') → LayoutConfig.layoutSlots[template].slots で描画順を決定
   │
   ▼ <cx-page-slot position="Summary"> ×N
[7] slot.components を flexType ごとに <cxOutlet> → [cxComponentWrapper]
   │
   ▼ ComponentWrapperDirective
[8] CmsComponentsService.getMapping(flexType) → cmsComponents[flexType].component
   │   (featureModules に属す typeCode なら、ここで遅延 import())
   ▼ ComponentHandler (Default / Lazy / WebComponent)
[9] ViewContainerRef.createComponent(component, injector=CmsInjectorService.getInjector(flexType, uid))
   │
   ▼ 生成された Angular コンポーネント
[10] inject(CmsComponentData).data$ → CmsService.getComponentData(uid)  → ストアにあれば即値、無ければ cms/components をバッチ取得
```

### 3.1 [1] すべての URL を CMS ページとして受ける

`spartacus/core-libs/storefront/cms-structure/routing/cms-route/add-cms-route.ts:12-22`
```ts
const cmsRoute: Route = {
  path: '**',
  canActivate: [CmsPageGuard],
  component: PageLayoutComponent,
};
...
    const router = injector.get(Router);
    router.config.push(cmsRoute);
```
`CmsRouteModule` が `APP_INITIALIZER` でこれを実行する(`cms-route.module.ts:12-17`)。他のルートに一致しない URL はすべて `PageLayoutComponent` で描画される。リポジトリ同梱の開発ガイドも「CMS コンポーネントを Angular のルートに書いてはいけない」と明記している(`spartacus/core-libs/skills/skills/spartacus-developer/references/cms-component-wiring.md`)。

### 3.2 [2] URL → PageContext

`spartacus/core-libs/core/src/routing/store/reducers/router.reducer.ts:186-214`
```ts
      if (params['productCode']) {
        context = { id: params['productCode'], type: PageType.PRODUCT_PAGE };
      } else if (params['categoryCode']) {
        context = { id: params['categoryCode'], type: PageType.CATEGORY_PAGE };
      ...
      } else if (state.data.pageLabel !== undefined) {
        context = { id: state.data.pageLabel, type: PageType.CONTENT_PAGE };
...
    if (!context) {
      if (state.url.length > 0) {
        const pageLabel = '/' + state.url.map((urlSegment) => urlSegment.path).join('/');
        context = { id: pageLabel, type: PageType.CONTENT_PAGE };
      } else {
        context = { id: HOME_PAGE_CONTEXT, type: PageType.CONTENT_PAGE };
```
ルートパラメータから Product/Category、無ければ URL パスをそのままコンテンツページのラベルに、空 URL ならホーム(`'__HOMEPAGE__'`, `page-context.model.ts:15`)。

### 3.3 [3][4] ページ取得は「無ければ取る」

`spartacus/core-libs/core/src/cms/facade/cms.service.ts:247-257`
```ts
  hasPage(pageContext: PageContext, forceReload = false): Observable<boolean> {
    return this.store.pipe(
      select(CmsSelectors.getPageStateIndexLoaderState(pageContext)),
      tap((entity: LoaderState<string>) => {
        const attemptedLoad = entity.loading || entity.success || entity.error;
        const shouldReload = forceReload && !entity.loading;
        if (!attemptedLoad || shouldReload) {
          this.store.dispatch(new CmsActions.LoadCmsPageData(pageContext));
```
NgRx の Effect が OCC を呼ぶ(`spartacus/core-libs/core/src/cms/store/effects/page.effect.ts:58-79`):
```ts
      ofType(CmsActions.LOAD_CMS_PAGE_DATA),
      map((action: CmsActions.LoadCmsPageData) => action.payload),
      groupBy((pageContext) => serializePageContext(pageContext)),
      mergeMap((group) =>
        group.pipe(
          switchMap((pageContext) =>
            this.cmsPageConnector.get(pageContext).pipe(
              mergeMap((cmsStructure: CmsStructureModel) => {
                const actions: Action[] = [
                  new CmsActions.CmsGetComponentFromPage(
                    (cmsStructure.components ?? []).map((component) => ({ component, pageContext }))
                  ),
                  new CmsActions.LoadCmsPageDataSuccess(pageContext, cmsStructure.page ?? {}),
```
エンドポイント定義(`spartacus/core-libs/core/src/cms/config/default-cms-config.ts:9-24`):
```ts
      endpoints: {
        component: 'users/${userId}/cms/components/${id}',
        components: 'users/${userId}/cms/components',
        pages: 'users/${userId}/cms/pages',
        page: 'users/${userId}/cms/pages/${id}',
      },
  ...
  componentsLoading: { pageSize: 50 },
```
クエリの組み立て(`spartacus/core-libs/core/src/occ/adapters/cms/occ-cms-page.adapter.ts:86-101`): ホームは引数なし、コンテンツページは `pageType=ContentPage&pageLabelOrId=...`、それ以外は `pageType=ProductPage&code=...`。デモで観測した URL と一致する(付録 A)。

### 3.4 [5] ページ応答にコンポーネントデータが同梱されている

`spartacus/core-libs/core/src/occ/adapters/cms/converters/occ-cms-page-normalizer.ts:26-35`
```ts
  convert(source: Occ.CMSPage, target: CmsStructureModel = {}): CmsStructureModel {
    this.normalizePageData(source, target);
    this.normalizePageSlotData(source, target);
    this.normalizePageComponentData(source, target);
    this.normalizeComponentData(source, target);
    return target;
  }
```
`normalizeComponentData`(同 `:160-190`)は `contentSlots.contentSlot[].components.component[]` の各オブジェクトをそのまま `target.components` に積む。これが 3.3 の `CmsGetComponentFromPage` でストアに入るため、個別のコンポーネント取得 API は不要になる。

**flexType の決定(マッピングキーのルール)** `occ-cms-page-normalizer.ts:151-158`
```ts
  protected getFlexTypeFromComponent(component: Occ.Component | any): string {
    if (component.typeCode === CMS_FLEX_COMPONENT_TYPE) {
      return component.flexType;
    } else if (component.typeCode === JSP_INCLUDE_CMS_COMPONENT_TYPE) {
      return component.uid;
    }
    return component.typeCode;
  }
```

| バックエンドの typeCode | フロントが `cmsComponents` のキーに使う値 |
|---|---|
| `CMSFlexComponent` | 属性 `flexType` |
| `JspIncludeComponent` | `uid` |
| それ以外(カスタム ItemType を含む) | `typeCode` そのもの |

### 3.5 [6] テンプレート名 → スロットの描画順

`spartacus/core-libs/storefront/cms-structure/page/page-layout/page-layout.service.ts:111-122`
```ts
    const config = this.getSlotConfig(page.template ?? '', 'slots', section, breakpoint);
    if (config && config.slots) {
      const pageSlots = page.slots ? Object.keys(page.slots) : [];
      return config.slots.filter((slot) => pageSlots.includes(slot));
    } else if (!section) {
      this.logMissingLayoutConfig(page);
      return page.slots ? Object.keys(page.slots) : [];
```
`LayoutConfig.layoutSlots[テンプレート名].slots` が描画順を決め、**設定に無いスロットは描画されない**(設定自体が無いテンプレートは全スロットを描画)。既定値は `spartacus/core-libs/storefront/recipes/config/layout-config.ts:32-66`(例: `LandingPage2Template: { slots: ['Section1','Section2A','Section2B','Section2C','Section3','Section4','Section5'] }`)。現在は `layoutConfigFactory()`(同 `:190-198`)経由で提供される。

### 3.6 [7] スロット → コンポーネント

`spartacus/core-libs/storefront/cms-structure/page/slot/page-slot.component.html:6-14`
```html
  <ng-container *ngFor="let component of components">
    <ng-template
      *ngIf="component.flexType"
      [cxOutlet]="component.flexType"
      [cxOutletContext]="{ component: component }"
      [cxOutletDefer]="getComponentDeferOptions(component.flexType)"
      (loaded)="isLoaded($event)"
    >
      <ng-container [cxComponentWrapper]="component" />
```
各コンポーネントは `flexType` 名のアウトレットを通る(= 利用者がアウトレットで差し替え可能)。`cxOutletDefer` によりビューポート外のコンポーネントは描画が遅延される。

### 3.7 [8][9] マッピング解決と Angular コンポーネント生成

`spartacus/core-libs/storefront/cms-structure/page/component/component-wrapper.directive.ts:81-101`
```ts
  private launchComponent() {
    const componentMapping = this.cmsComponentsService.getMapping(this.cxComponentWrapper.flexType ?? '');
    ...
    this.launcherResource = this.componentHandler
      .getLauncher(
        componentMapping,
        this.vcr,
        this.cmsInjector.getInjector(this.cxComponentWrapper.flexType ?? '', this.cxComponentWrapper.uid ?? '', this.injector),
        this.cmsComponentsService.getModule(this.cxComponentWrapper.flexType ?? '')
      )
```
マッピングが無い場合は描画されず、開発モードでは警告が出る(`spartacus/core-libs/storefront/cms-structure/services/cms-components.service.ts:170-176`):
```
No component implementation found for the CMS component type '<flexType>'.
Make sure you implement a component and register it in the mapper.
```
→ **バックエンドで新 typeCode を追加しただけでは何も表示されない**。フロントのマッピング追加が必須。

生成は Angular 標準 API(`spartacus/core-libs/storefront/cms-structure/page/component/handlers/default-component.handler.ts:56-69`):
```ts
        componentRef = viewContainerRef.createComponent(factory, undefined, injector, undefined, module);
```

### 3.8 [10] コンポーネントがデータを受け取る方法

`spartacus/core-libs/storefront/cms-structure/page/component/services/cms-injector.service.ts:28-49`
```ts
  public getInjector(type: string, uid: string, parentInjector?: Injector): Injector {
    const configProviders = this.cmsComponentsService.getMapping(type)?.providers ?? [];
    return Injector.create({
      providers: [
        {
          provide: CmsComponentData,
          useFactory: (dataProvider: ComponentDataProvider) => ({
            uid,
            data$: dataProvider.get(uid, type),
          }),
          deps: [ComponentDataProvider],
        },
        provideLcpPresenceForCmsComponent(),
        ...configProviders,
      ],
      parent: parentInjector ?? this.injector,
```
`spartacus/core-libs/storefront/cms-structure/page/model/cms-component-data.ts:10-13`
```ts
export abstract class CmsComponentData<T extends CmsComponent> {
  uid: string;
  data$: Observable<T>;
}
```
`data$` の実体は `CmsService.getComponentData(uid)`(`component-data.provider.ts:39-53`)。マッピングに静的 `data` があればそれが先に流れ、バックエンドの値で上書きされる。

---

## 4. なぜデモサイトの API 呼び出しが少ないのか

### 4.1 実測(Chrome, 2026-10-23, OPTIONS プリフライト除外)

**ホーム初回ロード** `/electronics-spa/en/USD/`

| # | OCC リクエスト | 発生源 |
|---|---|---|
| 1 | `GET basesites?fields=FULL` | サイトコンテキスト初期化(`default-occ-site-context-config.ts:21`) |
| 2 | `GET electronics-spa/users/anonymous/cms/pages?lang=en&curr=USD` | ホームページ構造 + **33 コンポーネントのデータ同梱**(73KB) |
| 3 | `GET electronics-spa/languages` | 言語セレクタ |
| 4 | `GET electronics-spa/currencies` | 通貨セレクタ |
| 5 | `GET .../cms/components?fields=DEFAULT&currentPage=0&pageSize=26&componentIds=...` | ナビゲーション子ノード等、ページ応答に無かった分の一括取得 |
| 6 | `GET .../cms/components?...&pageSize=8&componentIds=...` | 同上(別コンテキスト) |
| 7 | `HEAD .../consenttemplates` ×2 | 匿名同意 |
| 8 | `GET products/search?fields=products(code,name,price(formattedValue),images(DEFAULT),baseProduct)&query=&filters=code:300938,358639,...(17 件)&pageSize=100` | 商品カルーセル 2 つ分を **1 本に集約** |
| 9 | `GET .../users/anonymous/carts/{guid}` | ミニカート(匿名カートが localStorage に存在) |

GET/HEAD は 10 本(9 種類)。`cms/pages` 単体で 19 スロット・33 コンポーネントの全データを返す(curl で確認、付録 B)。

**ホーム → 商品詳細へ SPA 遷移**(リロードなし)

| # | OCC リクエスト |
|---|---|
| 1 | `GET .../cms/pages?pageType=ProductPage&code=300938` |
| 2 | `GET .../cms/components?fields=DEFAULT&productCode=300938&currentPage=0&pageSize=4&componentIds=...` |
| 3 | `GET products/300938?fields=<複数スコープを結合した fields>` |
| 4 | `GET products/300938?fields=classifications` |
| 5 | `GET products/300938/references?...&referenceType=SIMILAR` |
| 6 | `GET products/300938/reviews` |

basesites / languages / currencies / carts / consenttemplates は**再取得されない**。

デモは `<title>Csr</title>` の空シェル HTML(`<app-root>` が空、`cx-state` スクリプトなし)を配信しており、SSR ではない。したがって以下はすべて**クライアント側の設計**による削減である。

### 4.2 削減メカニズム(ソース根拠)

| # | メカニズム | 根拠 |
|---|---|---|
| (a) | **ページ応答にコンポーネントデータを同梱**し、ノーマライザが `components[]` に集約、`CmsGetComponentFromPage` でストアへ | `occ-cms-page-normalizer.ts:160-190`, `page.effect.ts:67-79`, `components.reducer.ts:71-85` |
| (b) | **取得済み・取得中・失敗済みなら再要求しない**(Entity Loader の `loading/success/error` フラグ) | `cms.service.ts:112-133`(`attemptedLoad`)、`cms.service.ts:247-257`(ページ) |
| (c) | **遷移先ページの応答に含まれる見込みのコンポーネントは待つ**(`couldBeLoadedWithPageData`) | `cms.service.ts:121-133` |
| (d) | **同一ティック内の要求をバッファして 1 本の `componentIds=` に集約**、50 件単位で分割 | `components.effect.ts:47-63`(`bufferDebounceTime`)、`cms-component.connector.ts:41-73`、`default-cms-config.ts:22` |
| (e) | **コンテンツページ間でコンポーネントキャッシュを共有**(`serializePageContext(ctx, true)` → `"ContentPage"`) | `cms-utils.ts:21-34`, `cms.service.ts:82-94` |
| (f) | **同一ページの重複ロードを `groupBy`+`switchMap` で抑止**、`RouteLoadStrategy.ONCE` なら再訪問時も再取得しない | `page.effect.ts:58-66`, `cms-page.guard.ts:89-91` |
| (g) | **静的 `cmsStructure` にあるページ/コンポーネントはバックエンドを呼ばない**(`ignoreBackend`, `getComponentsFromConfig`) | `cms-page.connector.ts:30-52`, `cms-component.connector.ts:41-50`, `cms-structure-config.service.ts:38-60` |
| (h) | **商品カルーセルは `products/search?filters=code:a,b,c` で最大 100 件を 1 本に集約**(スコープごとに `bufferDebounceTime`) | `product-carousel.component.ts:69-83`, `product-search-by-code.effect.ts:42-67`, `occ-product-search.adapter.ts:73-99` |
| (i) | **同一商品の複数スコープ要求を `fields` 結合で 1 URL に最適化** | `occ-requests-optimizer.service.ts:34-75`, `occ-product.adapter.ts:35-50`, `default-occ-product-config.ts:53-57`(`details` は `list`,`variants` を include) |
| (j) | **ビューポート外のコンポーネント描画を遅延**(描画されるまでデータ購読も始まらない) | `page-slot.component.html:11`(`cxOutletDefer`) |
| (k) | **機能モジュールの遅延ロードは 1 回限りでキャッシュ**(`shareReplay`) | `cms-features.service.ts:138-147`, `feature-modules.service.ts:42-71` |
| (l) | (デモ未使用)**SSR 時は CMS / Product / SiteContext / SiteTheme ストアを HTML に埋め込み、ブラウザは再取得しない** | `cms-store.module.ts:25-26`, `product-store.module.ts:24-25`, `site-context-store.module.ts:24`, `site-theme-store.module.ts:23`, `transfer-state.reducer.ts:24-34` |

「本来はコンポーネント数だけ API が飛ぶはず」という直感は、Spartacus では (a)(b)(d)(h) によって成り立たない。**1 ページ = `cms/pages` 1 本 + 不足分のバッチ数本** が設計上の期待値である。

---

## 5. バックエンドでカスタム CMS コンポーネントを作るとき、フロントへ渡す仕様

### 5.1 鍵になる 3 つの値

| 値 | バックエンドでの定義 | フロントでの使われ方 |
|---|---|---|
| `typeCode` | `*-items.xml` の ItemType 名(例: `MyPromoBannerComponent extends SimpleCMSComponent`) | `cmsComponents` のキー(3.4 の表)。**この文字列の一致がすべて** |
| `flexType` | `CMSFlexComponent` を使う場合のみ、その属性値 | `CMSFlexComponent` のときはこちらがキー |
| `uid` | コンポーネントインスタンスの uid | `CmsComponentData.uid` とデータ取得キー。`JspIncludeComponent` のときのみマッピングキー |

新しい ItemType を作る(= typeCode が新しい)のであれば、フロントに新しいマッピングが必要。**既存 typeCode のインスタンスを増やすだけなら、フロント作業は不要**(例: `SimpleResponsiveBannerComponent` をもう 1 つ置く)。

### 5.2 OCC が返す JSON の形(デモ実物)

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
**注意点**: OCC の CMS コンポーネント DTO は属性を文字列化する(`"container": "false"`、`productCodes` はスペース区切り)。真偽値・複数値・参照(商品コード、メディア)をどう表現するかを依頼書に明記すること。メディアは `media: { desktop:{url,altText,mime,code}, tablet, mobile, widescreen }` 形式(`cms.model.ts:99-117`、5.2 冒頭のバナー JSON 参照)。

### 5.3 フロント側の実装雛形(Angular)

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

### 5.4 マッピングで指定できるオプション

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

### 5.5 新しいスロットやページテンプレートを作る場合

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

### 5.6 コンポーネントが追加データを必要とする場合

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
`ProductSearchByCodeService.get` はストアに無いときだけロードを dispatch し(`product-search-by-code.service.ts:46-53`)、Effect が同時要求をまとめて `products/search?filters=code:...` 1 本にする(4.2 (h))。**バックエンドが CMS 属性に商品データをコピーして持つ必要はない**。逆に、OCC に無い情報が必要なら「商品 API 側の拡張」か「CMS 属性として持たせる」かを依頼書で決める。

### 5.7 既存コンポーネントの差し替え・部分差し替え

- **同じ typeCode に別コンポーネントを `provideConfig` で上書き**: アプリ側の設定が標準ライブラリの `provideDefaultConfig` より優先される(`cms-components.service.ts:126-133` の `deepMerge(featureMapping, staticConfig)` でアプリ設定が後勝ち)。バックエンド変更は不要。
- **アウトレット**で既存レイアウトの前後に差し込む(`provideOutlet({ id: 'AddToCart', position: OutletPosition.AFTER, component })`)。スロット内の各コンポーネントは `flexType` 名のアウトレットに包まれている(3.6)。
- **静的 `cmsStructure`**: バックエンド変更前にフロントだけで動作確認する手段(`spartacus/core-libs/storefront/cms-structure/utils/cms-structure.util.ts:31-66`, `cms-structure.config.ts:79-85`)。

使い分けはリポジトリ同梱の `spartacus/core-libs/skills/skills/spartacus-developer/references/placement-mechanisms.md` にも整理されている。

### 5.8 「FE への依頼書」に書くべき項目

1. **typeCode**(ItemType 名)。`CMSFlexComponent` 流用なら `flexType` の値
2. **OCC が返す属性の一覧**: 名前 / 型(すべて文字列化される点に注意) / 必須か / 例。真偽値・列挙・複数値・参照・メディア・ローカライズ属性の表現方法
3. **実際の `cms/pages` レスポンス JSON のサンプル**(開発環境の OCC から取得して添付)
4. **配置先**: ページテンプレート名、スロット位置名、既存か新規か(新規なら `layoutSlots` 追加が必要)
5. **追加で必要なデータ**: 商品・カテゴリ・在庫など、CMS 属性に持たせず参照だけ渡すもの
6. **振る舞い要件**: ログイン必須(`guards`)、子ルート、SSR 可否、遅延描画の可否、翻訳キー
7. **既存コンポーネントの流用可否**: 既存 typeCode(例: `SimpleResponsiveBannerComponent`, `CMSParagraphComponent`, `ProductCarouselComponent`)で済むならフロント作業はゼロ
8. **遅延ロードの希望**(機能単位でチャンク分割するか)

---

## 6. バックエンド側のチェックリスト

- [ ] `*-items.xml` で `SimpleCMSComponent`(または適切な親)を継承した ItemType を定義し、`typeCode` を決める
- [ ] OCC で属性が公開されるようにする(`cmsocc` の DTO / Converter / `fields=DEFAULT` のフィールド定義)。開発 OCC で `GET /occ/v2/{baseSite}/users/anonymous/cms/pages?pageType=ContentPage&pageLabelOrId=homepage` を叩いて JSON に出ることを確認
- [ ] ページテンプレート / コンテンツスロットにコンポーネントを配置し、カタログ同期(Staged → Online)
- [ ] フロントが参照する属性名・値の表現を固定し、依頼書(5.8)を書く
- [ ] 参照系データ(商品など)は OCC 商品 API で取得できる前提にする。CMS 属性へコピーしない
- [ ] 既存の `cms/pages` レスポンスサイズに注意する(ホームで 73KB)。巨大な HTML や大量リストを 1 コンポーネントに詰めない

---

## 7. 業務データを扱うカスタムコンポーネント: Facade / Connector / Adapter の作り方

5 章は「CMS 属性だけで完結するコンポーネント」だった。商品・在庫・会員情報・外部システムのデータなど**バックオフィスで編集しない動的データ**を表示するコンポーネントでは、Spartacus の階層に沿ってフロント側に 5〜6 ファイルを追加する。図は `docs/diagrams/spartacus-architecture.drawio` の「03 カスタムコンポーネントのデータ経路」。

### 7.1 原則(リポジトリ同梱ガイド)

`spartacus/core-libs/skills/skills/spartacus-developer/references/backend-communication.md:5-16`
> NEVER inject `HttpClient` in components or services. All backend communication goes through a layered pipeline: `Component → Facade → state layer → Connector → Adapter → Converter`. … Only **Adapters** use `HttpClient`.
> Facade — Public API consumed by components. / Connector — Thin delegation layer injecting the abstract Adapter. / Adapter — Abstract class in `connectors/`, OCC implementation in `occ/adapters/`. This is the ONLY layer that uses `HttpClient`. / Converter — Normalizers (backend→UI) and Serializers (UI→backend) are registered as `multi: true` providers on typed `InjectionToken`s.

同 `:20`: 「NEVER hardcode endpoint URLs. Configure them via `provideConfig`」。

### 7.2 各層の実物(`feature-libs/user/account` を例に)

標準ライブラリは 1 機能を `root` / `core` / `occ` / `components` の 4 エントリポイントに分ける(`spartacus/tsconfig.json:49-64` のパスマッピング、各ディレクトリの `ng-package.json`)。

| 層 | 置き場所 | 役割 | 実物 |
|---|---|---|---|
| Facade(抽象) | `root/facade/` | コンポーネントが使う公開 API。DI トークン兼契約。遅延ロード前はプロキシ | `feature-libs/user/account/root/facade/user-account.facade.ts:13-25` |
| Facade 実装 | `core/facade/` | 状態層(Query/Command または NgRx)。Connector を呼ぶ | `core/facade/user-account.service.ts:24-56` |
| Connector | `core/connectors/` | 機能向けの薄い委譲。Adapter 抽象を注入 | `core/connectors/user-account.connector.ts:16-29` |
| Adapter(抽象) | `core/connectors/` | バックエンド契約。OCC 以外にも差し替え可能 | `core/connectors/user-account.adapter.ts:14-20` |
| OCC Adapter | `occ/adapters/` | **唯一 `HttpClient` を使う層**。URL 組み立てと Normalizer 適用 | `occ/adapters/occ-user-account.adapter.ts:34-52` |
| エンドポイント設定 | `occ/adapters/config/` | `backend.occ.endpoints` に URL テンプレート | `occ/adapters/config/default-occ-user-account-endpoint.config.ts:9-18` |
| Converter / Normalizer | `occ/converters/` + `core/connectors/converters.ts` | OCC DTO → FE モデル | `feature-libs/organization/order-approval/occ/converters/occ-order-approval-normalizer.ts:12-29` |
| 配線 | `core/*-core.module.ts`, `occ/*-occ.module.ts`, `root/*-root.module.ts` | providers の束ね | `core/user-account-core.module.ts:11-14`, `occ/user-account-occ.module.ts:13-19` |

**Facade(抽象)** `spartacus/feature-libs/user/account/root/facade/user-account.facade.ts:13-25`
```ts
@Injectable({
  providedIn: 'root',
  useFactory: () =>
    facadeFactory({
      facade: UserAccountFacade,
      feature: USER_ACCOUNT_CORE_FEATURE,
      methods: ['get', 'getById'],
    }),
})
export abstract class UserAccountFacade {
  abstract get(): Observable<User | undefined>;
  abstract getById(userId: string): Observable<User | undefined>;
}
```
`facadeFactory` は「最初のメソッド呼び出し時に機能チャンクを遅延ロードし、その中の実装へ転送するプロキシ」を作る(`core-libs/core/src/lazy-loading/facade-factory/facade-factory.ts:11-24`, `facade-factory.service.ts:110-131`)。NgRx を使う機能は `async: true` を付ける(`feature-libs/storefinder/root/facade/store-finder.facade.ts:21-43`)。

**Facade 実装(Query パターン)** `spartacus/feature-libs/user/account/core/facade/user-account.service.ts:24-56`
```ts
@Injectable()
export class UserAccountService implements UserAccountFacade {
  protected userQuery: Query<User> = this.query.create(
    () =>
      this.userIdService
        .takeUserId(true)
        .pipe(switchMap((userId) => this.userAccountConnector.get(userId))),
    {
      reloadOn: [UserAccountChangedEvent],
      resetOn: [LoginEvent, LogoutEvent],
    }
  );
  ...
  get(): Observable<User | undefined> {
    return this.userQuery.get();
  }
}
```
`QueryService.create`(`core-libs/core/src/util/command-query/query.service.ts:31-60, 77-103`)は `loading / error / data` を保持し、購読中は 1 回しかロードしない。`reloadOn` は data を保ったまま再取得、`resetOn` は初期状態へ戻す。新規機能ではこの Query/Command が推奨で、NgRx は旧来機能に合わせる場合に使う(`backend-communication.md:5-11`)。書き込みは `CommandService`(`command.service.ts:27-53`、既定戦略 Queue)。

**Connector と Adapter 抽象** `spartacus/feature-libs/user/account/core/connectors/user-account.connector.ts:16-29`, `user-account.adapter.ts:14-20`
```ts
@Injectable()
export class UserAccountConnector {
  constructor(protected adapter: UserAccountAdapter) {}
  get(userId: string): Observable<User> {
    return this.adapter.load(userId);
  }
}
export abstract class UserAccountAdapter {
  abstract load(userId: string): Observable<User>;
}
```

**OCC Adapter** `spartacus/feature-libs/user/account/occ/adapters/occ-user-account.adapter.ts:34-52`
```ts
@Injectable()
export class OccUserAccountAdapter implements UserAccountAdapter {
  protected logger = inject(LoggerService);
  constructor(
    protected http: HttpClient,
    protected occEndpoints: OccEndpointsService,
    protected converter: ConverterService
  ) {}
  load(userId: string): Observable<User> {
    const url = this.occEndpoints.buildUrl('user', { urlParams: { userId } });
    return this.http.get<Occ.User>(url).pipe(
      catchError((error) => {
        throw tryNormalizeHttpError(error, this.logger);
      }),
      this.converter.pipeable(USER_ACCOUNT_NORMALIZER)
    );
  }
```

**エンドポイント設定と型拡張** `occ/adapters/config/default-occ-user-account-endpoint.config.ts:9-18`, `occ-user-account-endpoint.model.ts:9-22`
```ts
export const defaultOccUserAccountConfig: OccConfig = {
  backend: { occ: { endpoints: {
    user: 'users/${userId}',
    createVerificationToken: 'users/anonymous/verificationToken',
  } } },
};
declare module '@spartacus/core' {
  interface OccEndpoints extends UserAccountOccEndpoints {}
}
```
`OccEndpointsService.buildUrl`(`core-libs/core/src/occ/services/occ-endpoints.service.ts:86-150`)は `baseUrl + prefix + 現在の baseSite + endpoint` を組み立て、`${userId}` などを `urlParams` で埋め、`queryParams` を結合する。**`baseSiteId` はプレースホルダではなく `getBaseUrl()` がパスとして前置する**(同 `:233-238`)。

**Normalizer** `spartacus/feature-libs/organization/order-approval/occ/converters/occ-order-approval-normalizer.ts:12-29` と登録 `order-approval-occ.module.ts:24-36`
```ts
@Injectable({ providedIn: 'root' })
export class OccOrderApprovalNormalizer implements Converter<Occ.OrderApproval, OrderApproval> {
  convert(source: Occ.OrderApproval, target?: OrderApproval): OrderApproval {
    if (target === undefined) {
      target = { ...(source as any) } as OrderApproval;
    }
    if (source.order) {
      target.order = this.converter.convert(source.order, ORDER_NORMALIZER);
    }
    return target;
  }
}
...
providers: [
  provideDefaultConfig(defaultOccOrderApprovalConfig),
  { provide: OrderApprovalAdapter, useClass: OccOrderApprovalAdapter },
  { provide: ORDER_APPROVAL_NORMALIZER, useExisting: OccOrderApprovalNormalizer, multi: true },
```
`ConverterService.pipeable`(`core-libs/core/src/util/converter.service.ts:77-88, 130-137`)は登録された Normalizer を順に reduce し、未登録なら素通しする。**`multi: true` を忘れると既存の変換チェーンを丸ごと置き換えてしまう**(`normalizers.md:5-7`)。

**配線** `core/facade/facade-providers.ts:15-26`, `core/user-account-core.module.ts:11-14`, `occ/user-account-occ.module.ts:13-19`
```ts
export const facadeProviders: Provider[] = [
  UserAccountService,
  { provide: UserAccountFacade, useExisting: UserAccountService },
];
@NgModule({ providers: [UserAccountConnector, ...facadeProviders] })
export class UserAccountCoreModule {}
@NgModule({ providers: [
  provideDefaultConfig(defaultOccUserAccountConfig),
  { provide: UserAccountAdapter, useClass: OccUserAccountAdapter },
] })
export class UserAccountOccModule {}
```

**コンポーネントから使う** `components/login/login.component.ts:34-54` は `UserAccountFacade` を注入し `this.userAccount.get()` を購読するだけ。

### 7.3 HTTP リクエストに自動で付くもの(バックエンドが前提にできること)

`OccEndpointsService.buildUrl` で作った URL(= OCC の baseUrl 配下)に対してのみ、インターセプタが次を付与する。手組みの URL には付かない。

| 付与されるもの | 根拠 |
|---|---|
| クエリ `lang`, `curr` | `core-libs/core/src/occ/adapters/site-context/site-context.interceptor.ts:54-68` |
| `Authorization: Bearer <token>`(ログイン時。`basesites` は除外) | `core-libs/core/src/auth/user-auth/services/auth-http-header.service.ts:179-207, 220-226` |
| 401 時のトークン更新とリトライ | `auth.interceptor.ts:54-73` |
| `userId` の値は `'current'`(ログイン中)か `'anonymous'` | `core-libs/core/src/occ/utils/occ-user-ids.ts:7-8` |

エラー応答は OCC 標準の `{ "errors": [ { "type", "message", "reason", "subject", "subjectType" } ] }` が期待されている(`core-libs/core/src/util/try-normalize-http-error.ts:36-50` が `error.error.errors` 配列を `HttpErrorModel.details` に写す。DTO 型は `occ.models.ts:104-125` の `Occ.ErrorModel`)。

### 7.4 カスタム機能で追加するファイル一覧(雛形)

```
my-promo/
  root/
    feature-name.ts            export const MY_PROMO_FEATURE = 'myPromo';
    facade/my-promo.facade.ts  abstract class MyPromoFacade (facadeFactory)
    model/my-promo.model.ts    interface MyPromo { id; title; discountRate; ... }
    my-promo-root.module.ts    provideDefaultConfig({ featureModules: { myPromo: { cmsComponents: ['MyPromoBannerComponent'] } } })
  core/
    connectors/my-promo.adapter.ts     abstract class MyPromoAdapter { abstract load(userId, promoId): Observable<MyPromo> }
    connectors/my-promo.connector.ts   @Injectable() class MyPromoConnector
    connectors/converters.ts           export const MY_PROMO_NORMALIZER = new InjectionToken<Converter<Occ.MyPromo, MyPromo>>('MyPromoNormalizer')
    facade/my-promo.service.ts         QueryService で MyPromoFacade を実装
    my-promo-core.module.ts
  occ/
    model/occ-my-promo.models.ts       Occ 側 DTO 型 + declare module '@spartacus/core' { interface OccEndpoints { myPromo?: string } }
    adapters/default-occ-my-promo-config.ts   endpoints: { myPromo: 'users/${userId}/my-promos/${promoId}?fields=DEFAULT' }
    adapters/occ-my-promo.adapter.ts   buildUrl + http.get + tryNormalizeHttpError + converter.pipeable(MY_PROMO_NORMALIZER)
    converters/occ-my-promo-normalizer.ts
    my-promo-occ.module.ts
  components/
    my-promo-banner/my-promo-banner.component.ts   inject(CmsComponentData) で promoId を読み、inject(MyPromoFacade).get(promoId)
    my-promo-components.module.ts      provideDefaultConfig({ cmsComponents: { MyPromoBannerComponent: { component: MyPromoBannerComponent } } })
  my-promo.module.ts                   imports: [Core, Occ, Components]
アプリ側: provideConfig({ featureModules: { myPromo: { module: () => import('./my-promo.module').then(m => m.MyPromoModule) } } })
```

コンポーネント内の典型的な結線(CMS 属性 → 業務データ):
```ts
export class MyPromoBannerComponent {
  protected cms = inject<CmsComponentData<CmsMyPromoBannerComponent>>(CmsComponentData);
  protected promo = inject(MyPromoFacade);
  promo$ = this.cms.data$.pipe(
    map((d) => d.promoId),
    filter(Boolean),
    distinctUntilChanged(),
    switchMap((id) => this.promo.get(id))
  );
}
```
これは `ProductCarouselComponent` が `productCodes` を読んで `ProductSearchByCodeService.get` を呼ぶのと同じ形(5.6)。

---

## 8. バックエンド(Java)側: 何を、どの単位で返すか

> **根拠の範囲について**: SAP Commerce Cloud 本体(Java)は公開リポジトリが無いためクローンできない。本章のうち Java の API 名は SAP Help の公開ドキュメント([DataMapper](https://help.sap.com/doc/9fef7037b3304324b8891e84f19f2bf3/2211/en-US/de/hybris/platform/webservicescommons/mapping/DataMapper.html)、[Data Mapping Mechanism](https://help.sap.com/docs/SAP_COMMERCE/9d346683b0084da2938be8a285c0c27a/e571a0e6f7524d4ab62e29cc2b387aeb.html)、[KBA 2693560 field level configuration](https://userapps.support.sap.com/sap/support/knowledge/en/2693560))に基づく。**フロントが何を期待するか**は 7.3 のとおり Spartacus ソースで裏付けている。デモ OCC の実レスポンス(5.2、付録 B)も根拠に含む。

### 8.1 結論: 「コンポーネント単位」ではなく「リソース単位」

`@RestController`(SAP Commerce の OCC では `@Controller` + `@RequestMapping` + `@ResponseBody`)を**CMS コンポーネントごとに作ってはいけない**。判断は次の順(図「04 バックエンド判断フロー」):

| 問い | YES の場合 | 作るもの |
|---|---|---|
| ① CMS 管理者がバックオフィスで編集する内容か | ItemType の属性にする | **コントローラ不要**。`cms/pages` / `cms/components` が属性を自動で返す |
| ② 既存 OCC API(products, categories, carts, orders, users …)で取れるか | CMS 属性には code / ID だけ持たせ、FE が既存 Facade で取得 | **コントローラ不要**(例: `ProductCarouselComponent.productCodes`) |
| ③ 既存リソースに属性を足せば足りるか | 既存 WsDTO と Populator を拡張し、`fields` レベルに追加 | **DTO 拡張のみ**。FE は Occ モデル拡張 + Normalizer(`normalizers.md:17-26`) |
| ④ 上記で足りない | **新しいリソース**としてエンドポイントを設計 | 新コントローラ + WsDTO。FE は 7.4 の一式 |

「単位」の答え: **URL はドメインのリソース(名詞)で切る**。CMS コンポーネントは「どのリソースを、どう見せるか」の設定(参照 ID と表示オプション)だけを持つ。こうすると同じ API を複数コンポーネント・複数画面で再利用でき、FE 側のキャッシュ(Query / Entity Loader)とバッチ化(`bufferDebounceTime`)が効く。

### 8.2 ① CMS 属性で返す場合(コントローラ不要)

デモの実レスポンス(5.2)から読み取れる OCC CMS の出力規則:

| 観測事実 | 含意 |
|---|---|
| `"container": "false"`, `"external": "false"` | 真偽値も **文字列**。FE モデルは `string` で受け、`=== 'true'` で判定(`banner.component.ts:133-135` は `'true'` と `true` 両対応) |
| `"productCodes": "300938 358639 ..."` | 複数値は **スペース区切りの 1 文字列**。FE で `split(' ')`(`product-carousel.component.ts:74`) |
| `"media": { "desktop": {url, altText, mime, code}, "tablet": …, "mobile": …, "widescreen": … }` | メディアコンテナは breakpoint ごとのオブジェクト(`cms.model.ts:99-117`) |
| `"content": "<div class=...>…</div>"` | リッチテキストは HTML 文字列のまま |
| `uid`, `uuid`, `typeCode`, `modifiedtime`, `name`, `synchronizationBlocked` | 全コンポーネント共通の自動属性 |
| 言語依存属性 | `?lang=en` で解決済みの 1 値が返る(ローカライズは OCC 側で解決) |

バックエンド作業は `*-items.xml` に ItemType と属性を定義してバックオフィスで値を入れるだけ。依頼書には「属性名・型(文字列化後の表現)・例」を書く。**既存 typeCode のインスタンスを増やすだけならフロント作業ゼロ**(5.1)。

### 8.3 ③④ 新しいリソースを返す場合の設計ルール

フロント(7.3)と OCC の慣習から導かれるチェックリスト:

1. **URL**: `/{baseSiteId}/...` 配下。利用者固有なら `/{baseSiteId}/users/{userId}/my-promos/{promoId}`。`userId` には `current` / `anonymous` が来る前提で解決する(`occ-user-ids.ts:7-8`)。Spartacus 側の endpoints 設定は `'users/${userId}/my-promos/${promoId}'` と 1 対 1 になる。
2. **単件と一括の両方**: `GET /my-promos/{id}` と `GET /my-promos?ids=a,b,c`(または `filters=`)。FE は同一ティックの要求をまとめて 1 本にする設計なので(4.2 (d)(h))、一括エンドポイントが無いとコンポーネント数だけ API が飛ぶ。
3. **`fields` パラメータ**: `BASIC` / `DEFAULT` / `FULL` のレベルを `dto-level-mappings` に定義し、`DataMapper.map(data, XxxWsDTO.class, fields)` で返す。Spartacus の endpoints 設定は `?fields=DEFAULT` や `?fields=code,name,price(formattedValue)` を URL テンプレートに持つのが慣習(`default-occ-product-config.ts:14-27`、`default-occ-store-finder-config.ts:12-17`)。
4. **`lang` / `curr`**: 必ずクエリで来る(7.3)。ローカライズ属性と価格はこれで解決して返す。
5. **認証**: `users/{userId}` 配下はログイン時に Bearer トークンが付く。匿名可否はサーバ側で判断。
6. **エラー形式**: `ErrorListWsDTO`(`{ errors: [{ type, message, reason, subject, subjectType }] }`)で返す。FE はこれを `HttpErrorModel.details` に写して表示する(`try-normalize-http-error.ts:44-50`)。
7. **DTO の形**: フラットで、ネストはリソース参照(`product: { code, name }`)程度に抑える。FE の Normalizer は `{ ...source }` から始めて差分だけ変換するのが定石(`occ-order-approval-normalizer.ts:20-26`)なので、JSON のキー名がそのまま FE モデルのプロパティ名になる。キー名は camelCase。
8. **命名**: URL はコンポーネント名(`/myPromoBannerComponentData`)ではなくリソース名(`/my-promos`)。コンポーネントが変わっても API は残る。

### 8.4 Java 側の最小構成(参考・SAP Help の公開情報に基づく一般形)

```java
// OCC 拡張 (yocc テンプレートから生成した *occ 拡張) の web/src 配下
@Controller
@RequestMapping(value = "/{baseSiteId}/users/{userId}/my-promos")
public class MyPromosController extends BaseController {

  @Resource private MyPromoFacade myPromoFacade;   // facades 層: MyPromoData を返す
  @Resource private DataMapper dataMapper;          // webservicescommons の DataMapper

  @GetMapping(value = "/{promoId}")
  @ResponseBody
  public MyPromoWsDTO getPromo(
      @PathVariable String promoId,
      @RequestParam(defaultValue = DEFAULT_FIELD_SET) String fields) {
    MyPromoData data = myPromoFacade.getPromo(promoId);     // Service → DAO
    return dataMapper.map(data, MyPromoWsDTO.class, fields); // fields = BASIC/DEFAULT/FULL or 明示列挙
  }

  @GetMapping
  @ResponseBody
  public MyPromoListWsDTO getPromos(
      @RequestParam List<String> ids,
      @RequestParam(defaultValue = DEFAULT_FIELD_SET) String fields) {
    MyPromoListData data = myPromoFacade.getPromos(ids);     // 一括取得
    return dataMapper.map(data, MyPromoListWsDTO.class, fields);
  }
}
```
- `MyPromoWsDTO` は `*-beans.xml` で定義し、`dto-level-mappings` で `BASIC` / `DEFAULT` / `FULL` に含めるフィールドを宣言する(KBA 2693560)。
- `MyPromoData`(facades の Data オブジェクト)と `WsDTO` の名前を揃えると DataMapper の自動マッピングで済む。
- Spartacus 側の設定は `myPromo: 'users/${userId}/my-promos/${promoId}?fields=DEFAULT'`, `myPromos: 'users/${userId}/my-promos?fields=DEFAULT'` の 2 行。

### 8.5 依頼書に追加する項目(業務データがある場合)

5.8 の 8 項目に加えて:

9. **リソース名と URL**(単件 / 一括)、パス・クエリパラメータ
10. **WsDTO の JSON サンプル**(`fields=DEFAULT` と `FULL` の両方)
11. **`fields` レベルに含まれる属性一覧**
12. **認証要否**(匿名可 / ログイン必須)、`userId` の扱い
13. **エラー応答の `type` / `reason` 一覧**(FE でメッセージ表示に使う)
14. **CMS 属性との対応**: どの CMS 属性(例 `promoId`)がこの API の引数になるか

---

## 付録 A. OCC エンドポイントとデモで観測した URL の対応

| 定義(`default-cms-config.ts:13-16`) | 観測 URL |
|---|---|
| `users/${userId}/cms/pages` | `users/anonymous/cms/pages?lang=en&curr=USD`(ホーム)、`...?pageType=ProductPage&code=300938` |
| `users/${userId}/cms/components` | `users/anonymous/cms/components?fields=DEFAULT&currentPage=0&pageSize=26&componentIds=...` |

`fields` は `OccCmsComponentAdapter.findComponentsByIds` の既定引数 `'DEFAULT'`(`occ-cms-component.adapter.ts:51-68`)。ページ側に `fields` は付かない。

## 付録 B. `cms/pages`(homepage)レスポンスの構造(curl, 2026-10-23)

```
top keys: uid, uuid, title, template(LandingPage2Template), typeCode(ContentPage), name, robotTag, contentSlots, label
slots: 19
  Section1          SimpleResponsiveBannerComponent ×2
  Section2A/2B      SimpleResponsiveBannerComponent ×2 ずつ
  Section2C         MerchandisingCarouselComponent
  Section3          ProductCarouselComponent ×2
  Section4          SimpleResponsiveBannerComponent ×4
  Section5          SimpleResponsiveBannerComponent
  BottomHeaderSlot  CMSFlexComponent(flexType=PageTitleComponent)
  NavigationBar     CategoryNavigationComponent
  MiniCart          MiniCartComponent
  SiteContext       CMSSiteContextComponent ×2, CMSFlexComponent(SiteThemeSwitcherComponent)
  SiteLogo          SimpleBannerComponent
  Footer            FooterNavigationComponent, CMSFlexComponent ×2, CMSParagraphComponent
  SiteLinks         CMSLinkComponent ×4
  SearchBox         SearchBoxComponent
  HomepageNavLink   CMSLinkComponent
  HeaderLinks / TopHeaderSlot / PlaceholderContentSlot  (空)
components inline: 33  (すべて typeCode・uid・各属性を含む完全なデータ)
```

## 付録 C. 参照したリポジトリ内ドキュメント

- `spartacus/core-libs/skills/skills/spartacus-developer/references/cms-component-wiring.md` — マッピング登録・上書き・`CmsComponentData` の使い方・アンチパターン(Angular ルートに置かない)
- `spartacus/core-libs/skills/skills/spartacus-developer/references/placement-mechanisms.md` — CMS 配置 / アウトレット / 静的 `cmsStructure` の使い分け
- `spartacus/core-libs/skills/skills/spartacus-developer/references/lazy-loading.md`, `configuration.md`, `outlets.md`
