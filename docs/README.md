# SAP Composable Storefront (Spartacus) アーキテクチャ解説

## この資料が目指していること(質問の履歴から逆算)

ここまでの質問を並べると、知りたいことは一貫して **「画面に出ているものが、どこから来て、いつ取りに行かれ、何を変えるとどう反映されるのか」** である。最初の問い(「カスタムコンポーネントを作るときフロントに何を指示すればいいか」「なぜ API が少ないのか」)から、リソースの単位、呼び出し方の違い、ライフサイクル、毎回と初回の違いへと進んだのは、**静的な構造ではなく、動いている状態の仕組みを掴もうとしている**からだと読み取れる。

そこで本書は「どう動いているか」を 3 つの問いに分解し、章をその答えとして配置し直している。

| 問い | 一言の答え | 詳しく |
|---|---|---|
| **① どこから来るか**(データの出所) | 画面の構造は `cms/pages` 1 本から、コンポーネントの中身は同じ応答に同梱されて、業務データ(商品・カート・注文…)は「リソース」ごとの OCC API から来る。バックエンドの `typeCode` がフロントの Angular コンポーネントを選ぶ | [3 章](03-rendering-flow.md), [9 章](09-occ-resource-catalog.md), [11 章](11-custom-cms-component-spec.md) |
| **② いつ取りに行くか**(タイミング) | 起動時に 1 回(セッション)、ページ遷移のたび(`cms/pages`)、コンポーネントが初めて生成されたとき(業務データ)、ユーザー操作のたび(更新系)。取得済みはストアに残り、言語変更・ログイン・ログアウトで捨てられる | [6 章](06-application-lifecycle.md), [7 章](07-call-tiers.md), [4 章](04-page-to-component.md), [8 章](08-why-few-api-calls.md) |
| **③ 何を変えるとどう反映されるか**(変更の影響範囲) | CMS の配置・属性は次の遷移で反映。業務データの変更はリロードか言語変更まで反映されない。フロントの呼び出し方は通信層が共通で、状態層が 2 方式、リソースごとに「必要な ID」と「捨てる条件」が違う | [10 章](10-frontend-call-patterns.md), [7 章](07-call-tiers.md), [5 章](05-api-to-state.md), [12 章](12-backend-api-granularity.md) |

この 3 問に答えられれば、「このカスタムコンポーネントはどのリソースを参照し、フロントは何を・いつ呼び、更新後に何を取り直すか」が自分で導けるようになる。それが依頼書([11.8](11-custom-cms-component-spec.md), [12.5](12-backend-api-granularity.md), [10.6](10-frontend-call-patterns.md))の中身である。

## 読む順序

章番号は読む順に振ってある。**0 章から番号順に読めばよい**。各章の冒頭に「位置づけ」を 1 行置いているので、飛ばして読むときはそこで戻り先を確認する。

### 第 I 部 前提(0〜2 章)

- [0. 要約](00-summary.md) — 結論 8 行と図の一覧。先に読んでも、最後に読み返してもよい
- [1. Angular 入門(バックエンド担当者向け)](01-angular-basics.md) — 9 ページ。**まず [1.2 対応表](01-2-concept-map.md)・[1.3 骨格](01-3-app-skeleton.md)・[1.4 設定](01-4-config-di.md)・[1.5 NgRx](01-5-ngrx-state.md) の 4 ページ**。残り(1.1, 1.6〜1.9)は後の章で必要になったら戻る
- [2. Spartacus のパッケージ構成](02-package-layers.md) — `core` / `storefront` / 機能ライブラリの役割分担

### 第 II 部 動き: どう動いているか(3〜8 章)

- [3. URL からコンポーネント描画まで](03-rendering-flow.md) — **幹**。ページ遷移 1 回の中で起きる 10 ステップ。4〜8 章はこの章の拡大か前後
- [4. cms/pages 応答からコンポーネント描画まで](04-page-to-component.md) — 3 章のステップ 5〜10 の拡大。`cms/components` が飛ぶ(飛ばない)条件、`data$ | async` が値を出すまでの 8 段階、Redux DevTools で見える形
- [5. API の形と State の形はなぜ違うのか](05-api-to-state.md) — 4 章の段階 1〜2 の拡大。Normalizer / Effect / Reducer の 3 層
- [6. アプリケーションのライフサイクル](06-application-lifecycle.md) — 3 章の前後。起動から永続化までの 9 フェーズ、何を捨てるか
- [7. 呼び出しの 4 階層と「毎回」「初回」](07-call-tiers.md) — セッション / ページ / コンポーネント / アクション。デモで実測
- [8. なぜ API 呼び出しが少ないのか](08-why-few-api-calls.md) — 3〜7 章のまとめ。HTTP が飛ぶ前に通る 16 個の止め弁

### 第 III 部 境界: バックエンドとフロントの契約(9〜14 章)

- [9. OCC リソース一覧](09-occ-resource-catalog.md) — サイト設定 / CMS / 業務データの 3 層。カスタムをどのリソースの中で考えるか
- [10. フロント側の呼び出し方法はリソースごとに違うのか](10-frontend-call-patterns.md) — 通信層は共通、状態層は 2 方式、リソースごとの文脈と捨てる条件
- [11. カスタム CMS コンポーネントの依頼仕様](11-custom-cms-component-spec.md) — `typeCode` / `flexType` / `uid`、OCC JSON、Angular 側の雛形
- [12. 何を、どの単位で返すか](12-backend-api-granularity.md) — 判断の順序 ①〜④、DTO と `fields`、Java サンプル
- [13. JSP からヘッドレスへ](13-jsp-to-headless.md) — JSP が持っていた責務をどこへ移すか
- [14. バックエンド側のチェックリスト](14-backend-checklist.md)

### 第 IV 部 作る: フロント側の実装(15〜21 章)

- [15. Facade / Connector / Adapter の作り方](15-facade-connector-adapter.md) — 業務データを扱うコンポーネントの 4 層と雛形一式
- [16. 変更検知と dirty フラグ](16-change-detection.md) — API の応答が届いたあと、どの view が評価され、どの DOM が触られるか。ヘッダーが残り一覧の行が作り直される理由
- [17. zone.js と変更検知の実行モデル](17-zone-rendering.md) — zone.js が何を見張って tick を起こすか。dirty の印が付く時刻と見つかる時刻を 1 本の時間軸で
- [18. Signal API](18-signals.md) — 印の付け方が view 単位から「読んだ場所」単位に変わる。Observable + async パイプとの対応表、Spartacus 2612 での実態、カスタム実装での使い方
- [19. Query / Command パターン](19-query-command.md) — ストア無しで「取得済みなら取らない」「更新したら取り直す」をどう作っているか。Query の状態遷移表、Command の 4 strategy、EventService の配線、NgRx との対応表
- [20. zone.js と zoneless](20-zoneless.md) — zone.js を外すと 16〜17 章のどこが変わりどこが変わらないか。tick を起こす経路(2 本 → 1 本)、Global と Targeted、安定判定と SSR、Angular 21 の既定が zoneless なのに Spartacus が zone モードを明示する理由、両モードで動くカスタム実装の 4 規則
- [21. 状態管理の選択: NgRx と Signal](21-state-management.md) — 「signal か NgRx か」(状態の持ち方)と「zone か zoneless か」(変更検知)は別の軸。Store / Action / Reducer / Selector / Effect / Facade の仕事を signal / computed / resource / toSignal が何で担うか、Spartacus 2612 の集計(NgRx が木、signal は末端 13 ファイル)、状態の種類 ①〜④ で決める選び方
### 第 V 部 使う: 要件から触る場所を引き、書く(22〜25 章)

- [22. カスタマイズシナリオ 100](22-customization-scenarios.md) — 「〜を変えたい」100 件を、段 0(バックエンドのデータ・CMS だけ)〜段 5(Adapter / Facade 差し替え)と BE(バックエンド実装が必要)の 7 段に振り分けた索引。各行にフロントの作業・バックエンドの作業・根拠。設定がありそうで無い落とし穴の一覧
- [23. フロント側カスタマイズの実装ガイド](23-frontend-customization-guide.md) — どのファイルに何をどう書くか。`ng add` が作る骨格、root と遅延ロードの 2 層の injector による置き場所の 3 規則、段 1〜5 のコード例(設定・SCSS・アウトレット・部品の継承・Normalizer・Adapter / Service / Facade の差し替え・インターセプタ)、よくある失敗の見分け方
- [24. バックエンド側カスタマイズの実装ガイド](24-backend-customization-guide.md) — SAP Commerce の 4 層(型 items.xml・中身 ImpEx・変換 Data / WsDTO / Populator・窓口 OCC Controller)と置く拡張、CMS 属性が OCC でどんな形になるか(デモ実測)、Solr・OAuth・CORS、リリースの順番(バックエンドが先。fields に無い項目は 400)。SAP 公式サンプルリポジトリで書き方を確かめ、確かめられなかったものは「要確認」と明記
- [25. JSP やタグの Java 呼び出しと、フロント / バックの責務](25-jsp-java-calls-and-responsibilities.md) — アクセラレータの Web 拡張(ページコントローラ・BeforeViewHandler・Validator・JSP・タグ・EL 関数)はヘッドレスでは実行されない。ビュー層から Java を呼ぶ 8 つの形の行き先、OPF の JSP 版と Spartacus 版の比較、責務を決める 6 つの問い、両方に置くもの(正はバック、写しはフロント)、棚卸しの grep

- [付録](appendix.md) — デモ OCC の実レスポンス、エンドポイント設定の一覧

## 質問と、それに答えた章の対応

質問は時系列順。章番号は現在のもの(2026-10-26 に読む順へ振り直した)。

| 聞いたこと | 答えた章 |
|---|---|
| アーキテクチャを理解したい。カスタムコンポーネントでフロントに何を指示すればいいか。なぜデモの API が少ないのか | 3, 8, 11 |
| Angular の情報が無い | 1(9 ページ) |
| draw.io で図式化。Facade / Connector は要るのか。Java は何を返せばいいのか。`@RestController` をどの単位で | 15, 12, 図 01〜04 |
| JSP の URL を返していた所は REST 化でどう返すか | 13 |
| Angular は分割しても、なぜ表示できるのか | 1.3, 3(DOM の入れ子と `createComponent`) |
| 1.4 が全くわからない | 1.4 を Spring 対応表から書き直し |
| 「リソース単位」とは何か。Backoffice に無い言葉 | 12.1 冒頭、9 |
| ベースサイトや `cms/pages` も全部リソースか | 9.1(3 層) |
| カスタムコンポーネントはコンポーネントのリソースから派生するのか。リソースの単位をまとめてほしい | 9 |
| フロントの呼び出し方は全リソース共通か、リソースごとに違うか | 10 |
| イニシャライズからのライフサイクル全部 | 6 |
| 必ず呼ぶリソースと追加リソース、アクションごとのリソースという理解で合っているか。毎回と初回の違い | 7(実測付き) |
| `cms/pages` からコンポーネントの API を呼ぶまでの間、`async` パイプ実行までの間に何が行われているか | 4 |
| Redux DevTools で見える State の形が `cms/pages` の API 構造と一致しない。この違いはどのロジックが作っているか | 5 |
| 0 から読み進めて理解できるか。どの順番で読めばいいかわからない | 章番号を読む順に振り直し(本ページ) |
| カスタマイズシナリオをいっぱい作って。100 ケース目標 | 22 |
| フロントでカスタマイズするときの実装場所と実装方法をコード付きで | 23 |
| バックエンド側のカスタマイズをコード付きで | 24 |
| 既存アクセラレータで JSP やタグから Java を呼んでいた処理はどうなるか。フロントとバックの責務はどう分けるか | 25 |

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

## 章の一覧(番号順 = 読む順)

各章は 1 ページずつ分割し、冒頭に対応する図と「この章が答える問い」を置いている。図は [diagrams/](diagrams/)(draw.io 24 ページ + PNG / SVG)。図の番号は章番号と独立している(対応は [0 章の表](00-summary.md))。

- [0. 要約](00-summary.md)
- [1. Angular 入門(バックエンド担当者向け)と Spartacus への対応](01-angular-basics.md)
  - [1.1 技術スタック](01-1-tech-stack.md) / [1.2 基本概念 → Spartacus](01-2-concept-map.md) / [1.3 アプリの骨格](01-3-app-skeleton.md) / [1.4 設定の仕組み](01-4-config-di.md) / [1.5 状態管理(NgRx)](01-5-ngrx-state.md) / [1.6 ルーティング](01-6-routing.md) / [1.7 アウトレット](01-7-outlets.md) / [1.8 i18n](01-8-i18n.md) / [1.9 コンポーネントの書き方](01-9-component-style.md)
- [2. Spartacus のパッケージ構成](02-package-layers.md)
- [3. 全体像: URL からコンポーネント描画まで](03-rendering-flow.md)
- [4. `cms/pages` 応答からコンポーネント描画まで: `async` パイプが値を出すまでに何が起きているか](04-page-to-component.md)
- [5. API の形と State の形はなぜ違うのか: Normalizer / Effect / Reducer の 3 層による作り変え](05-api-to-state.md)
- [6. アプリケーションのライフサイクル: index.html 取得から永続化まで](06-application-lifecycle.md)
- [7. 呼び出しの 4 階層と「毎回」「初回」の違い](07-call-tiers.md)
- [8. なぜデモサイトの API 呼び出しが少ないのか](08-why-few-api-calls.md)
- [9. OCC リソース一覧: カスタムをどのリソースの中で考えるか](09-occ-resource-catalog.md)
- [10. フロント側の呼び出し方法はリソースごとに違うのか](10-frontend-call-patterns.md)
- [11. バックエンドでカスタム CMS コンポーネントを作るとき、フロントへ渡す仕様](11-custom-cms-component-spec.md)
- [12. バックエンド(Java)側: 何を、どの単位で返すか](12-backend-api-granularity.md)
- [13. JSP(アクセラレータ)のコンポーネントコントローラをヘッドレスに移すとき、何を返すか](13-jsp-to-headless.md)
- [14. バックエンド側のチェックリスト](14-backend-checklist.md)
- [15. 業務データを扱うカスタムコンポーネント: Facade / Connector / Adapter の作り方](15-facade-connector-adapter.md)
- [16. 変更検知と dirty フラグ: API の応答が届いたあと、どの view が描き直るのか](16-change-detection.md)
- [17. zone.js と変更検知の実行モデル: 印が付く瞬間と、印が見つかる瞬間](17-zone-rendering.md)
- [18. Signal API: 印の付け方が view 単位から「読んだ場所」単位に変わる](18-signals.md)
- [19. Query / Command パターン: ストア無しで「取得済みなら取らない」と「更新したら取り直す」を作る](19-query-command.md)
- [20. zone.js と zoneless: 「tick をいつ起こすか」を誰が決めるか](20-zoneless.md)
- [21. 状態管理の選択: NgRx(Store / Facade / Observable)と Signal(signal / computed / resource)](21-state-management.md)
- [22. カスタマイズシナリオ 100: その要件はどの段で吸収できるか](22-customization-scenarios.md)
- [23. フロント側カスタマイズの実装ガイド: どのファイルに、何を、どう書くか](23-frontend-customization-guide.md)
- [24. バックエンド側カスタマイズの実装ガイド: どの拡張に、何を、どう書くか](24-backend-customization-guide.md)
- [25. JSP やタグから Java を呼んでいた処理はどうなるか、フロントとバックの責務をどう分けるか](25-jsp-java-calls-and-responsibilities.md)
- [付録](appendix.md)
