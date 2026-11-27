# jQuery Zoom: 画像にマウスを乗せると、その場所を大きな画像で拡大する

> **この章が答える問い**: アクセラレータの `jquery.zoom.custom.js` は何をしていたのか。Spartacus には画像を拡大する仕組みがあるのか。あるなら、どう有効にし、どう動くのか。自分で書くなら、どう書けばよいのか

> **根拠の取り方**:
> - **プラグイン**: アクセラレータが読むファイル名にバージョンが無いので、npm の最新版 `jquery-zoom@1.7.22`(Jack Moore 作、MIT)を読んだ。本体は `jquery.zoom.js` の 236 行。以下 `pkg/` はパッケージのルート
> - **`.custom` について**: ファイル名に `.custom` が付いているので、アクセラレータ側で手が入っている。この章は元のプラグインについて書く。`.custom` での変更点は確認できない
> - **Spartacus**: SAP/spartacus `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`core/` は `core-libs/core/src/`、`fl/` は `feature-libs/` を指す
> - 代替ライブラリのバージョンは 2026-11-27 に npm で確認

---

### 先に話し言葉で: Spartacus には「ダイアログで拡大」がある

jQuery Zoom は、画像の上に大きな画像を重ね、マウスの位置に合わせて動かすプラグインです。マウスを乗せると拡大し、離すと戻ります。クリックで切り替える、押している間だけ拡大する、という動かし方も選べます。

Spartacus には **`@spartacus/product/image-zoom`** という画像ズームの機能ライブラリがあります。入れると、商品画像のコンポーネントがズーム付きのものに差し替わります。ただし動き方は jQuery Zoom と違います。メイン画像を押すとダイアログが開き、その中で画像を押すと 2 倍に拡大し、マウスやタッチで動かします。ページの上でマウスを乗せただけで拡大する動きはありません。

「乗せるだけで拡大」が要るなら、Angular で書けます。CSS の `transform: scale()` と `transform-origin` を、Pointer Events で更新するだけです。

---

### 1. jQuery Zoom は何をするか

#### 1.1 使い方

```js
// 画像を包む要素に付ける。url を省くと、中の <img> の src を使う
$('.js-zoom').zoom({ url: 'large.jpg', on: 'mouseover', magnify: 1 });

$('.js-zoom').trigger('zoom.destroy');   // 外す
```

#### 1.2 オプション

| オプション | 既定値 | 内容 | 場所 |
|---|---|---|---|
| `url` | `false` | 拡大に使う大きな画像の URL。省くと中の `img` の `data-src`、`currentSrc`、`src` の順に探す | `pkg/jquery.zoom.js:8`、`:99-107` |
| `on` | `'mouseover'` | 拡大の始め方。`'mouseover'`、`'grab'`(押している間)、`'click'`(押すと始まり、どこかを押すと終わる)、`'toggle'`(押すたびに切り替え) | `:12`、`:136-196` |
| `touch` | `true` | タッチでも動かす | `:13`、`:199-222` |
| `magnify` | `1` | 大きな画像を、さらに何倍にするか | `:16`、`:44-45` |
| `duration` | `120` | フェードイン・アウトの時間(ms) | `:11` |
| `target` | `false` | 拡大した画像を出す先の要素(既定は自分自身) | `:10`、`:88` |
| `callback` / `onZoomIn` / `onZoomOut` | `false` | 大きな画像を読み終えたとき、拡大・縮小したときに呼ぶ | `:9`、`:14-15` |

#### 1.3 中でどう動いているか

| 処理 | 中身 | 場所 |
|---|---|---|
| 大きな画像を読む | `document.createElement('img')` に `url` を入れる。読み終わるまで何も起きない | `pkg/jquery.zoom.js:92`、`:117`、`:231` |
| 重ねる | 出す先の要素を `position: relative` / `overflow: hidden` にし、大きな画像を `position: absolute`、`opacity: 0` で中に足す。`role="presentation"`、`alt=""` | `:33-50`、`:229-230` |
| 比率を出す | 「(大きな画像の幅 − 枠の幅) ÷ 元の要素の幅」を `xRatio` にする。高さも同じ | `:53-69` |
| 動かす | マウスの位置(`pageX - offset.left`)を枠の中に収め、`-比率` を掛けて大きな画像の `left` / `top` に入れる | `:70-79` |
| 見せる・隠す | jQuery の `fadeTo()` で `opacity` を 0 と 1 の間で変える | `:120-133` |
| タッチ | `touchstart` で拡大、`touchmove` で動かす、`touchend` で戻す。どれも `preventDefault()` するので、その上ではページがスクロールしない | `:199-222` |
| 外す | `zoom.destroy` イベントで、付けたイベントと画像を消し、`position` / `overflow` を元に戻す | `:109-115` |

キーボードで使う手段はありません。拡大の操作は、すべてマウスとタッチのイベントに付いています。

---

### 2. Spartacus の標準にあるか

**結論: 一部ある。** 画像の拡大は、機能ライブラリ `@spartacus/product/image-zoom` にある。ただし「ダイアログを開いて、その中で拡大する」形で、「マウスを乗せるだけで拡大」は無い。

#### 2.1 有効にする

- schematics の機能名は `Image-Zoom`(`core-libs/schematics/src/shared/libs-constants.ts:340`)。エントリポイントは `@spartacus/product/image-zoom`、`/root`、`/assets`(`:133-135`)
- ルートモジュールは、CMS の `ProductImagesComponent` が出てきたときにこの機能を遅延読み込みするよう登録する(`fl/product/image-zoom/root/product-image-zoom-root.module.ts:11-26`)
- 機能モジュールは、`ProductImagesComponent` の割り当てを `ProductImageZoomProductImagesComponent` に差し替える(`fl/product/image-zoom/components/product-image-zoom/product-image-zoom.module.ts:53-59`)。セレクタは標準と同じ `cx-product-images`(`product-image-zoom-product-images.component.ts:22`)

#### 2.2 どう動くか

以下 `zoom/` は `fl/product/image-zoom/components/product-image-zoom/` を指します。

| 処理 | 中身 | 場所 |
|---|---|---|
| ページ上の表示 | メイン画像、「拡大」ボタン(`cx-product-image-zoom-trigger`)、サムネイルの `cx-carousel-scrolling` | `zoom/product-image-zoom-product-images/product-image-zoom-product-images.component.html:1-41` |
| ダイアログを開く | メイン画像か「拡大」ボタンを押すと、`LaunchDialogService.launch(LAUNCH_CALLER.PRODUCT_IMAGE_ZOOM)`。閉じたら「拡大」ボタンにフォーカスを戻す | `product-image-zoom-product-images.component.html:4`、`zoom/product-image-zoom-trigger/product-image-zoom-trigger.component.ts:63-87` |
| ダイアログの設定 | `LayoutConfig.launch.PRODUCT_IMAGE_ZOOM` に `inline: true`、`DIALOG_TYPE.DIALOG` | `zoom/default-product-image-zoom-layout.config.ts:10-18` |
| ダイアログの中 | `cx-product-image-zoom-view`。前後ボタン、画像、ズームボタン、`cx-carousel` のサムネイル(幅 70px) | `zoom/product-image-zoom-view/product-image-zoom-view.component.html:1-98`、`zoom/product-image-zoom-thumbnails/product-image-zoom-thumbnails.component.html:2-9` |
| 拡大の始め方 | `md` 以上の幅ではクリック、`lg` 未満ではダブルクリックで切り替える(`BreakpointService`) | `product-image-zoom-view.component.ts:334-345` |
| 拡大のしかた | 拡大中は `.cx-zoom-container`(`overflow: hidden`)の中の `img` に `transform: scale(2)` | `fl/product/image-zoom/styles/_product-image-zoom-view.scss:70-95` |
| マウスで動かす | ポインタの位置が真ん中に来るよう `left` / `top` を計算し、`Renderer2.setStyle` で入れる。はみ出しすぎないよう 60px の余白で止める | `product-image-zoom-view.component.ts:280-292`、`:306-323`、`:374-400`、`:409-424` |
| タッチで動かす | `touchmove` の移動量を足していく | `product-image-zoom-view.component.ts:251-273` |
| キーボード | 機能トグル `a11yKeyboardAccessibleZoom` が有効なら(既定で `true`。`core/features-config/feature-toggles/config/feature-toggles.ts:1033`)、ズームイン・アウトのボタンが出る。画像を読み終えるまでは押せない(`cx-media` の `loaded` を使う) | `product-image-zoom-view.component.html:63-91`、`:15-34`、`product-image-zoom-view.component.ts:227-244`、`:426-428` |
| 拡大に使う画像 | 拡大画像の `cx-media` には `format` を渡していない。`format` が無いと、`MediaService` は設定にある一番大きい形式を選ぶ | `product-image-zoom-view.component.html:24-27`、`sf/shared/components/media/media.service.ts:255-275` |

#### 2.3 jQuery Zoom との差

| 機能 | jQuery Zoom 1.7.22 | `@spartacus/product/image-zoom` |
|---|---|---|
| どこで拡大するか | ページの上、その場 | ダイアログの中 |
| 始め方 | `mouseover` / `grab` / `click` / `toggle` | クリック(`md` 以上)、ダブルクリック(`lg` 未満)、ズームボタン |
| 倍率 | 大きな画像の実寸 × `magnify` | `scale(2)` に固定(SCSS) |
| 拡大用の画像 | `url` で別に指定 | 同じ画像群のうち一番大きい形式 |
| 動かし方 | マウスの位置に比例 | ポインタの位置を中心に寄せる |
| タッチ | あり(ページのスクロールを止める) | あり |
| キーボード | 無い | ズームボタン(機能トグル) |
| ギャラリー | 無い(別のプラグインと組み合わせる) | 前後ボタンとサムネイルを含む |

#### 2.4 Spartacus の部品と組み合わせる例

3.1 節の自前のコンポーネントを Spartacus の中で使うときは、`img` を `cx-media` にし、`container` に商品の画像群を渡します。形式の選び方と `srcset` を Spartacus に任せられます。拡大したときの画像は、`format` を渡さない `cx-media` にすると、2.2 節と同じく一番大きい形式が選ばれます。作ったコンポーネントは、CMS の `ProductImagesComponent` に割り当てて差し替えます。

---

### 3. Angular 標準で書くとどうなるか(Spartacus を使わない)

この節のコードは、`@angular/core` とブラウザ標準の API だけで書きます。Spartacus の部品(`cx-media`、`@spartacus/product/image-zoom` など)を使う書き方は 2 節です。

「乗せるだけで、その場で拡大」を書くなら、大きな画像を重ねずに、同じ `img` を `transform: scale()` で拡大し、`transform-origin` をポインタの位置にします。画像の寸法を読む必要がありません。

#### 3.1 乗せて拡大、押している間だけ拡大、押して切り替え

```ts
import { Component, computed, input, linkedSignal, output, signal } from '@angular/core';

type ZoomOn = 'mouseover' | 'grab' | 'toggle';   // jQuery Zoom の on に合わせた名前

@Component({
  selector: 'app-zoom',
  template: `
    <div class="frame" [class.is-zoomed]="zoomed()"
         (pointerenter)="enter()" (pointerleave)="leave()"
         (pointerdown)="down()" (pointerup)="up()" (click)="clickFrame()"
         (pointermove)="move($event)">
      <img [src]="shownSrc()" [attr.srcset]="zoomed() && largeReady() ? null : srcset()" [alt]="alt()"
           [style.transform]="zoomed() ? 'scale(' + magnify() + ')' : null"
           [style.transform-origin]="x() + '% ' + y() + '%'" />
    </div>
    <button type="button" [attr.aria-pressed]="zoomed()" (click)="setZoom(!zoomed())"
            (keydown.arrowleft)="nudge(-10, 0, $event)" (keydown.arrowright)="nudge(10, 0, $event)"
            (keydown.arrowup)="nudge(0, -10, $event)" (keydown.arrowdown)="nudge(0, 10, $event)">
      拡大
    </button>
  `,
  styles: `
    .frame { overflow: hidden; cursor: zoom-in; touch-action: pan-y; }
    .frame.is-zoomed { cursor: zoom-out; }
    .frame img { display: block; width: 100%; transition: transform 120ms; }
    @media (prefers-reduced-motion: reduce) { .frame img { transition: none; } }
  `,
})
export class ZoomComponent {
  src = input.required<string>();
  srcset = input<string>();
  alt = input('');
  large = input<string>();          // 拡大に使う別の大きな画像(jQuery Zoom の url)
  on = input<ZoomOn>('mouseover');
  magnify = input(2);
  zoomIn = output<void>();
  zoomOut = output<void>();

  zoomed = signal(false);
  x = signal(50);
  y = signal(50);
  // large が変わったら「まだ読んでいない」に戻る
  largeReady = linkedSignal({ source: this.large, computation: () => false });
  shownSrc = computed(() => (this.zoomed() && this.largeReady() ? this.large()! : this.src()));

  enter() { if (this.on() === 'mouseover') this.setZoom(true); }
  leave() { if (this.on() !== 'toggle') this.setZoom(false); }
  down()  { if (this.on() === 'grab') this.setZoom(true); }
  up()    { if (this.on() === 'grab') this.setZoom(false); }
  clickFrame() { if (this.on() === 'toggle') this.setZoom(!this.zoomed()); }

  move(e: PointerEvent) {
    const r = (e.currentTarget as HTMLElement).getBoundingClientRect();
    this.x.set(clamp(((e.clientX - r.left) / r.width) * 100));
    this.y.set(clamp(((e.clientY - r.top) / r.height) * 100));
  }

  // 拡大中は、ボタンにフォーカスがある状態で矢印キーを押すと、拡大する場所が動く
  nudge(dx: number, dy: number, e: Event) {
    if (!this.zoomed()) return;
    e.preventDefault();              // ページがスクロールしないように
    this.x.update((v) => clamp(v + dx));
    this.y.update((v) => clamp(v + dy));
  }

  setZoom(on: boolean) {
    if (on === this.zoomed()) return;
    this.zoomed.set(on);
    if (on) { this.loadLarge(); this.zoomIn.emit(); } else { this.zoomOut.emit(); }
  }

  // 大きな画像は、初めて拡大したときに読む。読み終わるまでは元の画像を拡大して見せる
  private loadLarge() {
    const url = this.large();
    if (!url || this.largeReady()) return;
    const img = new Image();          // イベントの中からしか呼ばれないので、サーバーでは動かない
    img.src = url;
    img.decode().then(
      () => { if (this.large() === url) this.largeReady.set(true); },
      () => { /* 読めなければ元の画像のまま */ },
    );
  }
}

const clamp = (v: number) => Math.min(100, Math.max(0, v));
```

jQuery Zoom のオプションとの対応は次のとおりです。

| jQuery Zoom のオプション(1.2 節) | この書き方 |
|---|---|
| `url` | `large`。初めて拡大したときに `new Image()` と `decode()` で読み、読み終わったら `src` を差し替える |
| `on: 'mouseover'` | `pointerenter` / `pointerleave` |
| `on: 'grab'` | `pointerdown` / `pointerup` |
| `on: 'click'` / `'toggle'` | `click` で切り替える(`'toggle'`)。「どこかを押すと終わる」`'click'` が要るなら、`inject(DOCUMENT)` の `click` を `afterNextRender()` の中で受け、`DestroyRef.onDestroy()` で外す |
| `touch` | Pointer Events がタッチも受け取る。`touch-action: pan-y` で縦のスクロールはブラウザに残す |
| `magnify` | `magnify`(`scale()` の倍率) |
| `duration` | `transition` の時間 |
| `target`(別の場所に出す) | 同じ画像を `target` 側の箱に置き、そちらに `transform` を付ける。座標は `x()` / `y()` をそのまま使える |
| `callback` / `onZoomIn` / `onZoomOut` | `output()` の `zoomIn` / `zoomOut`。読み終わりは `largeReady()` |
| `zoom.destroy` | 要らない。イベントはテンプレートに書いているので、コンポーネントが消えると外れる |

- マウスとタッチは Pointer Events でまとめて受け取れる。jQuery Zoom のように `mouse*` と `touch*` を別々に書かなくてよい
- jQuery Zoom はタッチで `preventDefault()` するので、画像の上ではページがスクロールしなかった。`touch-action: pan-y` なら、縦に払えばページがスクロールし、横に動かせば拡大の位置が動く
- キーボードの人のために、拡大を切り替えるボタン(`aria-pressed`)を付け、矢印キーで場所を動かせるようにする。jQuery Zoom にはキーボードの手段が無かった(1.3 節)
- 拡大した画像は見た目だけの変化なので、`alt` はそのままでよい
- 画像の読み込みを待つ書き方は、[waitForImages の章](./jquery-waitforimages.md) 3 節にまとめた

#### 3.2 SSR での注意

- `pointermove` などのイベントはブラウザでしか起きないので、3.1 節のコードはサーバーでもそのまま描ける。最初の状態(拡大していない)はサーバーとブラウザで同じ
- `getBoundingClientRect()` と `new Image()` は、イベントの中でだけ呼んでいる。コンストラクタや `ngOnInit` で呼ぶと、サーバーで失敗する
- 大きな画像を先に読んでおきたい(最初の拡大を速くしたい)なら、`afterNextRender()`(ブラウザでだけ動く。`@angular/core@21.2.26` の `types/core.d.ts:2576`)の中で `loadLarge()` を呼ぶ
- `document` や `window` が要るときは、グローバルではなく `inject(DOCUMENT)`(v21 では `@angular/core` から import できる)と、その `defaultView` を使う。描画と関係なく分けたいときは `isPlatformBrowser(inject(PLATFORM_ID))`(`@angular/common`)
- 後始末は `DestroyRef.onDestroy()` で書く

---

### 4. ほかの選択肢

| ライブラリ | 版 | peerDependencies | Angular 21 で | メモ |
|---|---|---|---|---|
| `ngx-image-zoom` | 3.0.0 | **無い**(依存は `tslib` だけ) | peerDependencies で判断できない | Angular 向け。npm の最終更新は 2023-10-31。使う前に Angular 21 でビルドできるか確かめる必要がある |
| `drift-zoom` | 1.5.1 | 無い | フレームワーク非依存 | jQuery Zoom に近い「乗せると横に拡大」。BSD-2 |
| `medium-zoom` | 1.1.2 | 無い | フレームワーク非依存 | 押すと画面いっぱいに拡大する |
| `@panzoom/panzoom` | 4.6.2 | 無い | フレームワーク非依存 | ドラッグ、ホイール、ピンチで拡大・移動 |
| `photoswipe` | 5.4.4 | 無い | フレームワーク非依存 | 全画面のギャラリー。ピンチで拡大 |

フレームワーク非依存のライブラリは、`afterNextRender()` の中で初期化し、`DestroyRef.onDestroy()` で後始末します。

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| 拡大できればよい(ダイアログでよい) | `@spartacus/product/image-zoom` を入れる。機能トグル `a11yKeyboardAccessibleZoom` は既定で有効なので、切らない |
| 倍率や見た目を変えたい | `_product-image-zoom-view.scss` の `scale(2)` などを上書きする |
| ページの上で、乗せるだけで拡大したい | 3.1 節の自前コンポーネントを作り、2.4 節のように `ProductImagesComponent` に割り当てる |
| Spartacus を使わない Angular アプリで、その場で拡大したい | 3.1 節のコンポーネント(`transform: scale()` と Pointer Events)。ライブラリは要らない |
| Spartacus を使わず、ダイアログで大きく見せたい | ブラウザ標準の `<dialog>` と `showModal()` の中に 3.1 節のコンポーネントを置く。全画面のギャラリーまで要るなら `photoswipe` |
| 乗せると横に別枠で拡大したい | `drift-zoom` を薄いコンポーネントで包む |
| ピンチやホイールでの拡大が要る | `@panzoom/panzoom` か `photoswipe` |

---

### 6. コンピュータサイエンスの観点から

- **座標の写像**: jQuery Zoom の中心は、「元の画像の上の位置」を「大きな画像の位置」に一次関数で写す計算だけ(`left × -xRatio`)。`transform-origin` を使う書き方では、この写像をブラウザの描画に任せている。拡大の中心をポインタの位置に置けば、その点が動かないまま周りが広がる
- **2 枚の画像か、1 枚の画像か**: jQuery Zoom は、大きな画像を別に読み、重ねる。画質はよいが、読み込みを待つ必要がある。`transform: scale()` は同じ画像を引き伸ばすだけなので、すぐに出るが、元の解像度が足りないとぼやける。`srcset` と `sizes` を使えば、ブラウザが画面の密度に合わせて大きいほうを選べる
- **入力の統一**: マウス、タッチ、ペンを別々のイベントで扱っていた時代の書き方が、Pointer Events で 1 つにまとまった。`touch-action` で「どのジェスチャーをブラウザに残すか」を宣言できるので、`preventDefault()` で全部止める必要もなくなった
