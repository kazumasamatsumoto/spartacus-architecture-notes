# 1.1 技術スタック(根拠: `spartacus/package.json`)

> **図**: 06 Angular アプリの骨格と設定 DI(`diagrams/spartacus-architecture.drawio`)。この節の各ライブラリ(Angular / NgRx / RxJS / i18next)が、左の AppModule と BaseCoreModule のどこで組み込まれるかの全体像

![06 Angular アプリの骨格と設定 DI](diagrams/page6.png)

> **この章が答える問い**: どのライブラリの、どのバージョンで動いているか

> 1 章の目次: [1. Angular 入門(バックエンド担当者向け)と Spartacus への対応](01-angular-basics.md)

| 技術 | バージョン | 役割 |
|---|---|---|
| Angular (`@angular/core`, `@angular/ssr`, `@angular/platform-server`) | ~21.2.23 | UI フレームワーク本体、SSR |
| NgRx (`@ngrx/store`, `@ngrx/effects`, `@ngrx/router-store`) | ~21.0.1 | 状態管理(Redux パターン) |
| RxJS | ~7.8.0 | 非同期ストリーム(`Observable`) |
| i18next (+ `i18next-http-backend`, `i18next-resources-to-backend`) | ~25.7.4 | 翻訳(Angular 標準 i18n ではない) |
| TypeScript / Node.js | ~5.9.3 / ^22.22.0 | `package.json:290`, `:11-13` |
| zone.js | ^0.16.0 | 変更検知(まだ zone ベース) |

利用者のアプリに `ng add @spartacus/schematics` で入る依存は `spartacus/core-libs/schematics/src/dependencies.json:10-23` に定義されている(`@angular/core ^21.2.23`, `@ngrx/store ^21.0.1`, `rxjs ^7.8.0` 等)。

---

[目次](README.md) | ← [1. Angular 入門(章の目次)](01-angular-basics.md) | [1.2 Angular の基本概念 → Spartacus での実体](01-2-concept-map.md) →
