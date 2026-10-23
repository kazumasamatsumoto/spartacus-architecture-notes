# 1.6 ルーティング

> **図**: 01 全体フロー URL→描画(`diagrams/spartacus-architecture.drawio`)。本節は図のステップ ①〜③: `**` ルート → CmsPageGuard → PageContext。Angular のルート定義にページを書かない理由

![01 全体フロー URL→描画](diagrams/page1.png)

> **この章が答える問い**: URL がなぜ Angular のルート定義ではなく CMS で決まるのか

> 1 章の目次: [1. Angular 入門(バックエンド担当者向け)と Spartacus への対応](01-angular-basics.md)

- `AppRoutingModule` は `RouterModule.forRoot([], { initialNavigation: 'enabledBlocking' })`(`core-libs/storefront/router/app-routing.module.ts:13-19`)。ルート配列は空。
- 機能ライブラリのルートは `data.cxRoute` 名だけを持ち、実パスは `RoutingConfig.routing.routes[name].paths` から `ConfigurableRoutesService` が起動時に埋める(`configurable-routes.service.ts:48-52, 77-97`)。既定は `core-libs/storefront/cms-structure/routing/default-routing-config.ts`(例 `product: { paths: ['product/:productCode/:name', 'product/:productCode'] }`)。
- 最後に `'**'` が追加され、残りはすべて CMS ページ(3.1)。
- ルーター状態は `@ngrx/router-store` + `CustomSerializer`(`router.reducer.ts:109-155`)でストアに入り、`PageContext` と `cmsRequired` を持つ。`CmsService` は `getNextPageContext` を見て、遷移先ページ応答で届く見込みのコンポーネント要求を抑止する(4.2 (c))。
- テンプレートからの URL 生成は `cxUrl` パイプ + `{ cxRoute: 'product', params: { code } }`(`url.pipe.ts:11-18`, `url-command.ts:7-10`)。

---

[目次](README.md) | ← [1.5 状態管理(NgRx)と「取得済みなら取らない」の実装](01-5-ngrx-state.md) | [1.7 アウトレット(マッピングを変えずに差し込む仕組み)](01-7-outlets.md) →
