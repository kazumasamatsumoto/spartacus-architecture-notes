# 0. 要約

> **まず 4 文で**(詳しくは 8.0): ① 読むときは State を先に見て、無ければ API を叩く。② 書くとき(カート追加、ログイン、注文)は必ず API を叩き、応答で State を更新する。③ 読みの引き金は「State に無いものを誰かが購読した瞬間」で、描画はその最も多い形。ページ本体だけは `CmsPageGuard` が先回りし、既定では遷移のたびに取り直す。④ API は State を埋めるだけで、描画は State を購読している view が勝手に更新する。「この API でどの DOM が描かれるか」ではなく「State のどこが変わり、誰がそれを購読しているか」で考える。

以下、6 点に展開する。

1. **Spartacus は Angular アプリ**である。SAP が提供するのは Angular ライブラリ群(`@spartacus/core`, `@spartacus/storefront`, 機能ライブラリ)で、利用者は Angular CLI プロジェクトにそれらを組み込む。
2. **描画の主導権は CMS バックエンドにある**。ルーティングは `**`(ワイルドカード)で全 URL を受け、OCC の `cms/pages` からページ構造(テンプレート → スロット → コンポーネント)を取得して描画する。Angular のルート定義にページを書くのではない。
3. **バックエンドの `typeCode`(CMSFlexComponent なら `flexType`)が、フロントの Angular コンポーネントを選ぶキー**になる。フロント側の作業は原則「`provideConfig({ cmsComponents: { <typeCode>: { component: XxxComponent } } })` を 1 つ追加し、`CmsComponentData<T>` を注入して `data$` を描く」だけ。
4. **API が少ないのは設計どおり**。`cms/pages` のレスポンスに全コンポーネントのデータが同梱され、NgRx ストアに入る。足りない分だけ `cms/components?componentIds=...` でまとめて取り、取得済みは再取得しない(`cms/pages` 自体は既定で遷移のたびに取得する。7 章)。商品カルーセルも `products/search?filters=code:...` で一括取得する。
5. デモサイトは **CSR 配信(SSR なし)**。それでもホーム初回表示の OCC GET は 9 本程度、商品詳細への SPA 遷移は 6 本だった。SSR を有効にすると TransferState でさらに減る。
6. **動的な業務データ**を表示するコンポーネントは、フロントに Facade / Connector / Adapter / Normalizer を追加し(15 章)、バックエンドは**コンポーネント単位ではなくリソース単位**(画面部品ごとではなく、商品・注文・店舗といった業務アイテムの型ごと。「リソース」は REST 用語で、12.1 冒頭で Backoffice の語彙に対応づけている)の OCC エンドポイントを用意する(12 章)。

### 図(draw.io)

`docs/diagrams/spartacus-architecture.drawio`(18 ページ)。PNG / SVG 書き出し済み。

| ページ | 内容 | 画像 |
|---|---|---|
| 01 全体フロー URL→描画 | 3 章の 10 ステップと OCC 呼び出しの対応 | [page1.png](diagrams/page1.png) |
| 02 レイヤ構成 | アプリ → 機能ライブラリ → storefront → core → OCC → SAP Commerce | [page2.png](diagrams/page2.png) |
| 03 カスタムコンポーネントのデータ経路 | 経路 A(CMS 属性)と経路 B(業務データ: Facade〜Java Controller) | [page3.png](diagrams/page3.png) |
| 04 バックエンド判断フロー | 何を・どの単位で返すかの判断木 | [page4.png](diagrams/page4.png) |
| 05 JSP→ヘッドレス 責務の移行 | JSP コンポーネントコントローラの各責務がどこへ移るか(13 章) | [page5.png](diagrams/page5.png) |
| 06 Angular アプリの骨格と設定 DI | main.ts → bootstrapApplication → AppModule → SpartacusModule の骨格と provideConfig の合成(1 章) | [page6.png](diagrams/page6.png) |
| 07 API 呼び出しを減らす仕組み | HTTP が飛ぶ前に通る 16 個の止め弁(8 章) | [page7.png](diagrams/page7.png) |
| 08 リソースごとの呼び出し方法の違い | 通信層は共通、状態層は 2 方式、リソースごとの文脈・捨てる条件・バッチの比較表(10 章) | [page8.png](diagrams/page8.png) |
| 09 アプリケーションのライフサイクル | index.html 取得 → 起動 → APP_INITIALIZER → ゲート → 描画 → 実行中イベント → SSR → 永続化の 9 フェーズ(6 章) | [page9.png](diagrams/page9.png) |
| 10 呼び出しの 4 階層と毎回・初回 | セッション / ページ / コンポーネント / アクションの 4 階層と、再訪時に何が飛ぶかの実測(7 章) | [page10.png](diagrams/page10.png) |
| 11 OCC リソースの 3 層とカスタムの置き場所 | サイト設定 / CMS / 業務データの 3 層、決め方の順序、業務データ層の主なリソース一覧(9 章) | [page11.png](diagrams/page11.png) |
| 12 cms/pages 応答 → async パイプまでの 8 段階 | 正規化 → ストア格納 → ガード → レイアウト → 遅延判定 → createComponent → data$ 購読 → async パイプ。段階ごとの通信・ストア・DOM・失敗範囲(4 章) | [page12.png](diagrams/page12.png) |
| 13 API の形 → State の形: 3 層の作り変え | cms/pages の JSON が Normalizer → Effect → Reducer を通って cms ステートになるまでと、State で見える違いごとの作り手・変えたいときの入口(5 章) | [page13.png](diagrams/page13.png) |
| 14 ルーティングと配置: 普通の Angular との違い | URL とページの対応表を誰が持つか(左)、配置は「文字列をキーに 4 つの表を引く」の繰り返し(右)(3 章 3.0) | [page14.png](diagrams/page14.png) |
| 15 変更検知の 3 段階と dirty の経路 | A いつ tick / B どの view(dirty 印は自分から根元まで、OnPush で印なしは飛ばす)/ C どのバインディングが DOM を触るか。ソートとホーム再訪を view の木で比較(16 章) | [page15.png](diagrams/page15.png) |
| 16 zone.js の見張りと dirty の 2 つの時刻 | zone.js がブラウザ API を差し替えてタスクを数え、Angular zone のマイクロタスクが 0 になった瞬間に tick を起こすまで。クリックと OCC 応答を時間軸に並べ、印を付ける時刻と見つける時刻を分ける(17 章) | [page16.png](diagrams/page16.png) |
| 17 Signal の反応グラフと async パイプとの違い | 値が変わってから DOM が変わるまでを Observable + async と signal で並べる。producer / consumer のリンクと、set() が印を付ける経路(18 章) | [page17.png](diagrams/page17.png) |
| 18 Query の状態機械と Command の戦略 | QueryService の 1 つの状態 { loading, error, data } が購読・再購読・reloadOn・resetOn・エラーでどう遷移し、どこで API が飛ぶか。Command の 4 strategy。EventService が結ぶ「書く → イベント → 取り直す」の実例(19 章) | [page18.png](diagrams/page18.png) |

![全体フロー](diagrams/page1.png)


---

[目次](README.md) | [1. Angular 入門(バックエンド担当者向け)と Spartacus への対応](01-angular-basics.md) →
