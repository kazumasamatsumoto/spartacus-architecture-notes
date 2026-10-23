# 4. なぜデモサイトの API 呼び出しが少ないのか

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

[目次](README.md) | ← [3. 全体像: URL からコンポーネント描画まで](03-rendering-flow.md) | [5. バックエンドでカスタム CMS コンポーネントを作るとき、フロントへ渡す仕様](05-custom-cms-component-spec.md) →
