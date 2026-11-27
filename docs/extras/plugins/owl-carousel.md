# Owl Carousel: 要素を横に並べ、スライドとして送るカルーセル

> **この章が答える問い**: アクセラレータの `owl.carousel.custom.js` は何をしていたのか。Spartacus には同じ役割の部品があるのか。Angular で自分で書くなら、どう書けばよいのか。自動再生はどう扱えばよいのか

> **根拠の取り方**:
> - **プラグイン**: アクセラレータが読むファイル名にバージョンが無いので、npm の最新版 `owl.carousel@2.3.4`(Owl Carousel 2)を読んだ。`src/js/` の本体とプラグイン 10 本。以下 `pkg/` はパッケージのルート。比較のため、1.x 系の `owlcarousel@1.3.3`(OwlFonk/OwlCarousel を作者以外が npm に載せたもの)も読んだ。以下 `v1/` はそのルート
> - **`.custom` について**: ファイル名に `.custom` が付いているので、アクセラレータ側で手が入っている。この章は元のプラグインについて書く。`.custom` での変更点と、アクセラレータが 1.x と 2.x のどちらを元にしているかは確認できない
> - **Spartacus**: SAP/spartacus `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`core/` は `core-libs/core/src/`、`fl/` は `feature-libs/`、`styles/` は `core-libs/styles/`(SCSS)を指す
> - 代替ライブラリのバージョンは 2026-11-27 に npm で確認

---

### 先に話し言葉で: Spartacus には 2 種類のカルーセルがある

Owl Carousel は、横に並べた要素を `transform: translate3d()` でずらして、スライドのように送るプラグインです。前後ボタン、ドット、ドラッグとスワイプ、画面幅ごとの表示数、ループ、自動再生を 1 つで持っています。

Spartacus には標準のカルーセルが 2 つあります。ページ送り型の **`cx-carousel`** と、横スクロール型の **`cx-carousel-scrolling`** です。商品カルーセルや商品画像のサムネイルは後者を使っています。どちらも自動再生とループは持っていません。

Angular で自分で書くなら、CSS の `scroll-snap` と `scrollBy()` で足ります。スワイプはブラウザの横スクロールがそのまま担います。自動再生が要るときは、止めるボタンを必ず付けます(WCAG 2.2.2)。

---

### 1. Owl Carousel は何をするか

#### 1.1 使い方

```js
$('.owl-carousel').owlCarousel({
  items: 4,
  loop: true,
  nav: true,
  dots: false,
  autoplay: true,
  autoplayTimeout: 5000,
  autoplayHoverPause: true,
  responsive: { 0: { items: 1 }, 640: { items: 2 }, 1024: { items: 4 } },
});

$('.owl-carousel').trigger('next.owl.carousel');  // 外から操作する
```

#### 1.2 主なオプション(2.3.4)

| オプション | 既定値 | 内容 | 場所 |
|---|---|---|---|
| `items` | `3` | 1 画面に並べる数 | `pkg/src/js/owl.carousel.js:182` |
| `loop` | `false` | 端まで行ったら最初に戻る(要素を複製する) | `:183` |
| `margin` / `stagePadding` | `0` | 要素の間隔、左右の余白 | `:193-194` |
| `mouseDrag` / `touchDrag` | `true` | マウスとタッチで引っ張って送る | `:188-189` |
| `autoWidth` | `false` | 要素ごとの幅を使う | `:198` |
| `smartSpeed` | `250` | 送るときのアニメーションの時間(ms) | `:203` |
| `responsive` | `{}` | 画面幅ごとにオプションを上書きする | `:207` |
| `responsiveRefreshRate` | `200` | `resize` を間引く時間(ms) | `:208` |
| `nav` / `navText` | `false` | 前後ボタン | `pkg/src/js/owl.navigation.js:129-133` |
| `dots` | `true` | ドット(ページ番号) | `owl.navigation.js:145` |
| `autoplay` / `autoplayTimeout` | `false` / `5000` | 自動再生と、その間隔 | `pkg/src/js/owl.autoplay.js:120-121` |
| `autoplayHoverPause` | `false` | マウスが乗っている間だけ止める | `owl.autoplay.js:122` |
| `lazyLoad` | `false` | `data-src` の画像を、表示する直前に読む | `pkg/src/js/owl.lazyload.js:84` |

1.x 系はオプション名が違います。`itemsDesktop: [1199, 4]` のような幅と数の組(`v1/owl-carousel/owl.carousel.js:1461-1465`)、`itemsCustom`(`:1460`)、`navigation` / `navigationText`(`:1476-1477`)、`pagination`(`:1481`)、`autoPlay` / `stopOnHover`(`:1473-1474`)です。`autoPlay: true` は 5000ms とみなされます(`:113-114`)。アクセラレータのコードを読むときは、どちらの名前で書かれているかで元の版の見当がつきます。

#### 1.3 中でどう動いているか

| 処理 | 中身 | 場所 |
|---|---|---|
| 送る | 並べた要素の親(stage)に `translate3d(xpx,0,0)` と `transition` を付ける。使えないブラウザでは jQuery の `animate({ left })` | `pkg/src/js/owl.carousel.js:933-958` |
| ループ | 先頭と末尾の要素を `outerHTML` で複製し、前後に足す。複製は「見た目だけの偽物」なので、中のイベントや状態は引き継がれない | `:322-344` |
| 画面幅の判定 | `window.innerWidth` を読み、`responsive` のキーのうち幅以下で最大のものを選ぶ。`matchMedia` は使わない(ソースに「`matchMedia` を使えるとよい」という TODO がある) | `:549-575`、`:1323-1335` |
| `resize` の間引き | `setTimeout` で `responsiveRefreshRate` ms 待ってから再計算する | `:685-687` |
| ドラッグ | `mousedown` / `touchstart` から始めて、移動量で stage をずらす | `:738-743`、`:755-` |
| 自動再生 | `setTimeout` を繰り返す。操作中とタブが裏にあるとき(`document.hidden`)は送らない | `pkg/src/js/owl.autoplay.js:131-141` |
| ホバーで止める | `mouseover` で止め、`mouseleave` で再開。キーボードのフォーカスでは止まらない | `owl.autoplay.js:86-95` |
| jQuery への登録 | `$.fn.owlCarousel`。`next` などの操作は `next.owl.carousel` のようなイベントでも呼べる | `owl.carousel.js:1713-1743` |

アクセシビリティの面では弱いところがあります。前後ボタンの既定の要素は `button type="button" role="presentation"` です(`owl.navigation.js:135`)。`role="presentation"` はボタンとしての意味を消します。ドットは中身が空の `<button role="button"><span></span></button>` で、読み上げる名前がありません(`owl.navigation.js:181-184`)。

---

### 2. Spartacus の標準にあるか

**結論: 一部ある。** カルーセルの部品は 2 つある。自動再生、ループ、ドラッグ、表示数の細かい設定は無い。

#### 2.1 `cx-carousel`(ページ送り型)

`CarouselComponent`(`sf/shared/components/carousel/carousel.component.ts:61-78`)。

```html
<cx-carousel
  [items]="items$"        <!-- Observable の配列。要素ごとに遅れて読める -->
  [template]="tpl"
  itemWidth="300px"       <!-- px か % -->
  [hideIndicators]="false"
/>
<ng-template #tpl let-item="item"> … </ng-template>
```

| 処理 | 中身 | 場所 |
|---|---|---|
| 1 ページの数 | `WindowRef.resize$` のたびに、ホスト要素の `clientWidth` ÷ `itemWidth` を切り捨てる。最低 1 | `sf/shared/components/carousel/carousel.service.ts:29-60` |
| `resize` の間引き | `debounceTime(300)` | `core/window/window-ref.ts:96-106` |
| ページの描き方 | `size` 個ずつ `.slide` にまとめ、表示中のものに `.active` を付ける | `sf/shared/components/carousel/carousel.component.html:39-71` |
| 送るときの見た目 | `.slide` を `opacity` で切り替え、`.item` を 0.25 秒ずつずらしてフェードインする。横に滑るのではない | `styles/scss/components/product/carousel/_carousel.scss:40-77` |
| 前後ボタン | 端では `aria-disabled`。ラベルは `carousel.previousSlide` / `nextSlide` | `carousel.component.html:6-37`、`:74-109` |
| ドット | `aria-label` にページ番号、`aria-current` で現在地 | `carousel.component.html:112-140` |
| キーボード | `cxFocusableCarouselItem` が付いた要素の間を左右キーで移動し、必要ならページを送る | `carousel.component.ts:210-287` |
| 隠れた要素 | `visibility: hidden` で Tab と読み上げから外す | `_carousel.scss:79-86` |
| SSR | `ngSkipHydration`。サーバーとブラウザで表示数が変わるため | `carousel.component.ts:57-65` |

使われている場所は、バナーのローテーション(`RotatingImagesComponent`。`sf/cms-components/content/banner-carousel/banner-carousel.component.html:1-7`、`itemWidth="100%"`)、画像ズームのサムネイル、検索ボックスの候補などです。

#### 2.2 `cx-carousel-scrolling`(横スクロール型)

`CarouselScrollingComponent`(`sf/shared/components/carousel-scrolling/carousel-scrolling.component.ts:53-67`)。入力は `items` / `template` / `title` / `trackByFn` / アイコンだけで、表示数の指定はありません。要素の幅は CSS で決まります。

| 処理 | 中身 | 場所 |
|---|---|---|
| 並べ方 | `overflow-x: auto` の横スクロール。`scroll-snap-type: x mandatory` と `scroll-snap-align: start` で要素の頭に止まる。スクロールバーは隠す | `styles/scss/components/product/carousel/_carousel-scrolling.scss:27-49` |
| スワイプ | ブラウザの横スクロールがそのまま担う。JS は書いていない | 同上 |
| 前後ボタン | `scrollBy({ left: 見えている幅, behavior: 'smooth' })` | `sf/shared/directives/horizontal-scrolling-position/horizontal-scrolling-position.directive.ts:149-185` |
| 端の判定 | 先頭と末尾に幅 0 の目印の `span` を置き、`IntersectionObserver` で見えているかを調べる。見えている幅は `ResizeObserver` で追う | `horizontal-scrolling-position.directive.ts:203-245`、`carousel-scrolling.component.html:29-47` |
| フォーカス | 要素にフォーカスが入ったら `scrollIntoView({ inline: 'nearest' })` | `carousel-scrolling.component.ts:177-190` |
| SSR | ブラウザでなければ監視を始めない | `horizontal-scrolling-position.directive.ts:122-123` |

使われている場所は、商品カルーセル(`ProductCarouselComponent`。`sf/cms-components/product/carousel/product-carousel/product-carousel.component.html:1-11`)、関連商品(`ProductReferencesComponent`)、商品画像のサムネイル(`sf/cms-components/product/product-images/product-images.component.html:10-16`)です。

#### 2.3 Owl Carousel との差

| 機能 | Owl Carousel 2.3.4 | `cx-carousel` | `cx-carousel-scrolling` |
|---|---|---|---|
| 送り方 | `translate3d` で滑らせる | ページ単位でフェード | ネイティブの横スクロール |
| 表示数 | `items` と `responsive` | `itemWidth` から自動計算 | CSS の幅で決まる |
| 前後ボタン | あり | あり | あり |
| ドット | あり | あり(`hideIndicators`) | 無い |
| ドラッグ・スワイプ | JS で実装 | 無い | ブラウザ標準のスクロール |
| ループ | 要素を複製 | 無い(端で止まる) | 無い |
| 自動再生 | あり | 無い | 無い |
| 遅延読み込み | `lazyLoad`(`data-src`) | 要素を Observable で渡す。画像は `cx-media` の `loading="lazy"` | 同左 |
| キーボード | 特に無い | 左右キー | 左右キー |
| 読み上げ | 弱い(1.3 節) | ラベル、`aria-current`、`aria-disabled` | ラベル、`aria-disabled` |

`sf/` と `fl/` と `integration-libs/` の `.ts` を `autoplay` で探すと、出てくるのは動画コンポーネントの `autoPlay` だけでした(`sf/cms-components/content/video/video.component.ts:45`)。カルーセルの自動再生は Spartacus に無いと言ってよいです。

---

### 3. Angular 標準で書くとどうなるか(Spartacus を使わない)

この節のコードは、`@angular/core` と `@angular/common`、ブラウザ標準の API だけで書きます。Spartacus の部品(`cx-carousel` など)を使う書き方は 2 節です。

考え方は 2.2 節の `cx-carousel-scrolling` と同じです。スクロールそのものはブラウザに任せ、Angular は「前後ボタン」「ページの印」「自動再生」だけを受け持ちます。

#### 3.1 前後ボタン、ドット、画面幅ごとの表示数

```ts
import {
  Component, DestroyRef, ElementRef, afterNextRender, afterRenderEffect,
  computed, inject, input, signal, viewChild,
} from '@angular/core';

export interface Slide { id: string; name: string; image: string; url: string; }

@Component({
  selector: 'app-carousel',
  template: `
    <section class="carousel" aria-roledescription="carousel" [attr.aria-label]="label()">
      <button type="button" class="nav" aria-label="前へ" [disabled]="atStart()" (click)="move(-1)">‹</button>
      <ul #track class="track" (scroll)="measure()">
        @for (item of items(); track item.id) {
          <li class="item">
            <a [href]="item.url">
              <img [src]="item.image" alt="" loading="lazy" />
              {{ item.name }}
            </a>
          </li>
        }
      </ul>
      <button type="button" class="nav" aria-label="次へ" [disabled]="atEnd()" (click)="move(1)">›</button>
      @if (pages() > 1) {
        <div class="dots">
          @for (p of pageList(); track p) {
            <button type="button" (click)="goTo(p)"
                    [attr.aria-label]="(p + 1) + ' / ' + pages() + ' ページ'"
                    [attr.aria-current]="p === page() ? 'true' : null"></button>
          }
        </div>
      }
    </section>
  `,
  styles: `
    :host { display: block; container-type: inline-size; }
    .track { --per-view: 1; --gap: 16px;
             display: flex; gap: var(--gap); margin: 0; padding: 0; list-style: none;
             overflow-x: auto; scroll-snap-type: x mandatory; scroll-behavior: smooth;
             overscroll-behavior-x: contain; }
    .item  { flex: 0 0 calc((100% - var(--gap) * (var(--per-view) - 1)) / var(--per-view));
             scroll-snap-align: start; }
    @container (min-width: 640px)  { .track { --per-view: 2; } }
    @container (min-width: 1024px) { .track { --per-view: 4; } }
    @media (prefers-reduced-motion: reduce) { .track { scroll-behavior: auto; } }
  `,
})
export class CarouselComponent {
  items = input.required<Slide[]>();
  label = input('おすすめ商品');

  private track = viewChild.required<ElementRef<HTMLElement>>('track');
  private pos = signal({ left: 0, width: 1, scroll: 1 });   // サーバーでは 1 ページとみなす

  atStart = computed(() => this.pos().left <= 0);
  atEnd   = computed(() => { const p = this.pos(); return p.left + p.width >= p.scroll - 1; });
  pages   = computed(() => { const p = this.pos(); return Math.max(1, Math.ceil(p.scroll / p.width - 0.01)); });
  page    = computed(() => this.atEnd() ? this.pages() - 1 : Math.round(this.pos().left / this.pos().width));
  pageList = computed(() => Array.from({ length: this.pages() }, (_, i) => i));

  constructor() {
    // 要素が描かれたあと(と items が変わったあと)に寸法を読む。ブラウザでだけ動く
    afterRenderEffect(() => { this.items(); this.measure(); });

    // 箱の幅が変わったら読み直す
    const destroyRef = inject(DestroyRef);
    afterNextRender(() => {
      const ro = new ResizeObserver(() => this.measure());
      ro.observe(this.track().nativeElement);
      destroyRef.onDestroy(() => ro.disconnect());
    });
  }

  measure() {
    const el = this.track().nativeElement;
    this.pos.set({ left: el.scrollLeft, width: el.clientWidth || 1, scroll: el.scrollWidth });
  }
  move(dir: 1 | -1) {
    const el = this.track().nativeElement;
    el.scrollBy({ left: dir * el.clientWidth });   // 見えている幅だけ送る。止まる位置は scroll-snap が決める
  }
  goTo(page: number) {
    const el = this.track().nativeElement;
    el.scrollTo({ left: page * el.clientWidth });
  }
}
```

- 画面幅ごとの表示数は、CSS 変数 `--per-view` とコンテナクエリで決める。JS で数えないので、サーバーとブラウザで HTML が同じになる。Owl の `responsive` は `window.innerWidth` で決まる(1.3 節)。ページ全体の幅で決めたいなら、`@container` を `@media` に変える
- 端の判定とページ数は、`scrollLeft` / `clientWidth` / `scrollWidth` から計算する。`scroll` は頻繁に起きるので、重くなるなら `requestAnimationFrame` で 1 フレームに 1 回にまとめる
- 前後ボタンは `<button>` なので、Tab と Enter / Space で使える。端では `disabled` にする。ボタンにフォーカスがあるまま `disabled` になるとフォーカスが外れるので、気になるなら `aria-disabled` にして `move()` の中で止める
- 中のリンクに Tab で入ると、ブラウザがその要素が見える位置までスクロールする。`cx-carousel-scrolling` が `scrollIntoView` でしていることは、横スクロールの箱ならブラウザが自分でする
- 左右の矢印キーは、横スクロールの箱にフォーカスがあればブラウザがスクロールする。箱にフォーカスを置けるようにするなら `tabindex="0"` と `aria-label` を付ける

Owl のオプションとの対応は次のとおりです。

| Owl のオプション | Angular 標準とブラウザ標準での書き方 |
|---|---|
| `items` / `responsive` | `--per-view` を `@container` か `@media` で変える |
| `margin` | `gap` |
| `stagePadding` | `.track` の `padding-inline` と `scroll-padding-inline` |
| `nav` / `navText` | `<button>` を 2 つ。中身はテンプレートに書く |
| `dots` | `pages()` と `goTo()` |
| `touchDrag` | ブラウザの横スクロール(JS は要らない) |
| `mouseDrag` | ブラウザ標準には無い。ホイール、トラックパッド、前後ボタンで足りることが多い。どうしても要るなら Pointer Events で `scrollLeft` を動かす |
| `smartSpeed` | `scroll-behavior: smooth`。時間は指定できない |
| `lazyLoad` | `<img loading="lazy">` |
| `autoplay` 系 | 3.2 節 |
| `loop` | 3.3 節 |

#### 3.2 自動再生を足す

WCAG 2.2.2(一時停止、停止、非表示)は、自動で始まり 5 秒より長く動き、ほかの内容と並んで出る動きに対して、止める仕組みを求めます。Owl の `autoplayHoverPause` はマウスでしか止まらず、これだけでは足りません。次の 4 つを入れます。

1. 見える「一時停止 / 再生」ボタン
2. フォーカスが中にある間とマウスが乗っている間は送らない
3. 動きを減らす設定(`prefers-reduced-motion`)の人には、自動では始めない
4. タブが裏にある間は送らない(Owl も `document.hidden` を見ている。1.3 節)

3.1 節のコンポーネントに足す部分だけを示します。

```ts
import { DOCUMENT, effect } from '@angular/core';   // DOCUMENT は v21 では @angular/core から import できる

autoplay = input(false);
interval = input(5000);

playing = signal(false);       // サーバーでは止めておく
hovered = signal(false);     // テンプレートから使うので private にしない
focused = signal(false);
private doc = inject(DOCUMENT);

constructor() {
  // …3.1 節の処理…
  afterNextRender(() => {      // ブラウザでだけ動く
    const reduce = this.doc.defaultView?.matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.playing.set(this.autoplay() && !reduce);
  });

  // playing() が true の間だけタイマーを動かす。false になるか、破棄されると止まる
  effect((onCleanup) => {
    if (!this.playing()) return;
    const id = setInterval(() => {
      if (this.hovered() || this.focused() || this.doc.hidden) return;
      if (this.atEnd()) this.goTo(0);   // 末尾まで来たら先頭へ戻す
      else this.move(1);
    }, this.interval());
    onCleanup(() => clearInterval(id));
  });
}
```

```html
<!-- テンプレートに足す。ボタンはカルーセルの先頭に置き、最初に見つかるようにする -->
<section … (pointerenter)="hovered.set(true)" (pointerleave)="hovered.set(false)"
           (focusin)="focused.set(true)" (focusout)="focused.set(false)">
  @if (autoplay()) {
    <button type="button" (click)="playing.set(!playing())">
      {{ playing() ? '一時停止' : '再生' }}
    </button>
  }
  …
</section>
```

- `effect()` はサーバーでも動くが、サーバーでは `playing()` が `false` のままなので、タイマーは作られない
- `focusout` は、中の要素から中の別の要素へ移るときにも起きる。厳密にするなら、`focusout` で `event.relatedTarget` が `section` の中にあるかを `contains()` で確かめる
- 送るたびに読み上げさせたいなら、止まっているときだけ `.track` に `aria-live="polite"` を付ける。自動で動いている間に読み上げ続けるのは煩わしい

#### 3.3 ループ

Owl のループは、要素を `outerHTML` で複製して前後に足します(1.3 節)。Angular で書くなら、複製は作りません。

- **横スクロール型(3.1 節)**: 末尾で「次へ」を押したら先頭へ戻す(`goTo(0)`)。Owl の `rewind` オプション(`pkg/src/js/owl.carousel.js:185`)と同じ振る舞い。3.2 節の自動再生もこの形
- **1 枚ずつのバナー型**: 「今何枚目か」を `signal` で持ち、`index.update((i) => (i + 1) % n)` で回す。表示は `transform: translateX(-100% × index)` で決める。書き方は [slideViewer の章](./jquery-slideviewer.md) 3.1 節と同じ
- 端から端へ「つながって見える」動きがどうしても要るなら、4 節のライブラリを使う(`embla-carousel-angular` なら、本体 `embla-carousel@8.6.0` の `loop` オプション。`esm/components/Options.d.ts:30`)

#### 3.4 SSR での注意

- サーバーには `window` も `matchMedia` も `ResizeObserver` も無い。これらは `afterNextRender()` か `afterRenderEffect()`(どちらもブラウザでだけ動く。`@angular/core@21.2.26` の `types/core.d.ts:2576`、`:2612`)の中で使う
- `document` が要るときは、グローバルの `document` ではなく `inject(DOCUMENT)` で受け取る。`window` は `inject(DOCUMENT).defaultView` で取る(サーバーでは `null` のことがある)
- サービスやディレクティブの中で、描画と関係なく「ブラウザかどうか」で分けたいなら、`isPlatformBrowser(inject(PLATFORM_ID))`(`@angular/common`)を使う
- サーバー側でタイマーを動かすと、アプリが安定せずに SSR が終わらないことがある。3.2 節のようにブラウザでだけタイマーを作る
- 後始末は `DestroyRef.onDestroy()` か、`effect()` の `onCleanup` で書く
- JS で表示数を数える作りは、サーバーとブラウザで HTML が変わる。2.1 節の `cx-carousel` が `ngSkipHydration` を付けているのはこのため。3.1 節のように CSS で幅を決める作りなら、この問題は起きない

---

### 4. ほかの選択肢

| ライブラリ | 版 | peerDependencies | Angular 21 で | メモ |
|---|---|---|---|---|
| `ngx-owl-carousel-o` | 最新 22.0.0、21 系は 21.0.3 | 21.0.3: `@angular/core` / `@angular/common` `^21.0.0`、`rxjs` | 21.0.3 なら可 | Owl Carousel 2 を Angular で書き直したもの。jQuery は不要。tarball に `@angular/animations` の参照は無い |
| `embla-carousel-angular` | 最新 22.0.0、21 系は 21.0.0 | 21.0.0: `@angular/core` / `@angular/common` `>=21.0.0` | 21.0.0 なら可 | 本体 `embla-carousel@8.6.0` は依存。自動再生は別パッケージ `embla-carousel-autoplay@8.6.0` |
| `swiper` | 14.4.0 | 無い | フレームワーク非依存 | Web Components 版(`swiper/element`)を `CUSTOM_ELEMENTS_SCHEMA` で使える |
| `keen-slider` | 6.8.6 | 無い | フレームワーク非依存 | 小さい |
| `@splidejs/splide` | 4.1.4 | 無い | フレームワーク非依存 | |

Angular CDK にはカルーセルの部品はありません。なお Spartacus は `@angular/cdk` に依存していません。

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| 商品を横に並べるだけ | `cx-carousel-scrolling`(商品カルーセルの標準) |
| バナーを 1 枚ずつ見せる | `cx-carousel` に `itemWidth="100%"`(`RotatingImagesComponent` の標準) |
| 標準の見た目を少し変えたい | SCSS を上書きする。`template` で中身を差し替える |
| スクロール型で、標準に無い振る舞いが少し要る | 3 節のように `scroll-snap` で自前のコンポーネントを書く |
| Spartacus を使わない Angular アプリで、横に並べて送るだけ | 3.1 節のコンポーネント(`scroll-snap` とコンテナクエリ)。ライブラリは要らない |
| Spartacus を使わず、自動再生も要る | 3.2 節を足す。ループやドラッグまで要るなら `embla-carousel-angular@21` |
| 自動再生、ループ、ドラッグが必須 | `embla-carousel-angular@21` か `ngx-owl-carousel-o@21`。自動再生には停止ボタンを付ける |
| Owl の設定をそのまま移したい | `ngx-owl-carousel-o@21`(オプション名がほぼ同じ) |

---

### 6. コンピュータサイエンスの観点から

- **「ずらす」から「スクロールさせる」へ**: Owl は、`overflow: hidden` の箱の中で stage を `translate3d` で動かす。スクロール位置、慣性、スワイプ、端での止まり方は、すべて JS で作り直している。CSS Scroll Snap が広く使えるようになってからは、スクロールそのものをブラウザに任せ、「どこで止まるか」だけを CSS で宣言できる。`cx-carousel-scrolling` はこの形
- **ループの複製は状態を壊す**: Owl のループは `outerHTML` で要素を複製する。複製された要素は別の DOM なので、Angular のコンポーネントやイベントは付いてこない。Angular の部品を中に入れるカルーセルでは、ループは複製ではなく、配列の並べ替え(循環バッファ)で作るほうが安全
- **`resize` から `ResizeObserver` と `IntersectionObserver` へ**: Owl と `cx-carousel` は `window` の `resize` を間引いて幅を読み直す。`cx-carousel-scrolling` は、箱そのものの幅を `ResizeObserver` で、端に来たかを `IntersectionObserver` で受け取る。ページ全体ではなく「その要素」に起きた変化だけが届く
