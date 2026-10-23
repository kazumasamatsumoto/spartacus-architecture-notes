# 1.2 Angular の基本概念 → Spartacus での実体

> **図**: 06 Angular アプリの骨格と設定 DI(`diagrams/spartacus-architecture.drawio`)。表の「Spartacus での実体」は、この図の左(モジュール/コンポーネント)と右(DI による設定)のどこかに必ず対応する

![06 Angular アプリの骨格と設定 DI](diagrams/page6.png)

> 1 章の目次: [1. Angular 入門(バックエンド担当者向け)と Spartacus への対応](01-angular-basics.md)

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

---

[目次](README.md) | ← [1.1 技術スタック(根拠: `spartacus/package.json`)](01-1-tech-stack.md) | [1.3 アプリの骨格(利用者が持つコード)](01-3-app-skeleton.md) →
