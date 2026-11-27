# waitForImages: 要素の中の画像が全部読み終わるまで待つ

> **この章が答える問い**: アクセラレータの `jquery.waitforimages.min.js` は何をしていたのか。Spartacus には画像の読み込みを待つ仕組みがあるのか。Angular では、そもそも画像を待つ必要があるのか。待つなら、どう書けばよいのか

> **根拠の取り方**:
> - **プラグイン**: アクセラレータが読むファイル名にバージョンが無いので、npm の最新版 `jquery.waitforimages@2.4.0`(Alex Dickson 作、MIT)を読んだ。本体は `src/jquery.waitforimages.js` の 226 行(`dist/` は同じものとその圧縮版)。以下 `pkg/` はパッケージのルート
> - **Spartacus**: SAP/spartacus `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`fl/` は `feature-libs/`、`styles/` は `core-libs/styles/`(SCSS)を指す
> - jQuery の非推奨 API は npm の `jquery@3.5.1` と `jquery@4.1.0` で確かめた
> - 代替ライブラリのバージョンは 2026-11-27 に npm で確認

---

### 先に話し言葉で: 1 枚ずつなら `cx-media` の `loaded`、全部なら数えればよい

waitForImages は、指定した要素の中にある画像を探し、全部の読み込みが終わったら(失敗も含めて)コールバックを呼ぶプラグインです。CSS の背景画像も対象にできます。jQuery の時代は、画像の寸法を読んでから配置を決めるプラグイン(カルーセルやズーム)の前に、よく呼ばれていました。

Spartacus には「要素の中の画像を全部待つ」仕組みはありません。代わりに、画像の部品 **`cx-media`** が 1 枚ごとに **`loaded` 出力**を出し、`is-loading` / `is-initialized` / `is-missing` のクラスを付けます。画像ズームは、この `loaded` を待ってからズームボタンを押せるようにしています。

Angular では、多くの場合、待つ必要そのものがありません。`aspect-ratio` や `width` / `height` 属性で場所を先に決めれば、配置は画像の読み込みに左右されません。どうしても待つなら、`(load)` と `(error)` を数える `signal` か、`HTMLImageElement.decode()` で書けます。

---

### 1. waitForImages は何をするか

#### 1.1 使い方

```js
// コールバックで受け取る
$('.gallery').waitForImages(function () {
  // 全部終わった(this は .gallery)
}, function (loaded, count, success) {
  // 1 枚終わるごと(this はその img)。success は失敗なら false
}, true);   // true = 背景画像なども待つ

// Deferred で受け取る
$('.gallery').waitForImages({ waitForAll: true })
  .progress(function (loaded, count, success) { … })
  .done(function () { … });
```

#### 1.2 API

| API | 内容 | 場所 |
|---|---|---|
| `.waitForImages(finished, each, waitForAll)` | 引数を並べて渡す形 | `pkg/src/jquery.waitforimages.js:81-88` |
| `.waitForImages({ finished, each, waitForAll })` | オブジェクトで渡す形 | `:73-78` |
| `.waitForImages(true)` | `waitForAll` だけ渡し、戻り値の Promise で受け取る形 | `:82-83` |
| 戻り値 | jQuery の `Deferred` の `promise()`。1 枚ごとに `notify`、全部で `resolve` | `:56`、`:201`、`:210`、`:223` |
| `$.waitForImages.hasImageProperties` | `waitForAll` のときに見る CSS プロパティ。既定は `backgroundImage`、`listStyleImage`、`borderImage`、`borderCornerImage`、`cursor` | `:22-29` |
| `$.waitForImages.hasImageAttributes` | 見る属性。既定は `srcset` | `:30` |
| `:has-src` / `:uncached` | jQuery のセレクタを足す。`src` が空でない `img`、まだ読み終わっていない(`!complete`)`img` | `:34-50` |

#### 1.3 中でどう動いているか

| 処理 | 中身 | 場所 |
|---|---|---|
| 画像を集める(通常) | 子孫の `img:has-src` の `src` を集める | `pkg/src/jquery.waitforimages.js:161-168` |
| 画像を集める(`waitForAll`) | 自分を含む全要素について、`img` の `src`、`getComputedStyle` で読んだ CSS プロパティの `url(...)`、`srcset` 属性を集める。要素の数だけ計算済みスタイルを読むので重い | `:109-159` |
| 0 枚なら | すぐに完了にする | `:176-179` |
| 読み込みを確かめる | 集めた URL ごとに `new Image()` を作り、`load` か `error` を 1 回だけ待つ。ページ上の `img` そのものではなく、**同じ URL をもう一度読ませて**、キャッシュから返るのを待つ作り | `:183-221` |
| `srcset` | 対応ブラウザでは `srcset` と `sizes` も写す | `:16-19`、`:216-219` |
| 数える | 1 枚終わるごとに `each` と `notify`、全部終わったら `finished` と `resolve` | `:190-212` |

**今の jQuery との関係**: `:100` の `$.isFunction` と `:82` の `$.type` は、`jquery@3.5.1` では非推奨の API を集めた `src/deprecated.js` に入っています(`:61`、`:64`)。3.5.1 では動きます。npm の最新の `jquery@4.1.0` の `dist/jquery.js` には、どちらもありません。jQuery 4 に上げると、このプラグインはそのままでは動きません。

**気をつけること**: `loading="lazy"` の画像があると、プラグインの `new Image()` がその場で読み込みを始めてしまいます。遅延読み込みを打ち消します。

---

### 2. Spartacus の標準にあるか

**結論: 一部ある。** 1 枚ずつの読み込み完了は `cx-media` の `loaded` で受け取れる。「要素の中の全部を待つ」部品は無い。

#### 2.1 `cx-media` の読み込みの状態

`MediaComponent`(`selector: 'cx-media'`。`sf/shared/components/media/media.component.ts:50`)。

```html
<cx-media [container]="product.images?.PRIMARY" format="product"
          [loading]="'eager'"
          (loaded)="onLoaded($event)" />   <!-- true: 読めた / false: 失敗か画像なし -->
```

| 仕組み | 中身 | 場所 |
|---|---|---|
| `loaded` 出力 | `img` の `load` で `true`、`error` か画像が無いときに `false` を出す | `sf/shared/components/media/media.component.ts:122`、`:179-184`、`:199-208`、`media.component.html:25-26`、`:43-44` |
| 状態のクラス | `is-loading`(読み込み中)、`is-initialized`(終わった)、`is-missing`(失敗か画像なし)をホストに付ける | `media.component.ts:134`、`:141`、`:148` |
| `loading` 入力 | `'lazy'` か `'eager'`。省くと全体の設定に従う | `media.component.ts:89` |
| 全体の設定 | `MediaConfig.imageLoadingStrategy`。既定は `LAZY` | `sf/shared/components/media/media.config.ts:76`、`media.service.ts:163-168` |
| 優先して読む | `fetchPriority` が `high` なら、`loading` の指定にかかわらず `eager` にする | `media.component.ts:217-222` |

`loaded` を使っている例は、画像ズームのダイアログです。拡大前と拡大後の `cx-media` の `(loaded)` で `imageLoaded` を `true` にし、それまではズームボタンを `disabled` にしています(`fl/product/image-zoom/components/product-image-zoom/product-image-zoom-view/product-image-zoom-view.component.html:16-32`、`:66`、`product-image-zoom-view.component.ts:426-428`)。

状態のクラスは、SCSS からも使えます。商品画像には、読み込み中にスピナーを出す、少し縮めて見せる、といった切り替えの変数があります(既定はどれも `false`)。

```scss
// styles/scss/components/product/details/_product-images.scss:1-5
$spinWhileLoading: false !default;
$spinWhileWaiting: false !default;
$overlayWhileLoading: false !default;
$zoomThumbOnHover: false !default;
$zoomOutWhileLoading: false !default;
```

`true` にすると、`cx-media.is-loading` などのクラスに合わせて効きます(`_product-images.scss:38-64`)。

#### 2.2 waitForImages との差

| 機能 | waitForImages 2.4.0 | `cx-media` |
|---|---|---|
| 単位 | 要素の中の全部 | 1 枚ずつ |
| 受け取り方 | コールバック、Deferred | `loaded` 出力(`EventEmitter<Boolean>`)、CSS クラス |
| 失敗 | `each` の第 3 引数が `false`。完了には数える | `loaded` が `false`、`is-missing` |
| 背景画像 | `waitForAll` で対象 | 対象外(`cx-media` は `img` / `picture` だけ) |
| 読み方 | 同じ URL を `new Image()` で読み直す | ページ上の `img` の `load` / `error` をそのまま使う |
| 遅延読み込み | 打ち消す | 尊重する(既定は `loading="lazy"`) |

`sf/`、`fl/`、`integration-libs/` の `.ts` を `new Image()`、`.decode()`、`naturalWidth` で探しても、見つかりませんでした。Spartacus の中に、画像を JS で読み直して待つコードはありません。

---

### 3. Angular で書くとどうなるか

#### 3.1 まず、待たなくて済むようにする

waitForImages が要ったのは、画像の寸法が決まるまで配置が決まらなかったからです。今は CSS で先に場所を取れます。

```css
.thumb img { width: 100%; aspect-ratio: 1 / 1; object-fit: contain; }
```

`img` に `width` と `height` の属性を書いても、ブラウザは縦横比を先に計算します(`cx-media` は `media.width` / `media.height` があれば属性に出します。`media.component.html:40-41`)。

#### 3.2 1 枚を待つ

```html
<img [src]="src" (load)="ready.set(true)" (error)="failed.set(true)" />
@if (!ready()) { <span class="spinner" aria-hidden="true"></span> }
```

Spartacus の中なら、`<img>` の代わりに `<cx-media (loaded)="ready.set($event)" />` と書きます。

#### 3.3 複数を全部待つ

```ts
import { Component, computed, input, signal } from '@angular/core';

@Component({
  selector: 'app-gallery',
  template: `
    <div class="gallery" [class.is-ready]="allDone()" [attr.aria-busy]="!allDone()">
      @for (img of images(); track img.src) {
        <img [src]="img.src" [alt]="img.alt" loading="eager"
             (load)="done.update((n) => n + 1)" (error)="done.update((n) => n + 1)" />
      }
    </div>
  `,
})
export class GalleryComponent {
  images = input.required<{ src: string; alt: string }[]>();
  done = signal(0);
  allDone = computed(() => this.done() >= this.images().length);
}
```

- 画像の配列が変わるときは、`done` を 0 に戻す
- `loading="lazy"` の画像は、画面に近づくまで読まれない。「全部待つ」とずっと終わらないことがある。待つ画像は `eager` にするか、見えている分だけを待つ
- JS で 1 枚の準備を確かめたいなら、`HTMLImageElement.decode()` が使える。読み込みとデコードが終わると解決する Promise を返す。失敗すると拒否される

```ts
private img = viewChild.required<ElementRef<HTMLImageElement>>('img');

constructor() {
  afterNextRender(async () => {           // ブラウザでだけ動く
    try { await this.img().nativeElement.decode(); this.ready.set(true); }
    catch { this.failed.set(true); }
  });
}
```

背景画像を待ちたいときは、CSS の背景をやめて `<img>`(`object-fit` で背景のように見せる)にするのが簡単です。

**SSR での注意**: サーバーでは画像は読まれず、`load` も起きない。「読めたら表示する」作りにすると、サーバーの HTML では画像が隠れたままになる。サーバーの HTML では見える状態にしておき、ブラウザで状態を足す。`decode()` や `new Image()` は `afterNextRender()` の中で呼ぶ(`@angular/core@21.2.26` の `types/core.d.ts:2576`)。

---

### 4. ほかの選択肢

| ライブラリ | 版 | peerDependencies | Angular 21 で | メモ |
|---|---|---|---|---|
| `imagesloaded` | 5.0.0 | 無い(依存は `ev-emitter`) | フレームワーク非依存 | waitForImages と同じ役割で、jQuery が無くても動く。背景画像も `{ background: true }` で待てる。`afterNextRender()` の中で呼ぶ |

Angular 向けの専用ライブラリを足す理由は、ほとんどありません。3 節の数行で足ります。

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| 画像が読めるまで場所が崩れる | 待たずに、`aspect-ratio` か `width` / `height` 属性で場所を取る |
| 読み込み中の見た目を変えたい | `cx-media` の `is-loading` / `is-missing` のクラスを CSS で使う。商品画像なら `$spinWhileLoading` などの変数 |
| 1 枚読めたら何かをしたい | `cx-media` の `(loaded)`(`true` / `false`) |
| 複数を全部待ちたい | `(load)` / `(error)`(または `loaded`)を `signal` で数える |
| 背景画像も含めて待ちたい | `<img>` に置き換える。どうしても背景なら `imagesloaded` |

---

### 6. コンピュータサイエンスの観点から

- **バリア同期**: waitForImages がしているのは、N 個の非同期処理が全部終わるのを待つ「バリア」で、`Promise.allSettled` と同じ形。失敗も「終わった」に数えるので、1 枚が壊れていても永遠に待つことはない
- **観測のために読み直す**: プラグインは、ページ上の `img` を監視せず、同じ URL の `new Image()` を作ってキャッシュに当てる。当時、`complete` や `load` がブラウザごとに不安定だった(キャッシュ済みの画像で `load` が起きない、など)ことへの回避策と考えられる。今は `decode()` があり、ページ上の要素そのものに「準備できたか」を問える
- **待つより宣言する**: 寸法を JS で測ってから配置する作りは、読み込みの順序に依存する。`aspect-ratio` で比率を宣言すれば、レイアウトは画像を待たずに決まる。Cumulative Layout Shift(CLS)という指標が生まれたのは、この「後から寸法が決まってずれる」問題を測るため
