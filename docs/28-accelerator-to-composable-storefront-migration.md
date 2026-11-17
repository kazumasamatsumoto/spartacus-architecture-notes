# 28. 動いている hybris(アクセラレータ)サイトを Composable Storefront へ移行する作業手順

> **図**: 27 アクセラレータからの移行手順(`diagrams/spartacus-architecture.drawio`)。左: 新規開発と移行で作業の向きが逆になること。中: 段階 0〜7。右: 同じバックエンドに 2 つのサイトを並べたデモの実測

![27 アクセラレータからの移行手順](diagrams/page27.png)

> **この章が答える問い**: 新しい部品はバックオフィス(型と CMS)から作る、という流れはよく聞く。では、いまアクセラレータ(JSP)で動いているサイトを Composable Storefront へ移すときは、何をどの順番でやればいいか

> **位置づけ**: 新しく作る部品 1 つの手順は 11 章(フロントへの依頼書)・14 章(バックエンドのチェックリスト)・24 章(バックエンドの書き方)にある。この章は、すでにある画面・CMS・URL・ロジックをまとめて移すときの全体の順番を扱う。各段階の中身は既存の章(13・22〜27 章)へ案内する

> **根拠の取り方**:
> - **Spartacus のソース**: `spartacus/` の `b7b028f`(2612.0.0)。パスは `spartacus/` からの相対
> - **CCv2 の構成**: SAP の公開サンプル [SAP-samples/cloud-commerce-sample-setup](https://github.com/SAP-samples/cloud-commerce-sample-setup) の `546fe5b`(`ccs/` と略す)
> - **同じバックエンドでのアクセラレータ用 CMS と Spartacus 用 CMS の違い**: デモ OCC の `electronics`(アクセラレータ用)と `electronics-spa`(Spartacus 用)を、27 章の [`tools/cms-page-coverage.py`](../tools/cms-page-coverage.py) で同じ 14 ページずつ比べた(2026-11-17 実測)
> - **SAP Commerce 本体のソースと help.sap.com は読めない**。アクセラレータ側の中の動き、CCv2 の細部は「要確認」と書く。手順の分け方は、上の根拠から組み立てた筆者の整理

---

### 先に話し言葉で: 新規は「作る順」、移行は「測ってから差分を作る順」

新しい部品は、型(`items.xml`)→ 中身(ImpEx・Backoffice)→ OCC で出す → フロントで描く、の順に 1 つずつ作ります。何も無いところから積むので、バックエンドが先です。

移行はこれと向きが逆です。画面も CMS も URL もロジックも、もう全部あります。だから最初の仕事は作ることではなく、**棚卸しと測定**です。今あるページを OCC から取り、Spartacus がそのまま描ける部品と描けない部品を数えます。そのうえで、足りない部分だけを作ります。

もう 1 つの違いは、**捨てるものと残すものが分かれる**ことです。残るのは Facade・Service・型・商品データ・注文データで、Spartacus もこれを OCC 経由で使います。捨てるのは storefront の Web 拡張(JSP、タグ、ページコントローラ、`web/src`)です。ヘッドレスではこれらが一度も実行されません(25 章)。CMS の中身はその中間で、多くを作り直します。

進め方としては、**同じバックエンドに Spartacus 用のサイトをもう 1 つ並べ**、アクセラレータを動かしたまま作ります。SAP のデモ OCC も、`electronics`(アクセラレータ用)と `electronics-spa`(Spartacus 用)を同じバックエンドで並べています(28.4)。

---

### 28.1 新規開発との違い

| | 新しい部品を作る(11・14・24 章) | 動いているサイトを移す(この章) |
|---|---|---|
| 出発点 | 何も無い | 画面・CMS・URL・ロジックが全部ある |
| 最初の作業 | 型を定義する(`items.xml`) | 今あるページを OCC で取り、部品のキーを数える(27.1) |
| バックエンドの仕事 | 型・ImpEx・Populator・OCC を足す | ほとんど足さない。`web/src` にあったロジックを Facade へ下ろし、足りない OCC を足す(25 章) |
| CMS | 新しい部品を 1 つ置く | ページごとに作り直す。ラベル、JSP の部品、スクリプトの部品(28.4) |
| フロント | 部品を 1 つ作って登録する | 標準の部品をそのまま使い、足りない分だけ作る(27 章) |
| 終わり方 | 部品が出たら終わり | URL を切り替え、アクセラレータの storefront 拡張を外して終わり |

---

### 28.2 全体の手順

| 段階 | やること | 成果物 | 詳しくは |
|---|---|---|---|
| 0 棚卸し | 画面と URL、CMS のページと部品、`web/src` のロジック、アドオン、外部スクリプトを一覧にする | 移行台帳 | 28.3 |
| 1 バックエンドを OCC で開く | `/occ` の Web アプリ、OAuth クライアント、CORS、Spartacus 用のベースサイト | `basesites` が新しいサイトを返す | 28.4 |
| 2 Spartacus アプリを作る | `ng add @spartacus/schematics`、ベースサイトと URL の形、CCv2 の `js-storefront/` | 空のホームが出る | 28.5 |
| 3 CMS を Spartacus 向けにする | ページのラベル、JSP の部品を Flex へ、テンプレートとスロット | `cms/pages` が全ページで 200 を返す | 28.6 |
| 4 部品を埋める | 対応の無いキーを仕分けて、作る・割り当てる・外す | 対応なしが 0 件 | 28.7 |
| 5 ロジックを移す | ページコントローラ・Validator・タグにあった処理を、Facade と OCC と Angular へ | 画面ごとの移植チケット | 28.8 |
| 6 URL と SEO | 商品・カテゴリ・コンテンツの URL、リダイレクト、SSR | 旧 URL が全部どこかに着く | 28.9 |
| 7 並行稼働と切り替え | リポジトリ、ログインとカート、SmartEdit、切り替えの単位、storefront 拡張を外す | 本番の切り替え | 28.10 |

段階 0〜2 は順番どおりに進めます。段階 3〜6 は画面ごとに回します(ホーム → 商品一覧 → 商品詳細 → カート → ログイン → チェックアウト → マイアカウント、など)。段階 7 のリポジトリの準備(26 章)は、段階 1 より前に決めておきます。

---

### 28.3 段階 0: 棚卸し

移行台帳の列は次のとおりです。1 行が 1 画面です。

| 列 | 取り方 |
|---|---|
| 画面と今の URL | storefront 拡張のページコントローラの `@RequestMapping` を grep する(25 章の grep) |
| CMS のページ | `cms/pages?pageType=ContentPage&pageLabelOrId=<ラベル>` などで取る。uid・テンプレート・ラベル |
| 部品のキーと対応の有無 | 27.1 の 2 つのスクリプト(`tools/cms-mapping-keys.js`、`tools/cms-page-coverage.py`)を、**今のアクセラレータのサイト**に向けて流す |
| `web/src` のロジック | ページコントローラ・BeforeViewHandler・Validator・タグ・EL 関数の呼び出し(25.1 の 8 つの形) |
| アドオン | `localextensions.xml` と CCv2 の `manifest.json` の `storefrontAddons`(`ccs/core-customize/manifest.json:8-17`)。アドオンの JSP 部分は Spartacus では動かない |
| 外部スクリプト | 分析タグ、同意バナー、決済のスクリプト。アクセラレータでは JSP に直書きされていることが多い |

この段階で、**同じ名前の機能が Spartacus の機能ライブラリにあるか**も見ておきます。`spartacus/feature-libs/` と `spartacus/integration-libs/` のディレクトリ名が、そのまま機能の一覧です(`asm`、`cart`、`checkout`、`order`、`organization`、`storefinder`、`smartedit`、`opf`、`cdc` など)。アドオン 1 つが、機能ライブラリ 1 つと OCC の拡張 1 つに置き換わる、というのが基本の形です。どのアドオンがどのライブラリに対応するかは、公開のソースからは確かめられませんでした。要確認です。

---

### 28.4 段階 1: バックエンドを OCC で開き、Spartacus 用のサイトを並べる

**Web アプリと拡張**: SAP の CCv2 サンプルは、1 つの環境でアクセラレータと OCC を同時に動かしています。`localextensions.xml` には次のものが並んでいます。

- **アクセラレータ**: `yacceleratorstorefront`(54 行)
- **OCC**: `commercewebservices`(78 行)、`cmsocc`(240 行)、`webservicescommons`(246 行)
- **Spartacus のサンプルデータ**: `spartacussampledata`(259 行)

`manifest.json` では、アクセラレータの Web アプリ(`accstorefront` の aspect、320 行)と、`commercewebservices` を `/occ` に載せる設定(504-505 行)が同じ環境にあります。移行中はこの形のまま進めます。

**CORS**: ブラウザが別の origin から OCC を呼ぶので、`corsfilter.commercewebservices.*` が要ります。サンプルでは `ccs/core-customize/manifest.json:446-458` に、許可する origin・ヘッダー・メソッドが並んでいます。サンプルの origin は `*` ですが、本番では Spartacus を配信する origin に絞ります。

**OAuth クライアント**: Spartacus の既定の `client_id` は `mobile_android_public` です(`core-libs/core/src/auth/user-auth/config/default-auth-config.ts:50`)。バックエンドに同じ名前のクライアントを作るか、フロントの設定を自社のクライアント名に合わせます(24.9)。

**ベースサイト**: デモ OCC の `basesites` から、`electronics` と `electronics-spa` の値を抜き出しました(2026-11-17)。

| | `electronics`(アクセラレータ用) | `electronics-spa`(Spartacus 用) |
|---|---|---|
| `urlEncodingAttributes` | `storefront`, `language` | `storefront`, `language`, `currency` |
| `urlPatterns`(抜粋) | `?site=electronics`、`electronics.` で始まるホスト | 上の 2 つに加えて `https?://[^/]+/electronics-spa(…)`、`https?://localhost(:\d+)?/?$` |
| `theme` | `alpha` | `santorini` |

Spartacus は、ベースサイトを設定に固定していないとき、起動時に `basesites` を取ります。そして**今の URL に `urlPatterns` が合うサイト**を選びます(`core-libs/core/src/site-context/config/config-loader/site-context-config-initializer.ts:100-106`)。どのサイトにも合わなければ、`Cannot get base site config!` を投げて止まります(同 67 行)。この読み込みは、`context.baseSite` を静的に設定していないときだけ動きます(`core-libs/core/src/site-context/site-context.module.ts:34-40`)。URL に何を載せるかは `urlEncodingAttributes` から決まります。OCC の `storefront` は Spartacus の `baseSite` に読み替えられます(同 initializer 80 行・111-114 行)。

つまり、Spartacus 用のサイトを新しく作るなら、**Spartacus を配信する URL に合う `urlPatterns`** を入れておかないと起動しません。既存のアクセラレータのサイトをそのまま使う場合も、パターンを足す必要があります。

**サイトを新しく作るか、既存のサイトを使うか**: デモは新しく作る形です。新しいサイトにすると、CMS(28.6)をアクセラレータと別に作り直せるので、アクセラレータを止めずに作業できます。既存のサイトに Spartacus を向けると、CMS の変更がそのままアクセラレータの画面にも効いてしまいます。新しいサイトを作る場合も、商品カタログと価格・在庫のデータは共有できます。どの型のどの属性を共有するかは、自社のサイトの構成で確かめます。

---

### 28.5 段階 2: Spartacus アプリを作る

- **アプリを作る:** `ng add @spartacus/schematics` で骨格を作ります(23.1)。そのとき聞かれる OCC の接続先、ベースサイト、URL に載せる値(`urlParameters`)は、28.4 で作ったサイトに合わせます(`core-libs/schematics/src/add-spartacus/configuration.ts:143-145`)。
- **CCv2 に載せる:** サンプルは `js-storefront/manifest.json` で、アプリごとに SSR のエントリと CSR の webroot を指定しています(`ccs/js-storefront/manifest.json:1-14`)。
- **リポジトリ:** 保守と並行する場合のリポジトリの分け方は 26 章です。

この段階の完了条件は、ホームが空のレイアウトで表示されることです。ヘッダー、フッター、スロットの枠がそろえば十分です。ここで CMS の部品が欠けていても問題ありません。

---

### 28.6 段階 3: CMS を Spartacus 向けにする(実測)

同じバックエンドの 2 つのサイトから同じページを取り、部品の中身を比べました(`fields=DEFAULT`。2026-11-17)。

| ページ | `electronics` のラベル / 部品数 / JSP / Flex | `electronics-spa` のラベル / 部品数 / JSP / Flex |
|---|---|---|
| ホーム | `homepage` / 26 / 2 / 0 | `homepage` / 33 / 0 / 6 |
| カート | `cart` / 22 / 7 / 0 | `/cart` / 37 / 0 / 20 |
| ログイン | `login` / 15 / 4 / 0 | `/login` / 22 / 0 / 7 |
| アドレス帳 | `address-book` / 14 / 2 / 0 | `/my-account/address-book` / 22 / 0 / 7 |
| プロフィール変更 | `update-profile` / 14 / 3 / 0 | `/my-account/update-profile` / 21 / 0 / 6 |
| FAQ | `/faq` / 15 / 2 / 0 | `/faq` / 22 / 0 / 5 |

この表から、作り直すものが 3 つ分かります。

1. **ページのラベル**: Spartacus は、コンテンツページを URL のパスそのまま(`/my-account/address-book` など)で取りにいきます(3 章・4 章)。アクセラレータの CMS はラベルが `address-book` です。そのため、`pageLabelOrId=/my-account/address-book` で取ると `CMSItemNotFoundError` が返ります(実測)。`/cart` や `/login` はアクセラレータ側でも取れましたが、マイアカウントの下のページは取れませんでした。ラベルを URL の形にそろえるか、Spartacus のルートの `paths` をアクセラレータのラベルに合わせるかの、どちらかが要ります。
2. **JSP の部品を Flex へ**: アクセラレータの CMS は `JspIncludeComponent` で JSP を差し込んでいます。Spartacus 用の CMS では、同じ場所が `CMSFlexComponent` になっています(上の表で JSP が 0、Flex が増えている)。Spartacus は `JspIncludeComponent` の uid をキーに引くので(27 章)、作り直さなくても描ける部品があります。ただ、対応表に無い uid もあります(28.7)。
3. **部品の数が増える**: Spartacus 用のページは部品が多くなっています。アクセラレータでは JSP 1 枚が描いていた範囲を、Spartacus では複数の部品に分けて CMS に置くからです。カートは 22 個から 37 個に増えています。

**テンプレート名はそのまま使える**: どちらのサイトでも、テンプレート名は同じでした(`LandingPage2Template`、`CartPageTemplate`、`AccountPageTemplate`、`ContentPage1Template` など)。Spartacus の `LayoutConfig` も、このテンプレート名でスロットの並びを決めています(`core-libs/storefront/recipes/config/layout-config.ts:55-130`)。アクセラレータで独自に作ったテンプレートには、`layoutSlots` を足します(22 章、M11)。

**作り直し方**: SAP は、アクセラレータの電子機器サイトに対して Spartacus 用の CMS を `spartacussampledata` として配っています。デモの `electronics-spa` はこのデータです。中身の ImpEx は公開のソースでは読めませんでした。自社のサイトでは、このサンプルのページを見本に、ImpEx で新しいサイトの CMS を作るのが近道です(書き方は 24.4)。サンプルの ImpEx の場所と中身は要確認です。

---

### 28.7 段階 4: 対応の無い部品を埋める(実測)

27 章のスクリプトを、アクセラレータ用の `electronics` の 14 ページに流しました。対象はホーム・カート・ログイン・アドレス帳・プロフィール変更・FAQ・注文履歴・支払い情報・チェックアウトのログイン・注文完了・検索結果なし・404・商品詳細・カテゴリです。Spartacus 用の `electronics-spa` の同じページとも比べました。

| | `electronics`(アクセラレータの CMS のまま) | `electronics-spa`(Spartacus 用の CMS) |
|---|---|---|
| ページに来たキー | 44 種類 | 63 種類 |
| 対応なし | 15 | 6 |
| うち `JspIncludeComponent` | 20 種類中 8 が対応なし | JSP は 0 |

`electronics` で対応の無かった 15 件は、次の 4 つに分かれます。

| 分類 | キー | Spartacus 用の CMS(`electronics-spa`)ではどうなっているか | どうするか |
|---|---|---|---|
| 全ページに出るスクリプトの部品 | `AssistedServiceComponent`、`PersonalizationScriptComponent`、`ProfileTagScriptComponent` | ASM と Personalization の部品は無い。ProfileTag は Flex の `ProfileTagComponent`(対応あり) | CMS から外し、機能ライブラリで受け持つ。ASM は `feature-libs/asm`、ProfileTag は `integration-libs/cds`(`integration-libs/cds/src/config/cds-config.ts`)。Personalization の受け手は要確認 |
| 全ページに出る同意の JSP | `AnonymousConsentManagementComponent`、`CookieNotificationComponent` | Flex の `AnonymousConsentManagementBannerComponent`・`AnonymousConsentOpenDialogComponent`(対応あり。`core-libs/storefront/cms-components/anonymous-consent-management/anonymous-consent-management.module.ts:17, 27`) | 部品を Spartacus 用のものに差し替える |
| ページ固有の JSP | `NewCustomerLoginComponent`、`OrderConfirmationContinueButtonComponent` | ログインのページは `ReturningCustomerRegisterComponent` などの Flex に置き換わっている。注文完了ページは Spartacus 用のサイトで取れず(404)、比べられなかった | 27.3 の C の手順で、既存の Angular の部品に割り当てるか、新しく作る |
| Spartacus 用の CMS でも対応が無いもの | `CheckoutComponent`、`PromotionsComponent`、`PotentialPromotionsComponent`、`ReturningCustomerCheckoutLoginComponent`、`CartSuggestionComponent`、`BundleCarouselComponent` | 同じ名前の Flex または型のまま残り、やはり対応なし(27 章の 6 件と同じ並び) | SAP のサンプルでも描かれていない。要るものだけを 27.3 の D の手順で作り、残りは CMS から外す |
| 実装の無い型 | `SaveForLaterCMSComponent`、`ChineseAccountAddressBookComponent` | 来ない | 使っていなければ CMS から外す |

`CartComponent`、`UpdateProfileComponent` など 12 件の `JspIncludeComponent` には対応がありました。Spartacus が、アクセラレータの JSP の uid と同じ名前をキーとして登録しているからです(27 章)。ただし、名前で引けても、Angular の部品が受け取るのは OCC の `CmsComponentData` だけです。JSP がサーバー側で受け取っていた値(ページコントローラが `model` に入れたもの)は来ません。見た目と動きが同じになるかは、画面ごとに確かめます(25 章)。

---

### 28.8 段階 5: ページコントローラと JSP のロジックを移す

25 章の手順を画面ごとに回します。

1. **Facade へ下ろす**: `web/src` に直接書かれたロジック(コントローラの中の計算、BeforeViewHandler の差し替え、Validator)を Facade へ移します。アクセラレータを動かしたまま変えられるので、移行の最初に保守のリリースで出せます(26 章の「upstream first」)。
2. **OCC を足す**: その Facade を OCC から呼べるようにします。`fields` の項目を足すか、新しいリソースを作ります(12 章・24.6・24.7)。応答の形は 13 章の規則に従います。ビューを返さず、State に入る形で返します。
3. **Angular に写す**: 見た目、文言、画面の一時的な状態はフロントで持ちます。ログイン必須や入力チェックは、正をバックエンドに置き、フロントには写しを置きます(25.4)。

チェックアウトと支払いは、このパターンの例外になりやすい部分です。決済代行の JSP やスクリプトは、Spartacus 用の連携ライブラリ(`integration-libs/opf`、`integration-libs/digital-payments` など)に置き換わることが多く、置き換えの単位が「画面」ではなく「決済の方式」になります(25 章の OPF の比較)。

---

### 28.9 段階 6: URL と SEO

**Spartacus の既定の URL**: 商品詳細は `product/:productCode/:name`、カテゴリは `category/:categoryCode` です(`core-libs/storefront/cms-structure/routing/default-routing-config.ts:62-72`)。アクセラレータとは形が違います。

**アクセラレータ形式の URL も受け付ける**: Spartacus は、設定の `paths` に加えて、`**/p/:productCode` と `**/c/:categoryCode` の形も、商品詳細とカテゴリのルートとして受け付けます。

- 商品詳細: `core-libs/storefront/cms-pages/product-details-page/product-details-url-matcher.ts:22-26, 31-36`
- カテゴリ: `core-libs/storefront/cms-pages/product-listing-page/product-listing-url-matcher.ts:22-26`

`p` や `c` の前にある部分(カテゴリ名や商品名)は読み捨てられます(`core-libs/storefront/cms-structure/routing/suffix-routes/suffix-url-matcher.ts:31-47`)。そのため、検索エンジンやブックマークに残っている `…/Open-Catalogue/Cameras/…/p/1934793` のような旧 URL も、Spartacus の商品詳細に着きます。

ただし、Spartacus が**作る**リンクは `paths` の 1 つ目の形になります。旧 URL のままリンクを作りたいなら、`routing.routes.product.paths` をアクセラレータの形に合わせて `provideConfig` します(22 章、23 章)。

**残りの URL**: コンテンツページは CMS のラベル(28.6)、マイアカウントとチェックアウトは Spartacus のルートの `paths` で決まります。棚卸し(28.3)の URL の一覧と突き合わせて、着かない URL を出します。着かない URL は、`paths` を足すか、Spartacus の前に置いた Web サーバーで 301 リダイレクトします。

**SSR**: 検索エンジンと初期表示のために、本番は SSR で配信します。サンプルの `js-storefront/manifest.json` でも `ssr.enabled: true` です(`ccs/js-storefront/manifest.json:6-9`)。SSR と TransferState の仕組みは 3 章と 8 章にあります。

---

### 28.10 段階 7: 並行稼働と切り替え

**リポジトリ**: 保守チームの構成を変えずに並行させる方法は 26 章です(方式 A: `git subtree`、方式 B: デプロイのたびに組み立てる)。

**ログインとカート**: アクセラレータは Web アプリのセッションで、Spartacus は OAuth のトークンで、ログインを持ちます。そのため、2 つの画面の間でログインはつながらないと考えておきます。会員のカートは OCC の `users/{userId}/carts` で取れるので、どちらでログインしても同じものが見えるはずです。匿名のカートは、アクセラレータではセッションに、Spartacus ではブラウザに識別子が残ります。こちらは引き継がれないと考えておきます。どちらも要確認です。「URL の一部だけを Spartacus に切り替える」ときは、ここが一番の問題になります。

**切り替えの単位**:

| 単位 | 形 | 注意 |
|---|---|---|
| サイト全体を一度に | ドメインの向き先を Spartacus に変える | ログインとカートの問題が出ない。準備期間が長い |
| ドメイン・国ごと | 国別のサイトを 1 つずつ切り替える | ベースサイトが分かれていれば自然に分けられる |
| 画面(パス)ごと | 前段の Web サーバーで、パスごとに振り分ける | 画面をまたぐとログインとカートが切れる。チェックアウトを途中で切るのは避ける |

**SmartEdit**: Spartacus 側には `@spartacus/smartedit` を入れます。既定のプレビューのルートは `cx-preview`、既定の `allowOrigin` は `localhost:9002` です(`feature-libs/smartedit/root/config/default-smart-edit-config.ts:11-12`)。この 2 つを、自社の SmartEdit とストアフロントの URL に合わせます。SmartEdit 側でストアフロントを許可する設定は、要確認です。

**最後に外すもの**: 切り替えが終わったら、`manifest.json` からアクセラレータの Web アプリ(`accstorefront` の aspect、`storefrontAddons`)を外します。`localextensions.xml` からは `yacceleratorstorefront` とアドオンの拡張を外します。Facade・Service・型の拡張は残します。

---

### 28.11 1 画面ぶんのチケットの書き方

段階 3〜6 は、画面ごとに次のチケットで回すと漏れが少なくなります。

```text
画面: カート(旧 URL /cart、Spartacus ルート cart)
[CMS]   ページ uid=cartPage、ラベル cart → /cart。テンプレート CartPageTemplate
        JSP の部品 7: 対応表で引ける 2(CartComponent・CartTotalsComponent)/ 対応なし 3(Checkout・Promotions・PotentialPromotions)/ 同意の 2 は Spartacus の部品へ
[部品]  対応なし: CartSuggestionComponent(使っていないので外す)、SaveForLaterCMSComponent(作る)
[ロジック] (例)CartPageController の数量の上限→ Facade へ。OCC の cart validate で返す。フロントは写し
[URL]   /cart は同じ。旧 /cart/checkout → Spartacus の checkout へ 301
[確認]  cms/pages?pageType=ContentPage&pageLabelOrId=/cart が 200。cms-page-coverage.py で NO が 0
```

---

### 28.12 まとめ

| 問い | 答え |
|---|---|
| 新規開発と何が違うか | 新規は型から作る。移行は今あるページを OCC で測ってから、差分だけを作る |
| 何が残り、何を捨てるか | Facade・Service・型・データは残る。storefront の Web 拡張(JSP・タグ・`web/src`)は捨てる。CMS の中身は作り直す |
| 最初の手順 | 棚卸し。27 章のスクリプトを**今のアクセラレータのサイト**に流す(デモでは 44 種類中 15 が対応なし) |
| バックエンドで最初にやること | `/occ`・OAuth クライアント・CORS。Spartacus 用のベースサイトを作り、配信する URL に合う `urlPatterns` を入れる(合わないと起動しない) |
| CMS で作り直すもの | ページのラベル(URL の形に)、JSP の部品(Flex に)、スクリプトの部品(外す)。テンプレート名はそのまま使える |
| 旧 URL | `…/p/<コード>` と `…/c/<コード>` は既定で受け付ける。作るリンクを旧形式にするなら `paths` を変える |
| 切り替え | 同じバックエンドに 2 つのサイトを並べて作る。画面ごとに切り替えると、ログインと匿名のカートが切れる(要確認) |

---

[目次](README.md) | ← [27. フロントエンドだけでコンポーネントをカスタマイズする方法の一覧: 標準にある部品・JSP 由来の部品・無い部品](27-frontend-component-customization-catalog.md) | [番外. サブエージェントとスキルの分け方](extra-agent-split-patterns.md) →
