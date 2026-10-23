# 1.4 設定の仕組み(`provideConfig` が効く理由)

> **図**: 06 Angular アプリの骨格と設定 DI(`diagrams/spartacus-architecture.drawio`)。本節は図の右半分: provideDefaultConfig / provideConfig が multi: true の配列として届き、deepMerge で 1 つの Config になる流れ

![06 Angular アプリの骨格と設定 DI](diagrams/page6.png)

> **この章が答える問い**: `provideConfig` を 1 行足すだけでなぜライブラリの挙動が変わるのか(DI と `multi: true`)

> 1 章の目次: [1. Angular 入門(バックエンド担当者向け)と Spartacus への対応](01-angular-basics.md)

**この節の結論**: Spartacus の設定は「1 つの設定ファイル」ではない。ライブラリとアプリがそれぞれ持ち寄った**設定の断片**を、Angular の DI(依存性注入)が起動時に **1 つのオブジェクトに合成**している。だから「カスタムコンポーネントを足す」依頼は「アプリ側に `provideConfig(...)` を 1 つ足してください」で済み、ライブラリ本体のコードは触らない。

## 1.4.1 前提: Angular の DI を Spring で言い換える

Angular の DI は Spring の DI と同じ発想で、対応はほぼ 1 対 1 である。

| Spring での書き方 | Angular での書き方 | 意味 |
|---|---|---|
| コンストラクタ引数に `@Autowired` | `constructor(protected config: CmsConfig)` または `inject(CmsConfig)` | 「この型の実体をください」と宣言すると、フレームワークが実体を渡す |
| `@Bean` で実体の作り方を登録 | プロバイダ `{ provide: キー, useValue: 値 }` | 「このキーを要求されたらこの値を渡す」という登録 |
| Bean 名 / `@Qualifier` | `InjectionToken`(クラスではない値を区別するためのキー) | 設定オブジェクトのように「型だけでは区別できない値」に名前を付ける |
| `List<Foo>` を注入すると該当 Bean が全部集まる | `multi: true` | **同じキーに複数登録すると、注入時に配列で渡される** |
| `application-prod.properties` で既定値を上書き | `provideDefaultConfig`(既定値)と `provideConfig`(上書き) | 後に合成される方が勝つ |

一番大事なのは `multi: true` である。これがあるから、ライブラリ A、ライブラリ B、利用者のアプリが**別々のファイルで**「設定の一部」を登録でき、Spartacus はそれを配列として受け取って合成できる。

## 1.4.2 登場人物は 4 つだけ

すべて `spartacus/core-libs/core/src/config/config-tokens.ts` にある。

| 名前 | 正体 | 中身 |
|---|---|---|
| `DefaultConfigChunk`(`:59-61`) | InjectionToken、`multi` | ライブラリが `provideDefaultConfig(...)` で登録した設定片の**配列** |
| `ConfigChunk`(`:52`) | InjectionToken、`multi` | アプリが `provideConfig(...)` で登録した設定片の**配列** |
| `DefaultConfig`(`:32-35`)/ `RootConfig`(`:44-47`) | InjectionToken | 上の 2 つの配列をそれぞれ `deepMerge` で 1 個にしたもの |
| `Config`(`:17-21`) | 抽象クラス(注入キーとして使う) | `deepMerge({}, DefaultConfig, RootConfig)` の**最終形**。Spartacus の全サービスはこれを読む |

流れを 1 枚にすると次のとおり。

```
ライブラリ側(@spartacus/*)                    アプリ側(spartacus-configuration.module.ts など)
provideDefaultConfig({cmsComponents:{A}})        provideConfig({backend:{occ:{baseUrl}}})
provideDefaultConfig({cmsComponents:{B}})        provideConfig({cmsComponents:{A: 差し替え}})
provideDefaultConfig({layoutSlots:{...}})        provideConfig({layoutSlots:{MyTemplate}})
        │ multi: true → 配列                            │ multi: true → 配列
        ▼                                               ▼
  DefaultConfig = deepMerge(配列...)              RootConfig = deepMerge(配列...)
        └───────────────┐           ┌───────────────────┘
                        ▼           ▼
          Config = deepMerge({}, DefaultConfig, RootConfig)   ← 後ろ(アプリ)が勝つ
                        │
                        ▼
   CmsConfig / LayoutConfig / OccConfig / RoutingConfig …(同じ 1 個を型付きで覗く窓)
                        │
                        ▼
   CmsComponentsService.getMapping(flexType) → config.cmsComponents[flexType]
   PageLayoutService → config.layoutSlots[template]
   OccEndpointsService.buildUrl → config.backend.occ.endpoints
```

## 1.4.3 ソースで確認する

**登録側**: `provideConfig` / `provideDefaultConfig` は「プロバイダ 1 個を返すだけの関数」である。
`spartacus/core-libs/core/src/config/config-providers.ts:18-27, 55-61`
```ts
export function provideConfig(config: Config = {}, defaultConfig = false): ValueProvider {
  return {
    provide: defaultConfig ? DefaultConfigChunk : ConfigChunk, // どちらの配列に入れるか
    useValue: config,                                          // 渡された設定片そのもの
    multi: true,                                               // 追記(置き換えではない)
  };
}
export function provideDefaultConfig(config: Config = {}): ValueProvider {
  return { provide: DefaultConfigChunk, useValue: config, multi: true };
}
```

**合成側**: 配列を `deepMerge` で畳み込む。
`spartacus/core-libs/core/src/config/config-tokens.ts:10-47`
```ts
export function configFactory() {
  // 既定 → アプリ の順に重ねる。同じキーはアプリが勝つ
  return deepMerge({}, inject(DefaultConfig), inject(RootConfig));
}
@Injectable({ providedIn: 'root', useFactory: configFactory })
export abstract class Config {}            // ← 各サービスが constructor で受け取るのはこれ

export function defaultConfigFactory() {
  // DefaultConfigChunk を「配列として」注入し、全部重ねる
  return deepMerge({}, ...(inject(DefaultConfigChunk, { optional: true }) ?? []));
}
export function rootConfigFactory() {
  return deepMerge({}, ...(inject(ConfigChunk, { optional: true }) ?? []));
}
```

## 1.4.4 具体例: Paragraph を自作コンポーネントに差し替える

**(1) ライブラリが既定を登録する**(`spartacus/core-libs/storefront/cms-components/content/paragraph/paragraph.module.ts:21-32`)
```ts
provideDefaultConfig(<CmsConfig>{
  cmsComponents: {
    CMSParagraphComponent:    { component: ParagraphComponent },
    CMSTabParagraphComponent: { component: ParagraphComponent },
  },
}),
```

**(2) アプリが 1 キーだけ上書きする**(`spartacus-configuration.module.ts` の `providers` に追加)
```ts
provideConfig(<CmsConfig>{
  cmsComponents: {
    CMSParagraphComponent: { component: MyParagraphComponent },
  },
}),
```

**(3) 起動時に `Config` に合成された結果**(`cmsComponents` の部分だけ抜粋)
```jsonc
{
  "cmsComponents": {
    "CMSParagraphComponent":    { "component": MyParagraphComponent },  // アプリが勝った
    "CMSTabParagraphComponent": { "component": ParagraphComponent }     // 触っていないので既定のまま
    // ... BannerModule など他ライブラリが登録した数十キーもここに同居
  }
}
```

**(4) 描画時に読まれる**(`spartacus/core-libs/storefront/cms-structure/services/cms-components.service.ts:165-168`)
```ts
getMapping(componentType: string): CmsComponentMapping {
  const componentConfig =
    this.mappings[componentType] ??
    (this.staticCmsConfig ?? this.config.cmsComponents)?.[componentType];
```
OCC が返した `typeCode`(= `flexType`)`"CMSParagraphComponent"` をキーにこの表を引き、`MyParagraphComponent` を生成する(3 章)。**キーは OCC の `typeCode` 文字列そのもの**なので、バックエンド側が決めた型名をフロントに正確に伝えることが最重要になる。

## 1.4.5 `deepMerge` のルール(ここを知らないと事故る)

`spartacus/core-libs/core/src/config/utils/deep-merge.ts:7-9, 31-48`

| 値の種類 | 挙動 | 例 |
|---|---|---|
| オブジェクト同士 | **キー単位で再帰的に重ねる** | `cmsComponents` は既定の数十キーにアプリのキーが追加・上書きされる |
| 文字列・数値・真偽・クラス参照 | 後勝ちで置き換え | `component: MyParagraphComponent` |
| **配列** | `isObject` が `false` のため**丸ごと置き換え** | `layoutSlots.X.slots: [...]` を一部だけ足すつもりで書くと、既定の要素が消える。既定を含めて全部書く |

合成の順番は `default → 遅延モジュールの default → 遅延モジュールの config → root(アプリ)` で固定されており(`spartacus/core-libs/core/src/config/services/configuration.service.ts:92-98`)、**どんな順序でモジュールを import してもアプリの `provideConfig` が最後に勝つ**。

## 1.4.6 `CmsConfig` / `LayoutConfig` などは「同じ 1 個を覗く窓」

`spartacus/core-libs/core/src/routing/configurable-routes/config/routing-config.ts:22-27`
```ts
@Injectable({ providedIn: 'root', useExisting: Config })  // RoutingConfig を要求されたら Config と同じ実体を渡す
export abstract class RoutingConfig {
  routing?: RoutingConfigDefinition;                      // Config のうち routing キーだけを型で見せる
}
```
`CmsConfig`, `LayoutConfig`, `OccConfig`, `StateConfig` も同じ形である。つまり実体は常に 1 個の合成済みオブジェクトで、クラス名の違いは「TypeScript 上でどのキーを見せるか」の違いでしかない。サービスが `constructor(protected config: CmsConfig)` と書いていても、受け取っているのは `Config` そのものである。

## 1.4.7 バックエンド担当者にとっての意味

- フロントへの依頼は「`spartacus-configuration.module.ts` の `providers` に `provideConfig({...})` を追加」という粒度で書ける。既存ライブラリの変更は不要。
- 上書きの単位は**キー 1 つ**。`cmsComponents` に新しい `typeCode` を足しても、既存の数十キーは影響を受けない。
- 配列を含む設定(`layoutSlots` の `slots`、`routing` の `paths` など)は丸ごと置換なので、「追加」ではなく「全部を書いた完成形」を依頼書に載せる。

---

[目次](README.md) | ← [1.3 アプリの骨格(利用者が持つコード)](01-3-app-skeleton.md) | [1.5 状態管理(NgRx)と「取得済みなら取らない」の実装](01-5-ngrx-state.md) →
