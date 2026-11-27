# Colorbox: 画像・HTML・iframe をページの上に重ねて出すライトボックス

> **この章が答える問い**: アクセラレータが読み込んでいる `jquery.colorbox-min.js` は何をしているのか。Spartacus には同じ役割の仕組みがあるのか。Angular では、モーダルやライトボックスをどう書けばよいのか

> **根拠の取り方**:
> - **プラグイン**: npm の `jquery-colorbox@1.6.4`(ファイル名にバージョンが無いので、npm の最新版を使った。最新版の公開は 2016-05-10)。アクセラレータが読む `jquery.colorbox-min.js` も、このパッケージに含まれている(先頭のコメントは `Colorbox 1.6.4`)。行番号は圧縮前の `jquery.colorbox.js` で示す。以下 `pkg/` はパッケージのルート
> - **Spartacus**: [SAP/spartacus](https://github.com/SAP/spartacus) `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`fl/` は `feature-libs/` を指す。SCSS は `core-libs/styles/` にある
> - 代替ライブラリのバージョンと peerDependencies は 2026-11-27 に npm で確認した。Angular の API は `@angular/core@21.2.26` の型定義で確かめた

---

### 先に話し言葉で: Spartacus には「ダイアログを開く仕組み」がある

Colorbox は、リンクをクリックすると、画像や HTML をページの上に重ねて表示するプラグインです。背景を暗くし、Esc キーや背景のクリックで閉じます。画像を何枚かまとめて「前へ」「次へ」で送る機能もあります。

Spartacus には、これにあたる仕組みが標準であります。**`LaunchDialogService`** でダイアログのコンポーネントを開き、**`cxFocus`** ディレクティブでフォーカスを閉じ込めます。閉じたときは、開いたボタンにフォーカスを戻します。商品画像の拡大表示(`fl/product/image-zoom`)も、この仕組みで作られています。

一方で、「画像を何枚か送りながら見る」ためだけの汎用のライトボックスは、Spartacus にはありません。そこが要るときは、ブラウザ標準の `<dialog>` で小さなコンポーネントを書くか、フレームワーク非依存のライブラリを使います。

---

### 1. Colorbox は何をするか

#### 1.1 使い方

```js
// 要素に対して設定する。クリックすると開く
$('a.gallery').colorbox({ rel: 'gallery', maxWidth: '95%' });

// コードから直接開く・閉じる
$.colorbox({ html: '<p>こんにちは</p>' });
$.colorbox.close();
```

#### 1.2 主なオプション

既定値は `pkg/jquery.colorbox.js:10-72` にまとまっている。

| 分類 | オプション | 内容 |
|---|---|---|
| 中身の種類 | `inline` / `html` / `photo` / `iframe` | ページ内の要素、HTML 文字列、画像、iframe のどれを出すか。どれでもなければ `href` を Ajax で読む |
| まとめて送る | `rel`、`loop`、`slideshow`、`slideshowSpeed` | 同じ `rel` の要素を 1 つのグループにし、前へ・次へで送る。スライドショーもできる |
| 大きさ・位置 | `width` / `height`、`maxWidth` / `maxHeight`、`initialWidth` / `initialHeight`、`top` / `left` など、`fixed`、`scalePhotos` | 大きさと置き場所。画像は最大の大きさに合わせて縮める |
| 見た目 | `transition`(`elastic` / `fade` / `none`)、`speed`、`fadeOut`、`opacity`、`className` | 開くときのアニメーション、背景の濃さ |
| 閉じ方 | `overlayClose`、`escKey`、`closeButton` | 背景のクリック、Esc キー、閉じるボタン |
| キーボード | `arrowKey` | 左右の矢印キーで前へ・次へ |
| フォーカス | `trapFocus`、`returnFocus` | フォーカスを閉じ込める、閉じたら元の要素に戻す(どちらも既定で `true`。`:69-70`) |
| 文言 | `current`、`previous`、`next`、`close`、`xhrError`、`imgError` | ボタンやエラーの文言 |
| コールバック | `onOpen`、`onLoad`、`onComplete`、`onCleanup`、`onClosed` | 開閉の各段階で呼ばれる |

公開メソッドは `$.colorbox.close()`、`next()`、`prev()`、`resize()`、`position()`、`remove()` など(`:637-1103`)。iframe の中からは `parent.jQuery.colorbox.close()` で閉じられる(`:595-596`)。

#### 1.3 中でどう動いているか

| 処理 | 中身 | 場所 |
|---|---|---|
| 枠を 1 つだけ作る | ダイアログの DOM(`#colorbox`、背景の `#cboxOverlay`)を最初に 1 回だけ作り、`body` の末尾に足す。以後は使い回す | `pkg/jquery.colorbox.js:469-518` |
| クリックはイベントの委譲で拾う | `document` に `click` を 1 つだけ付け、`.cboxElement` のクリックを拾う。Ctrl / Shift などを押したクリックは無視する(新しいタブで開けるように) | `:522-530`, `:571` |
| 中身の種類で分ける | `inline` は元の場所に空の `div` を置いてから要素を移し、閉じたら戻す。`iframe` は表示の直前に作る。それ以外の URL は `$.fn.load` で Ajax 取得 | `:952-966`, `:1031` |
| ダイアログの属性 | `role="dialog"` と `tabindex="-1"` を付ける。`aria-modal` や `aria-labelledby` は付けない | `:471-478` |
| フォーカスを閉じ込める | `document` に `focus` イベントを**キャプチャ**で付け、ダイアログの外にフォーカスが移ったら、ダイアログ自身にフォーカスを戻す | `:259-264`, `:429-440` |
| フォーカスを戻す | 閉じたあと(`cbox_closed`)、開いた要素にフォーカスする | `:442-447` |
| キー操作 | `document` の `keydown` で Esc(27)なら閉じる。左右の矢印(37 / 39)なら前へ・次へ | `:552-567` |
| 背景のクリック | `overlayClose` が真なら閉じる | `:545-549` |
| 画面の大きさが変わったら | `resize` で位置を計算し直す | `:725-726` |
| 外への通知 | `cbox_open`、`cbox_load`、`cbox_complete`、`cbox_cleanup`、`cbox_closed` を `document` に流す | `:130-135`, `:294-299` |

**やっていないこと**: 背面のスクロールを止める処理は無い(`body` に触るのは DOM を足す `:515-516` だけ)。背面の要素をスクリーンリーダーから隠す処理(`aria-hidden` / `inert`)も無い。フォーカスの閉じ込めは「外に出たら戻す」方式なので、Tab キーを押すとダイアログ自身に戻り、ダイアログの中の最後の要素から最初の要素へは回らない。

---

### 2. Spartacus の標準にあるか

**結論: 一部ある。** モーダルダイアログの仕組み(開く、閉じる、フォーカスの管理、背面のスクロールを止める)は標準である。画像を送るギャラリー型のライトボックスは、汎用の部品としては無い。

#### 2.1 `LaunchDialogService` でダイアログを開く

ダイアログは「呼び出し名(`LAUNCH_CALLER`)」と「どのコンポーネントを、どう出すか」の設定で決まる。

```ts
// 1. 設定: 呼び出し名とコンポーネントを結び付ける
provideConfig(<LayoutConfig>{
  launch: {
    MY_DIALOG: {
      inlineRoot: true,              // アプリのルートの直下に描く
      component: MyDialogComponent,
      dialogType: DIALOG_TYPE.DIALOG, // Bootstrap の modal のクラスを付ける
    },
  },
});
```

```ts
// 2. 開く側
@ViewChild('open') openElement: ElementRef;   // 閉じたときにフォーカスを戻す先
private launchDialogService = inject(LaunchDialogService);
private vcr = inject(ViewContainerRef);

openDialog(): void {
  this.launchDialogService
    .openDialog('MY_DIALOG', this.openElement, this.vcr, { productCode: '123' })
    ?.pipe(take(1))
    .subscribe();
}
```

```ts
// 3. ダイアログ側
@Component({
  selector: 'app-my-dialog',
  template: `
    <div class="modal-dialog" role="dialog" aria-labelledby="dlgTitle"
         [cxFocus]="focusConfig" (esc)="close('Escape')">
      <div class="modal-content">
        <h2 id="dlgTitle">タイトル</h2>
        <button type="button" (click)="close('Close')">閉じる</button>
      </div>
    </div>`,
  imports: [FocusDirective],
})
export class MyDialogComponent {
  focusConfig: FocusConfig = { trap: true, block: true, autofocus: 'button', focusOnEscape: true };
  private launchDialogService = inject(LaunchDialogService);
  data$ = this.launchDialogService.data$;            // 開く側から渡したデータ

  close(reason: string) {
    this.launchDialogService.closeDialog(reason);
  }
}
```

この書き方は、Spartacus 自身の同意ダイアログと同じ形である。

| 部品 | 場所 |
|---|---|
| 設定の例(`inlineRoot` + `DIALOG_TYPE.DIALOG`) | `sf/cms-components/anonymous-consent-management/default-anonymous-consent-layout.config.ts:11-19` |
| 開く側の例 | `sf/cms-components/anonymous-consent-management/open-dialog/anonymous-consent-open-dialog.component.ts:36-45` |
| ダイアログ側の例(`role="dialog"`、`[cxFocus]`、`(esc)`) | `sf/shared/components/anonymous-consents-dialog/anonymous-consent-dialog.component.html:1-7`、`.component.ts:66-71` |
| 背景のクリックで閉じる例(ホスト要素そのもののクリックを見る) | `sf/shared/components/anonymous-consents-dialog/anonymous-consent-dialog.component.ts:84-90` |
| 画像の拡大表示(ライトボックスに近い) | `fl/product/image-zoom/components/product-image-zoom/default-product-image-zoom-layout.config.ts:10-18`、ダイアログ側 `product-image-zoom-dialog/product-image-zoom-dialog.component.ts:38-43` |

#### 2.2 仕組み

| 処理 | 中身 | 場所 |
|---|---|---|
| 開く | 設定を探し、描き方(戦略)を選び、コンポーネントを作る。渡したデータは `data$` で流す | `sf/layout/launch-dialog/services/launch-dialog.service.ts:52-97` |
| 描き方の種類 | `inline`(渡した `ViewContainerRef` に描く)、`inlineRoot`(アプリのルートの直下)、`outlet`(アウトレットに描く)、`cxRoute`(ページ遷移) | `sf/layout/launch-dialog/config/launch-config.ts:13-76` |
| ルートの直下に描く | コンポーネントを作り、`ApplicationRef` に付け、ルートの要素に `appendChild` する | `sf/layout/launch-dialog/services/inline-root-render.strategy.ts:36-65` |
| 見た目の種類 | `DIALOG`、`POPOVER`、`POPOVER_CENTER`、`POPOVER_CENTER_BACKDROP`、`SIDEBAR_START`、`SIDEBAR_END` | `launch-config.ts:81-88` |
| クラスを付ける | `DIALOG` なら `d-block fade modal show` を付け、`body` に `modal-open` を付ける | `sf/layout/launch-dialog/services/launch-render.strategy.ts:35`, `:104-136` |
| 背面のスクロールを止める | `body.modal-open { overflow: hidden }`(Bootstrap の SCSS) | `core-libs/styles/vendor/bootstrap/scss/_modal.scss:15-17` |
| 閉じる | `closeDialog(reason)` で `dialogClose` に値を流す。開いた側の `openDialog()` の Observable がそれを受け、フォーカスを戻し、登録を消し、コンポーネントを破棄する | `launch-dialog.service.ts:61-69`, `:134-140` |
| フォーカスを戻す | 開いた要素(か、その中の最初のフォーカスできる要素)にフォーカスする。`tabindex` が無ければ一時的に `-1` を付ける | `launch-dialog.service.ts:147-160` |
| 同じダイアログを二重に開かない | 同じ呼び出し名が描画中なら、`multi: true` のときだけ描く | `launch-render.strategy.ts:92-102` |
| `body` のクラスを外す | `DIALOG` のときだけ `modal-open` を外す | `launch-render.strategy.ts:145-153` |

#### 2.3 `cxFocus` でフォーカスを管理する

`cxFocus` は、いくつかのフォーカス機能を 1 つの設定オブジェクトで束ねたディレクティブである(`sf/layout/a11y/keyboard-focus/focus.directive.ts:12-16`)。ダイアログでよく使う項目は次のとおり。型は `sf/layout/a11y/keyboard-focus/keyboard-focus.model.ts` にある。

| 項目 | 内容 | 場所 |
|---|---|---|
| `trap` | Tab / Shift+Tab と上下の矢印キーで、中の要素を循環させる。最後の次は最初に戻る | `keyboard-focus.model.ts:137`、`trap/trap-focus.directive.ts:23-39` |
| `trapTabOnly` | Tab / Shift+Tab だけを循環させる(矢印キーはそのまま) | `keyboard-focus.model.ts:139` |
| `block` | ホスト要素に `tabindex="-1"` を付ける | `keyboard-focus.model.ts:28`、`block/block-focus.directive.ts:30-35` |
| `autofocus` | 開いたとき最初にフォーカスする要素(セレクタも書ける) | `keyboard-focus.model.ts:84` |
| `focusOnEscape` | Esc でホストにフォーカスを戻す。同時に `(esc)` イベントを出す | `keyboard-focus.model.ts:65`、`escape/escape-focus.directive.ts:36-47` |
| `lock` | 中の要素を Tab の順番から外し、Enter で中に入る | `keyboard-focus.model.ts:146` |

#### 2.4 Colorbox との差

| 観点 | Colorbox | Spartacus(`LaunchDialogService` + `cxFocus`) |
|---|---|---|
| 中身 | 画像、HTML 文字列、ページ内の要素、iframe、Ajax | Angular のコンポーネント。データは `data$` で渡す |
| 画像のグループと送り | `rel` で自動。矢印キーで送る | 汎用の部品は無い。画像の拡大表示(`fl/product/image-zoom`)は商品画像専用 |
| 閉じ方 | Esc、背景のクリック、閉じるボタン | Esc は `(esc)` を受けて自分で `closeDialog()` を呼ぶ。背景のクリックは各ダイアログが自分で書く |
| フォーカスの閉じ込め | `focus` のキャプチャで外に出たら戻す | キー操作で中を循環させる(`trap`) |
| フォーカスを戻す | 開いた要素へ | 開いた要素(か、その中の最初の要素)へ |
| 背面のスクロール | 止めない | `DIALOG` なら `body.modal-open` で止める |
| `aria-*` | `role="dialog"` だけ | `role` や `aria-labelledby` は各ダイアログのテンプレートで書く |
| 見た目の種類 | 中央の箱 1 種類 | モーダル、ポップオーバー、サイドバー |
| アニメーション | `elastic` / `fade` | Bootstrap の `fade` クラス。凝った動きは無い |
| SSR | 考慮なし(ブラウザ専用) | Angular の描画なので、サーバーでも動く |

---

### 3. Angular で書くとどうなるか

Spartacus の画面の中なら、まず 2 節の `LaunchDialogService` を使う。Spartacus の外の小さな画面、または画像ギャラリーのように独自の作りが要る場面では、ブラウザ標準の **`<dialog>`** が使える。

`<dialog>` を `showModal()` で開くと、ブラウザが次のことを引き受ける。

- 最前面(top layer)に出す。`z-index` の競争が要らない
- 背面の要素を操作できなくする。背面はフォーカスもクリックもできず、支援技術からも隠れる(背面が `inert` になったのと同じ扱い)
- Esc キーで閉じる(`cancel` イベントが出る)
- `::backdrop` 疑似要素で背景を描ける

背面のスクロールは止まらない。止めたいときは、開いている間だけ `body` に `overflow: hidden` を付ける。閉じたあとのフォーカスは、主要なブラウザでは開く前の要素に戻る。ただし、確実にしたいなら自分で戻す。

```ts
import { Component, ElementRef, afterNextRender, signal, viewChild, input } from '@angular/core';

@Component({
  selector: 'app-lightbox',
  template: `
    <dialog #dlg (close)="opened.set(false)" (click)="onBackdrop($event)"
            aria-labelledby="lbTitle">
      @if (opened()) {
        <h2 id="lbTitle" class="visually-hidden">画像 {{ index() + 1 }} / {{ images().length }}</h2>
        <img [src]="images()[index()].url" [alt]="images()[index()].alt" />
        <button type="button" (click)="move(-1)" aria-label="前へ">‹</button>
        <button type="button" (click)="move(1)" aria-label="次へ">›</button>
        <button type="button" (click)="dlg.close()">閉じる</button>
      }
    </dialog>`,
  host: { '(keydown.arrowleft)': 'move(-1)', '(keydown.arrowright)': 'move(1)' },
})
export class LightboxComponent {
  images = input.required<{ url: string; alt: string }[]>();
  index = signal(0);
  opened = signal(false);
  private dlg = viewChild.required<ElementRef<HTMLDialogElement>>('dlg');

  open(i: number) {
    this.index.set(i);
    this.opened.set(true);
    this.dlg().nativeElement.showModal();   // ブラウザでクリックされたときだけ呼ばれる
  }

  move(step: number) {
    const n = this.images().length;
    this.index.update((i) => (i + step + n) % n);   // 端で一周する(Colorbox の loop: true)
  }

  // dialog 要素そのもの(= 背景)をクリックしたときだけ閉じる(Colorbox の overlayClose)
  onBackdrop(e: MouseEvent) {
    if (e.target === this.dlg().nativeElement) this.dlg().nativeElement.close();
  }
}
```

**ポイント**

- 中身は `@if (opened())` の中に置く。閉じている間は DOM に作らないので、画像も読み込まない
- 開く・閉じるのアニメーションは CSS で書く。`dialog[open]` と `@starting-style`、または Angular の `animate.enter` / `animate.leave` を使う(`@angular/core` の機能。`@angular/animations` は 20.2 で非推奨なので使わない)。詳しくは [番外 4 の 7 節](../replacing-jquery.md)
- `<dialog>` を使わず `div` で作るなら、背面の要素に `inert` 属性を付けると、背面をまとめて操作できなくできる。ただし、ダイアログを背面の外(`body` の直下など)に置く必要がある

**SSR での注意**

- `showModal()` はブラウザの API なので、サーバーでは呼ばない。上の例のように、クリックなどブラウザでしか起きない操作から呼べば安全である
- 「ページを開いたらすぐダイアログを出す」ときは、`afterNextRender(() => …)` の中で `showModal()` を呼ぶ。`afterNextRender` はブラウザでだけ実行される
- `document.body` にクラスを付けるときは、`inject(DOCUMENT)` と `Renderer2` を使う。Spartacus の `LaunchRenderStrategy` もこの形である(`launch-render.strategy.ts:61-66`, `:114`)

---

### 4. ほかの選択肢

| ライブラリ | バージョン | peerDependencies | Angular 21 で使えるか | 内容 |
|---|---|---|---|---|
| `@angular/cdk`(`Dialog`) | `21.2.14`(dist-tag `v21-lts`) | `@angular/core` `^21.0.0 \|\| ^22.0.0` | 使える | フォーカスの閉じ込め・戻し、スクロールの制御、オーバーレイを備えたダイアログ。`latest` は 22.x(Angular 22 以降が必要) |
| `@ng-bootstrap/ng-bootstrap`(`NgbModal`) | `20.0.0` | `@angular/core` `^21.0.0` ほか、`@angular/localize`、`@popperjs/core` | 20.x なら使える。`latest`(21.0.0)は Angular 22 が必要 | Bootstrap の見た目のモーダル |
| `ngx-bootstrap`(`ModalModule`) | `21.2.2` | `@angular/core` `^21.2.0` | 21.x なら使える。`latest`(22.0.0)は Angular 22 が必要 | Bootstrap の見た目のモーダル |
| `a11y-dialog` | `8.1.5` | なし | 使える(フレームワーク非依存) | 小さなアクセシブルなダイアログ |
| `micromodal` | `0.7.0` | なし | 使える(フレームワーク非依存) | 小さなモーダル |
| `photoswipe` | `5.4.4` | なし | 使える(フレームワーク非依存) | 画像ギャラリー専用。ピンチやスワイプに対応 |
| `glightbox` | `3.3.1` | なし | 使える(フレームワーク非依存) | 画像・動画・iframe のライトボックス。Colorbox に一番近い |

- **Spartacus は `@angular/cdk` に依存していない。** CDK の `Dialog` を使うなら、新しく依存を足すことになる。バージョンは Angular に揃える(`v21-lts`)
- ng-bootstrap と ngx-bootstrap は、最新版が Angular 22 向けになっている。Spartacus の `develop`(Angular `~21.2.23`)では、1 つ前のメジャーを選ぶ
- フレームワーク非依存のライブラリは DOM を直接触る。`afterNextRender` の中で初期化し、`DestroyRef.onDestroy` で破棄する

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| Spartacus の画面の中で、確認や入力のダイアログを出す | `LaunchDialogService` + `cxFocus`(2 節) |
| 商品画像を大きく見せる | Spartacus の画像ズーム(`fl/product/image-zoom`)を使う、または拡張する |
| 画像を何枚か送る、汎用のライトボックスが要る | `<dialog>` で小さなコンポーネントを書く(3 節)。ピンチやスワイプまで要るなら `photoswipe` |
| CMS の HTML の中のリンクから、iframe や外部ページを開きたい | まず、別ページへの遷移で済まないかを考える。要るなら `<dialog>` の中に `<iframe>` を置く |
| 多くの画面で多種類のダイアログを、Spartacus の外の仕組みでそろえたい | `@angular/cdk@21` の `Dialog`。依存が増えることを受け入れる |

---

### 6. コンピュータサイエンスの観点から

- **「モーダル」はブラウザが持つべき状態だった**: Colorbox の時代は、「背面を触れなくする」ことを JS で再現するしかなかった。半透明の `div` で覆い、`focus` イベントを横取りし、`z-index` を大きくする。どれも近似で、スクリーンリーダーからは背面が見えたままだった。`<dialog>` の `showModal()` と `inert` 属性によって、この状態をブラウザ自身が持つようになった。最前面(top layer)は `z-index` の外にあるので、重なり順の競争も無くなった
- **フォーカスの閉じ込めの 2 つの方式**: Colorbox は「外に出たら戻す」(`focus` のキャプチャ)。Spartacus の `trap` は「端で押された Tab を横取りして反対の端へ送る」。前者は Tab の循環が自然にならず、後者はマウスやスクリーンリーダーの操作で外に出るのを防げない。背面を `inert` にする方式は、背面そのものを「フォーカスできない」状態にするので、どちらの穴も無い
- **DOM の置き場所と論理上の親子**: Colorbox も Spartacus の `inlineRoot` も、ダイアログを `body` やルートの直下に移す。重なり順や `overflow: hidden` の影響を避けるためである。その代わり、DOM の親子と「どのボタンから開いたか」という論理上の親子がずれる。フォーカスを戻す処理(`returnFocus`、`openDialog()` の `openElement`)は、このずれを埋めるためにある
