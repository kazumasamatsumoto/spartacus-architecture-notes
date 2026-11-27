# jQuery Templates(jquery.tmpl): 文字列のテンプレートにデータを流し込んで DOM を作る

> **この章が答える問い**: アクセラレータが読み込む `jquery.tmpl-1.0.0pre.min.js` は何をしているのか。Angular のテンプレート、`ng-template` / `ngTemplateOutlet`、Spartacus のアウトレットは、その代わりになるのか

> **根拠の取り方**:
> - **プラグイン**: npm には 1.0.0pre が無い(npm の `jquery.tmpl` は別人による 2011 年の包み直しで、版は 0.0.2)。そのため、公式のリポジトリ [BorisMoore/jquery-tmpl](https://github.com/BorisMoore/jquery-tmpl) の `master`(コミット `ef4ae98374e5f3d9bd84d16c54ad30801c1ec002`)の `jquery.tmpl.js`(見出しが `jQuery Templates Plugin 1.0.0pre`)と `README.md` を読んだ。以下 `pkg/` はリポジトリのルート
>   - 見出しが「1.0.0pre」のまま `master` に積まれた変更がある(例: AMD 対応の包み `pkg/jquery.tmpl.js:10-18`)。アクセラレータが同梱しているファイルが、どのコミットのものかは確認できなかった
> - **jQuery**: npm の `jquery@3.5.1`(アクセラレータが読み込んでいる版。[番外 4](../replacing-jquery.md) の根拠と同じ)と `jquery@4.1.0` の `dist/jquery.js`
> - **Angular**: npm の `@angular/common@21.2.26` の型定義
> - **Spartacus**: SAP/spartacus `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/` を指す
> - 代替ライブラリのバージョンは 2026-11-27 に `npm view` で確認した

---

### 先に話し言葉で: Angular のテンプレートそのものが置き換え先

jQuery Templates は、`<li>${Name}</li>` のような文字列のテンプレートにデータを流し込み、DOM を作るプラグインです。`{{if}}` や `{{each}}` で条件分岐と繰り返しも書けます。2010 年に jQuery 公式のプラグインとして作られましたが、ベータのまま開発が止まりました。後継は JsRender とされています(`pkg/README.md:3-4`)。

Angular では、この役割を**テンプレートの仕組みそのもの**が担います。`${Name}` は `{{ name }}`、`{{if}}` は `@if`、`{{each}}` は `@for` です。しかも Angular のテンプレートはビルド時にコンパイルされるので、jquery.tmpl のように実行時に `new Function` で JS を組み立てることはありません。

名前を付けたテンプレートを登録して、別の場所で呼び出す使い方には、`<ng-template>` と `ngTemplateOutlet` が当たります。Spartacus では、さらに**アウトレット**(`cxOutlet` / `cxOutletRef` / `provideOutlet`)が「名前付きのテンプレートを外から差し替える」仕組みとして用意されています。

置き換えで別のテンプレートエンジンを足す必要は、ほとんどありません。

---

### 1. jQuery Templates は何をするか

#### 1.1 主な API

```js
// 名前を付けて登録し、データを流し込んで DOM に追加する
$.template('movieTemplate', '<li><b>${Name}</b> (${ReleaseYear})</li>');
$.tmpl('movieTemplate', movies).appendTo('#movieList');

// <script type="text/x-jquery-tmpl"> に書いたテンプレートを使う
$('#movieTemplate').tmpl(movies).appendTo('#movieList');
```

| API | 内容 | 場所 |
|---|---|---|
| `$.tmpl(tmpl, data, options)` | テンプレートにデータを流し込み、できた要素を jQuery オブジェクトで返す。`data` が配列なら、要素ごとに描く | `pkg/jquery.tmpl.js:126-160` |
| `$(selector).tmpl(data, options)` | 選んだ要素(普通は `<script>`)の中身をテンプレートとして使う | `:88-90` |
| `$.template(name, tmpl)` | テンプレートをコンパイルし、名前を付けて保存する。`$.template(name)` で取り出す | `:183-207` |
| `$.tmplItem(elem)` / `$(elem).tmplItem()` | 描いた要素から、元のデータ(`data`)とテンプレートの情報を引く | `:163-170`, `:93-95` |
| `$item.update()` | データを変えたあと、そのテンプレートの部分だけ描き直す | `:487-491` |
| `.appendTo()` などの上書き | `appendTo`・`prependTo`・`insertBefore`・`insertAfter`・`replaceAll` を上書きし、描いた要素とデータの対応を記録する | `:53-83` |

テンプレートのタグは次のとおりです(`pkg/jquery.tmpl.js:216-255`)。

| タグ | 内容 | Angular での書き方 |
|---|---|---|
| `${expr}` / `{{= expr}}` | 値をエスケープして出す | `{{ expr }}` |
| `{{html expr}}` | 値を**エスケープせずに** HTML として出す | `[innerHTML]="expr"`(Angular がサニタイズする) |
| `{{if cond}}…{{else cond2}}…{{else}}…{{/if}}` | 条件分岐 | `@if (cond) {…} @else if (cond2) {…} @else {…}` |
| `{{each(i, v) list}}…{{/each}}` | 繰り返し。既定の変数名は `$index`、`$value` | `@for (v of list; track v.id; let i = $index) {…}` |
| `{{tmpl(data) "#name"}}` | 別のテンプレートを入れ子で描く | 子コンポーネント、または `ngTemplateOutlet` |
| `{{wrap "#name"}}…{{/wrap}}` | 中身を別のテンプレートで包む | `<ng-content>` |
| `{{! comment}}` | コメント | `<!-- -->` |

#### 1.2 中でどう動いているか

| 処理 | 中身 | 場所 |
|---|---|---|
| テンプレートを JS の関数にコンパイルする | テンプレート文字列を正規表現で切り分け、各タグを JS のコード片に置き換えてつなぎ、`new Function("jQuery", "$item", …)` で関数にする | `pkg/jquery.tmpl.js:324-368` |
| データを変数として見せる | 生成した関数の中身を `with($data){ … }` で囲む。テンプレートに `${Name}` と書くと `$data.Name` が読まれる | `:327-330` |
| 文字列をつないでから DOM にする | 関数は文字列の配列を返す。それを 1 本の HTML 文字列につなぎ、jQuery で DOM にする | `:281-314` |
| 要素とデータを結び付ける | HTML の各要素に `_tmplitem="番号"` 属性を一時的に付け、DOM に入れたあと `jQuery.data` に置き換える | `:287`, `:388` 以降 |
| エスケープ | `$.encode` は `<`、`>`、`"`、`'` を文字参照に置き換える。コメントには `&` も置き換えると書いてあるが、コードは `&` を置き換えていない | `:209-212` |

注意点が 3 つあります。

- **CSP**: `new Function` を使うので、CSP で `script-src` に `'unsafe-eval'` を許可しないと動かない
- **`{{html}}` は素通し**: `{{html expr}}` は値をそのまま HTML として出す(`:242-245`)。信頼できない値を入れると XSS になる
- **jQuery 3 との相性**: jquery.tmpl は `jQuery.fn.domManip` を上書きする(`:19`, `:102-121`)。jQuery 3.5.1 では `domManip` は外から見えない内部関数になっていて(`jquery@3.5.1` の `dist/jquery.js:6047`)、`jQuery.fn.domManip` は定義されていない。そのため、この上書きは jQuery 本体からは呼ばれない。どの機能に影響が出るかは、動かして確かめていない。また jquery.tmpl が使う `jQuery.isArray` と `jQuery.trim` は、3.5.1 では非推奨の互換 API で(`dist/jquery.js:10787`, `:10811`)、`jquery@4.1.0` には無い

---

### 2. Spartacus の標準にあるか

結論: **ある**(Angular のテンプレートと、Spartacus のアウトレット)。jquery.tmpl と同じく「文字列から実行時にテンプレートを作る」仕組みは無い。

#### 2.1 Angular のテンプレート

Spartacus のコンポーネントは、すべて Angular のテンプレートで描かれています。jquery.tmpl の 1 回の `$.tmpl(...).appendTo(...)` が、コンポーネント 1 つに当たります。

#### 2.2 `ng-template` と `ngTemplateOutlet`

名前を付けたテンプレートを、同じコンポーネントの中で使い回すときに使います。`@angular/common` の `NgTemplateOutlet` は、`ngTemplateOutlet`(テンプレート)と `ngTemplateOutletContext`(渡すデータ)を受け取ります(`@angular/common@21.2.26` の `types/_common_module-chunk.d.ts:919-937`)。

Spartacus の HTML テンプレートでは 17 か所で使われています。例: `sf/shared/components/star-rating/star-rating.component.html:11`、`sf/shared/components/popover/popover.component.html:18`。

#### 2.3 Spartacus のアウトレット

アウトレットは、「名前の付いた差し込み口」と「そこに入れるテンプレート」を、別々の場所で書ける仕組みです。`$.template('name', …)` で名前を付けて登録し、`$.tmpl('name', data)` で呼ぶ関係に似ています。違いは、**標準のテンプレートを残したまま、外から差し替えや前後への追加ができる**ことです。

| 部品 | 内容 | 場所 |
|---|---|---|
| `[cxOutlet]` | 差し込み口。`<ng-template [cxOutlet]="'名前'">…</ng-template>` の中身が既定のテンプレートになる | `sf/cms-structure/outlet/outlet.directive.ts:33-60` |
| `[cxOutletContext]` | 差し込むテンプレートに渡すデータ。テンプレートでは `let-ctx` で受ける(`$implicit` として渡す) | `:46`, `:176-181` |
| `OutletPosition` | `REPLACE`(置き換え)・`BEFORE`(前に足す)・`AFTER`(後に足す) | `sf/cms-structure/outlet/outlet.model.ts:9-13` |
| 置き換えが無いとき | 登録が無ければ、`[cxOutlet]` の中身(既定のテンプレート)を描く | `outlet.directive.ts:137-139` |
| `*cxOutletRef` | 自作のテンプレートを、名前と位置を付けて登録する | `sf/cms-structure/outlet/outlet-ref/outlet-ref.directive.ts:17-34` |
| `provideOutlet()` | コンポーネントを、名前と位置を付けて登録する(プロバイダで書く) | `sf/cms-structure/outlet/outlet.providers.ts:41-47` |
| `OutletService` | 名前ごとにテンプレートやコンポーネントを保存する登録簿 | `sf/cms-structure/outlet/outlet.service.ts:30-62` |

商品の概要では、価格の表示がアウトレットになっています。

```html
<!-- sf/cms-components/product/product-summary/product-summary.component.html:6-16 -->
<ng-template
  [cxOutlet]="outlets.PRICE"
  [cxOutletContext]="{ product: product }"
>
  <div [attr.aria-label]="'productSummary.newItemPrice' | cxTranslate" class="price">
    {{ product?.price?.formattedValue }}
  </div>
</ng-template>
```

`outlets.PRICE` の値は `'PDP.PRICE'` です(`sf/cms-components/product/product-outlets.model.ts:9`)。これを置き換えるには、自分のテンプレートを登録します。

```html
<ng-template cxOutletRef="PDP.PRICE" let-ctx>
  <div class="price my-price">{{ ctx.product?.price?.formattedValue }}</div>
</ng-template>
```

このテンプレートを書くコンポーネントでは、`OutletRefDirective`(または `OutletRefModule`。`sf/cms-structure/outlet/outlet-ref/outlet-ref.module.ts:13-16`)を `imports` に入れます。登録は `ngOnInit` で行われるので(`outlet-ref.directive.ts:29-30`)、そのコンポーネントが画面にある間だけ置き換えが効きます。常に効かせたいなら、コンポーネントを `provideOutlet()` で登録します。

アウトレットの全体像は [1.7 節](../../01-7-outlets.md) にあります。

#### 2.4 jquery.tmpl との機能の差

| 機能 | jquery.tmpl | Angular / Spartacus |
|---|---|---|
| 値の埋め込み | `${x}`(実行時にエスケープ) | `{{ x }}`(エスケープ。ビルド時にコンパイル) |
| HTML の埋め込み | `{{html x}}`(素通し) | `[innerHTML]`(サニタイズされる) |
| 条件・繰り返し | `{{if}}`、`{{each}}` | `@if`、`@for`、`@switch` |
| 名前付きテンプレート | `$.template(name, …)`(グローバルな登録簿) | 同じコンポーネント内なら `<ng-template #name>` + `ngTemplateOutlet`、外から差し替えるならアウトレット |
| データの変更で描き直す | `$item.update()` を自分で呼ぶ | 変更検知が自動で描き直す(signal、`async` パイプ) |
| 文字列から実行時にテンプレートを作る | できる | できない(AOT。3.6 節) |
| CSP | `'unsafe-eval'` が要る | 要らない |

#### 2.5 Spartacus の部品と組み合わせる例

3 節の書き方(`ngTemplateOutlet` など)は、自作のコンポーネントの中で使うものです。**Spartacus の標準コンポーネントの中身**を差し替えたいときは、`ngTemplateOutlet` ではなく、次のどちらかを使います。

| したいこと | 方法 |
|---|---|
| 差し込み口(`[cxOutlet]`)がある場所を差し替える・前後に足す | アウトレット。`*cxOutletRef` か `provideOutlet()`(2.3 節) |
| 差し込み口が無いコンポーネントを丸ごと差し替える | CMS のマッピング(`cmsComponents`)で自作のコンポーネントに差し替える |

SSR については、アウトレットもサーバーで描けます。`cxOutletDefer` を付けたアウトレットは、画面に入るまで描くのを遅らせます(`sf/cms-structure/outlet/outlet.directive.ts:56`, `:85`)。この遅延はブラウザでの表示位置に基づくので、サーバーでどう扱われるかは個別に確かめます。

Spartacus には、CMS や API から届いた文字列をテンプレートとして実行時に描く仕組みはありません(3.6 節)。

---

### 3. Angular 標準で書くとどうなるか(Spartacus を使わない)

この節は、`@angular/core` と `@angular/common` だけで書きます。Spartacus のアウトレットや CMS のマッピングを使う書き方は 2.3 節と 2.5 節にあります。

#### 3.1 jquery.tmpl の典型例を置き換える

```html
<!-- アクセラレータ(jquery.tmpl) -->
<script id="cartItemTmpl" type="text/x-jquery-tmpl">
  <li>
    <span class="name">${name}</span>
    {{if promotion}}<span class="promo">{{html promotion}}</span>{{/if}}
    <span class="price">${price}</span>
  </li>
</script>
<script>$('#cartItemTmpl').tmpl(entries).appendTo('#cartItems');</script>
```

```ts
// Angular
import { Component, input } from '@angular/core';

interface Entry { code: string; name: string; promotion?: string; price: string }

@Component({
  selector: 'app-cart-items',
  template: `
    <ul>
      @for (e of entries(); track e.code) {
        <li>
          <span class="name">{{ e.name }}</span>
          @if (e.promotion) {
            <span class="promo" [innerHTML]="e.promotion"></span>
          }
          <span class="price">{{ e.price }}</span>
        </li>
      } @empty {
        <li>カートは空です</li>
      }
    </ul>
  `,
})
export class CartItemsComponent {
  readonly entries = input<Entry[]>([]);
}
```

`entries` を新しい配列に変えれば、Angular が差分だけ描き直します。`$item.update()` や `.remove()` は要りません。

#### 3.2 テンプレートを差し替え可能にする: `ngTemplateOutlet`

「行の描き方を呼び出し側が決める」部品は、テンプレートを入力で受け取ります。

```ts
import { Component, contentChild, input, TemplateRef } from '@angular/core';
import { NgTemplateOutlet } from '@angular/common';

@Component({
  selector: 'app-list',
  imports: [NgTemplateOutlet],
  template: `
    @for (item of items(); track $index) {
      <ng-container
        [ngTemplateOutlet]="row() ?? defaultRow"
        [ngTemplateOutletContext]="{ $implicit: item }" />
    }
    <ng-template #defaultRow let-item>{{ item }}</ng-template>
  `,
})
export class ListComponent<T> {
  readonly items = input<T[]>([]);
  readonly row = contentChild<TemplateRef<{ $implicit: T }>>(TemplateRef);
}
```

```html
<app-list [items]="movies">
  <ng-template let-m><b>{{ m.name }}</b> ({{ m.year }})</ng-template>
</app-list>
```

#### 3.3 入れ子と包み: `{{tmpl}}` と `{{wrap}}`

`{{tmpl(data) "#name"}}` で別のテンプレートを入れ子に描いていたところは、子コンポーネントにします。`{{wrap "#name"}}…{{/wrap}}` で中身を包んでいたところは、`<ng-content>` で中身を受け取るコンポーネントにします。

```ts
import { Component, input } from '@angular/core';

// {{wrap "#panelTmpl"}}…{{/wrap}} に当たる
@Component({
  selector: 'app-panel',
  template: `
    <section class="panel" [attr.aria-labelledby]="headingId()">
      <h2 [id]="headingId()">{{ heading() }}</h2>
      <ng-content />
    </section>
  `,
})
export class PanelComponent {
  readonly heading = input.required<string>();
  readonly headingId = input.required<string>();
}
```

```html
<!-- {{tmpl(entries) "#cartItemTmpl"}} を、子コンポーネントの呼び出しにする -->
<app-panel heading="カート" headingId="cart-heading">
  <app-cart-items [entries]="entries()" />
</app-panel>
```

#### 3.4 データの取り出しと描き直し: `$.tmplItem` と `$item.update()`

jquery.tmpl では、クリックされた要素から `$.tmplItem(elem).data` で元のデータを引き、データを変えたら `$item.update()` で描き直していました。Angular では、`@for` の中のイベントにデータをそのまま渡せます。データは signal に持ち、新しい値を入れれば描き直されます。

```ts
import { Component, signal } from '@angular/core';

interface Movie { id: number; name: string; year: number; watched: boolean }

@Component({
  selector: 'app-movies',
  template: `
    <ul>
      @for (m of movies(); track m.id) {
        <li>
          <b>{{ m.name }}</b> ({{ m.year }})
          <button type="button" [attr.aria-pressed]="m.watched" (click)="toggle(m)">
            見た
          </button>
        </li>
      }
    </ul>
  `,
})
export class MoviesComponent {
  readonly movies = signal<Movie[]>([
    { id: 1, name: 'Meet Joe Black', year: 1998, watched: false },
    { id: 2, name: 'The Matrix', year: 1999, watched: true },
  ]);

  toggle(m: Movie): void {
    // $.tmplItem(this).data に当たるのが引数の m。$item.update() は要らない
    this.movies.update((list) =>
      list.map((x) => (x.id === m.id ? { ...x, watched: !x.watched } : x)),
    );
  }
}
```

- `track m.id` で、どの行がどのデータかを Angular が覚える。jquery.tmpl が `_tmplitem` 属性と `jQuery.data` で行っていたこと(1.2 節)に当たる
- 押すと状態が切り替わるボタンには `aria-pressed` を付け、状態を支援技術に伝える。`<button>` なので、キーボード(Enter と Space)でも操作できる

#### 3.5 あとから命令的に差し込む: `ViewContainerRef`

`$.tmpl(...).appendTo('#target')` のように、イベントのたびに断片を足していく使い方は、`ViewContainerRef.createEmbeddedView` で書けます。ただし、多くの場合は 3.4 節のように「配列に足して `@for` で描く」ほうが簡単です。

```ts
import { Component, TemplateRef, ViewContainerRef, viewChild } from '@angular/core';

@Component({
  selector: 'app-notices',
  template: `
    <ng-template #noticeTmpl let-msg><p class="notice">{{ msg }}</p></ng-template>
    <div role="status" aria-live="polite">
      <ng-container #host />
    </div>
  `,
})
export class NoticesComponent {
  private readonly tmpl = viewChild.required<TemplateRef<{ $implicit: string }>>('noticeTmpl');
  private readonly host = viewChild.required('host', { read: ViewContainerRef });

  add(msg: string): void {
    // $.tmpl('#noticeTmpl', msg).appendTo(...) に当たる
    this.host().createEmbeddedView(this.tmpl(), { $implicit: msg });
  }

  clear(): void {
    this.host().clear();
  }
}
```

足した断片も Angular のテンプレートなので、`{{ msg }}` はエスケープされます。差し込む先を `role="status"` の要素の中にしておくと、足した文が読み上げられます(差し込む要素そのものに `role="status"` を付けて足すと、読み上げられないことがある)。

#### 3.6 実行時に文字列のテンプレートが来る場合

CMS や API から「テンプレートの文字列」が届き、それを実行時に描きたい、という使い方は Angular の得意分野ではありません。Angular のテンプレートはビルド時にコンパイルされ、実行時に文字列からコンポーネントを作るには JIT コンパイラ(`@angular/compiler`)が要ります。

この場合は、次のどちらかにします。

- テンプレートはコードに置き、届くのは**データだけ**にする(推奨)
- どうしても文字列のテンプレートが要るなら、ロジックを持たないテンプレートエンジン(4 節)で HTML 文字列を作り、`[innerHTML]` で出す。Angular がサニタイズするので、イベントやコンポーネントは使えない

#### 3.7 SSR での注意

- Angular のテンプレートは、サーバーでもそのまま描ける。jquery.tmpl でブラウザが後から描いていた部分も、サーバーの HTML に含まれるようになる
- jquery.tmpl はブラウザの DOM と jQuery を前提にしている(`document.createElement` など。`pkg/jquery.tmpl.js:318`)。サーバーでは動かさない
- `ngTemplateOutlet`、子コンポーネント、`<ng-content>` も、サーバーで描ける
- 3.5 節の `createEmbeddedView` は、ボタンを押したときなど、利用者の操作から呼ぶ。サーバーで呼ぶ場面は普通は無い。描画のあとブラウザでだけ足したいものがあるなら、`afterNextRender` の中で呼ぶ

---

### 4. ほかの選択肢

Angular のアプリでは、テンプレートエンジンを足す必要はほとんどありません。3.6 節の「実行時に文字列のテンプレートが来る」場合に限った候補です。

| ライブラリ | 版(2026-11-27) | peerDependencies | 内容 |
|---|---|---|---|
| `jsrender` | 1.2.0 | なし | jquery.tmpl の後継として作者が案内しているもの(`pkg/README.md:3-8`)。タグの書き方が似ている |
| `mustache` | 4.2.0 | なし | ロジックを持たないテンプレート。値は既定でエスケープされる |
| `handlebars` | 4.7.10 | なし | Mustache の上位互換。ヘルパーを足せる |

いずれも中身は読んでいません。文字列のテンプレートを実行時に関数へコンパイルするライブラリは、jquery.tmpl と同じく CSP の `'unsafe-eval'` が要ることがあります。使う前に確かめます。

Angular CDK の Portal(`@angular/cdk/portal`)も、テンプレートやコンポーネントを別の場所に描く仕組みです。ただし **Spartacus は `@angular/cdk` に依存していません**。Spartacus ではアウトレットが同じ役割を担うので、足す理由は薄いです。

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| データを一覧や部品として描く | Angular のテンプレート(`{{ }}`、`@if`、`@for`) |
| 同じコンポーネント内で、同じ断片を何度も使う | `<ng-template #name>` + `ngTemplateOutlet` |
| 呼び出し側に描き方を決めさせる部品を作る | テンプレートを `contentChild` や `input` で受け、`ngTemplateOutlet` で描く |
| Spartacus 標準の画面の一部を差し替える・前後に足す | アウトレット(`cxOutletRef`、`provideOutlet`)。差し込み口が無ければ CMS のマッピングを差し替える(2.5 節) |
| Spartacus を使わない Angular アプリで、`$.template` の名前付きテンプレートや `{{wrap}}` を置き換える | 同じコンポーネント内なら `<ng-template>` + `ngTemplateOutlet`、ほかの部品と組み合わせるなら子コンポーネントと `<ng-content>`(3.2〜3.3 節)。アウトレットに当たる部品は要らない |
| `$.tmplItem` / `$item.update()` でデータを引いて描き直していた | `@for` のイベントにデータを渡し、signal を更新する(3.4 節) |
| `.appendTo()` で断片を足していく | まず配列に足して `@for` で描く。命令的に足すなら `ViewContainerRef.createEmbeddedView`(3.5 節) |
| `{{html …}}` で HTML を出していた | `[innerHTML]`。Angular が許さないもの(`style` 属性など)が要るなら [DOMPurify の章](dompurify.md) |
| 実行時に文字列のテンプレートが届く | まずデータだけ受け取る形に変える。無理なら Mustache などで文字列を作り `[innerHTML]` |

---

### 6. コンピュータサイエンスの観点から

- **実行時コンパイルとビルド時コンパイル**: jquery.tmpl は、ブラウザの中で毎回テンプレートを JS に変換します(`new Function`)。Angular はビルド時に変換を済ませ、ブラウザには結果の JS だけを送ります。前者は柔軟ですが、テンプレートの誤りが実行時まで見つからず、CSP の `'unsafe-eval'` も要ります。後者は型検査ができ、誤りがビルドで見つかります
- **文字列をつなぐか、DOM を差分で更新するか**: jquery.tmpl はテンプレートから HTML 文字列を作り、丸ごと DOM にします。データが変わると、その部分を作り直して入れ替えます(`$item.update()`、`pkg/jquery.tmpl.js:487-491`)。Angular はテンプレートの中の「変わり得る場所」だけを覚えておき、値が変わった場所だけを書き換えます。入力欄のフォーカスやスクロール位置が失われないのは、この違いによります
- **`with` 文の名残**: jquery.tmpl は `with($data)` でデータを変数のように見せています(`:330`)。`with` は、どの変数がどこから来るかを実行するまで決められないため、strict モードでは使えません。Angular のテンプレートは、どの名前がコンポーネントのどのプロパティかをコンパイル時に決めます
