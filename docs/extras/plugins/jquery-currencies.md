# jquery.currencies: ページ上の金額を、ブラウザの中で別の通貨に換算して書き換える(と考えられる)

> **この章が答える問い**: アクセラレータが読み込む `jquery.currencies.min.js` は何をするものか。原典はどれか。Spartacus では、通貨の切り替えと金額の表示をどう扱っているのか。Angular で通貨を整形するなら何を使うのか

> **根拠の取り方**:
> - **プラグイン(原典の特定)**: `jquery.currencies.min.js` という名前のファイルを配っている原典として、Shopify 向けの [carolineschnapp/currencies](https://github.com/carolineschnapp/currencies)(Caroline Schnapp 作、MIT)が見つかった。npm の `jquery.currencies.js@1.0.0`(2023-11-07 に第三者が公開。2026-11-27 時点で唯一の版)は、このリポジトリの `jquery.currencies.js` と `jquery.currencies.min.js` をそのまま収めたもので、`master`(コミット `240aa0dde325431b7e733d474bc99ceaeb36ff9b`)のファイルとバイト単位で一致した。以下 `pkg/` はこのパッケージのルート
>   - **アクセラレータが同梱している `jquery.currencies.min.js` が、この原典と同じものかは確認できなかった**。アクセラレータのファイルの中身を読めておらず、SAP Commerce との関係を示す資料も見つからなかった。1.3 節に、同じものだとすると不自然な点を挙げる。本章の 1 節は「原典がこれだとしたら」という前提で読んでほしい
>   - 原典が前提にしている Shopify の `currencies.js`(換算レートと `Currency.convert` を持つ)は読めていない
> - **Angular**: npm の `@angular/core@21.2.26` と `@angular/common@21.2.26` の型定義(`types/`)と実装(`fesm2022/`)。`CurrencyPipe`、`formatCurrency` と `Intl.NumberFormat` の出力は、Node.js 22.23.5 で実際に呼んで確かめた
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
| `il/opf/gift-card/root/components/opf-gift-card-order-summary/opf-gift-card-order-summary.component.html:64` | `\| currency` パイプ |

Spartacus には `cxNumeric`(`DecimalPipe` を継承し、言語を Spartacus の現在の言語に合わせる。`core/i18n/numeric.pipe.ts:12-44`)と `cxDate` はありますが、**`cxCurrency` のような通貨用のパイプはありません**。

#### 2.6 Spartacus の部品と組み合わせる例

**まずはサーバーの `formattedValue` を出す**

Spartacus の画面と書式を揃えるなら、これが一番確実です。

```html
<span class="price">{{ product.price?.formattedValue }}</span>
```

**ブラウザで計算した金額を、Spartacus の現在の通貨と言語で整形する**

数量を変えたときの小計など、ブラウザで計算した数値を出すときは、3.2 節の `CurrencyPipe` に、`CurrencyService` と `LanguageService` の現在の値を渡します。

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

- Spartacus の言語(`LanguageService.getActive()`)の値で、Angular のロケールデータを `registerLocaleData` で登録しておく(3.1 節)。Spartacus の `cxNumeric` は、登録が無いと `'en'` に切り替えている(`core/i18n/numeric.pipe.ts:26-34`)
- 通貨記号の位置や桁区切りは Angular(CLDR)の規則で決まる。SAP Commerce の `formattedValue` と同じになるとは限らない。同じ画面に両方を並べると、書式がずれて見えることがある
- 金額の計算の丸めは、Spartacus の `fl/order/components/amend-order/amend-order.service.ts:126-127` では、100 倍して `Math.round` で丸めている
- SSR では、言語は `LanguageService` から取り、サーバーとブラウザで同じ値を使う。Spartacus の通貨の保存は `localStorage` なので、SSR の時点では読めず、サーバーは設定の既定通貨(または URL の通貨)で描く
- 参考価格(3.6 節)の換算レートは、OCC か別の API から取る

---

### 3. Angular 標準で書くとどうなるか(Spartacus を使わない)

この節は、`@angular/core`、`@angular/common`、`@angular/common/http`、RxJS とブラウザ標準の `Intl.NumberFormat` だけで書きます。Spartacus の `CurrencyService` や OCC の `formattedValue` を使う書き方は 2.6 節にあります。

jquery.currencies の機能(1.1 節)は、次のように置き換えます。

| jquery.currencies | Angular 標準 | 節 |
|---|---|---|
| `Currency.moneyFormats`、`formatMoney` | `CurrencyPipe`(`\| currency`)、`formatCurrency`、`Intl.NumberFormat`。書式は CLDR のデータから決まる | 3.1〜3.4 |
| `Currency.currentCurrency`、`Currency.cookie` | 通貨を signal に持つサービスと、Cookie への保存 | 3.3 |
| `convertAll`(画面の文字を書き換える) | 通貨が変わったら数値を取り直し、テンプレートで描き直す | 3.5 |
| `Currency.convert`(換算) | サーバーから受け取ったレートで計算し、参考価格として出す | 3.6 |

#### 3.1 アプリ全体の既定を決める: `LOCALE_ID`、`DEFAULT_CURRENCY_CODE`、`registerLocaleData`

```ts
// app.config.ts
import { ApplicationConfig, DEFAULT_CURRENCY_CODE, LOCALE_ID } from '@angular/core';
import { registerLocaleData } from '@angular/common';
import localeJa from '@angular/common/locales/ja';
import localeDe from '@angular/common/locales/de';

// en-US 以外のロケールは、使うものをすべて登録する
registerLocaleData(localeJa);
registerLocaleData(localeDe);

export const appConfig: ApplicationConfig = {
  providers: [
    { provide: LOCALE_ID, useValue: 'ja' },
    { provide: DEFAULT_CURRENCY_CODE, useValue: 'JPY' },
  ],
};
```

| 部品 | 役割 | 既定 | 場所 |
|---|---|---|---|
| `LOCALE_ID`(`@angular/core`) | 数値・日付・通貨の書式を決めるロケール。パイプに `locale` を渡さないときに使われる | `en-US` | `@angular/core@21.2.26` の `types/core.d.ts:4568` |
| `DEFAULT_CURRENCY_CODE`(`@angular/core`) | `CurrencyPipe` に通貨コードを渡さないときに使う通貨。**ロケールとは関係しない**(型定義のコメント) | `USD` | `types/core.d.ts:4569-4612`、実装は `fesm2022/_debug_node-chunk.mjs:18429-18430` |
| `registerLocaleData`(`@angular/common`) | ロケールの書式データ(CLDR から作ったもの)を登録する。`@angular/common/locales/<id>` に各ロケールのデータがある | `en-US` だけ組み込み | `@angular/common@21.2.26` の `types/common.d.ts:244` |

- 登録していないロケールを `CurrencyPipe` や `formatCurrency` に渡すと、`NG0701: Missing locale data for the locale "fr".` という例外になる(Node.js 22 で `formatCurrency` を呼んで確認)
- `LOCALE_ID` と `DEFAULT_CURRENCY_CODE` は、アプリを起動するときに決まる値である。利用者が画面で通貨や言語を切り替える場合は、3.3 節のように、パイプの引数で渡す
- `DEFAULT_CURRENCY_CODE` を設定しないと、通貨コードを省いた `| currency` は、ロケールが `ja` でもドルで出る(`CurrencyPipe` の既定は `'USD'`。`fesm2022/_common_module-chunk.mjs:3173`。`ja` で `$1,234.50` になることを確認)。通貨コードは、なるべくパイプに明示する

#### 3.2 テンプレートで整形する: `CurrencyPipe`

`transform(value, currencyCode?, display?, digitsInfo?, locale?)` です(`@angular/common@21.2.26` の `types/_common_module-chunk.d.ts:1604`, `:1641-1643`)。

```html
{{ 1234.5 | currency: 'JPY' : 'symbol' : undefined : 'ja' }}     <!-- ￥1,235 -->
{{ 1234.5 | currency: 'EUR' : 'symbol' : undefined : 'de' }}     <!-- 1.234,50 € -->
{{ 1234.5 | currency: 'USD' }}                                   <!-- $1,234.50(LOCALE_ID が en-US のとき) -->
{{ 1.5    | currency: 'KWD' : 'symbol' : undefined : 'en-US' }}  <!-- KWD1.500 -->
{{ 1234.5 | currency: 'USD' : 'code' }}                          <!-- USD1,234.50 -->
```

(コメントの結果は、`@angular/common@21.2.26` の `CurrencyPipe` と `formatCurrency` を Node.js 22 で直接呼んで確かめた。テンプレートに書いて動かしてはいない)

| 引数 | 内容 |
|---|---|
| `currencyCode` | ISO 4217 の通貨コード。省くと `DEFAULT_CURRENCY_CODE` |
| `display` | `'symbol'`(既定。`$`)、`'symbol-narrow'`(`CA$` ではなく `$`)、`'code'`(`USD`)、任意の文字列(その文字列を記号の代わりに使う。`''` で記号を消す) |
| `digitsInfo` | `'1.0-0'` のように小数の桁数を指定する。省くと通貨ごとの桁数(JPY は 0、KWD は 3)になる(`@angular/common@21.2.26` の `fesm2022/_common_module-chunk.mjs:1106-1107`) |
| `locale` | 書式のロケール。省くと `LOCALE_ID` |

jquery.currencies が `moneyFormats` の表と `JOD`・`KWD`・`BHD` の特別扱いで書いていたこと(`pkg/jquery.currencies.js:594`)は、ここまでで標準でまかなえます。

#### 3.3 利用者が通貨を切り替える: signal に持ち、Cookie に保存する

jquery.currencies の `Currency.currentCurrency` と `Currency.cookie` に当たるものを、小さなサービスにします。Cookie にするのは、SSR のときにサーバーでも読めるからです(3.8 節)。

```ts
import {
  DEFAULT_CURRENCY_CODE, DOCUMENT, effect, inject, Injectable, LOCALE_ID,
  PLATFORM_ID, REQUEST, signal,
} from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

export const CURRENCIES = ['JPY', 'USD', 'EUR'] as const;
export type CurrencyCode = (typeof CURRENCIES)[number];
const COOKIE = 'currency';

@Injectable({ providedIn: 'root' })
export class CurrencyContext {
  private readonly doc = inject(DOCUMENT);
  private readonly isBrowser = isPlatformBrowser(inject(PLATFORM_ID));
  private readonly request = inject(REQUEST); // SSR のときだけ値がある。それ以外は null

  /** 書式のロケール。言語を切り替えるなら、これも set する(registerLocaleData 済みのものだけ) */
  readonly locale = signal(inject(LOCALE_ID));
  readonly currency = signal<CurrencyCode>(
    this.readCookie() ?? (inject(DEFAULT_CURRENCY_CODE) as CurrencyCode),
  );

  constructor() {
    // 選んだ通貨を Cookie に書く(jquery.currencies の Currency.cookie.write に当たる)
    effect(() => {
      const code = this.currency();
      if (this.isBrowser) {
        this.doc.cookie = `${COOKIE}=${code}; path=/; max-age=31536000; SameSite=Lax`;
      }
    });
  }

  private readCookie(): CurrencyCode | null {
    const raw = this.isBrowser ? this.doc.cookie : (this.request?.headers.get('cookie') ?? '');
    const value = raw.match(/(?:^|;\s*)currency=([A-Z]{3})/)?.[1];
    return CURRENCIES.find((c) => c === value) ?? null;
  }
}
```

通貨を選ぶ UI は、jquery.currencies には無かったので自分で作ります。ラベル付きの `<select>` にすれば、キーボードでも支援技術でもそのまま使えます。

```ts
import { Component, inject } from '@angular/core';
import { CURRENCIES, CurrencyCode, CurrencyContext } from './currency-context';

@Component({
  selector: 'app-currency-select',
  template: `
    <label for="currency-select">通貨</label>
    <select id="currency-select" (change)="select($event)">
      @for (c of currencies; track c) {
        <option [value]="c" [selected]="c === ctx.currency()">{{ symbol(c) }} {{ c }}</option>
      }
    </select>
  `,
})
export class CurrencySelectComponent {
  protected readonly ctx = inject(CurrencyContext);
  protected readonly currencies = CURRENCIES;

  select(e: Event): void {
    this.ctx.currency.set((e.target as HTMLSelectElement).value as CurrencyCode);
  }

  /** 通貨記号は Intl から取る(@angular/common の getCurrencySymbol は非推奨) */
  symbol(code: string): string {
    return new Intl.NumberFormat(this.ctx.locale(), { style: 'currency', currency: code })
      .formatToParts(0)
      .find((p) => p.type === 'currency')?.value ?? code;
  }
}
```

表示する側は、パイプに今の通貨とロケールを渡します。

```html
{{ amount() | currency: ctx.currency() : 'symbol' : undefined : ctx.locale() }}
```

- `REQUEST` は `@angular/core` の注入トークンで、SSR のときに今の要求(`Request`)が入る。それ以外では `null`(`types/core.d.ts:9388`、実装は `fesm2022/core.mjs:2912-2915`)
- `getCurrencySymbol` と `getNumberOfCurrencyDigits` は、`@angular/common@21` で非推奨になっている。型定義のコメントは `Intl.NumberFormat` を使うよう勧めている(`types/common.d.ts:790-813`)
- `@angular/forms` を使うなら、`<select [formControl]>` や `[(ngModel)]` でもよい

#### 3.4 コンポーネントの外で整形する: `Intl.NumberFormat`

パイプが使えない場所(サービスの中、`computed` の中など)では、ブラウザ標準の `Intl.NumberFormat` か、`@angular/common` の `formatCurrency` を使います。

```ts
const fmt = new Intl.NumberFormat('ja-JP', { style: 'currency', currency: 'JPY' });
fmt.format(1234.5); // "￥1,235"(JPY は小数 0 桁。Node.js 22 で確認)

// 通貨とロケールが変わったときだけ作り直す
readonly formatter = computed(
  () => new Intl.NumberFormat(this.ctx.locale(), { style: 'currency', currency: this.ctx.currency() }),
);
readonly label = computed(() => this.formatter().format(this.amount()));
```

`Intl.NumberFormat` は通貨ごとの小数の桁数を知っています。`resolvedOptions().maximumFractionDigits` で桁数も取れます(USD なら 2)。

**`CurrencyPipe` と `Intl.NumberFormat` は、同じ書式になるとは限りません**。`CurrencyPipe` は Angular に同梱された CLDR のデータを使い、`Intl.NumberFormat` は実行環境(ブラウザや Node.js)の ICU のデータを使います。たとえば `en-US` の `KWD` 1.5 は、`formatCurrency` では `KWD1.500`、Node.js 22 の `Intl.NumberFormat` では `KWD 1.500`(空白あり)でした。1 つの画面では、どちらかに揃えます。

#### 3.5 通貨が変わったら数値を取り直す

jquery.currencies の `convertAll` は、画面の文字を読んで書き換えていました。Angular では、通貨が変わったら価格のデータを取り直し、テンプレートで描き直します。

```ts
import { Component, computed, inject, input } from '@angular/core';
import { CurrencyPipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { switchMap } from 'rxjs';
import { CurrencyContext } from './currency-context';

interface PriceDto { value: number; currency: string }

@Component({
  selector: 'app-price',
  imports: [CurrencyPipe],
  template: `
    @if (price(); as p) {
      <span class="price">{{ p.value | currency: p.currency : 'symbol' : undefined : ctx.locale() }}</span>
    }
  `,
})
export class PriceComponent {
  readonly code = input.required<string>();
  protected readonly ctx = inject(CurrencyContext);
  private readonly http = inject(HttpClient);

  private readonly query = computed(() => ({ code: this.code(), curr: this.ctx.currency() }));

  readonly price = toSignal(
    toObservable(this.query).pipe(
      switchMap(({ code, curr }) =>
        this.http.get<PriceDto>(`/api/products/${code}/price`, { params: { curr } }),
      ),
    ),
  );
}
```

- `switchMap` なので、通貨を続けて切り替えたときは、前の要求の結果を捨てる
- 通貨は、サーバーが返した `p.currency` を使って整形する。画面の選択と応答がずれても、金額と通貨記号が食い違わない
- `HttpClient` を使うには、アプリの providers に `provideHttpClient()` を入れる

#### 3.6 別の通貨で「参考価格」を出したい場合

jquery.currencies のように、決済しない通貨で参考価格を見せたい要件もあり得ます。その場合も、換算レートはサーバーから取り、`Intl.NumberFormat` か `CurrencyPipe` で整形します。画面の文字を読んで書き換える方式は、Angular では使いません(Angular が描き直すと、書き換えた文字が元に戻るため)。参考価格であることを画面に明示し、カートや注文の金額と混ぜないようにします。

#### 3.7 金額の計算

- 浮動小数点の誤差に注意する。`0.1 + 0.2` は `0.30000000000000004` になる。合計などは、通貨の最小単位(セントなど)の整数で計算し、最後に割り戻す
- 最小単位の桁数は通貨ごとに違う。`new Intl.NumberFormat('en', { style: 'currency', currency }).resolvedOptions().maximumFractionDigits` で取れる。「100 で割る」と決め打ちしない
- 正しい金額(請求する額)は、サーバーで決める。ブラウザの計算は表示のためだけに使う

#### 3.8 SSR での注意

- `CurrencyPipe` と `Intl.NumberFormat` は Node.js でも動く。ただし、サーバーとブラウザで使うロケールが違うと、ハイドレーションのあとに表示が変わる。ロケールと通貨は、サーバーでもブラウザでも同じ値になるように決める
- 3.3 節のように通貨を Cookie に置けば、サーバーでも `inject(REQUEST)` の Cookie から読める。`localStorage` に置くと、サーバーでは読めず、サーバーは既定の通貨で描き、ブラウザで別の通貨に変わる
- `document.cookie` は、`inject(DOCUMENT)` から触る。書き込みは `isPlatformBrowser(inject(PLATFORM_ID))` でブラウザに限る。ブラウザでだけ、描画のあとに読み直したいものがあれば `afterNextRender` の中で行う
- `Intl.NumberFormat` の結果は、実行環境の ICU の版で変わることがある(3.4 節)。サーバー(Node.js)とブラウザで書式を完全に揃えたいなら、Angular に同梱のデータを使う `CurrencyPipe` / `formatCurrency` に寄せる
- jquery.currencies の `document.cookie` の直接参照や `$('span.money')` は、サーバーには無い

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
| ブラウザで計算した金額を出す(小計など) | `CurrencyPipe` に現在の通貨と言語を渡す。ロケールデータを登録する(Spartacus なら 2.6 節) |
| サービスの中で整形する | `Intl.NumberFormat`(3.4 節) |
| Spartacus を使わず、アプリの既定の言語と通貨を決める | `LOCALE_ID` と `DEFAULT_CURRENCY_CODE` を providers に書き、使うロケールを `registerLocaleData` で登録する(3.1 節) |
| Spartacus を使わず、利用者に通貨を選ばせる | 通貨を signal に持つサービスを作り、Cookie に保存する。UI はラベル付きの `<select>`。パイプには通貨とロケールを引数で渡す(3.3 節) |
| Spartacus を使わず、通貨が変わったら価格を取り直す | 通貨の signal を `toObservable` にし、`switchMap` で `HttpClient` の要求をし直す(3.5 節) |
| SSR でサーバーとブラウザの表示を揃える | 通貨は Cookie に置いてサーバーでも読む。書式は `CurrencyPipe` / `formatCurrency` に揃える(3.8 節) |
| ブラウザで金額の計算を多く行う | `currency.js` や `dinero.js` で誤差を避ける。ただし正しい金額はサーバーで決める |
| 決済しない通貨で参考価格を出す | レートをサーバーから取り、`Intl.NumberFormat` で整形し、参考価格と明示する |

---

### 6. コンピュータサイエンスの観点から

- **表示された文字を「データ」として読まない**: jquery.currencies は、画面に描かれた `$1,234.50` から数字だけを抜き出して金額に戻します(`pkg/jquery.currencies.js:592-598`)。表示は書式やロケールで形が変わるので、そこから元の値を正しく戻すのは難しく、桁区切りと小数点が逆の書式では簡単に壊れます。Spartacus は数値(`value`)と表示(`formattedValue`)を別々に受け取り、表示を読み戻すことはしません。「状態から表示を作り、表示から状態を作らない」という一方向の流れは、[番外 4](../replacing-jquery.md) で書いた jQuery から Angular への考え方の転換と同じです
- **お金は整数で数える**: jquery.currencies は金額を「セント単位の整数」として扱います(`formatMoney` の引数は `cents`)。`0.1 + 0.2` が `0.30000000000000004` になる浮動小数点の誤差を避ける、昔からの定石です。`dinero.js` も同じ考え方です。一方で、小数の桁数は通貨ごとに違う(JPY は 0、KWD は 3)ので、「100 で割る」と決め打ちすると壊れます。原典が `JOD`・`KWD`・`BHD` を特別扱いしているのはそのためです(`:594`)。`Intl.NumberFormat` は通貨ごとの桁数のデータを持っています(`KWD` なら `1.500`)
- **整形の規則はデータとして持つ**: 原典の `moneyFormats` は、約 120 通貨の書式を手書きの表で持っています。ブラウザと Angular は、同じ情報を Unicode の CLDR という共通のデータから引きます。手書きの表は更新されにくく(原典には 2016 年に廃止された `BYR` が残っている)、共通のデータに任せるほうが正確です
