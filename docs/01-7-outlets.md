# 1.7 アウトレット(マッピングを変えずに差し込む仕組み)

> **図**: 01 全体フロー URL→描画(`diagrams/spartacus-architecture.drawio`)。本節は図のステップ ⑥〜⑦: PageLayoutComponent と <cx-page-slot> の各段にある cxOutlet が差し込み点。マッピングを変えずに前後・置換できる

![01 全体フロー URL→描画](diagrams/page1.png)

> 1 章の目次: [1. Angular 入門(バックエンド担当者向け)と Spartacus への対応](01-angular-basics.md)

`spartacus/core-libs/storefront/cms-structure/outlet/outlet.model.ts:9-13`
```ts
export enum OutletPosition {
  REPLACE = 'replace',
  BEFORE = 'before',
  AFTER = 'after',
}
```
`[cxOutlet]` ディレクティブは、登録されたテンプレート/コンポーネントを自身の前・置換・後に描画する(`outlet.directive.ts:121-139`)。ページテンプレート名(`page-layout.component.html:4`)、スロット位置、コンポーネントの `flexType`(`page-slot.component.html:1-15`)がそのままアウトレット ID になるため、**バックエンドの typeCode 名は、フロントにとってアウトレット名でもある**。登録は `provideOutlet({ id, position, component })`(`outlet.providers.ts:41-47`、既定 AFTER)または `<ng-template cxOutletRef="..." cxOutletPos="before">`。

---

[目次](README.md) | ← [1.6 ルーティング](01-6-routing.md) | [1.8 i18n](01-8-i18n.md) →
