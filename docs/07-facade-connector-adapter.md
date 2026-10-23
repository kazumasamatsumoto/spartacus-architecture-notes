# 7. 業務データを扱うカスタムコンポーネント: Facade / Connector / Adapter の作り方

> **図**: 03 カスタムコンポーネントのデータ経路(`diagrams/spartacus-architecture.drawio`)。本章が扱うのは右の経路 B(Facade → Query/Store → Connector → Adapter → Normalizer → OCC)

![03 カスタムコンポーネントのデータ経路](diagrams/page3.png)


5 章は「CMS 属性だけで完結するコンポーネント」だった。商品・在庫・会員情報・外部システムのデータなど**バックオフィスで編集しない動的データ**を表示するコンポーネントでは、Spartacus の階層に沿ってフロント側に 5〜6 ファイルを追加する。図は `docs/diagrams/spartacus-architecture.drawio` の「03 カスタムコンポーネントのデータ経路」。

### 7.1 原則(リポジトリ同梱ガイド)

`spartacus/core-libs/skills/skills/spartacus-developer/references/backend-communication.md:5-16`
> NEVER inject `HttpClient` in components or services. All backend communication goes through a layered pipeline: `Component → Facade → state layer → Connector → Adapter → Converter`. … Only **Adapters** use `HttpClient`.
> Facade — Public API consumed by components. / Connector — Thin delegation layer injecting the abstract Adapter. / Adapter — Abstract class in `connectors/`, OCC implementation in `occ/adapters/`. This is the ONLY layer that uses `HttpClient`. / Converter — Normalizers (backend→UI) and Serializers (UI→backend) are registered as `multi: true` providers on typed `InjectionToken`s.

同 `:20`: 「NEVER hardcode endpoint URLs. Configure them via `provideConfig`」。

### 7.2 各層の実物(`feature-libs/user/account` を例に)

標準ライブラリは 1 機能を `root` / `core` / `occ` / `components` の 4 エントリポイントに分ける(`spartacus/tsconfig.json:49-64` のパスマッピング、各ディレクトリの `ng-package.json`)。

| 層 | 置き場所 | 役割 | 実物 |
|---|---|---|---|
| Facade(抽象) | `root/facade/` | コンポーネントが使う公開 API。DI トークン兼契約。遅延ロード前はプロキシ | `feature-libs/user/account/root/facade/user-account.facade.ts:13-25` |
| Facade 実装 | `core/facade/` | 状態層(Query/Command または NgRx)。Connector を呼ぶ | `core/facade/user-account.service.ts:24-56` |
| Connector | `core/connectors/` | 機能向けの薄い委譲。Adapter 抽象を注入 | `core/connectors/user-account.connector.ts:16-29` |
| Adapter(抽象) | `core/connectors/` | バックエンド契約。OCC 以外にも差し替え可能 | `core/connectors/user-account.adapter.ts:14-20` |
| OCC Adapter | `occ/adapters/` | **唯一 `HttpClient` を使う層**。URL 組み立てと Normalizer 適用 | `occ/adapters/occ-user-account.adapter.ts:34-52` |
| エンドポイント設定 | `occ/adapters/config/` | `backend.occ.endpoints` に URL テンプレート | `occ/adapters/config/default-occ-user-account-endpoint.config.ts:9-18` |
| Converter / Normalizer | `occ/converters/` + `core/connectors/converters.ts` | OCC DTO → FE モデル | `feature-libs/organization/order-approval/occ/converters/occ-order-approval-normalizer.ts:12-29` |
| 配線 | `core/*-core.module.ts`, `occ/*-occ.module.ts`, `root/*-root.module.ts` | providers の束ね | `core/user-account-core.module.ts:11-14`, `occ/user-account-occ.module.ts:13-19` |

**Facade(抽象)** `spartacus/feature-libs/user/account/root/facade/user-account.facade.ts:13-25`
```ts
@Injectable({
  providedIn: 'root',
  useFactory: () =>
    facadeFactory({
      facade: UserAccountFacade,
      feature: USER_ACCOUNT_CORE_FEATURE,
      methods: ['get', 'getById'],
    }),
})
export abstract class UserAccountFacade {
  abstract get(): Observable<User | undefined>;
  abstract getById(userId: string): Observable<User | undefined>;
}
```
`facadeFactory` は「最初のメソッド呼び出し時に機能チャンクを遅延ロードし、その中の実装へ転送するプロキシ」を作る(`core-libs/core/src/lazy-loading/facade-factory/facade-factory.ts:11-24`, `facade-factory.service.ts:110-131`)。NgRx を使う機能は `async: true` を付ける(`feature-libs/storefinder/root/facade/store-finder.facade.ts:21-43`)。

**Facade 実装(Query パターン)** `spartacus/feature-libs/user/account/core/facade/user-account.service.ts:24-56`
```ts
@Injectable()
export class UserAccountService implements UserAccountFacade {
  protected userQuery: Query<User> = this.query.create(
    () =>
      this.userIdService
        .takeUserId(true)
        .pipe(switchMap((userId) => this.userAccountConnector.get(userId))),
    {
      reloadOn: [UserAccountChangedEvent],
      resetOn: [LoginEvent, LogoutEvent],
    }
  );
  ...
  get(): Observable<User | undefined> {
    return this.userQuery.get();
  }
}
```
`QueryService.create`(`core-libs/core/src/util/command-query/query.service.ts:31-60, 77-103`)は `loading / error / data` を保持し、購読中は 1 回しかロードしない。`reloadOn` は data を保ったまま再取得、`resetOn` は初期状態へ戻す。新規機能ではこの Query/Command が推奨で、NgRx は旧来機能に合わせる場合に使う(`backend-communication.md:5-11`)。書き込みは `CommandService`(`command.service.ts:27-53`、既定戦略 Queue)。

**Connector と Adapter 抽象** `spartacus/feature-libs/user/account/core/connectors/user-account.connector.ts:16-29`, `user-account.adapter.ts:14-20`
```ts
@Injectable()
export class UserAccountConnector {
  constructor(protected adapter: UserAccountAdapter) {}
  get(userId: string): Observable<User> {
    return this.adapter.load(userId);
  }
}
export abstract class UserAccountAdapter {
  abstract load(userId: string): Observable<User>;
}
```

**OCC Adapter** `spartacus/feature-libs/user/account/occ/adapters/occ-user-account.adapter.ts:34-52`
```ts
@Injectable()
export class OccUserAccountAdapter implements UserAccountAdapter {
  protected logger = inject(LoggerService);
  constructor(
    protected http: HttpClient,
    protected occEndpoints: OccEndpointsService,
    protected converter: ConverterService
  ) {}
  load(userId: string): Observable<User> {
    const url = this.occEndpoints.buildUrl('user', { urlParams: { userId } });
    return this.http.get<Occ.User>(url).pipe(
      catchError((error) => {
        throw tryNormalizeHttpError(error, this.logger);
      }),
      this.converter.pipeable(USER_ACCOUNT_NORMALIZER)
    );
  }
```

**エンドポイント設定と型拡張** `occ/adapters/config/default-occ-user-account-endpoint.config.ts:9-18`, `occ-user-account-endpoint.model.ts:9-22`
```ts
export const defaultOccUserAccountConfig: OccConfig = {
  backend: { occ: { endpoints: {
    user: 'users/${userId}',
    createVerificationToken: 'users/anonymous/verificationToken',
  } } },
};
declare module '@spartacus/core' {
  interface OccEndpoints extends UserAccountOccEndpoints {}
}
```
`OccEndpointsService.buildUrl`(`core-libs/core/src/occ/services/occ-endpoints.service.ts:86-150`)は `baseUrl + prefix + 現在の baseSite + endpoint` を組み立て、`${userId}` などを `urlParams` で埋め、`queryParams` を結合する。**`baseSiteId` はプレースホルダではなく `getBaseUrl()` がパスとして前置する**(同 `:233-238`)。

**Normalizer** `spartacus/feature-libs/organization/order-approval/occ/converters/occ-order-approval-normalizer.ts:12-29` と登録 `order-approval-occ.module.ts:24-36`
```ts
@Injectable({ providedIn: 'root' })
export class OccOrderApprovalNormalizer implements Converter<Occ.OrderApproval, OrderApproval> {
  convert(source: Occ.OrderApproval, target?: OrderApproval): OrderApproval {
    if (target === undefined) {
      target = { ...(source as any) } as OrderApproval;
    }
    if (source.order) {
      target.order = this.converter.convert(source.order, ORDER_NORMALIZER);
    }
    return target;
  }
}
...
providers: [
  provideDefaultConfig(defaultOccOrderApprovalConfig),
  { provide: OrderApprovalAdapter, useClass: OccOrderApprovalAdapter },
  { provide: ORDER_APPROVAL_NORMALIZER, useExisting: OccOrderApprovalNormalizer, multi: true },
```
`ConverterService.pipeable`(`core-libs/core/src/util/converter.service.ts:77-88, 130-137`)は登録された Normalizer を順に reduce し、未登録なら素通しする。**`multi: true` を忘れると既存の変換チェーンを丸ごと置き換えてしまう**(`normalizers.md:5-7`)。

**配線** `core/facade/facade-providers.ts:15-26`, `core/user-account-core.module.ts:11-14`, `occ/user-account-occ.module.ts:13-19`
```ts
export const facadeProviders: Provider[] = [
  UserAccountService,
  { provide: UserAccountFacade, useExisting: UserAccountService },
];
@NgModule({ providers: [UserAccountConnector, ...facadeProviders] })
export class UserAccountCoreModule {}
@NgModule({ providers: [
  provideDefaultConfig(defaultOccUserAccountConfig),
  { provide: UserAccountAdapter, useClass: OccUserAccountAdapter },
] })
export class UserAccountOccModule {}
```

**コンポーネントから使う** `components/login/login.component.ts:34-54` は `UserAccountFacade` を注入し `this.userAccount.get()` を購読するだけ。

### 7.3 HTTP リクエストに自動で付くもの(バックエンドが前提にできること)

`OccEndpointsService.buildUrl` で作った URL(= OCC の baseUrl 配下)に対してのみ、インターセプタが次を付与する。手組みの URL には付かない。

| 付与されるもの | 根拠 |
|---|---|
| クエリ `lang`, `curr` | `core-libs/core/src/occ/adapters/site-context/site-context.interceptor.ts:54-68` |
| `Authorization: Bearer <token>`(ログイン時。`basesites` は除外) | `core-libs/core/src/auth/user-auth/services/auth-http-header.service.ts:179-207, 220-226` |
| 401 時のトークン更新とリトライ | `auth.interceptor.ts:54-73` |
| `userId` の値は `'current'`(ログイン中)か `'anonymous'` | `core-libs/core/src/occ/utils/occ-user-ids.ts:7-8` |

エラー応答は OCC 標準の `{ "errors": [ { "type", "message", "reason", "subject", "subjectType" } ] }` が期待されている(`core-libs/core/src/util/try-normalize-http-error.ts:36-50` が `error.error.errors` 配列を `HttpErrorModel.details` に写す。DTO 型は `occ.models.ts:104-125` の `Occ.ErrorModel`)。

### 7.4 カスタム機能で追加するファイル一覧(雛形)

```
my-promo/
  root/
    feature-name.ts            export const MY_PROMO_FEATURE = 'myPromo';
    facade/my-promo.facade.ts  abstract class MyPromoFacade (facadeFactory)
    model/my-promo.model.ts    interface MyPromo { id; title; discountRate; ... }
    my-promo-root.module.ts    provideDefaultConfig({ featureModules: { myPromo: { cmsComponents: ['MyPromoBannerComponent'] } } })
  core/
    connectors/my-promo.adapter.ts     abstract class MyPromoAdapter { abstract load(userId, promoId): Observable<MyPromo> }
    connectors/my-promo.connector.ts   @Injectable() class MyPromoConnector
    connectors/converters.ts           export const MY_PROMO_NORMALIZER = new InjectionToken<Converter<Occ.MyPromo, MyPromo>>('MyPromoNormalizer')
    facade/my-promo.service.ts         QueryService で MyPromoFacade を実装
    my-promo-core.module.ts
  occ/
    model/occ-my-promo.models.ts       Occ 側 DTO 型 + declare module '@spartacus/core' { interface OccEndpoints { myPromo?: string } }
    adapters/default-occ-my-promo-config.ts   endpoints: { myPromo: 'users/${userId}/my-promos/${promoId}?fields=DEFAULT' }
    adapters/occ-my-promo.adapter.ts   buildUrl + http.get + tryNormalizeHttpError + converter.pipeable(MY_PROMO_NORMALIZER)
    converters/occ-my-promo-normalizer.ts
    my-promo-occ.module.ts
  components/
    my-promo-banner/my-promo-banner.component.ts   inject(CmsComponentData) で promoId を読み、inject(MyPromoFacade).get(promoId)
    my-promo-components.module.ts      provideDefaultConfig({ cmsComponents: { MyPromoBannerComponent: { component: MyPromoBannerComponent } } })
  my-promo.module.ts                   imports: [Core, Occ, Components]
アプリ側: provideConfig({ featureModules: { myPromo: { module: () => import('./my-promo.module').then(m => m.MyPromoModule) } } })
```

コンポーネント内の典型的な結線(CMS 属性 → 業務データ):
```ts
export class MyPromoBannerComponent {
  protected cms = inject<CmsComponentData<CmsMyPromoBannerComponent>>(CmsComponentData);
  protected promo = inject(MyPromoFacade);
  promo$ = this.cms.data$.pipe(
    map((d) => d.promoId),
    filter(Boolean),
    distinctUntilChanged(),
    switchMap((id) => this.promo.get(id))
  );
}
```
これは `ProductCarouselComponent` が `productCodes` を読んで `ProductSearchByCodeService.get` を呼ぶのと同じ形(5.6)。


---

[目次](README.md) | ← [6. バックエンド側のチェックリスト](06-backend-checklist.md) | [8. バックエンド(Java)側: 何を、どの単位で返すか](08-backend-api-granularity.md) →
