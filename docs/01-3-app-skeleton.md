# 1.3 アプリの骨格(利用者が持つコード)

> **図**: 06 Angular アプリの骨格と設定 DI(`diagrams/spartacus-architecture.drawio`)。本節は図の左半分: main.ts → bootstrapApplication → app.config.ts(importProvidersFrom(AppModule))→ SpartacusModule → 3 モジュール

![06 Angular アプリの骨格と設定 DI](diagrams/page6.png)

> 1 章の目次: [1. Angular 入門(バックエンド担当者向け)と Spartacus への対応](01-angular-basics.md)

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

---

[目次](README.md) | ← [1.2 Angular の基本概念 → Spartacus での実体](01-2-concept-map.md) | [1.4 設定の仕組み(`provideConfig` が効く理由)](01-4-config-di.md) →
