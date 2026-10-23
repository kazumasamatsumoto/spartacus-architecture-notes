# 0. 要約

1. **Spartacus は Angular アプリ**である。SAP が提供するのは Angular ライブラリ群(`@spartacus/core`, `@spartacus/storefront`, 機能ライブラリ)で、利用者は Angular CLI プロジェクトにそれらを組み込む。
2. **描画の主導権は CMS バックエンドにある**。ルーティングは `**`(ワイルドカード)で全 URL を受け、OCC の `cms/pages` からページ構造(テンプレート → スロット → コンポーネント)を取得して描画する。Angular のルート定義にページを書くのではない。
3. **バックエンドの `typeCode`(CMSFlexComponent なら `flexType`)が、フロントの Angular コンポーネントを選ぶキー**になる。フロント側の作業は原則「`provideConfig({ cmsComponents: { <typeCode>: { component: XxxComponent } } })` を 1 つ追加し、`CmsComponentData<T>` を注入して `data$` を描く」だけ。
4. **API が少ないのは設計どおり**。`cms/pages` のレスポンスに全コンポーネントのデータが同梱され、NgRx ストアに入る。足りない分だけ `cms/components?componentIds=...` でまとめて取り、取得済みは再取得しない。商品カルーセルも `products/search?filters=code:...` で一括取得する。
5. デモサイトは **CSR 配信(SSR なし)**。それでもホーム初回表示の OCC GET は 9 本程度、商品詳細への SPA 遷移は 6 本だった。SSR を有効にすると TransferState でさらに減る。
6. **動的な業務データ**を表示するコンポーネントは、フロントに Facade / Connector / Adapter / Normalizer を追加し(7 章)、バックエンドは**コンポーネント単位ではなくリソース単位**(画面部品ごとではなく、商品・注文・店舗といった業務アイテムの型ごと。「リソース」は REST 用語で、8.1 冒頭で Backoffice の語彙に対応づけている)の OCC エンドポイントを用意する(8 章)。

### 図(draw.io)

`docs/diagrams/spartacus-architecture.drawio`(7 ページ)。PNG / SVG 書き出し済み。

| ページ | 内容 | 画像 |
|---|---|---|
| 01 全体フロー URL→描画 | 3 章の 10 ステップと OCC 呼び出しの対応 | [page1.png](diagrams/page1.png) |
| 02 レイヤ構成 | アプリ → 機能ライブラリ → storefront → core → OCC → SAP Commerce | [page2.png](diagrams/page2.png) |
| 03 カスタムコンポーネントのデータ経路 | 経路 A(CMS 属性)と経路 B(業務データ: Facade〜Java Controller) | [page3.png](diagrams/page3.png) |
| 04 バックエンド判断フロー | 何を・どの単位で返すかの判断木 | [page4.png](diagrams/page4.png) |
| 05 JSP→ヘッドレス 責務の移行 | JSP コンポーネントコントローラの各責務がどこへ移るか(9 章) | [page5.png](diagrams/page5.png) |
| 06 Angular アプリの骨格と設定 DI | main.ts → bootstrapApplication → AppModule → SpartacusModule の骨格と provideConfig の合成(1 章) | [page6.png](diagrams/page6.png) |
| 07 API 呼び出しを減らす仕組み | HTTP が飛ぶ前に通る 16 個の止め弁(4 章) | [page7.png](diagrams/page7.png) |

![全体フロー](diagrams/page1.png)


---

[目次](README.md) | [1. Angular 入門(バックエンド担当者向け)と Spartacus への対応](01-angular-basics.md) →
