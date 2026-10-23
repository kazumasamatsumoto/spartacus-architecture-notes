# 6. バックエンド側のチェックリスト

> **図**: 04 バックエンド判断フロー(`diagrams/spartacus-architecture.drawio`)。チェックリストの前提になる「何を・どの単位で返すか」の判断木(詳細は 8 章)

![04 バックエンド判断フロー](diagrams/page4.png)

> **この章が答える問い**: バックエンド側で何を用意すればフロントが困らないか


- [ ] `*-items.xml` で `SimpleCMSComponent`(または適切な親)を継承した ItemType を定義し、`typeCode` を決める
- [ ] OCC で属性が公開されるようにする(`cmsocc` の DTO / Converter / `fields=DEFAULT` のフィールド定義)。開発 OCC で `GET /occ/v2/{baseSite}/users/anonymous/cms/pages?pageType=ContentPage&pageLabelOrId=homepage` を叩いて JSON に出ることを確認
- [ ] ページテンプレート / コンテンツスロットにコンポーネントを配置し、カタログ同期(Staged → Online)
- [ ] フロントが参照する属性名・値の表現を固定し、依頼書(5.8)を書く
- [ ] 参照系データ(商品など)は OCC 商品 API で取得できる前提にする。CMS 属性へコピーしない
- [ ] 既存の `cms/pages` レスポンスサイズに注意する(ホームで 73KB)。巨大な HTML や大量リストを 1 コンポーネントに詰めない


---

[目次](README.md) | ← [5. バックエンドでカスタム CMS コンポーネントを作るとき、フロントへ渡す仕様](05-custom-cms-component-spec.md) | [7. 業務データを扱うカスタムコンポーネント: Facade / Connector / Adapter の作り方](07-facade-connector-adapter.md) →
