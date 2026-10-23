# spartacus-architecture-notes

SAP Composable Storefront (Spartacus) のアーキテクチャを、ソースコードを根拠に解説したノートです。
バックエンド(SAP Commerce Cloud)でカスタム CMS コンポーネントを作る担当者が、フロントエンド側へ何を依頼すればよいかを理解することを目的にしています。

- [docs/spartacus-architecture.md](docs/spartacus-architecture.md) — 本文(Angular 基盤、CMS 描画フロー、API 削減の仕組み、カスタムコンポーネントの依頼仕様、Facade/Connector/Adapter、バックエンドの返し方)
- [docs/diagrams/spartacus-architecture.drawio](docs/diagrams/spartacus-architecture.drawio) — draw.io 図(4 ページ)。PNG / SVG も同じフォルダ

![全体フロー](docs/diagrams/page1.png)

## 調査対象

- [SAP/spartacus](https://github.com/SAP/spartacus) `develop` ブランチ、コミット `b7b028f22814412ccbd8be3c7f688d4119abdc5f`(2026-10-22)、バージョン 2612.0.0
- 文書中の `spartacus/<path>:<line>` は、上記コミットをクローンしたリポジトリ内のファイルと行番号を指します
- デモサイト https://composable-storefront-demo.eastus.cloudapp.azure.com/electronics-spa/en/USD/ の挙動は 2026-10-23 時点の実測です

## ライセンス表記

文書中に引用している TypeScript / HTML のコード断片は SAP/spartacus のものであり、
[Apache License 2.0](https://github.com/SAP/spartacus/blob/develop/LICENSE.txt) に基づきます。
Copyright SAP SE or an SAP affiliate company and Spartacus contributors.
