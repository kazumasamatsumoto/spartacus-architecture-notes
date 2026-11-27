# syncHeight: 並んだ要素の高さを、一番高いものに揃える

> **この章が答える問い**: アクセラレータの `jquery.syncheight.custom.js` は何をしていたのか。Spartacus では、商品の一覧のカードの高さはどう揃っているのか。Angular で高さを揃えたいとき、JS は要るのか

> **根拠の取り方**:
> - **プラグイン**: Dirk Ginader 氏の syncHeight(MIT / GPL の二重ライセンス)。npm には本家が無い(npm の `syncheight-mp` は第三者のフォーク)。そこで GitHub の [ginader/syncHeight](https://github.com/ginader/syncHeight) の `master`(コミット `b1ea6cdda77a0de1a87618a2b44683e0ce3dc055`、2015-03-17)を読んだ。`package.json` とファイルの見出しの版は 1.5。以下 `pkg/` はリポジトリのルート
> - **`.custom` について**: ファイル名に `.custom` が付いているので、アクセラレータ側で手が入っている。この章は元のプラグインについて書く。`.custom` での変更点と、元にした版は確認できない
> - **Spartacus**: SAP/spartacus `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`styles/` は `core-libs/styles/`(SCSS)を指す
> - 代替の方法は CSS とブラウザ標準の API なので、ライブラリのバージョンの確認は無い

---

### 先に話し言葉で: 高さ揃えは、今は CSS の仕事

syncHeight は、指定した要素の高さを測り、一番高いものに合わせて `min-height` を書き込むプラグインです。商品の一覧で、名前の長さが違うカードの高さを揃えるのに使われていました。CSS の flexbox がまだ使えなかった時代の道具です。

Spartacus に同じプラグインはありません。要りません。商品の一覧は Bootstrap の `.row`(flexbox)の中にカードを並べているので、**同じ行のカードは CSS だけで同じ高さになります**。カードの中も flexbox で縦に並べ、商品名の高さを固定し、価格の欄を伸ばして下を揃えています。

Angular で新しく書くなら、CSS Grid を使います。カードの中の「画像」「名前」「価格」の位置まで行ごとに揃えたいなら、CSS の `subgrid` が使えます。JS で高さを測るのは、CSS でどうしても揃えられないときの最後の手段です。

---

### 1. syncHeight は何をするか

#### 1.1 使い方

```js
// 画像の読み込みを待ってから揃える(README の推奨)
$(window).load(function () {
  $('.product-item').syncHeight({ updateOnResize: true });
});
// 狭い画面では揃えるのをやめる
$(window).resize(function () {
  if ($(window).width() < 500) { $('.product-item').unSyncHeight(); }
});
```

#### 1.2 API とオプション(1.5)

| API / オプション | 既定値 | 内容 | 場所 |
|---|---|---|---|
| `$.fn.syncHeight(config)` | — | 選んだ要素の高さを揃える | `pkg/jquery.syncheight.js:75-104` |
| `updateOnResize` | `false` | `window` の `resize` のたびに揃え直す | `:77`、`:98-102` |
| `height` | `false` | 数値を渡すと、測らずにその高さ(px)にする | `:78`、`:86-90` |
| `$.fn.unSyncHeight()` | — | 書き込んだ高さを消し、`resize` の購読をやめる(1.4 で追加) | `:106-114` |
| `$.getSyncedHeight(selector)` | — | 一番高い要素の高さを返す | `:60-73` |

#### 1.3 中でどう動いているか

| 処理 | 中身 | 場所 |
|---|---|---|
| 書き込む先の決め方 | 普通は `min-height`。IE6 だけ `height`(IE6 は `min-height` を解さない)。`navigator.userAgent` で判定する | `pkg/jquery.syncheight.js:35-58` |
| 高さを測る | いったん `min-height: 0px` に戻してから `css('height')` を読み、最大値を取る | `:64-71` |
| 揃える | 全要素に `min-height: <最大値>px` を書き込む | `:93-95` |
| 画面幅の変化 | `updateOnResize` のときだけ、`resize.syncHeight` という名前の付いたイベントで全体を測り直す。間引きは無い | `:98-102` |
| 揃え直さない場面 | 画像の読み込み、文字の大きさの変更、Web フォントの読み込み、中身の書き換え。`resize` 以外では測り直さない | — |

注意点:

- **選んだ要素を全部 1 つの高さにする**: 行ごとではない。3 列 × 4 行の一覧なら、12 枚全部が一番高い 1 枚に合わせられる。行ごとに揃えたいなら、行ごとに呼び分ける必要がある
- **`unSyncHeight()` はページ全体の購読を外す**: `$(window).unbind('resize.syncHeight')` は、別の要素のために登録した分も外す(`:108`)
- **ページの再描画(レイアウト)を何度も起こす**: 要素ごとに「書き込む → 読む」を繰り返すので、要素の数だけブラウザが配置を計算し直す(6 節)

---

### 2. Spartacus の標準にあるか

**結論: 同じ部品は無い。商品の一覧は CSS(flexbox)だけで、行ごとに高さが揃う。**

#### 2.1 商品の一覧(グリッド表示)

```html
<!-- sf/cms-components/product/product-list/container/product-list.component.html:52-58 -->
<div class="row">
  <cx-product-grid-item
    *ngFor="let product of model?.products; let i = index"
    [product]="product"
    [itemIndex]="i"
    class="col-12 col-sm-6 col-md-4"
  />
</div>
```

| 仕組み | 中身 | 場所 |
|---|---|---|
| 行は flexbox | `.row` は `display: flex; flex-wrap: wrap`。flexbox の子は、既定で行の高さいっぱいに伸びる(`align-items: stretch`)。だから同じ行のカードは同じ高さになる | `styles/vendor/bootstrap/scss/mixins/_grid.scss:22-24`、`styles/vendor/bootstrap/scss/_grid.scss:57-58`(Bootstrap 4.6.2) |
| カードの中も flexbox | `cx-product-grid-item` は `display: flex; flex-direction: column` | `styles/scss/components/product/list/_product-grid-item.scss:1-3` |
| 名前の高さを固定 | `.cx-product-name` は `height: 40px`、`overflow: hidden`、`text-overflow: ellipsis`、`line-clamp: 2`。名前が長くても 2 行分の高さに収める | `_product-grid-item.scss:48-61` |
| 価格の欄を伸ばす | `.cx-product-price-container` に `flex-grow: 1`。残りの高さを価格の欄が吸収し、その下のボタンの位置が揃う | `_product-grid-item.scss:68-69` |
| 画像の高さ | `img` に `aspect-ratio: 1 / 1`。画像が読み込まれる前から高さが決まっている | `_product-grid-item.scss:18-23` |

syncHeight との差:

| 項目 | syncHeight | Spartacus の商品グリッド |
|---|---|---|
| 揃える単位 | 選んだ要素の全部 | 行ごと(flexbox の性質) |
| 画像や Web フォントの読み込み後 | 揃え直さない | ブラウザが自動で配置し直す |
| 画面幅が変わったとき | `updateOnResize` で JS が測り直す | 列の数が `col-sm-6` / `col-md-4` で変わり、高さも自動で揃う |
| 中の部品の位置 | 揃えない(カード全体の高さだけ) | 名前の高さ固定と `flex-grow` で、ボタンの位置まで揃う |
| SSR | ブラウザでしか動かない | CSS なので、サーバーで描いた HTML の時点で揃っている |

#### 2.2 ほかの場所

カード部品(`cx-card`)にも、親いっぱいに伸ばすためのクラス `.cx-card-fit-to-container`(`height: 100%`、縦の flexbox)があります(`styles/scss/components/misc/card/_card.scss:43-48`)。住所や支払い方法のカードを並べるときに使われています。

---

### 3. Angular で書くとどうなるか

#### 3.1 CSS Grid で並べる

```ts
@Component({
  selector: 'app-tile-list',
  template: `
    <ul class="tiles">
      @for (t of tiles(); track t.id) {
        <li class="tile">
          <img [src]="t.image" alt="" width="300" height="300" />
          <h3>{{ t.name }}</h3>
          <p class="price">{{ t.price }}</p>
          <button type="button">カートに入れる</button>
        </li>
      }
    </ul>
  `,
  styles: `
    .tiles {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 24px;
      /* grid の行の中のセルは、既定で行の高さいっぱいに伸びる */
    }
    .tile { display: flex; flex-direction: column; }
    .tile button { margin-top: auto; }   /* ボタンをいつも下端に置く */
  `,
})
export class TileListComponent {
  tiles = input.required<Tile[]>();
}
```

`margin-top: auto` は、flexbox の中で「残りの余白を全部上に取る」指定です。Spartacus の `flex-grow: 1` と同じ役割です。

#### 3.2 中の部品の位置まで揃える: `subgrid`

名前が 1 行のカードと 3 行のカードが並ぶと、3.1 節では価格の位置がカードごとにずれます。行の中で「名前の段」の高さを揃えたいときは、カードを親の grid の行に参加させます。

```css
.tiles {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 24px;
}
.tile {
  display: grid;
  grid-row: span 4;                 /* 画像・名前・価格・ボタンの 4 段 */
  grid-template-rows: subgrid;      /* 段の高さは親が決める */
}
```

同じ行のカードの「名前の段」は、その行で一番長い名前の高さになります。syncHeight を部品ごとに何度も呼んでいたコード(`$('.name').syncHeight(); $('.price').syncHeight();`)は、これで置き換わります。

#### 3.3 どうしても JS で測るとき

CSS で揃えられない配置(行をまたいだ揃え、別々の親にある要素どうし)では、`ResizeObserver` で測ります。`resize` ではなく要素の大きさの変化を受け取るので、画像やフォントの読み込みにも反応します。

```ts
@Directive({ selector: '[appSyncHeight]' })
export class SyncHeightDirective {
  private host = inject(ElementRef<HTMLElement>);
  private destroyRef = inject(DestroyRef);

  constructor() {
    afterNextRender(() => {                     // ブラウザでだけ動く
      const items = Array.from(
        this.host.nativeElement.querySelectorAll<HTMLElement>('[appSyncItem]')
      );
      const sync = () => {
        items.forEach((el) => (el.style.minHeight = ''));               // まとめて戻す
        const max = Math.max(...items.map((el) => el.offsetHeight));    // まとめて読む
        items.forEach((el) => (el.style.minHeight = `${max}px`));       // まとめて書く
      };
      const ro = new ResizeObserver(() => requestAnimationFrame(sync));
      items.forEach((el) => ro.observe(el));
      this.destroyRef.onDestroy(() => ro.disconnect());
    });
  }
}
```

ここでの `min-height` の書き込み自体も大きさの変化なので、`ResizeObserver` がもう一度呼ばれます。値が変わらなければ止まりますが、無限に呼び合わないか確かめておきます。

**SSR での注意**:

- サーバーには配置の計算が無い。`offsetHeight` は測れず、`ResizeObserver` も無い。測る処理は `afterNextRender()`(`@angular/core@21.2.26` の `types/core.d.ts:2576`)の中に置く
- JS で揃える作りは、サーバーで描いた HTML では揃っておらず、ブラウザで JS が動いた瞬間に高さが変わる。画面がガタつく(CLS が増える)。CSS で揃える作りなら、この問題は起きない

---

### 4. ほかの選択肢

ライブラリは要りません。CSS(flexbox、grid、`subgrid`、`aspect-ratio`、`line-clamp`)とブラウザ標準の `ResizeObserver` で足ります。

同じ目的の jQuery プラグイン(`jquery-match-height` など)はありますが、どれも JS で測る方式で、syncHeight と同じ弱点(SSR、ガタつき)を持ちます。Angular CDK にも高さ揃えの部品はありません。

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| Spartacus の商品一覧 | 何もしない。標準で行ごとに揃っている |
| 商品一覧の見た目を変えたい(名前の行数など) | `.cx-product-name` の `height` と `line-clamp` を SCSS で上書きする |
| 独自のカードの一覧 | CSS Grid か `.row` + `col-*`。ボタンを下端に置くなら `margin-top: auto` |
| カードの中の段(名前、価格)の位置まで揃えたい | `grid-template-rows: subgrid` |
| 画像の高さで崩れる | `img` に `width` / `height` 属性か `aspect-ratio` |
| 別々の親にある要素の高さを揃えたい | 配置を見直す。どうしても要るなら 3.3 節の `ResizeObserver` |

---

### 6. コンピュータサイエンスの観点から

- **「行の高さ」はレイアウトの問題で、レイアウトはブラウザの仕事**: CSS 2.1 の `float` や `inline-block` で並べた要素は、互いの高さを知らない。だから JS で測って揃えるしかなかった。flexbox と grid は「並んだ要素の大きさを、一緒に決める」レイアウトの方式で、高さ揃えはその結果として自然に起きる。`subgrid` は、それを入れ子の要素にまで広げた
- **読みと書きを交互にするとレイアウトが何度も走る**: ブラウザは、スタイルを書き換えたあとに大きさを読まれると、その場で配置を計算し直す(強制同期レイアウト)。syncHeight は要素ごとに「`min-height` を戻す → `height` を読む」を繰り返す(`pkg/jquery.syncheight.js:64-71`)。要素が n 個なら n 回、配置が計算される。3.3 節のように「全部戻す → 全部読む → 全部書く」とまとめれば 1 回で済む
- **`resize` から `ResizeObserver` へ**: `window` の `resize` は窓の大きさしか教えてくれない。中身が変わって要素が伸びても通知は来ない。`ResizeObserver` は要素ごとの大きさの変化を、レイアウトの計算のあと、描画の前にまとめて届ける
