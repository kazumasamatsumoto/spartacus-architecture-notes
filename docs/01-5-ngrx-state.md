# 1.5 状態管理(NgRx)と「取得済みなら取らない」の実装

> **図**: 07 API 呼び出しを減らす仕組み(`diagrams/spartacus-architecture.drawio`)。本節の Entity Loader(loading / success / error)が、図の弁①・弁⑤・弁⑫に当たる。NgRx の Action → Effect → Reducer → Selector の役割分担も図の各列と対応

![07 API 呼び出しを減らす仕組み](diagrams/page7.png)

> 1 章の目次: [1. Angular 入門(バックエンド担当者向け)と Spartacus への対応](01-angular-basics.md)

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

---

[目次](README.md) | ← [1.4 設定の仕組み(`provideConfig` が効く理由)](01-4-config-di.md) | [1.6 ルーティング](01-6-routing.md) →
