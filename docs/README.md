# SAP Composable Storefront (Spartacus) アーキテクチャ解説

**目的**: バックエンド(SAP Commerce Cloud)でカスタム CMS コンポーネントを作る担当者が、フロントエンド(Spartacus)側に「何を・どう」依頼すればよいかを、ソースコードを根拠に理解する。

**調査対象**

| 項目 | 値 | 根拠 |
|---|---|---|
| リポジトリ | https://github.com/SAP/spartacus `develop` | クローン先 `spartacus/`(本リポジトリ直下) |
| コミット | `b7b028f22814412ccbd8be3c7f688d4119abdc5f`(2026-10-22) | `git log -1` |
| Spartacus バージョン | 2612.0.0 | `spartacus/package.json:3` |
| Angular | ~21.2.23 | `spartacus/package.json`(`@angular/core`) |
| NgRx / RxJS / i18next | ~21.0.1 / ~7.8.0 / ~25.7.4 | 同上 |
| デモサイト | https://composable-storefront-demo.eastus.cloudapp.azure.com/electronics-spa/en/USD/ | 2026-10-23 実測 |

本書のソース引用はすべて `spartacus/<パス>:<行>` 形式で、上記コミットのファイルを指す。

---

## 目次

各章は 1 ページずつ分割しています。図は [diagrams/](diagrams/) にあり、各ページの末尾に前後の章へのリンクがあります。

- [0. 要約](00-summary.md)
- [1. Angular 入門(バックエンド担当者向け)と Spartacus への対応](01-angular-basics.md)
- [2. Spartacus のパッケージ構成](02-package-layers.md)
- [3. 全体像: URL からコンポーネント描画まで](03-rendering-flow.md)
- [4. なぜデモサイトの API 呼び出しが少ないのか](04-why-few-api-calls.md)
- [5. バックエンドでカスタム CMS コンポーネントを作るとき、フロントへ渡す仕様](05-custom-cms-component-spec.md)
- [6. バックエンド側のチェックリスト](06-backend-checklist.md)
- [7. 業務データを扱うカスタムコンポーネント: Facade / Connector / Adapter の作り方](07-facade-connector-adapter.md)
- [8. バックエンド(Java)側: 何を、どの単位で返すか](08-backend-api-granularity.md)
- [9. JSP(アクセラレータ)のコンポーネントコントローラをヘッドレスに移すとき、何を返すか](09-jsp-to-headless.md)
- [付録](appendix.md)
