# BlockUI: 処理が終わるまで、画面や要素を半透明の膜で覆って操作できなくする

> **この章が答える問い**: アクセラレータが読み込んでいる `jquery.blockUI-2.66.js` は何をしているのか。Spartacus には同じ役割の仕組みがあるのか。Angular では「処理中は触らせない」をどう書けばよいのか

> **根拠の取り方**:
> - **プラグイン**: BlockUI 2.66 は npm に無い(npm の `block-ui` は 2.70.0 と 2.70.1 だけ)。そこで、公式の GitHub リポジトリ [malsup/blockui](https://github.com/malsup/blockui) を取得し、版を 2.66 に上げたコミット `35c4a7a`(2013-10-09、「version bump」)の `jquery.blockUI.js` を読んだ。先頭のコメントは `Version 2.66.0-2013.10.09`、本文は `$.blockUI.version = 2.66`。以下 `pkg/` はこのファイルを指す。2.66 から 2.70.0 への差分は 7 行だけである
> - **Spartacus**: [SAP/spartacus](https://github.com/SAP/spartacus) `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`core/` は `core-libs/core/src/`、`fl/` は `feature-libs/` を指す。SCSS は `core-libs/styles/` にある
> - 代替ライブラリのバージョンと peerDependencies は 2026-11-27 に npm で確認した

---

### 先に話し言葉で: 「膜」より「その場で待つ」を表す

BlockUI は、Ajax の処理が終わるまで、ページ全体や特定の要素を半透明の膜で覆うプラグインです。膜の上に「お待ちください」といったメッセージを出し、膜の下のクリックやキー操作を止めます。

Spartacus には、BlockUI という名前の部品はありません。ただし、同じ目的の仕組みはそろっています。読み込み中の表示には **`cx-spinner`**、ボタンを押したあとの待ち状態には **`cx-progress-button`** があります。注文の確定中は、**`LaunchDialogService`** で背景を暗くしたスピナーを全画面に出しています。BlockUI のおまけの機能 `$.growlUI`(数秒で消える通知)には、**`GlobalMessageService`** があたります。

Angular では、膜で覆うより先に、「処理中」という状態を 1 つの `signal` で持ちます。その状態で、ボタンを `disabled` にし、フォームを止め、スピナーを出します。どうしても領域ごと止めたいときは、ブラウザ標準の `inert` 属性が使えます。

---

### 1. BlockUI は何をするか

#### 1.1 使い方

```js
// ページ全体
$.blockUI({ message: '<h1>処理中です</h1>' });
$.unblockUI();

// 特定の要素だけ
$('#cart').block({ message: null });
$('#cart').unblock();

// 数秒で消える通知(おまけ)
$.growlUI('保存しました', 'カートを更新しました');
```

公開されているのは `$.blockUI` / `$.unblockUI`(`pkg/jquery.blockUI-2.66.js:32-33`)、`$.fn.block` / `$.fn.unblock`(`:76-108`)、`$.growlUI`(`:36`)の 5 つである。

#### 1.2 主なオプション

既定値は `$.blockUI.defaults`(`:113-243`)にある。

| オプション | 既定値 | 内容 | 場所 |
|---|---|---|---|
| `message` | `'<h1>Please wait...</h1>'` | 膜の上に出す内容。HTML 文字列、DOM 要素、`null`(出さない) | `:115` |
| `css` / `overlayCSS` | 白い箱 / 黒の 60% | メッセージと膜のスタイル。`cursor: 'wait'` も付く | `:125-149` |
| `baseZ` | `1000` | 膜の `z-index` の基準 | `:182` |
| `bindEvents` | `true` | 膜の下のマウス・キーのイベントを止める | `:193` |
| `constrainTabKey` | `true` | Tab キーでメッセージの外に出られないようにする | `:197` |
| `focusInput` | `true` | ページ全体を覆ったとき、メッセージの中の最初の入力欄にフォーカスする | `:213` |
| `focusableElements` | `':input:enabled:visible'` | フォーカスできる要素の条件 | `:216` |
| `fadeIn` / `fadeOut` | `200` / `400` | 出すとき・消すときのフェードの時間(ミリ秒) | `:200`、`:203` |
| `timeout` | `0` | 指定したミリ秒のあと自動で外す | `:206` |
| `showOverlay` | `true` | 膜を出すか | `:209` |
| `onBlock` / `onUnblock` / `onOverlayClick` | `null` | 出し終えたとき、外し終えたとき、膜をクリックしたとき | `:223-233` |
| `ignoreIfBlocked` | `false` | すでに覆っていれば何もしない | `:242` |
| `theme` / `draggable` | `false` / `true` | jQuery UI のテーマを使う | `:117-120` |

#### 1.3 中でどう動いているか

| 処理 | 中身 | 場所 |
|---|---|---|
| 3 枚の層を重ねる | iframe(古い IE 用。既定では使わない)、膜(`.blockOverlay`)、メッセージ(`.blockMsg`)。`z-index` を 1 ずつ、メッセージは +10 上げる | `:291-324` |
| ページ全体と要素で置き方を変える | ページ全体は `position: fixed`。要素は `position: absolute` で、要素が `static` なら一時的に `relative` にする | `:89-92`, `:305-341` |
| イベントを止める | ページ全体を覆うときだけ、`document` に `mousedown mouseup keydown keypress keyup touchstart touchend touchmove` を付ける。メッセージの中のイベントと、覆われていない場所のイベントは通す | `:537-556`, `:563-587` |
| 要素だけを覆うとき | イベントは止めない(`if (!full …) return`)。膜がクリックを受け止めるだけで、Tab キーでは膜の下の要素にフォーカスできる | `:547-548` |
| Tab キーを閉じ込める | メッセージの中の最後の要素で Tab、最初の要素で Shift+Tab を押すと、反対の端にフォーカスを送る | `:565-575`, `:589-595` |
| 最初のフォーカス | ページ全体を覆ったら、20ms 後にメッセージの中の最初の入力欄にフォーカスする | `:435-440` |
| 自動で外す | `timeout` が 0 でなければ `setTimeout` で外す | `:444-453` |
| 既存の要素をメッセージにする | 元の場所と `display` を覚えておき、外すときに戻す | `:270-285` |

**やっていないこと**: `aria-busy`、`role="status"`、`aria-live` といった属性は一切付けない(ファイル中に `aria` も `role` も出てこない)。そのため、スクリーンリーダーの利用者には「処理中である」ことも「終わった」ことも伝わらない。

---

### 2. Spartacus の標準にあるか

**結論: 一部ある。** 「膜で覆う」汎用の部品は無い。目的ごとに、次の部品がある。

#### 2.1 読み込み中の表示: `cx-spinner`

```html
@if (loading()) {
  <cx-spinner />
}
```

| 項目 | 中身 | 場所 |
|---|---|---|
| コンポーネント | `selector: 'cx-spinner'`。入力は無い | `sf/shared/components/spinner/spinner.component.ts:12-21` |
| テンプレート | `role="status"` を持つ箱の中に、翻訳キー `spinner.loading` の文字を置く。文字は見た目では回る輪に置き換わる | `sf/shared/components/spinner/spinner.component.html:1-3` |
| 見た目 | CSS 変数(`--cx-spinner-radius` など)で大きさと色を変えられる | `core-libs/styles/scss/components/misc/spinner/_spinner.scss:4-10` |

#### 2.2 ボタンを押したあとの待ち: `cx-progress-button`

```html
<cx-progress-button [loading]="saving()" [disabled]="form.invalid"
                    (clickEvent)="save()">保存</cx-progress-button>
```

`loading` が真の間、ボタンは `disabled` になり、中にスピナーが出る(`sf/shared/components/progress-button/progress-button.component.html:1-14`、入力は `progress-button.component.ts:16-29`)。BlockUI で「二度押しを防ぐ」ためにページを覆っていたなら、多くはこれで足りる。

#### 2.3 全画面を覆う: `LaunchDialogService` + `POPOVER_CENTER_BACKDROP`

Spartacus 自身が、注文の確定中にこの方法を使っている。BlockUI の `$.blockUI()` に一番近い。

```ts
// 設定(fl/checkout/base/components/checkout-place-order/default-place-order-spinner-layout.config.ts:13-21)
launch: {
  PLACE_ORDER_SPINNER: {
    inline: true,
    component: SpinnerComponent,
    dialogType: DIALOG_TYPE.POPOVER_CENTER_BACKDROP,
  },
},
```

```ts
// 使う側(fl/checkout/base/components/checkout-place-order/checkout-place-order.component.ts:144-166 を簡略化)
const spinner$ = this.launchDialogService.launch(LAUNCH_CALLER.PLACE_ORDER_SPINNER, this.vcr);
this.orderFacade.placeOrder(termsChecked).subscribe({
  next: () => this.routingService.go({ cxRoute: 'orderConfirmation' }),  // 成功したら画面ごと移る
  error: () => {
    spinner$?.subscribe((c) => {
      this.launchDialogService.clear(LAUNCH_CALLER.PLACE_ORDER_SPINNER);
      c?.destroy();
    }).unsubscribe();
  },
});
```

| 項目 | 中身 | 場所 |
|---|---|---|
| 膜の見た目 | `.cx-dialog-popover-center-backdrop` は `position: fixed`、全画面、`z-index: 1050`、`rgba(0, 0, 0, 0.5)`、中央寄せ | `core-libs/styles/scss/misc/_dialog.scss:1-9`, `:27-36` |
| クラスを付ける処理 | `POPOVER_CENTER_BACKDROP` なら上のクラスを付ける | `sf/layout/launch-dialog/services/launch-render.strategy.ts:47-49`, `:122-124` |
| 呼び出し名 | `LAUNCH_CALLER.PLACE_ORDER_SPINNER` | `sf/layout/launch-dialog/config/launch-config.ts:98` |
| 画面を離れたら外す | `ngOnDestroy` で `clear()` | `checkout-place-order.component.ts:172-174` |

この方法は、膜で**クリック**を受け止める。BlockUI の `bindEvents` のように、キー操作まで止める処理は無い。

#### 2.4 数秒で消える通知: `GlobalMessageService`(`$.growlUI` の代わり)

```ts
inject(GlobalMessageService).add({ key: 'cart.updated' }, GlobalMessageType.MSG_TYPE_CONFIRMATION);
```

| 項目 | 中身 | 場所 |
|---|---|---|
| 追加する | `add(text, type, timeout?)`。文字列か翻訳キーを渡す | `core/global-message/facade/global-message.service.ts:43-55` |
| 消えるまでの時間 | 確認・情報は 3 秒、エラー・警告は 7 秒 | `core/global-message/config/default-global-message-config.ts:10-28` |
| 表示 | `cx-global-message`。読み上げ用のメッセージは `aria-live="polite"` の領域に出す | `sf/cms-components/misc/global-message/global-message.component.ts:22`、`.component.html:1-23` |

#### 2.5 BlockUI との差

| 観点 | BlockUI | Spartacus |
|---|---|---|
| ページ全体を止める | `$.blockUI()`。クリックもキーも止める | `POPOVER_CENTER_BACKDROP` の膜。クリックは止まるが、キーは止まらない |
| 要素だけを止める | `$(el).block()` | 汎用の部品は無い。各コンポーネントが `@if` でスピナーを出し、ボタンを `disabled` にする |
| ボタンの二度押し防止 | 膜で覆う | `cx-progress-button` の `loading` |
| 処理中であることの読み上げ | 無い | `cx-spinner` が `role="status"` を持つ |
| 短い通知 | `$.growlUI` | `GlobalMessageService` |
| メッセージの文言 | HTML を直接渡す | 翻訳キー(`spinner.loading` など) |

---

### 3. Angular で書くとどうなるか

**まず、状態を 1 つにまとめる。** 「処理中か」を `signal` で持ち、その値から見た目を決める。膜は、その見た目の 1 つにすぎない。

```ts
import { Component, inject, signal } from '@angular/core';
import { finalize } from 'rxjs';
import { SpinnerComponent } from '@spartacus/storefront';

@Component({
  selector: 'app-cart-panel',
  imports: [SpinnerComponent],
  template: `
    <section class="cart-panel" [attr.aria-busy]="busy()" [attr.inert]="busy() ? '' : null">
      …カートの中身…
      <button type="button" (click)="update()" [disabled]="busy()">数量を更新</button>
    </section>
    @if (busy()) {
      <div class="cart-panel__overlay"><cx-spinner /></div>
    }
  `,
  styles: `
    :host { position: relative; display: block; }
    .cart-panel__overlay {
      position: absolute; inset: 0;
      display: grid; place-items: center;
      background: rgb(255 255 255 / 0.6);
    }
  `,
})
export class CartPanelComponent {
  busy = signal(false);
  private cart = inject(MyCartFacade);   // 例: 自前のファサード

  update() {
    this.busy.set(true);
    this.cart.update().pipe(finalize(() => this.busy.set(false))).subscribe();
  }
}
```

**ポイント**

- **`inert` 属性**: 付けた要素とその子孫は、クリックもフォーカスもできなくなり、支援技術からも隠れる。BlockUI の `bindEvents` と `constrainTabKey` を、JS 無しでまとめて実現できる。BlockUI の要素ブロックでは Tab で膜の下に入れたが、`inert` ならその穴も無い。Angular では `[attr.inert]="busy() ? '' : null"` と書く。Spartacus にも同じ書き方がある(`fl/product-configurator/common/components/configurator-cart-entry-bundle-info/configurator-cart-entry-bundle-info.component.html:53`)
- **`aria-busy="true"`**: 領域が更新中であることを支援技術に伝える。スピナーの `role="status"` と合わせて使う
- **`finalize`**: 成功でも失敗でも、必ず `busy` を戻す。BlockUI でよくあった「エラーのときに `$.unblockUI()` を呼び忘れて、画面が固まる」を防ぐ
- **ちらつきを防ぐ**: すぐ終わる処理でスピナーが一瞬だけ出るのを避けたいなら、CSS の `animation-delay` で 200ms ほど遅れて表示する。JS のタイマーは要らない
- **ページ全体**: ページ全体を止めるなら、Spartacus の画面では 2.3 節の `LaunchDialogService` を使う。Spartacus の外なら、`<dialog>` を `showModal()` で開き、中にスピナーを置く。背面は自動で操作できなくなる。ただし、Esc キーで閉じられてしまうので、`cancel` イベントで `preventDefault()` する

**SSR での注意**

- 上の例は `signal` とテンプレートだけで書いているので、サーバーでもそのまま描ける。サーバーでは `busy()` が `false` のまま描かれる
- `document.body` に膜を足す書き方(BlockUI の `$.blockUI()` と同じ形)は、サーバーでは `document` が無いので動かない。全画面の膜もテンプレートの中に書くか、`LaunchDialogService` に任せる
- `showModal()` はブラウザでだけ呼ぶ。ユーザーの操作から呼ぶか、`afterNextRender` の中で呼ぶ

---

### 4. ほかの選択肢

| ライブラリ | バージョン | peerDependencies | Angular 21 で使えるか | 内容 |
|---|---|---|---|---|
| `ng-block-ui` | `4.0.1`(公開 2023-05-25) | `@angular/core` `>=14.0.0`、`@angular/platform-browser-dynamic`、`@angular/router`、`zone.js` `>=0.11.4` ほか | 範囲としては入るが、`zone.js` を peer に要求する。2023 年から更新が無い | BlockUI の考え方をそのまま Angular に移したもの |
| `ngx-spinner` | `22.0.1` | `@angular/core` `>=20.0.0`、`@angular/common` `>=20.0.0` | 使える | 全画面または要素の上に出すスピナー |
| `@ngx-loading-bar/core` | `7.0.1` | `@angular/common` `>=16.0.0`、`rxjs` `^7.0.0` | 使える | 画面上部の細い進捗バー。画面は止めない |
| `@angular/cdk`(`Overlay`) | `21.2.14`(dist-tag `v21-lts`) | `@angular/core` `^21.0.0 \|\| ^22.0.0` | 使える | 膜(backdrop)付きのオーバーレイを自分で組み立てる部品 |

- **Spartacus は `@angular/cdk` に依存していない。** CDK を使うなら依存を足すことになり、バージョンは Angular に揃える
- BlockUI は「画面を止める」ことが目的になりやすい。ライブラリを足す前に、`signal` と `disabled` / `inert` で済まないかを確かめる

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| ボタンの二度押しを防ぎたい | `cx-progress-button` の `loading`、または `[disabled]="busy()"` |
| 一部の領域が更新中であることを示したい | `@if (busy())` で `cx-spinner` を重ね、領域に `inert` と `aria-busy` |
| 注文の確定など、ページ全体を止めたい | `LaunchDialogService` + `DIALOG_TYPE.POPOVER_CENTER_BACKDROP`(Spartacus の注文確定と同じ) |
| 数秒で消える通知を出したい(`$.growlUI`) | `GlobalMessageService.add()` |
| 通信中であることをさりげなく示したい | 画面上部の進捗バー(`@ngx-loading-bar/core` など) |

---

### 6. コンピュータサイエンスの観点から

- **排他制御を UI でやっていた**: BlockUI の膜は、「処理中に別の操作をさせない」ための粗いロックである。画面全体を止めるので確実だが、関係の無い部分まで止まる。状態を `signal` で持つと、「このボタンだけ」「この領域だけ」と、ロックの範囲を細かく選べる。より確実にしたいなら、サーバー側で冪等性(同じ要求を 2 回受けても結果が同じになること)を保証する
- **イベントを捨てるか、要素を不活性にするか**: BlockUI は、`document` に付けたハンドラでイベントを 1 つずつ捨てている。捨て漏れ(要素ブロックの Tab キーなど)が出やすい。`inert` は、要素の側を「操作の対象にならない」状態にする。止めたいものを列挙する方式から、止める範囲を宣言する方式に変わった
- **見えない人にとっての「待ち」**: 膜とアニメーションは、目で見ている人にしか伝わらない。`role="status"`、`aria-live`、`aria-busy` によって、待ちの開始と終わりを支援技術に伝えられる。BlockUI には、この層がまるごと無かった
