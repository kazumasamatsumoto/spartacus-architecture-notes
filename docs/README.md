# SAP Composable Storefront (Spartacus) アーキテクチャ解説

## この資料が目指していること(質問の履歴から逆算)

ここまでの質問を並べると、知りたいことは一貫して **「画面に出ているものが、どこから来て、いつ取りに行かれ、何を変えるとどう反映されるのか」** である。最初の問い(「カスタムコンポーネントを作るときフロントに何を指示すればいいか」「なぜ API が少ないのか」)から、リソースの単位、呼び出し方の違い、ライフサイクル、毎回と初回の違いへと進んだのは、**静的な構造ではなく、動いている状態の仕組みを掴もうとしている**からだと読み取れる。

そこで本書は「どう動いているか」を 3 つの問いに分解し、章をその答えとして配置し直している。

| 問い | 一言の答え | 詳しく |
|---|---|---|
| **① どこから来るか**(データの出所) | 画面の構造は `cms/pages` 1 本から、コンポーネントの中身は同じ応答に同梱されて、業務データ(商品・カート・注文…)は「リソース」ごとの OCC API から来る。バックエンドの `typeCode` がフロントの Angular コンポーネントを選ぶ | [3 章](03-rendering-flow.md), [10 章](10-occ-resource-catalog.md), [5 章](05-custom-cms-component-spec.md) |
| **② いつ取りに行くか**(タイミング) | 起動時に 1 回(セッション)、ページ遷移のたび(`cms/pages`)、コンポーネントが初めて生成されたとき(業務データ)、ユーザー操作のたび(更新系)。取得済みはストアに残り、言語変更・ログイン・ログアウトで捨てられる | [12 章](12-application-lifecycle.md), [13 章](13-call-tiers.md), [14 章](14-page-to-component.md), [4 章](04-why-few-api-calls.md) |
| **③ 何を変えるとどう反映されるか**(変更の影響範囲) | CMS の配置・属性は次の遷移で反映。業務データの変更はリロードか言語変更まで反映されない。フロントの呼び出し方は通信層が共通で、状態層が 2 方式、リソースごとに「必要な ID」と「捨てる条件」が違う | [11 章](11-frontend-call-patterns.md), [13 章](13-call-tiers.md), [15 章](15-api-to-state.md), [8 章](08-backend-api-granularity.md) |

この 3 問に答えられれば、「このカスタムコンポーネントはどのリソースを参照し、フロントは何を・いつ呼び、更新後に何を取り直すか」が自分で導けるようになる。それが依頼書([5.8](05-custom-cms-component-spec.md), [8.5](08-backend-api-granularity.md), [11.6](11-frontend-call-patterns.md))の中身である。

## 読む順序(4 部構成)

章番号は調べた順に付いているので、**理解の順序は章番号と違う**。以下の順で読むことを勧める。

### 第 I 部 動き: どう動いているか(まずここ)

1. [12. アプリケーションのライフサイクル](12-application-lifecycle.md) — 起動から永続化までの 9 フェーズ。どの段階で何が呼ばれ、何が捨てられるか
2. [3. URL からコンポーネント描画まで](03-rendering-flow.md) — ページ遷移 1 回の中で起きる 10 ステップ
3. [13. 呼び出しの 4 階層と「毎回」「初回」](13-call-tiers.md) — セッション / ページ / コンポーネント / アクション。実測付き
4. [14. cms/pages 応答からコンポーネント描画まで](14-page-to-component.md) — 応答が届いてから `cms/components` が飛ぶ(飛ばない)まで、`data$ | async` が値を出すまでの 8 段階
5. [15. API の形と State の形はなぜ違うのか](15-api-to-state.md) — `cms/pages` の JSON が Normalizer / Effect / Reducer の 3 層で `cms` ステートの形に作り変えられるまで。DevTools で見える形の由来
6. [4. なぜ API 呼び出しが少ないのか](04-why-few-api-calls.md) — HTTP が飛ぶ前に通る 16 個の止め弁

### 第 II 部 境界: バックエンドとフロントの契約

6. [10. OCC リソース一覧](10-occ-resource-catalog.md) — サイト設定 / CMS / 業務データの 3 層。カスタムをどのリソースの中で考えるか
7. [11. フロント側の呼び出し方法はリソースごとに違うのか](11-frontend-call-patterns.md) — 通信層は共通、状態層は 2 方式、リソースごとの文脈と捨てる条件
8. [5. カスタム CMS コンポーネントの依頼仕様](05-custom-cms-component-spec.md) — `typeCode` / `flexType` / `uid`、OCC JSON、Angular 側の雛形
9. [8. 何を、どの単位で返すか](08-backend-api-granularity.md) — 判断の順序 ①〜④、DTO と `fields`、Java サンプル
10. [9. JSP からヘッドレスへ](09-jsp-to-headless.md) — JSP が持っていた責務をどこへ移すか
11. [6. バックエンド側のチェックリスト](06-backend-checklist.md)

### 第 III 部 作る: フロント側の実装

12. [7. Facade / Connector / Adapter の作り方](07-facade-connector-adapter.md) — 業務データを扱うコンポーネントの 4 層と雛形一式

### 第 IV 部 前提知識: 必要になったら戻る

13. [1. Angular 入門(バックエンド担当者向け)](01-angular-basics.md) — 9 ページ。特に [1.3 骨格](01-3-app-skeleton.md)・[1.4 設定の仕組み](01-4-config-di.md)・[1.9 書き方](01-9-component-style.md)
14. [2. Spartacus のパッケージ構成](02-package-layers.md)
15. [0. 要約](00-summary.md) — 結論 8 行と図の一覧
16. [付録](appendix.md)

## 質問と、それに答えた章の対応

| 聞いたこと | 答えた章 |
|---|---|
| アーキテクチャを理解したい。カスタムコンポーネントでフロントに何を指示すればいいか。なぜデモの API が少ないのか | 3, 4, 5 |
| Angular の情報が無い | 1(9 ページ) |
| draw.io で図式化。Facade / Connector は要るのか。Java は何を返せばいいのか。`@RestController` をどの単位で | 7, 8, 図 01〜04 |
| JSP の URL を返していた所は REST 化でどう返すか | 9 |
| Angular は分割しても、なぜ表示できるのか | 1.3, 3(DOM の入れ子と `createComponent`) |
| 1.4 が全くわからない | 1.4 を Spring 対応表から書き直し |
| 「リソース単位」とは何か。Backoffice に無い言葉 | 8.1 冒頭、10 |
| ベースサイトや `cms/pages` も全部リソースか | 10.1(3 層) |
| カスタムコンポーネントはコンポーネントのリソースから派生するのか。リソースの単位をまとめてほしい | 10 |
| フロントの呼び出し方は全リソース共通か、リソースごとに違うか | 11 |
| イニシャライズからのライフサイクル全部 | 12 |
| 必ず呼ぶリソースと追加リソース、アクションごとのリソースという理解で合っているか。毎回と初回の違い | 13(実測付き) |
| `cms/pages` からコンポーネントの API を呼ぶまでの間、`async` パイプ実行までの間に何が行われているか | 14 |
| Redux DevTools で見える State の形が `cms/pages` の API 構造と一致しない。この違いはどのロジックが作っているか | 15 |

## 調査対象

| 項目 | 値 | 根拠 |
|---|---|---|
| リポジトリ | https://github.com/SAP/spartacus `develop` | クローン先 `spartacus/`(本リポジトリ直下) |
| コミット | `b7b028f22814412ccbd8be3c7f688d4119abdc5f`(2026-10-22) | `git log -1` |
| Spartacus バージョン | 2612.0.0 | `spartacus/package.json:3` |
| Angular | ~21.2.23 | `spartacus/package.json`(`@angular/core`) |
| NgRx / RxJS / i18next | ~21.0.1 / ~7.8.0 / ~25.7.4 | 同上 |
| デモサイト | https://composable-storefront-demo.eastus.cloudapp.azure.com/electronics-spa/en/USD/ | 2026-10-23 実測 |

本書のソース引用はすべて `spartacus/<パス>:<行>` 形式で、上記コミットのファイルを指す。ルール: ソースコードの参照が必要な場合はリポジトリをクローンして根拠とする。SAP Commerce 本体(Java)はクローンできないため、Java 側は SAP Help の公開ドキュメントとデモ OCC の実レスポンスを根拠にし、その旨を各所に明記している。

## 章の一覧(番号順)

各章は 1 ページずつ分割し、冒頭に対応する図と「この章が答える問い」を置いている。図は [diagrams/](diagrams/)(draw.io 13 ページ + PNG / SVG)。

- [0. 要約](00-summary.md)
- [1. Angular 入門(バックエンド担当者向け)と Spartacus への対応](01-angular-basics.md)
  - [1.1 技術スタック](01-1-tech-stack.md) / [1.2 基本概念 → Spartacus](01-2-concept-map.md) / [1.3 アプリの骨格](01-3-app-skeleton.md) / [1.4 設定の仕組み](01-4-config-di.md) / [1.5 状態管理(NgRx)](01-5-ngrx-state.md) / [1.6 ルーティング](01-6-routing.md) / [1.7 アウトレット](01-7-outlets.md) / [1.8 i18n](01-8-i18n.md) / [1.9 コンポーネントの書き方](01-9-component-style.md)
- [2. Spartacus のパッケージ構成](02-package-layers.md)
- [3. 全体像: URL からコンポーネント描画まで](03-rendering-flow.md)
- [4. なぜデモサイトの API 呼び出しが少ないのか](04-why-few-api-calls.md)
- [5. バックエンドでカスタム CMS コンポーネントを作るとき、フロントへ渡す仕様](05-custom-cms-component-spec.md)
- [6. バックエンド側のチェックリスト](06-backend-checklist.md)
- [7. 業務データを扱うカスタムコンポーネント: Facade / Connector / Adapter の作り方](07-facade-connector-adapter.md)
- [8. バックエンド(Java)側: 何を、どの単位で返すか](08-backend-api-granularity.md)
- [9. JSP(アクセラレータ)のコンポーネントコントローラをヘッドレスに移すとき、何を返すか](09-jsp-to-headless.md)
- [10. OCC リソース一覧: カスタムをどのリソースの中で考えるか](10-occ-resource-catalog.md)
- [11. フロント側の呼び出し方法はリソースごとに違うのか](11-frontend-call-patterns.md)
- [12. アプリケーションのライフサイクル: index.html 取得から永続化まで](12-application-lifecycle.md)
- [13. 呼び出しの 4 階層と「毎回」「初回」の違い](13-call-tiers.md)
- [14. cms/pages 応答からコンポーネント描画まで: async パイプが値を出すまでに何が起きているか](14-page-to-component.md)
- [15. API の形と State の形はなぜ違うのか: Normalizer / Effect / Reducer の 3 層による作り変え](15-api-to-state.md)
- [付録](appendix.md)
