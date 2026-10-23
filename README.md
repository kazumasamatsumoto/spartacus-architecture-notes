# spartacus-architecture-notes

SAP Composable Storefront (Spartacus) のアーキテクチャを、ソースコードを根拠に解説したノートです。
バックエンド(SAP Commerce Cloud)でカスタム CMS コンポーネントを作る担当者が、フロントエンド側へ何を依頼すればよいかを理解することを目的にしています。

- [docs/README.md](docs/README.md) — 目次。本文は章ごとに 1 ページ(`docs/00-summary.md` 〜 `docs/09-jsp-to-headless.md`, `docs/appendix.md`)
- [docs/diagrams/spartacus-architecture.drawio](docs/diagrams/spartacus-architecture.drawio) — draw.io 図(5 ページ)。PNG / SVG も同じフォルダ

![全体フロー](docs/diagrams/page1.png)

## 調査対象

- [SAP/spartacus](https://github.com/SAP/spartacus) `develop` ブランチ、コミット `b7b028f22814412ccbd8be3c7f688d4119abdc5f`(2026-10-22)、バージョン 2612.0.0
- 文書中の `spartacus/<path>:<line>` は、上記コミットをクローンしたリポジトリ内のファイルと行番号を指します
- デモサイト https://composable-storefront-demo.eastus.cloudapp.azure.com/electronics-spa/en/USD/ の挙動は 2026-10-23 時点の実測です

## ライセンス表記

文書中に引用している TypeScript / HTML のコード断片は SAP/spartacus のものであり、
[Apache License 2.0](https://github.com/SAP/spartacus/blob/develop/LICENSE.txt) に基づきます。
Copyright SAP SE or an SAP affiliate company and Spartacus contributors.

## 図の再生成

`docs/diagrams/spartacus-architecture.drawio` が draw.io の元ファイルです(draw.io / diagrams.net でそのまま開けます)。
このファイルは `tools/gen_drawio.py` から生成しており、再生成と画像書き出しは次のとおりです。

```bash
python3 tools/gen_drawio.py                      # → docs/diagrams/spartacus-architecture.drawio
drawio -x -f png -s 1.5 -p 1 -o docs/diagrams/page1.png docs/diagrams/spartacus-architecture.drawio   # ページ番号は 1〜5
```
