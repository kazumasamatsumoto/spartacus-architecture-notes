# 10. OCC リソース一覧: カスタムをどのリソースの中で考えるか

> **図**: 04 バックエンド判断フロー(`diagrams/spartacus-architecture.drawio`)。判断木の ①〜④ は「どのリソースに置くか」の問いであり、本章の一覧表がその選択肢になる

![04 バックエンド判断フロー](diagrams/page4.png)

> **根拠の範囲**: URL パターンと設定ファイルは Spartacus のソース(各 `default-occ-*-config.ts`)から収集した 45 ファイル分の実値。対応する ItemType 名は SAP Commerce の標準型システムの一般知識であり、本リポジトリの範囲では検証できないため、Backoffice の「型」検索で確認すること。

## 10.1 考え方: カスタムコンポーネントは「`cms/components` の 1 件」として既に公開されている

OCC のリソースは 3 層に分かれる。

```
A. サイト設定層   basesites / languages / currencies / countries …
B. CMS 層         cms/pages → cms/components/{uid}      ← カスタム CMS コンポーネントはここに自動で現れる
C. 業務データ層   products / carts / orders / users / stores …  ← コンポーネントが参照する「もの」
```

- B 層の `cms/components/{uid}` は **AbstractCMSComponent の全サブタイプ**を返す汎用リソースである。items.xml に新しい型を足せば、`typeCode` と属性が `cms/pages` / `cms/components` から返る(8.2)。**カスタムコンポーネントのために新しい URL は要らない**。
- カスタムコンポーネントが業務データを表示するなら、その業務データは C 層のどのリソースに属するかを決め、CMS 属性には参照 ID(商品コード、店舗 ID など)だけを持たせる(8.1 ②)。
- C 層に該当リソースが無い概念だけが、新しいリソースの設計対象になる(8.1 ④、8.3)。

したがって「カスタムを考える単位」は次の順である: **まず B 層(属性で済むか)→ 次に C 層の既存リソース(参照 ID で済むか / DTO 拡張で済むか)→ 最後に C 層の新リソース**。

## 10.2 リソース一覧

URL の先頭には共通で `{baseUrl}/occ/v2/{baseSiteId}/` が付く(`spartacus/core-libs/core/src/occ/config/default-occ-config.ts` の `prefix: '/occ/v2/'`)。`users/${userId}` の `userId` は `current`(ログイン済み)または `anonymous` を Spartacus が自動で補う(7.3)。

### A. サイト設定層(読み取り専用。カスタムの対象になることはまれ)

| URL パターン | 対応 ItemType | Spartacus の設定箇所 | カスタムの置き場所 |
|---|---|---|---|
| `basesites` | BaseSite | `core-libs/core/src/occ/adapters/site-context/default-occ-site-context-config.ts:21` | 無し(サイト固有の値は CMS 属性か別リソースへ) |
| `languages`, `currencies` | Language, Currency | 同 `:13-14` | 無し |
| `countries`, `countries/{isoCode}/regions`, `regions/{regionId}/cities`, `cities/{cityId}/districts` | Country, Region, City, District | 同ファイル | 無し |
| `titles` | Title | `feature-libs/user/profile/occ/adapters/config/default-occ-user-profile-endpoint.config.ts` | 無し |
| `cardtypes` | CreditCardType | `feature-libs/checkout/base/occ/config/default-occ-checkout-config.ts:17` | 無し |

### B. CMS 層(カスタム CMS コンポーネントはここ)

| URL パターン | 対応 ItemType | Spartacus の設定箇所 | カスタムの置き場所 |
|---|---|---|---|
| `users/{userId}/cms/pages`(`pageType`, `code`, `pageLabelOrId` で指定) | AbstractPage(ContentPage / ProductPage / CategoryPage / CatalogPage) | `core-libs/core/src/cms/config/default-cms-config.ts:15` | ページテンプレート・スロット・コンポーネント配置。**コードではなく Backoffice / ImpEx** |
| `users/{userId}/cms/pages/{id}` | 同上 | 同 `:16` | 同上 |
| `users/{userId}/cms/components?componentIds=a,b,c` | AbstractCMSComponent の全サブタイプ | 同 `:14` | **items.xml の新しいコンポーネント型 + 属性**。OCC が自動公開(8.2 の出力規則) |
| `users/{userId}/cms/components/{id}` | 同上 | 同 `:13` | 同上 |

### C. 業務データ層(コンポーネントが参照する「もの」)

**C-1 商品カタログ**

| URL パターン | 対応 ItemType | Spartacus の設定箇所 | カスタムの置き場所 |
|---|---|---|---|
| `products/{productCode}?fields=...`(`details` / `list` / `price` / `stock` / `attributes` などのスコープ別) | Product(とその VariantProduct 系) | `core-libs/core/src/occ/adapters/product/default-occ-product-config.ts:16-27` | **商品に属性を足す**なら `ProductWsDTO` 拡張 + `fields` レベル追加(8.1 ③)。FE は `ProductScope` に新スコープを足すか既存スコープの `fields` を上書き |
| `products/search?query=...`, `categories/{categoryCode}/products`, `products/suggestions` | Product の検索結果(Solr) | 同 `:37-49` | 検索結果に項目を足すなら Solr インデックス + `ProductWsDTO`。ファセット追加も同様 |
| `products/{productCode}/reviews` | CustomerReview | 同 `:31` | レビューに属性追加なら `ReviewWsDTO` 拡張 |
| `products/{productCode}/references?referenceType=...` | ProductReference | 同 `:36` | 新しい参照種別は enum 追加のみ |
| `products/{productCode}/stock`, `products/{productCode}/stock/{storeName}` | StockLevel | `feature-libs/pickup-in-store/occ/adapters/default-occ-stock-config.ts` | 在庫表示の拡張はここ |
| `orgProducts/{productCode}`(B2B 数量別価格) | PriceRow | `feature-libs/product/bulk-pricing/occ/config/default-occ-bulk-pricing-config.ts` | — |
| `products/{productCode}/configurators/...`, `ccpconfigurator/{configId}`, `cpqconfigurator/{configurationId}` | 製品コンフィグレータ(別アドオン) | `feature-libs/product-configurator/**/default-occ-configurator-*-config.ts` | — |

**C-2 ユーザー(顧客)**

| URL パターン | 対応 ItemType | Spartacus の設定箇所 | カスタムの置き場所 |
|---|---|---|---|
| `users/{userId}` | Customer(User) | `feature-libs/user/account/occ/adapters/config/default-occ-user-account-endpoint.config.ts` | **顧客に属性を足す**なら `UserWsDTO` 拡張(8.1 ③) |
| `users/{userId}/addresses`, `.../addresses/{addressId}`, `.../addresses/verification` | Address | `core-libs/core/src/occ/adapters/user/default-occ-user-config.ts` | 住所項目追加なら `AddressWsDTO` 拡張 |
| `users/{userId}/paymentdetails`, `.../paymentdetails/{id}` | PaymentInfo(CreditCardPaymentInfo) | 同 | — |
| `users/{userId}/consents`, `.../consenttemplates`, `users/anonymous/consenttemplates` | Consent, ConsentTemplate | 同 | 同意種別は ConsentTemplate のデータ追加のみ |
| `users/{userId}/customercoupons`, `.../customercoupons/{code}/claim`, `.../notification` | CustomerCoupon | 同 | — |
| `users/{userId}/notificationpreferences`, `users/{userId}/productinterests` | NotificationPreference, ProductInterest | 同 | — |
| `users/{userId}/wishlists`, `.../wishlists/{id}/entries` | Wishlist(実装により Cart 型。要確認) | `feature-libs/user/wishlist/occ/adapters/config/default-occ-user-wishlist-endpoint.config.ts` | — |
| `users/{userId}/tickets`, `.../tickets/{id}/events`, `/ticketCategories` | CsTicket, CsTicketEvent | `feature-libs/customer-ticketing/occ/config/default-occ-customer-ticketing-config.ts` | 問い合わせ項目追加なら `TicketWsDTO` 拡張 |
| `users/{userId}/futureStocks`, `users/{userId}/futureStocks/{productCode}` | FutureStock | `feature-libs/product/future-stock/occ/config/default-occ-future-stock.config.ts` | — |

**C-3 カート / チェックアウト**

| URL パターン | 対応 ItemType | Spartacus の設定箇所 | カスタムの置き場所 |
|---|---|---|---|
| `users/{userId}/carts`, `users/{userId}/carts/{cartId}?fields=...` | Cart | `feature-libs/cart/base/occ/config/default-occ-cart-config-factory.ts:17-33` | **カートに属性を足す**なら `CartWsDTO` 拡張 + `fields`(8.1 ③) |
| `users/{userId}/carts/{cartId}/entries`, `.../entries/{entryNumber}` | CartEntry(AbstractOrderEntry) | 同 | 明細に属性を足すなら `OrderEntryWsDTO` 拡張 |
| `.../carts/{cartId}/vouchers`, `.../applyVoucher`, `.../removeVoucher` | Voucher | 同 | — |
| `.../carts/{cartId}/email`, `.../guestuser`, `.../accessCode`, `.../validate` | Cart の操作 | 同 | — |
| `.../carts/{cartId}/addresses/delivery`, `.../addresses/billing`, `.../deliverymodes`, `.../deliverymode`, `.../paymentdetails`, `.../payment/sop/*` | Address, DeliveryMode, PaymentInfo | `feature-libs/checkout/base/occ/config/default-occ-checkout-config.ts:9-31` | 配送・支払の選択肢追加は DeliveryMode / PaymentMode のデータ追加 |
| `.../carts/{cartId}/costcenter`, `.../paymenttype`(B2B) | B2BCostCenter, PaymentType | `feature-libs/checkout/b2b/occ/config/default-occ-checkout-b2b-config.ts` | — |
| `.../carts/{cartId}/requestedretrievaldate`, `.../serviceOrder/*`, `.../giftCards`, `.../paymentOption` | 各アドオンの拡張 | `feature-libs/requested-delivery-date`, `integration-libs/s4-service`, `integration-libs/opf` | **既存リソース(カート)の下にサブリソースを足した実例**。自社拡張の URL 設計はこれに倣う |

**C-4 注文**

| URL パターン | 対応 ItemType | Spartacus の設定箇所 | カスタムの置き場所 |
|---|---|---|---|
| `users/{userId}/orders`, `users/{userId}/orders/{orderId}?fields=FULL` | Order | `feature-libs/order/occ/config/default-occ-order-config.ts:13-14` | **注文に属性を足す**なら `OrderWsDTO` 拡張 + `fields` |
| `.../orders/{orderId}/cancellation`, `.../orders/{orderCode}/consignments/{code}/tracking` | OrderCancelRequest, Consignment | 同 | — |
| `users/{userId}/orderReturns`, `.../orderReturns/{code}` | ReturnRequest | 同 | — |
| `users/{userId}/replenishmentOrders`, `.../replenishmentOrders/{code}/orders` | ReplenishmentOrder(B2B) | 同 | — |
| `.../orders/{orderId}/invoices`, `.../invoices/{id}/download`, `.../orders/{orderId}/attachments` | Invoice, 添付ファイル | `feature-libs/pdf-invoices`, order config | ファイル返却の実例(バイナリは `/download` サブリソース) |

**C-5 店舗**

| URL パターン | 対応 ItemType | Spartacus の設定箇所 | カスタムの置き場所 |
|---|---|---|---|
| `stores?query=...&latitude=...`, `stores/{storeId}`, `stores/storescounts` | PointOfService | `feature-libs/storefinder/occ/adapters/default-occ-store-finder-config.ts`, `feature-libs/pickup-in-store/occ/adapters/default-occ-pickup-location-config.ts` | **店舗に属性を足す**なら `PointOfServiceWsDTO` 拡張 |

**C-6 B2B 組織(B2B サイトのみ)**

| URL パターン | 対応 ItemType | Spartacus の設定箇所 |
|---|---|---|
| `users/{userId}/orgUnits`, `.../orgUnits/{id}`, `.../orgUnits/{id}/addresses`, `.../availableOrgUnitNodes`, `.../orgUnitsRootNodeTree` | B2BUnit | `feature-libs/organization/administration/occ/config/default-occ-organization-config.ts` |
| `users/{userId}/orgCustomers`, `.../orgCustomers/{id}/roles`, `.../approvers`, `.../permissions`, `.../orgUserGroups` | B2BCustomer | 同 |
| `users/{userId}/budgets`, `/costcenters`, `/costcenters/{code}/budgets` | B2BBudget, B2BCostCenter | 同 |
| `users/{userId}/orderApprovalPermissions`, `/orderApprovalPermissionTypes`, `users/{userId}/orderapprovals`, `.../decision` | B2BPermission, 注文承認 | 同 |
| `users/{userId}/orgUnitUserGroups`, `.../members` | B2BUserGroup | 同 |
| `users/{userId}/quotes`, `.../quotes/{code}/action`, `.../comments`, `.../discounts` | Quote | `feature-libs/quote/occ/config/default-occ-quote-config.ts` |
| `users/{userId}/orgUnits/{id}/accountSummary`, `.../orgDocuments` | 口座サマリ(B2B アドオン) | `feature-libs/organization/account-summary/occ/config/default-occ-account-summary-config.ts` |
| `/orgUsers`(登録) | B2BCustomer | `feature-libs/organization/user-registration/occ/config/default-occ-organization-config.ts` |

### D. OCC 以外の Web サービス(参考)

`/assistedservicewebservices/...`(ASM)、`punchout/sessions/{id}`、`users/{userId}/subscriptions`(Subscription Billing)などは、別の拡張モジュールが提供する Web サービスで、OCC の `prefix` を持たない絶対パスで設定されている(`integration-libs/**/default-occ-*-config.ts`)。自社で **OCC とは別の独立 Web アプリ**を立てる場合の前例になる。

## 10.3 置き場所の決め方(例 3 つ)

| 要件 | どのリソースか | 判断 | バックエンドの作業 | フロントの作業 |
|---|---|---|---|---|
| 「店舗ごとのおすすめ商品バナー」を CMS で配置したい | B 層(コンポーネント)+ C-1(商品)+ C-5(店舗) | 8.1 ①②: 既存リソースで足りる | items.xml に `StoreRecommendationComponent`(属性: `storeCode`, `productCodes`)を追加。**コントローラ不要** | `provideConfig` で `cmsComponents` に追加、`ProductService` / 店舗 Facade で取得(5 章、7 章) |
| 商品詳細に「産地」「認証マーク」を出したい | C-1(商品) | 8.1 ③: 既存リソースに属性を足す | Product に属性追加、`ProductWsDTO` + Populator 拡張、`fields` レベル `DEFAULT` または新レベルに追加 | `Product` モデル拡張 + `ProductScope` の `fields` に項目追加、Normalizer は不要なことが多い |
| 「キャンペーン応募状況」を表示したい(既存の型に相当するものが無い) | C 層に新リソース | 8.1 ④ | 新 ItemType `CampaignEntry`、`users/{userId}/campaignEntries` と `.../campaignEntries/{code}` のコントローラ + `CampaignEntryWsDTO`(8.3 の設計ルール) | 7.4 の一式(Facade / Connector / Adapter / Normalizer / endpoints 設定) |

## 10.4 新リソースの URL を切るときのルール(既存パターンから帰納)

1. **名詞の複数形・小文字**: `products`, `carts`, `orders`, `stores`, `tickets`。コンポーネント名や画面名を URL にしない。
2. **ユーザー固有なら `users/{userId}/` の下**、全員共通なら直下: `users/{userId}/orders` と `products/{code}` の対比。Spartacus が `userId` を自動で埋めるのは `users/${userId}` パターンだけ(7.3)。
3. **親子関係はパスで表す**: `products/{code}/reviews`、`carts/{cartId}/entries/{entryNumber}`、`orders/{id}/consignments/{code}/tracking`。
4. **状態遷移はサブリソース名で**: `orders/{id}/cancellation`、`quotes/{code}/action`、`carts/{cartId}/validate`。動詞の URL(`/cancelOrder`)は既存 OCC にも少数あるが新設では避ける。
5. **フィールド選択は `fields` パラメータ**(`BASIC` / `DEFAULT` / `FULL` と個別指定)で、URL を増やさない。Spartacus は同じ URL の `fields` を結合して 1 リクエストにまとめる(4.2 (k))。
6. **ファイルは `/download` または `/attachments/{id}`** のサブリソースで返す(注文の請求書、チケットの添付の実例)。

---

[目次](README.md) | ← [9. JSP(アクセラレータ)のコンポーネントコントローラをヘッドレスに移すとき、何を返すか](09-jsp-to-headless.md) | [11. フロント側の呼び出し方法はリソースごとに違うのか](11-frontend-call-patterns.md) →
