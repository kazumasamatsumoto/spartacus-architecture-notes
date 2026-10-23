# 1. Angular 入門(バックエンド担当者向け)と Spartacus への対応

> **図**: 06 Angular アプリの骨格と設定 DI(`diagrams/spartacus-architecture.drawio`)。左: main.ts → bootstrapApplication → app.config.ts(importProvidersFrom(AppModule))→ SpartacusModule の骨格。右: provideConfig / provideDefaultConfig が deepMerge で 1 つの Config になる流れ(1.3, 1.4)

![06 Angular アプリの骨格と設定 DI](diagrams/page6.png)


> この章は、Angular を知らない読者が 2 章以降を読めるようにするための最小限の対応表です。各概念の「Spartacus ではここ」を実ファイルで示します。

## この章のページ

- [1.1 技術スタック(根拠: `spartacus/package.json`)](01-1-tech-stack.md)
- [1.2 Angular の基本概念 → Spartacus での実体](01-2-concept-map.md)
- [1.3 アプリの骨格(利用者が持つコード)](01-3-app-skeleton.md)
- [1.4 設定の仕組み(`provideConfig` が効く理由)](01-4-config-di.md)
- [1.5 状態管理(NgRx)と「取得済みなら取らない」の実装](01-5-ngrx-state.md)
- [1.6 ルーティング](01-6-routing.md)
- [1.7 アウトレット(マッピングを変えずに差し込む仕組み)](01-7-outlets.md)
- [1.8 i18n](01-8-i18n.md)
- [1.9 コンポーネントの書き方(標準ライブラリの実例)](01-9-component-style.md)

読む順番は上から。急ぐ場合は 1.2(対応表)→ 1.3(骨格)→ 1.4(設定)→ 1.9(書き方)の 4 ページで 2 章以降に進める。

---

[目次](README.md) | ← [0. 要約](00-summary.md) | [1.1 技術スタック(根拠: `spartacus/package.json`)](01-1-tech-stack.md) →
