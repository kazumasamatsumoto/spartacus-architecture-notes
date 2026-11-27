# slideViewer 1.2: 画像を 1 枚ずつ横に送り、番号のボタンで切り替えるギャラリー

> **この章が答える問い**: アクセラレータの `jquery.slideviewer.custom.1.2.js`(商品画像のギャラリー)は何をしていたのか。Spartacus の商品画像コンポーネントで置き換えられるのか。自分で書くなら、どう書けばよいのか

> **根拠の取り方**:
> - **プラグイン**: npm の `jquery.slideviewer` は、npm が置いた「security holding package」(`0.0.1-security`)で、中身は無い。作者(Gian Carlo Mingati)のページ `gcmingati.net` は、この作業環境からは名前解決できず読めなかった。そこで、GitHub の公開リポジトリに置かれた `jquery.slideviewer.1.2.js` の写しを 3 つ取り、比べて読んだ。2 つはヘッダーが `slideViewer 1.2` / `Version: 1.2.3 (9-JULY-2010)` で、違いは読み込み中の画像のパス 1 行だけだった。もう 1 つは 1.2.1。以下 `sv/` は 1.2.3 の写し(91 行)を指す。**作者が配布した原本と同じかは確認できていない**
> - **`.custom` について**: ファイル名に `.custom` が付いているので、アクセラレータ側で手が入っている。この章は元のプラグインについて書く。`.custom` での変更点は確認できない
> - **Spartacus**: SAP/spartacus `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`fl/` は `feature-libs/`、`styles/` は `core-libs/styles/`(SCSS)を指す
> - 代替ライブラリのバージョンは 2026-11-27 に npm で確認

---

### 先に話し言葉で: 「メイン画像とサムネイル」は Spartacus の標準

slideViewer は、`<ul>` に並べた画像を横一列につなげ、`left` をアニメーションさせて 1 枚ずつ見せるプラグインです。画像の下に `1` `2` `3` … の番号のリンクを作り、押すとその画像まで滑ります。画像の左半分を押すと前へ、右半分で次へ進みます。

Spartacus では、商品画像は **`cx-product-images`**(CMS の `ProductImagesComponent`)が標準で表示します。メイン画像が 1 枚と、サムネイルの横スクロールです。サムネイルにフォーカスが入ると(クリックも含む)、メイン画像が切り替わります。滑るアニメーションと番号のボタンはありません。

「サムネイルで選ぶギャラリー」でよければ、標準のままで足ります。「横に滑る 1 枚ずつのスライド」が要るなら、Angular で `signal` 1 つと CSS の `transform` / `transition` で書けます。

---

### 1. slideViewer は何をするか

#### 1.1 使い方

```html
<div id="gallery" class="svw">
  <ul>
    <li><img src="1.jpg" alt="正面"></li>
    <li><img src="2.jpg" alt="側面"></li>
  </ul>
</div>
<script>
  $(window).on('load', function () {   // 画像の幅を読むので、読み込み後に呼ぶ
    $('#gallery').slideView({ easeFunc: 'easeInOutExpo', easeTime: 750 });
  });
</script>
```

#### 1.2 オプション(1.2.3)

| オプション | 既定値 | 内容 | 場所 |
|---|---|---|---|
| `easeFunc` | `"easeInOutExpo"` | 送るときのイージング。jQuery の本体には無い名前なので、`jquery.easing` が要る | `sv/:23` |
| `easeTime` | `750` | 送る時間(ms) | `sv/:24` |
| `uiBefore` | `false` | 番号のリンクを画像の上に置くか(既定は下) | `sv/:25` |
| `toolTip` | `false` | 番号にマウスを乗せると、画像の `alt` をツールチップで出す | `sv/:26` |
| `ttOpacity` | `0.9` | ツールチップの不透明度 | `sv/:27` |

ヘッダーには「jQuery v1.4.1 以降と `jquery.easing.1.2` が要る」と書かれています(`sv/:11-12`)。

#### 1.3 中でどう動いているか

| 処理 | 中身 | 場所 |
|---|---|---|
| 読み込み中の表示 | ページの準備ができたら、すべての `div.svw` の先頭にくるくる回る画像を足す。`slideView()` を呼ぶと消す | `sv/:16-18`、`:31` |
| 寸法を決める | **最初の画像**の幅と高さを読み、箱の大きさにする。`ul` の幅は「画像の幅 × 枚数」。全部の画像が同じ大きさである前提 | `sv/:33-39` |
| 番号のリンクを作る | 箱の後ろ(または前)に `div.stripTransmitter` を足し、`<a href="#">1</a>` … を並べる。`title` に画像の `alt` を入れる | `sv/:41-44` |
| 送る | 番号を押すと `current` クラスを付け替え、`ul` の `left` を `-(幅 × 番号)` へ `animate()` する | `sv/:45-51` |
| 画像を押して送る | 押した位置が箱の左半分なら前、右半分なら次の番号のリンクを `trigger("click")` する。端では反対の端へ戻る | `sv/:55-68` |
| ツールチップ | `body` に `div.tooltip` を足し、`.live('mousemove')` でマウスの位置に出す | `sv/:73-88` |
| ID の採番 | グローバル変数 `j` で `stripTransmitter0`、`1` … と番号を振る | `sv/:19`、`:90` |

**今の jQuery では、そのままでは動かない**: `sv/:35` の `.size()` は jQuery 3.0 で、`sv/:79`、`:85` の `.live()` は jQuery 1.9 で削除されました。アクセラレータが読み込む `jquery@3.5.1`([番外 4](../replacing-jquery.md) の調べ)の `dist/jquery.js` にも、どちらもありません。また 3.5.1 の `jQuery.easing` は `linear` と `swing` だけです(npm の `jquery@3.5.1` の `dist/jquery.js:7246-7254`)。`.custom` の変更には、このあたりの手直しが含まれていると考えられますが、確認はできていません(推測)。

**アクセシビリティ**: 番号のリンクは `href="#"` の `<a>` で、読み上げは「1」「2」だけです。画像を押して送る操作はマウスだけで、キーボードでは使えません。今どの画像かは `current` クラスで見た目にだけ出ています。

---

### 2. Spartacus の標準にあるか

**結論: 一部ある。** 商品画像のギャラリー(メイン画像とサムネイル)は標準にある。横に滑るスライドと番号のボタンは無い。

#### 2.1 `cx-product-images`

CMS の `ProductImagesComponent` に `ProductImagesComponent`(`selector: 'cx-product-images'`)が割り当てられています(`sf/cms-components/product/product-images/product-images.module.ts:32-33`、`product-images.component.ts:22`)。商品詳細ページに置くだけで動き、入力はありません。商品は `CurrentProductService` から取ります。

```html
<!-- sf/cms-components/product/product-images/product-images.component.html:1-27 -->
<cx-media [container]="main" … />                 <!-- メイン画像 -->
<cx-carousel-scrolling class="thumbs" [items]="thumbs" [template]="thumb" />
<ng-template #thumb let-item="item">
  <cx-media [container]="item.container" tabindex="0"
            (focus)="openImage(item.container)"
            [class.is-active]="isActive(item.container) | async" format="product" />
</ng-template>
```

| 処理 | 中身 | 場所 |
|---|---|---|
| 最初のメイン画像 | 商品の `images.PRIMARY` | `sf/cms-components/product/product-images/product-images.component.ts:42` |
| サムネイル | `images.GALLERY` を並べる。**2 枚未満なら出さない** | `product-images.component.ts:98-108` |
| 切り替え | サムネイルの `focus` で `openImage()` を呼び、メイン画像の `BehaviorSubject` を更新する | `product-images.component.ts:34`、`:57-59`、`product-images.component.html:23` |
| 選択中の印 | `zoom.url` が同じものに `is-active` を付ける | `product-images.component.ts:61-74` |
| サムネイルの並べ方 | `cx-carousel-scrolling`(横スクロールと `scroll-snap`。[Owl Carousel の章](./owl-carousel.md) 2.2 節) | `product-images.component.html:10-16` |
| LCP 対策 | メイン画像に `fetchPriority` を渡す(`cxLcpContext`) | `product-images.component.html:2-6` |
| 見た目 | 縦並び。画像は `aspect-ratio: 1 / 1` と `object-fit: scale-down`。サムネイルは幅 120px | `styles/scss/components/product/details/_product-images.scss:9-80` |

画像ズームのライブラリ(`@spartacus/product/image-zoom`)を入れると、同じ CMS コンポーネントがズーム付きのものに差し替わります([jQuery Zoom の章](./jquery-zoom.md))。そのダイアログの中には、前後ボタンと `cx-carousel` のサムネイルがあります。

#### 2.2 slideViewer との差

| 機能 | slideViewer 1.2.3 | `cx-product-images` |
|---|---|---|
| 見せ方 | 横一列の画像を滑らせる | メイン画像を差し替える(アニメーションなし) |
| 選び方 | 番号のリンク、画像の左右を押す | サムネイルを押すか、Tab でフォーカスする |
| 前後ボタン | 無い(画像の左右を押す) | 無い(ズームのダイアログにはある) |
| 画像の大きさ | 最初の画像の寸法に固定 | CSS で決める。`srcset` で解像度を選ぶ |
| キーボード | 番号のリンクに Tab で行ける | サムネイルに Tab で行き、フォーカスで切り替わる |
| 読み上げ | 「1」「2」… | 画像の `alt` |
| データ | HTML に書いた `<img>` | OCC の商品の `images`(`PRIMARY` / `GALLERY`) |

---

### 3. Angular 標準で書くとどうなるか(Spartacus を使わない)

この節のコードは、`@angular/core` とブラウザ標準の API だけで書きます。Spartacus の部品(`cx-product-images` など)を使う書き方は 2 節です。

「横に滑る 1 枚ずつのスライド」を書くなら、状態は「今何枚目か」の 1 つだけです。滑らせるのは CSS に任せます。

#### 3.1 番号のボタン、前後ボタン、キーボード

```ts
import { Component, computed, input, linkedSignal } from '@angular/core';

export interface GalleryImage { src: string; alt: string; }

@Component({
  selector: 'app-slide-viewer',
  template: `
    <section class="viewer" aria-roledescription="carousel" [attr.aria-label]="label()"
             (keydown.arrowleft)="step(-1)" (keydown.arrowright)="step(1)">
      <div class="viewport">
        <ul class="strip" [style.transform]="offset()">
          @for (img of images(); track img.src; let i = $index) {
            <li [attr.aria-hidden]="i !== index() ? 'true' : null">
              <img [src]="img.src" [alt]="img.alt" [attr.loading]="i === 0 ? null : 'lazy'" />
            </li>
          }
        </ul>
        @if (images().length > 1) {
          <button type="button" class="prev" aria-label="前の画像" (click)="step(-1)">‹</button>
          <button type="button" class="next" aria-label="次の画像" (click)="step(1)">›</button>
        }
      </div>
      <p class="status" aria-live="polite">{{ index() + 1 }} / {{ images().length }}: {{ current()?.alt }}</p>
      @if (images().length > 1) {
        <div class="pager">
          @for (img of images(); track img.src; let i = $index) {
            <button type="button" (click)="index.set(i)"
                    [attr.aria-current]="i === index() ? 'true' : null"
                    [attr.aria-label]="(i + 1) + '枚目: ' + img.alt"
                    [title]="img.alt">{{ i + 1 }}</button>
          }
        </div>
      }
    </section>
  `,
  styles: `
    .viewport { position: relative; overflow: hidden; aspect-ratio: 1 / 1; }
    .strip    { display: flex; height: 100%; margin: 0; padding: 0; list-style: none;
                transition: transform 750ms cubic-bezier(0.87, 0, 0.13, 1); }  /* easeInOutExpo に近い */
    .strip li { flex: 0 0 100%; }
    .strip img { width: 100%; height: 100%; object-fit: contain; }
    .prev, .next { position: absolute; inset-block: 0; width: 50%; opacity: 0; }  /* 画像の左半分・右半分 */
    .prev { inset-inline-start: 0; cursor: w-resize; }
    .next { inset-inline-end: 0; cursor: e-resize; }
    .prev:focus-visible, .next:focus-visible { opacity: 1; }
    @media (prefers-reduced-motion: reduce) { .strip { transition: none; } }
  `,
})
export class SlideViewerComponent {
  images = input.required<GalleryImage[]>();
  label = input('商品画像');

  // images が変わったら 0 枚目に戻る。ボタンで set() もできる
  index = linkedSignal({ source: this.images, computation: () => 0 });
  current = computed(() => this.images()[this.index()]);
  offset = computed(() => `translateX(${-100 * this.index()}%)`);

  step(dir: 1 | -1) {
    const n = this.images().length;
    if (n > 0) this.index.update((i) => (i + dir + n) % n);   // 端では反対の端へ(slideViewer と同じ)
  }
}
```

slideViewer の機能との対応は次のとおりです。

| slideViewer の機能(1 節) | この書き方 |
|---|---|
| 横一列に並べて `left` を `animate()` | `flex: 0 0 100%` で並べ、`transform` を `transition` で動かす。`easeTime` / `easeFunc` は `transition` の時間と `cubic-bezier()`。`jquery.easing` は要らない |
| 番号のリンク | `<button>`。`aria-label` に画像の `alt`、`aria-current` で今の画像 |
| 画像の左半分・右半分を押して送る | 画像の上に、透明な「前の画像」「次の画像」の `<button>` を半分ずつ重ねる。キーボードでも押せ、フォーカスが当たると見える |
| 端では反対の端へ戻る | `step()` の `% n` |
| `toolTip`(番号に乗せると `alt` を出す) | `title` 属性。読み上げには `aria-label` が効くので、ツールチップに頼らない。今の画像の説明は `.status` に文字で出す |
| `uiBefore`(番号を画像の上に置く) | テンプレートで `.pager` を前に書く |
| 読み込み中のくるくる | 要らない。`aspect-ratio` で場所を先に取るので、読み込みを待たずに配置が決まる |
| グローバルな連番 ID | 要らない。状態はコンポーネントのインスタンスが持つ |

- 左右の矢印キーは、フォーカスが `section` の中にあるときに効く。`(keydown.arrowleft)` は、キーの名前でイベントを絞る Angular のテンプレートの書き方
- `aria-hidden` は、見えていない画像を読み上げから外すため。画像の中にリンクやボタンを入れるなら、`aria-hidden` ではなく `inert` 属性にする(Tab でも入れなくなる)
- `.status` の `aria-live="polite"` で、切り替えたときに「2 / 5: 側面」と読み上げる

#### 3.2 ネイティブのスワイプが要るとき

`transform` で動かす書き方では、指で横に払っても送れません。スワイプが要るなら、`transform` の代わりに横スクロールと `scroll-snap` で書きます([Owl Carousel の章](./owl-carousel.md) 3.1 節)。`.item` を `flex: 0 0 100%` にすれば 1 枚ずつになります。番号のボタンは `scrollTo({ left: i * clientWidth })` で送ります。

#### 3.3 SSR での注意

- 3.1 節の書き方は `window` も `document` も使わないので、サーバーでもそのまま描ける。サーバーとブラウザで同じ HTML になる(最初は 0 枚目)
- slideViewer のように画像の寸法を読む作りは、サーバーでは寸法が 0 になる。寸法が要るなら、`afterNextRender()`(ブラウザでだけ動く。`@angular/core@21.2.26` の `types/core.d.ts:2576`)の中で読む
- 3.2 節のスクロール型で `scrollTo()` を使うのはクリックの中だけなので、サーバーでは呼ばれない。最初の表示位置を JS で変えたいときだけ `afterNextRender()` を使う
- `document` が要るときは `inject(DOCUMENT)`(v21 では `@angular/core` から import できる)、ブラウザかどうかで分けたいときは `isPlatformBrowser(inject(PLATFORM_ID))`(`@angular/common`)を使う

---

### 4. ほかの選択肢

| ライブラリ | 版 | peerDependencies | Angular 21 で | メモ |
|---|---|---|---|---|
| `ng-gallery` | 12.0.0 | `@angular/core` / `@angular/common` / `@angular/cdk` `>=16.0.0`、`rxjs` | peerDependencies の上では可 | ギャラリー専用。**`@angular/cdk` が要る**。Spartacus は CDK に依存していないので、新しく足すことになる |
| `photoswipe` | 5.4.4 | 無い | フレームワーク非依存 | 全画面で見るライトボックス。ピンチでの拡大も持つ |
| `lightgallery` | 3.0.0 | 無い | フレームワーク非依存 | ライセンスが `GPL-3.0-only` か商用 |
| カルーセルのライブラリ | — | — | — | `embla-carousel-angular@21`、`swiper` など。[Owl Carousel の章](./owl-carousel.md) 4 節 |

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| メイン画像とサムネイルで足りる | `cx-product-images`(標準のまま) |
| 見た目だけ変えたい(縦並びを横並びに、など) | `_product-images.scss` の `%cx-product-images` を上書きする |
| 拡大も要る | `@spartacus/product/image-zoom`([jQuery Zoom の章](./jquery-zoom.md)) |
| 横に滑るスライドと番号のボタンが要る | 3.1 節の自前コンポーネントを作り、CMS の `ProductImagesComponent` に割り当てる |
| Spartacus を使わない Angular アプリで、横に滑るギャラリーが要る | 3.1 節のコンポーネント(`linkedSignal` と CSS の `transform`)。ライブラリは要らない |
| Spartacus を使わず、スワイプも要る | 3.2 節の `scroll-snap` で書く |
| 全画面で見せたい | `photoswipe` |

---

### 6. コンピュータサイエンスの観点から

- **寸法を読むか、比率で宣言するか**: slideViewer は、最初の画像の `width()` を読んで箱の幅を決める。画像が読み終わるまで幅は 0 なので、`window` の `load` を待って呼ぶ必要があった。CSS の `%`、`flex: 0 0 100%`、`aspect-ratio` で比率を宣言すれば、読み込みを待たずに配置が決まる。レイアウトのずれ(CLS)も起きにくい
- **アニメーションの主体**: jQuery の `animate({ left })` は、JS がフレームごとに `left` を書き換える。毎回レイアウトの計算がやり直しになる。CSS の `transition` と `transform` なら、ブラウザが合成(コンポジット)の段階だけで動かせる
- **グローバルな連番 ID**: slideViewer は、グローバル変数 `j` で DOM の ID を振る。同じページに部品が増えたり消えたりすると、番号が衝突する。Angular のコンポーネントは状態をインスタンスに持つので、DOM の ID で部品を探す必要がない
