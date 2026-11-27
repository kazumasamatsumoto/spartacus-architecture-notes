# jquery.currencies: ページ上の金額を、ブラウザの中で別の通貨に換算して書き換える(と考えられる)

> **この章が答える問い**: アクセラレータが読み込む `jquery.currencies.min.js` は何をするものか。原典はどれか。Spartacus では、通貨の切り替えと金額の表示をどう扱っているのか。Angular で通貨を整形するなら何を使うのか

> **根拠の取り方**:
> - **プラグイン(原典の特定)**: `jquery.currencies.min.js` という名前のファイルを配っている原典として、Shopify 向けの [carolineschnapp/currencies](https://github.com/carolineschnapp/currencies)(Caroline Schnapp 作、MIT)が見つかった。npm の `jquery.currencies.js@1.0.0`(2023-11-07 に第三者が公開。2026-11-27 時点で唯一の版)は、このリポジトリの `jquery.currencies.js` と `jquery.currencies.min.js` をそのまま収めたもので、`master`(コミット `240aa0dde325431b7e733d474bc99ceaeb36ff9b`)のファイルとバイト単位で一致した。以下 `pkg/` はこのパッケージのルート
>   - **アクセラレータが同梱している `jquery.currencies.min.js` が、この原典と同じものかは確認できなかった**。アクセラレータのファイルの中身を読めておらず、SAP Commerce との関係を示す資料も見つからなかった。1.3 節に、同じものだとすると不自然な点を挙げる。本章の 1 節は「原典がこれだとしたら」という前提で読んでほしい
>   - 原典が前提にしている Shopify の `currencies.js`(換算レートと `Currency.convert` を持つ)は読めていない
> - **Angular**: npm の `@angular/common@21.2.26` の型定義
> - **Spartacus**: SAP/spartacus `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`core/` は `core-libs/core/src/`、`fl/` は `feature-libs/`、`il/` は `integration-libs/` を指す。`.spec.ts` は除いて grep した
> - 代替ライブラリのバージョンは 2026-11-27 に `npm view` で確認した

---

### 先に話し言葉で: Spartacus は「ブラウザで換算しない」

原典の jquery.currencies は、ページ上の `span.money` に書かれた金額を読み取り、別の通貨に換算して書き換えるスクリプトです。選んだ通貨は Cookie に保存します。換算レートは別のスクリプト(Shopify の `currencies.js`)から受け取ります。

Spartacus には、**ブラウザで金額を換算する仕組みはありません**。通貨を切り替えると、Spartacus は商品やカートを OCC から取り直します。OCC は、その通貨での価格と、表示用に整形した文字列(`formattedValue`)を返します。画面はその文字列を出すだけです。換算も整形もサーバー(SAP Commerce)の仕事です。

通貨の切り替えの UI は、標準の **`cx-site-context-selector`** にあります。選んだ通貨は `CurrencyService` が持ち、`localStorage` に保存します。

ブラウザで金額を整形する必要があるときは、Angular の **`CurrencyPipe`**(`| currency`)か、ブラウザ標準の **`Intl.NumberFormat`** を使います。ただし、サーバーが返す `formattedValue` と書式がずれないように気をつけます。

---

### 1. jquery.currencies(原典)は何をするか

#### 1.1 主な API

```js
// 選んだ通貨を Cookie に書く・読む
Currency.cookie.write('CAD');
var saved = Currency.cookie.read();

// ページ上の金額を、ある通貨から別の通貨へ書き換える
Currency.convertAll('CAD', 'USD', 'span.money', 'money_with_currency_format');
```

| API | 内容 | 場所 |
|---|---|---|
| `Currency.cookie.write(code)` / `read()` / `destroy()` | 通貨コードを Cookie に保存する。既定の名前は `currency`、有効期限 365 日、`path=/` | `pkg/jquery.currencies.js:26-42` |
| `Currency.moneyFormats` | 通貨コードごとの書式。`money_format`(例: `${{amount}}`)と `money_with_currency_format`(例: `${{amount}} USD`)。約 120 通貨 | `:44-533` |
| `Currency.formatMoney(cents, format)` | 「セント単位の整数」を書式に当てはめて文字列にする | `:535-572` |
| `Currency.convertAll(old, new, selector?, format?)` | `selector`(既定 `span.money`)の要素の金額を読み、換算して書き換える | `:578-609` |
| `Currency.currentCurrency` | 今表示している通貨。`convertAll` が更新する | `:574`, `:607` |
| `Currency.format` | 既定の書式名。`'money_with_currency_format'` | `:576` |

書式の中の `{{amount}}` などは、次のように数値に置き換わります(`:557-570`)。

| プレースホルダ | 小数 | 桁区切り | 小数点 |
|---|---|---|---|
| `{{amount}}` | 2 桁 | `,` | `.` |
| `{{amount_no_decimals}}` | 0 桁 | `,` | — |
| `{{amount_with_comma_separator}}` | 2 桁 | `.` | `,` |
| `{{amount_no_decimals_with_comma_separator}}` | 0 桁 | `.` | — |

#### 1.2 中でどう動いているか

| 処理 | 中身 | 場所 |
|---|---|---|
| Cookie プラグインを同梱 | ファイルの先頭に、Klaus Hartl の `jQuery.cookie`(2006 年)を丸ごと含む。すでに `$.cookie` があれば上書きする | `pkg/jquery.currencies.js:1-11` |
| 画面の文字から金額を読む | 要素の HTML から数字以外をすべて消し、整数として読む(`replace(/[^0-9]/g, '')`)。つまり `$1,234.50` は `123450`(セント)になる | `:592`, `:595`, `:598` |
| 書式で読み方を変える | 元の通貨の書式が小数なしなら 100 倍し、`JOD`・`KWD`・`BHD`(小数 3 桁の通貨)なら 10 で割る | `:591-596` |
| 換算はよそに任せる | `Currency.convert(cents, old, new)` を呼ぶ。この関数は**このファイルに無い**。Shopify の `currencies.js` が持つ | `:592-598`、`pkg/README.md`(Dependencies) |
| 換算結果を要素に覚えさせる | `data-currency-USD` のような属性に整形済みの文字列を保存し、次に同じ通貨へ戻すときは再計算しない。`data-currency` に今の通貨を書く | `:581-585`, `:602`, `:605` |
| 整形は Shopify を優先 | `Shopify.formatMoney` が関数なら、それに任せる | `:536-538` |
| 最後に Cookie を書く | `convertAll` の最後で、新しい通貨を Cookie に保存する | `:608` |

README には「Cookie の既定の名前は `currencies`」とありますが、コードは `currency` です(`:32`)。

#### 1.3 アクセラレータのファイルと同じものか、の疑問

原典がそのまま SAP Commerce のアクセラレータで動くとは考えにくい点があります。

- `Currency.formatMoney` は最初に `typeof Shopify.formatMoney` を評価する(`:536`)。グローバルの `Shopify` が無いページでは、ここで `ReferenceError` になる。Shopify 以外のサイトで `convertAll` を呼ぶと、そのままでは失敗する
- 換算に使う `Currency.convert` とレートは、Shopify の `currencies.js` が前提で、このファイルには無い
- SAP Commerce の価格は、通貨ごとにサーバーで決まる(価格行が通貨を持つ)。ブラウザで換算し直す必要は普通は無い

そのため、アクセラレータの `jquery.currencies.min.js` は、(a) 原典に手を入れたもの、(b) 同じ名前の別のライブラリ、(c) 読み込まれているが実際には呼ばれていないもの、のどれかである可能性があります。どれなのかは、アクセラレータのファイルの中身と `acc.*.js` の呼び出し箇所を見ないと決められません。**本章ではこの点を確認できていません。**

---

### 2. Spartacus の標準にあるか

結論: **無い**(ブラウザで換算する仕組みは無い)。**通貨の切り替えと、サーバーが整形した金額の表示はある。**

#### 2.1 金額の表示: OCC の `formattedValue`

OCC の価格は、数値と、表示用に整形した文字列の両方を持ちます。

```ts
// core/model/product.model.ts:68-75
export interface Price {
  currencyIso?: string;
  formattedValue?: string;
  maxQuantity?: number;
  minQuantity?: number;
  priceType?: PriceType;
  value?: number;
}
```

Spartacus の画面は、ほぼ `formattedValue` をそのまま出しています(HTML テンプレートで 112 か所)。

```html
<!-- sf/cms-components/product/product-summary/product-summary.component.html:14 -->
{{ product?.price?.formattedValue }}

<!-- sf/cms-components/product/product-list/product-list-item/product-list-item.component.html:45 -->
{{ product.price?.formattedValue }}
```

金額の書式(記号の位置、桁区切り、小数の桁数)は、SAP Commerce 側が通貨と言語に合わせて決めます。jquery.currencies の `moneyFormats` に当たる表は、Spartacus にはありません。

#### 2.2 通貨の切り替え

| 段階 | 中身 | 場所 |
|---|---|---|
| UI | `cx-site-context-selector`。`<select>` で通貨を選ぶ。選択肢の表示は `記号 + ' ' + ISO コード`(例: `$ USD`) | `sf/cms-components/misc/site-context-selector/site-context-selector.component.html:4-13`、`site-context-component.service.ts:131-132` |
| 選んだ値を渡す | `set active(value)` から `SiteContextComponentService.setActive()` を経て、`CurrencyService.setActive()` を呼ぶ | `site-context-selector.component.ts:68-70` |
| 状態を持つ | `CurrencyService` は NgRx のストアに `SetActiveCurrency` を送る。許可された通貨(`context` の設定)以外は無視する | `core/site-context/facade/currency.service.ts:67-77`, `:96-103` |
| 使える通貨の一覧 | `getAll()`。未取得なら OCC の `currencies` を読みに行く | `currency.service.ts:37-52` |
| 変わったことを知らせる | 前の値と今の値を比べ、変わっていれば `CurrencyChange` アクションを出す(最初の設定では出さない) | `core/site-context/store/effects/currencies.effect.ts:53-65` |
| 保存する | `CurrencyStatePersistenceService` が `localStorage`(既定)に保存し、次に開いたときに読み戻す | `core/site-context/services/currency-state-persistence.service.ts:24-42`、`core/state/services/state-persistence.service.ts:48` |
| イベント | `CurrencySetEvent`(`activeCurrency` を持つ)。`EventService` で購読できる | `core/site-context/events/site-context.events.ts:23-29` |

#### 2.3 通貨が変わったあと何が起きるか

| 何が | どうなるか | 場所 |
|---|---|---|
| OCC への要求 | `SiteContextInterceptor` が、OCC の URL への要求すべてに `curr=<通貨>` と `lang=<言語>` を付ける | `core/occ/adapters/site-context/site-context.interceptor.ts:58-63` |
| 商品の状態 | `CurrencyChange` で商品のストアを空にする | `core/product/store/reducers/index.ts:46-57` |
| 商品・検索 | `CurrencyChange` で取り直す | `core/product/store/effects/product.effect.ts:29`、`product-search-by-code.effect.ts:30`、`product-search-by-category.effect.ts:28` |
| カート | `CurrencyChange` で取り直す(機能フラグ `enableCartReloadOnContextChange` が関わる) | `fl/cart/base/core/store/effects/cart.effect.ts:46-54`、`cart-entry.effect.ts:27` |
| 注文詳細、ウィッシュリストなど | 同じく `CURRENCY_CHANGE` を見て取り直す | `fl/order/core/store/effects/order-details.effect.ts:93`、`fl/cart/wish-list/core/store/effects/wish-list.effect.ts:129` |

jquery.currencies が「画面の文字を読んで書き換える」のに対し、Spartacus は「データを取り直して描き直す」方式です。

#### 2.4 jquery.currencies との機能の差

| 機能 | jquery.currencies(原典) | Spartacus |
|---|---|---|
| 換算 | ブラウザで `Currency.convert`(外部のレート) | しない。サーバーがその通貨の価格を返す |
| 整形 | `moneyFormats` の表と `formatMoney` | サーバーの `formattedValue` |
| 金額の出どころ | 画面に描かれた文字 | OCC の `Price`(数値と文字列) |
| 通貨の保存 | Cookie(`currency`) | `localStorage`(既定)。URL に通貨を載せる設定もある(`context.urlParameters`。`core/site-context/config/site-context-config.ts:16`) |
| 通貨の選択 UI | 無い(自分で作る) | `cx-site-context-selector` |
| 端数 | `toFixed` で丸める(`pkg/jquery.currencies.js:551`) | サーバーで決まる |

#### 2.5 Spartacus がブラウザで整形している例外

`formatCurrency` や `Intl.NumberFormat` をブラウザで使っている箇所が、少しだけあります。

| 場所 | 何をしているか |
|---|---|
| `fl/order/components/amend-order/amend-order.service.ts:123-137` | 返品・取消の数量を変えたときの金額を、ブラウザで計算して `formatCurrency` で整形する。ロケールは `'en'` に固定されている(`:132` の TODO コメント) |
| `fl/quote/components/summary/seller-edit/quote-summary-seller-edit.component.service.ts:55-69` | 見積もりの値引き入力欄の書式に `Intl.NumberFormat` を使う |
| `fl/product-configurator/rulebased/cpq/common/converters/cpq-configurator-normalizer-utils.service.ts:157` | CPQ の価格を `formatCurrency` で整形する |
| `il/opf/gift-card/root/components/opf-gift-card-order-summary/opf-gift-card-order-summary.component.html:64` | `| currency` パイプ |

Spartacus には `cxNumeric`(`DecimalPipe` を継承し、言語を Spartacus の現在の言語に合わせる。`core/i18n/numeric.pipe.ts:12-44`)と `cxDate` はありますが、**`cxCurrency` のような通貨用のパイプはありません**。

---

### 3. Angular で書くとどうなるか

#### 3.1 まずはサーバーの `formattedValue` を出す

Spartacus の画面と書式を揃えるなら、これが一番確実です。

```html
<span class="price">{{ product.price?.formattedValue }}</span>
```

#### 3.2 ブラウザで計算した金額を整形する: `CurrencyPipe`

数量を変えたときの小計など、ブラウザで計算した数値を出すときは `CurrencyPipe` を使います。`transform(value, currencyCode?, display?, digitsInfo?, locale?)` です(`@angular/common@21.2.26` の `types/_common_module-chunk.d.ts:1604`, `:1641-1643`)。

```ts
import { Component, computed, inject, input } from '@angular/core';
import { CurrencyPipe } from '@angular/common';
import { toSignal } from '@angular/core/rxjs-interop';
import { CurrencyService, LanguageService, Price } from '@spartacus/core';

@Component({
  selector: 'app-subtotal',
  imports: [CurrencyPipe],
  template: `
    @if (currency(); as cur) {
      {{ total() | currency: cur : 'symbol' : undefined : lang() }}
    }
  `,
})
export class SubtotalComponent {
  readonly unitPrice = input.required<Price>();
  readonly quantity = input(1);

  readonly currency = toSignal(inject(CurrencyService).getActive());
  readonly lang = toSignal(inject(LanguageService).getActive(), { initialValue: 'en' });

  readonly total = computed(() => (this.unitPrice().value ?? 0) * this.quantity());
}
```

注意点:

- `CurrencyPipe` は、`locale` に渡した言語の**ロケールデータ**が登録されていないと例外になる。Spartacus の `cxNumeric` も同じ理由で、登録が無いと `'en'` に切り替えている(`core/i18n/numeric.pipe.ts:26-34`)。使う言語は `registerLocaleData` で登録しておく
- 通貨記号の位置や桁区切りは Angular(CLDR)の規則で決まる。SAP Commerce の `formattedValue` と同じになるとは限らない。同じ画面に両方を並べると、書式がずれて見えることがある
- 金額の計算は、浮動小数点の誤差に注意する。Spartacus の `amend-order.service.ts:126-127` は、100 倍して `Math.round` で丸めている

#### 3.3 コンポーネントの外で整形する: `Intl.NumberFormat`

パイプが使えない場所(サービスの中など)では、ブラウザ標準の `Intl.NumberFormat` を使います。

```ts
const fmt = new Intl.NumberFormat('ja-JP', { style: 'currency', currency: 'JPY' });
fmt.format(1234.5); // "￥1,235"(JPY は小数 0 桁。Node.js 上で確認)
```

`Intl.NumberFormat` は通貨ごとの小数の桁数(JPY は 0、KWD は 3 など)を知っています。jquery.currencies が `moneyFormats` の表と `JOD`・`KWD`・`BHD` の特別扱いで書いていたこと(`pkg/jquery.currencies.js:594`)は、標準でまかなえます。

#### 3.4 別の通貨で「参考価格」を出したい場合

jquery.currencies のように、決済しない通貨で参考価格を見せたい要件もあり得ます。その場合も、換算レートは OCC か別の API から取り、`Intl.NumberFormat` で整形します。画面の文字を読んで書き換える方式は、Angular では使いません(Angular が描き直すと、書き換えた文字が元に戻るため)。参考価格であることを画面に明示し、カートや注文の金額と混ぜないようにします。

#### 3.5 SSR での注意

- `formattedValue` はサーバーの文字列なので、SSR でもブラウザでも同じ表示になる
- `CurrencyPipe` と `Intl.NumberFormat` は Node.js でも動く。ただし、サーバーとブラウザで使うロケールやタイムゾーンが違うと、ハイドレーションのあとに表示が変わることがある。言語は Spartacus の `LanguageService` から取り、両方で同じ値を使う
- jquery.currencies の Cookie(`document.cookie`)や `$('span.money')` はサーバーには無い。Spartacus の通貨の保存は `localStorage` なので、SSR の時点では読めず、サーバーは設定の既定通貨(または URL の通貨)で描く

---

### 4. ほかの選択肢

| ライブラリ | 版(2026-11-27) | peerDependencies | 内容 |
|---|---|---|---|
| `jquery.currencies.js` | 1.0.0 | なし | 1 節の原典を npm に載せたもの。jQuery と Shopify の `currencies.js` が前提 |
| `currency.js` | 2.0.4 | なし | 金額の加減乗除を、浮動小数点の誤差なしで行う小さなライブラリ |
| `dinero.js` | 2.0.2 | なし | 金額を「最小単位の整数 + 通貨」で表し、計算・換算・整形を行う |

いずれも中身は読んでいません。整形だけなら `Intl.NumberFormat` と `CurrencyPipe` で足ります。上の 2 つは、ブラウザで金額の計算を多く行う場合の候補です。

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| 商品やカートの金額を出す | OCC の `formattedValue` をそのまま出す |
| 通貨を切り替える UI が要る | 標準の `cx-site-context-selector`(CMS の通貨セレクタのコンポーネント) |
| 通貨が変わったときに自作の処理を走らせる | `CurrencyService.getActive()` を購読する。または `EventService` で `CurrencySetEvent` を受ける |
| ブラウザで計算した金額を出す(小計など) | `CurrencyPipe` に現在の通貨と言語を渡す。ロケールデータを登録する |
| サービスの中で整形する | `Intl.NumberFormat` |
| ブラウザで金額の計算を多く行う | `currency.js` や `dinero.js` で誤差を避ける。ただし正しい金額はサーバーで決める |
| 決済しない通貨で参考価格を出す | レートをサーバーから取り、`Intl.NumberFormat` で整形し、参考価格と明示する |

---

### 6. コンピュータサイエンスの観点から

- **表示された文字を「データ」として読まない**: jquery.currencies は、画面に描かれた `$1,234.50` から数字だけを抜き出して金額に戻します(`pkg/jquery.currencies.js:592-598`)。表示は書式やロケールで形が変わるので、そこから元の値を正しく戻すのは難しく、桁区切りと小数点が逆の書式では簡単に壊れます。Spartacus は数値(`value`)と表示(`formattedValue`)を別々に受け取り、表示を読み戻すことはしません。「状態から表示を作り、表示から状態を作らない」という一方向の流れは、[番外 4](../replacing-jquery.md) で書いた jQuery から Angular への考え方の転換と同じです
- **お金は整数で数える**: jquery.currencies は金額を「セント単位の整数」として扱います(`formatMoney` の引数は `cents`)。`0.1 + 0.2` が `0.30000000000000004` になる浮動小数点の誤差を避ける、昔からの定石です。`dinero.js` も同じ考え方です。一方で、小数の桁数は通貨ごとに違う(JPY は 0、KWD は 3)ので、「100 で割る」と決め打ちすると壊れます。原典が `JOD`・`KWD`・`BHD` を特別扱いしているのはそのためです(`:594`)。`Intl.NumberFormat` は通貨ごとの桁数のデータを持っています(`KWD` なら `1.500`)
- **整形の規則はデータとして持つ**: 原典の `moneyFormats` は、約 120 通貨の書式を手書きの表で持っています。ブラウザと Angular は、同じ情報を Unicode の CLDR という共通のデータから引きます。手書きの表は更新されにくく(原典には 2016 年に廃止された `BYR` が残っている)、共通のデータに任せるほうが正確です
