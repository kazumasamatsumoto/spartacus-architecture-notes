# 番外 4. jQuery の置き換えをどう考えるか: 「DOM を探して書き換える」から「状態を書き換える」へ

> **この章が答える問い**: アクセラレータの `acc.*.js` に大量にある jQuery のコードを、Spartacus(Angular)に移すとき、何をどう考えればよいのか。1 行ずつ書き換えればよいのか。直接 DOM を触ってよい場面はあるのか。`$.ajax` の先にあったものはどうなるのか

> **根拠の取り方**:
> - **jQuery**: npm の `jquery@3.5.1`(アクセラレータの `javaScript.tag` が読み込んでいる版)と、npm の公開日時の記録
> - **Angular**: npm の `@angular/core@21.2.26` の型定義と、`@angular/animations@21.2.26` の非推奨表示
> - **Spartacus**: [SAP/spartacus](https://github.com/SAP/spartacus) `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`fl/` は `feature-libs/` を指す
> - 件数は 2026-11-27 に `grep` で数えた。`.spec.ts` は除いた

---

### 先に話し言葉で: jQuery は「部品」ではなく「考え方」だった

jQuery の置き換えは、プラグインの置き換えとは性質が違います。プラグインはカルーセルやモーダルといった「部品」なので、同じ役割の部品を探せば済みます。jQuery は部品ではありません。**「DOM を探して、直接書き換える」という書き方そのもの**です。

```js
// jQuery: 「どの要素を、どう変えるか」を書く
$('.js-mini-cart-link').on('click', function () {
  $('.mini-cart-layer').addClass('open');
  $('.js-mini-cart-count').text(count);
});
```

Angular では、DOM を探しません。**状態(変数)を変えると、テンプレートがその状態に合わせて DOM を描き直します。**

```html
<!-- Angular: 「状態と見た目の関係」を書く -->
<button (click)="open.set(true)">カート</button>
<div class="mini-cart-layer" [class.open]="open()">
  {{ count() }}
</div>
```

そのため、jQuery を 1 行ずつ Angular の API に書き換えても、うまくいきません。`$('.x').addClass('open')` を `renderer.addClass(el, 'open')` に変えるのは、書き方を変えただけです。DOM を直接書き換える考え方は、そのまま残ります。

置き換えでやることは、jQuery のコードを読んで **「これはどの状態を表現しているのか」を取り出し、その状態をコンポーネントに持たせる** ことです。DOM を直接触ってよいのは、Angular が描いていない DOM を扱うときなど、少数の例外だけです(4 節)。

---

### 1. jQuery が担っていた役割

jQuery が登場した 2006 年頃は、ブラウザごとに DOM の API が違い、標準の機能も足りませんでした。jQuery はその差を埋める層でした。今は、ほとんどの役割がブラウザの標準か Angular に移っています。

| 役割 | jQuery | 今の標準(ブラウザ) | Angular / Spartacus |
|---|---|---|---|
| 要素を探す | `$('.x')` | `querySelector` | 探さない。テンプレートに書く。どうしても要るなら `viewChild()` |
| 表示を変える | `.addClass()`、`.show()`、`.text()`、`.html()` | `classList`、`textContent` | `[class.x]`、`@if`、`{{ }}`、`[innerHTML]` |
| イベント | `.on('click', …)`、イベントの委譲 | `addEventListener` | `(click)`、`host: { '(click)': … }` / `@HostListener` |
| 通信 | `$.ajax`、`$.get`、`$.post` | `fetch` | `HttpClient`。Spartacus では Facade / Connector / Adapter 経由([15 章](../15-facade-connector-adapter.md)) |
| 起動 | `$(document).ready` | `DOMContentLoaded` | コンポーネントの生成、`ngOnInit`、`APP_INITIALIZER` |
| 非同期の待ち合わせ | `$.Deferred`、`.done()` | `Promise` | `Observable`(RxJS)、Signal |
| 便利関数 | `$.each`、`$.extend`、`$.trim`、`$.isArray` | `forEach`、`Object.assign` / スプレッド構文、`trim`、`Array.isArray` | 同左 |
| アニメーション | `.fadeIn()`、`.slideUp()`、`.animate()` | CSS の `transition` / `@keyframes`、Web Animations API | CSS、`animate.enter` / `animate.leave`(8 節) |
| データの保持 | `.data('key', v)` | `dataset` | コンポーネントのフィールド、Signal、サービス |
| 部品どうしの連絡 | `.trigger('customEvent')`、`ACC.xxx` を直接呼ぶ | `CustomEvent` | `output()`、サービスの `Subject`、Spartacus の `EventService` |

**Spartacus は jQuery に依存していません。** Spartacus のルートの `package.json` にも、各ライブラリの `package.json` にも、`jquery` は出てきません。

---

### 2. 置き換えの例

#### 2.1 表示の切り替え

```js
// jQuery
$('.js-toggle-details').on('click', function () {
  $(this).toggleClass('active');
  $(this).next('.details').slideToggle();
});
```

```ts
// Angular: 状態は「開いているか」の 1 つだけ
@Component({
  selector: 'app-details',
  template: `
    <button [class.active]="open()" (click)="open.update((v) => !v)"
            [attr.aria-expanded]="open()">詳細</button>
    @if (open()) {
      <div class="details" animate.enter="slide-in" animate.leave="slide-out">…</div>
    }
  `,
})
export class DetailsComponent {
  open = signal(false);
}
```

jQuery の `$(this).next('.details')` は、「ボタンの次にある要素」という **DOM の位置関係** に頼っています。HTML の構造を変えると壊れます。Angular では、ボタンと詳細が同じ状態(`open`)を見ているので、位置関係に頼りません。`aria-expanded` も同じ状態から出せます。

#### 2.2 通信して画面を更新する

```js
// jQuery: JSP のコントローラに POST し、返ってきた HTML を差し込む
$.post(ACC.config.encodedContextPath + '/cart/add', $form.serialize())
  .done(function (html) {
    $('#addToCartLayer').html(html);
    ACC.minicart.refreshMiniCartCount();
  });
```

```ts
// Spartacus: Facade に頼むだけ。ミニカートは同じ状態を見ているので勝手に更新される
this.activeCartFacade.addEntry(productCode, quantity);
```

(`ActiveCartFacade.addEntry` は `fl/cart/base/root/facade/active-cart.facade.ts:100`)

ここで変わるのは、フロントのコードだけではありません。

- **送り先が変わる**: `/cart/add` は JSP のコントローラです。Spartacus からは呼べません。OCC(`/occ/v2/…`)に同じ機能があるかを確認し、無ければバックエンドに作ってもらいます([12 章](../12-backend-api-granularity.md))
- **返ってくるものが変わる**: アクセラレータでは、サーバーが **HTML の断片** を返し、jQuery がそれを差し込むことがよくありました(カート追加後のレイヤー、ミニカート、クイックビューなど)。ヘッドレスでは JSON を返し、HTML はフロントが描きます([13 章](../13-jsp-to-headless.md))
- **ほかの部品への通知が要らなくなる**: `refreshMiniCartCount()` のように、ほかの部品を明示的に呼んで更新させる必要はありません。カートの状態は 1 か所(NgRx の Store)にあり、それを見ている部品がすべて描き直されます([5 章](../05-api-to-state.md))

#### 2.3 部品どうしの連絡

```js
// jQuery: 別の部品のメソッドを直接呼ぶ、または独自イベントを投げる
$(document).trigger('cart:updated', [cartData]);
$(document).on('cart:updated', function (e, data) { … });
```

| 関係 | Angular / Spartacus |
|---|---|
| 親と子 | `input()` / `output()` |
| 離れた部品どうしで、データを共有する | サービスに状態を持たせる(Spartacus の Facade がこれにあたる) |
| 離れた部品どうしで、「起きたこと」を知らせる | Spartacus の `EventService`(`core-libs/core/src/event/event.service.ts:47`)。カート追加の成功は `CartAddEntrySuccessEvent`(`fl/cart/base/root/events/cart.events.ts:66`)。タグマネージャー連携もここにつなぐ |

---

### 3. jQuery のコードを読むときの 3 つの問い

`acc.*.js` の関数を 1 つずつ読み、次の 3 つを書き出します。これが Angular 側の設計の材料になります。

1. **これはどの状態を表現しているか**: 「開いている」「選ばれている」「読み込み中」「件数」など。状態が見つかれば、DOM の操作はテンプレートの束縛に置き換わる
2. **その DOM は誰が描いているか**: 自分のテンプレートなら、束縛に置き換える。サードパーティの部品が描いた DOM なら、4 節の例外として扱う
3. **いつ実行されるか**: ページを開いたとき、クリックしたとき、通信が終わったとき。Spartacus は SSR で動くので、**サーバー上で実行されても壊れないか** も確認する。`window` や `document` に触る処理は、ブラウザでだけ動かす

---

### 4. 直接 DOM を触ってよい例外

Spartacus 本体にも、DOM を直接触るコードはあります(件数は `sf/` と `fl/` の `.ts` のうち、該当するファイルの数)。

| 書き方 | ファイル数 |
|---|---|
| `ElementRef` | 69 |
| `nativeElement` | 60 |
| `WindowRef` | 33 |
| `@HostListener` | 29 |
| `@HostBinding` | 28 |
| `Renderer2` | 23 |
| `querySelector` | 21 |
| `inject(DOCUMENT)` / `@Inject(DOCUMENT)` | 9 |
| `fromEvent(` | 1 |

ただし、使われる場面は限られています。

| 場面 | Spartacus での例 | 書き方 |
|---|---|---|
| **Angular が描いていない DOM に手を入れる** | ng-select(サードパーティ)が描いた入力欄に、`role="combobox"` や `aria-expanded` を後から付ける(`sf/shared/components/ng-select-a11y/ng-select-a11y.directive.ts:40-41`, `:110-152`) | `ElementRef` で自分の要素を取り、その中を `querySelector` で探し、`Renderer2.setAttribute` で書く |
| **フォーカスを動かす** | ダイアログを閉じたら、開いたボタンにフォーカスを戻す(`sf/layout/launch-dialog/services/launch-dialog.service.ts:64`, `:147-156`) | `ElementRef.nativeElement.focus()` |
| **外部のスクリプトを読み込む** | Web Components の JS を `<script>` で読み込む(`sf/cms-structure/page/component/handlers/web-component.handler.ts:105-114`) | `inject(DOCUMENT)` と `Renderer2.createElement('script')` |
| **ブラウザのイベントを Observable にする** | 画像ズームのクリックとダブルクリック(`fl/product/image-zoom/components/product-image-zoom/product-image-zoom-view/product-image-zoom-view.component.ts:336-340`) | `fromEvent(element.nativeElement, 'click')` |
| **画面の大きさを知る** | `BreakpointService`([番外 3](breakpoint-observer.md)) | `WindowRef` |

例外のときに守ること:

- **`window` と `document` をグローバルから直接読まない**: Spartacus の `WindowRef` か、Angular の `inject(DOCUMENT)` を使う。SSR ではグローバルの `window` が無いので、直接読むとサーバー側で落ちる
- **描いたあとに測る処理は `afterNextRender` で**: 要素の大きさや位置を測る処理は、描画が終わってから、ブラウザでだけ動かす。Angular の `afterNextRender` がこのための API(Spartacus 本体の `sf/` と `fl/` には、まだ使っている箇所が無い)
- **自分のテンプレートが描いた要素の中身を、外から書き換えない**: Angular が次に描き直したとき、書き換えが消えるか、食い違う

---

### 5. 棚卸しの手順

`acc.*.js` を `grep` で分類すると、作業量と、バックエンドへの依頼が見えます。

| 探す文字列 | 分類 | 移行先 |
|---|---|---|
| `$.ajax`、`$.get`、`$.post`、`.load(` | 通信 | Facade。**送り先の URL を一覧にして、OCC に対応する API があるかを確認する**(バックエンドへの依頼の元になる) |
| `.html(`、`.append(`、`.replaceWith(` に、通信の結果を渡している箇所 | サーバーが返す HTML の差し込み | JSON を返す API に変え、HTML はコンポーネントで描く |
| `.addClass`、`.removeClass`、`.toggleClass`、`.show`、`.hide`、`.toggle` | 表示の状態 | Signal と `[class.x]`、`@if` |
| `.on(`、`.click(`、`.change(`、`.submit(` | イベント | テンプレートの `(event)` |
| `.val(`、`.serialize(`、`.prop('checked')` | フォームの値 | Reactive Forms |
| `.trigger(`、`ACC.<別のモジュール>.` の呼び出し | 部品どうしの連絡 | サービス、`EventService` |
| `.fadeIn`、`.slideDown`、`.animate(` | アニメーション | CSS、`animate.enter` / `animate.leave` |
| `$(window).on('resize'`、`enquire.register` | 画面の大きさ | `BreakpointService`([番外 3](breakpoint-observer.md))、CSS のメディアクエリ |
| `ACC.config.` | サーバーから渡された設定値 | Spartacus の設定(`provideConfig`)、またはサイトのコンテキスト |
| `_autoload` 配列 | 起動時に呼ばれる関数 | その画面のコンポーネント |

特に 1 行目の **通信の送り先の一覧** は、早めに作ります。JSP のコントローラにしか無い処理は、フロントだけでは移せないからです。

---

### 6. jQuery を残すという選択肢

期限の都合で、一部の画面に jQuery を残すこともできます(`angular.json` の `scripts` に入れる)。ただし、次の問題を抱えます。

| 問題 | 中身 |
|---|---|
| DOM の持ち主が 2 人になる | Angular が描いた DOM を jQuery が書き換えると、次に描き直したとき食い違う |
| SSR で動かない | jQuery のコードはブラウザでしか動かない。サーバーで描いた HTML とブラウザでの見た目がずれる |
| バンドルが増える | `jquery@3.5.1` の `jquery.min.js` は 89,476 バイト(gzip 後 約 30KB)。これにプラグインが加わる |
| 版が古い | アクセラレータの 3.5.1 は 2020-05 の版。現行は 4.x(4.0.0 が 2026-01、4.1.0 が 2026-11 に公開)。残すなら更新も必要になる |

残す場合は、**撤去の期限** と、**jQuery が触ってよい DOM の範囲**(Angular が描かない領域だけ)を決めておきます。

---

### 7. アニメーション

jQuery の `.fadeIn()` や `.slideUp()` は、JS でスタイルを少しずつ変える仕組みでした。今は CSS の `transition` / `@keyframes` で済みます。

Angular 側では、要素が出入りするときのアニメーションに `animate.enter` / `animate.leave` を使います。以前の `@angular/animations` パッケージ(`trigger()`、`state()`、`transition()`)は **Angular 20.2 で非推奨** になり、v23 で削除される予定です(`@angular/core@21.2.26` の型定義 `types/_discovery-chunk.d.ts:5363`、npm の `@angular/animations@21.2.26` の非推奨表示)。古い記事の書き方は使わないようにします。

Spartacus 本体は `@angular/animations` を使っていません(`sf/` と `fl/` に `import` が無い)。

---

### 8. コンピュータサイエンスの観点から

- **命令的と宣言的**: jQuery は「何をどの順で変えるか」を書く **命令的** なスタイル。Angular のテンプレートは「状態と見た目の関係」を書く **宣言的** なスタイル。命令的なコードでは、画面の正しさは「すべての操作が正しい順で行われたか」に依存する。宣言的なコードでは、画面は常に「今の状態を関数に通した結果」なので、状態さえ正しければ画面も正しい
- **状態の置き場所**: jQuery のコードでは、状態が DOM そのもの(`class` や `data-*`)に置かれていることが多い。DOM が「真実の唯一の出どころ」になるため、別の部品が同じ情報を知りたいとき、DOM を読みに行くしかない。Angular では状態をコンポーネントやサービスに置き、DOM はその写しにすぎない
- **差分の計算を誰がやるか**: 命令的なコードでは、「前の画面から何を変えるか」を人間が考える。Angular はテンプレートをコンパイルして「どの束縛がどの DOM に対応するか」を記録しておき、変更検知のときに値が変わった束縛だけを書き換える([16 章](../16-change-detection.md)、[17 章](../17-zone-rendering.md))。React の仮想 DOM とは方式が違うが、「差分の計算をフレームワークに任せる」点は同じ
- **互換層の役目が終わった**: jQuery は、ブラウザごとの差を吸収する互換層だった。`querySelector`、`classList`、`fetch`、`Promise` などが標準になり、ブラウザ間の差が小さくなったことで、互換層としての役目はほぼ終わっている
