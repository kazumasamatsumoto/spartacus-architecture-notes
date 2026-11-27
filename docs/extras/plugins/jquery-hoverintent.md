# hoverIntent: マウスが「止まりかけた」ときだけホバーとみなす

> **この章が答える問い**: アクセラレータが読み込んでいる `jquery.hoverIntent.js` は何をしているのか。Spartacus のナビゲーションのフライアウトは、ホバーをどう扱っているのか。Angular では「うっかり通り過ぎただけでメニューが開く」をどう防げばよいのか

> **根拠の取り方**:
> - **プラグイン**: npm の `jquery-hoverintent@1.10.2`(ファイル名にバージョンが無いので、npm の最新版を使った。ファイル先頭の日付は 2020-04-28、npm への公開は 2021-12-13)。`jquery.hoverIntent.js` の全 169 行を読んだ。以下 `pkg/` はパッケージのルート
> - **Spartacus**: [SAP/spartacus](https://github.com/SAP/spartacus) `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`fl/` は `feature-libs/` を指す。SCSS は `core-libs/styles/` にある
> - 代替ライブラリのバージョンと peerDependencies は 2026-11-27 に npm で確認した。Angular の API は `@angular/core@21.2.26` の型定義で確かめた

---

### 先に話し言葉で: Spartacus のフライアウトは CSS の `:hover` だけ

hoverIntent は、jQuery の `.hover()` を少し賢くしたプラグインです。マウスが要素に入ってもすぐには反応しません。一定の間隔でマウスの位置を測り、ほとんど動かなくなったときに初めて「ホバーした」とみなします。メニューの上を素早く横切っただけで、フライアウトが次々に開くのを防ぎます。

Spartacus には、hoverIntent にあたる仕組みはありません。デスクトップのナビゲーション(`NavigationUIComponent`)のフライアウトは、CSS の `:hover` でそのまま開きます。遅れも、マウスの速さの判定もありません。キーボードでは、Space / Enter で開き、Esc で閉じます。

「通り過ぎただけで開く」が気になるなら、まず CSS の `transition-delay` で開くのを少し遅らせます。マウスの速さで判定したいときだけ、小さなディレクティブを書きます。どちらの方法でも、キーボードとタッチの操作を別に用意することが前提です。

---

### 1. hoverIntent は何をするか

#### 1.1 使い方

```js
// .hover() と同じ形
$('.nav > li').hoverIntent(openMenu, closeMenu);

// 設定オブジェクト
$('.nav').hoverIntent({
  over: openMenu,
  out: closeMenu,
  selector: '> li',     // イベントの委譲
  sensitivity: 6,
  interval: 100,
  timeout: 300,
});
```

引数は「`over` と `out`」「1 つの関数(入るときも出るときも呼ぶ)」「設定オブジェクト」の 3 通りに書ける(`pkg/jquery.hoverIntent.js:17-30`, `:104-115`)。

#### 1.2 オプション

既定値は `pkg/jquery.hoverIntent.js:47-51`。

| オプション | 既定値 | 内容 |
|---|---|---|
| `interval` | `100` | マウスの位置を測る間隔(ミリ秒) |
| `sensitivity` | `6` | 1 回の間隔で動いた距離がこのピクセル数より小さければ「止まった」とみなす |
| `timeout` | `0` | 要素から出たあと、`out` を呼ぶまでの遅れ(ミリ秒) |
| `over` / `out` | (必須) | 入ったとき・出たときに呼ぶ関数 |
| `selector` | なし | イベントの委譲に使うセレクタ |

#### 1.3 中でどう動いているか

| 処理 | 中身 | 場所 |
|---|---|---|
| 入ったとき | `mouseenter` で入った位置を覚え、要素に `mousemove` を付けて位置を追い始める。`interval` 後に比べる | `pkg/jquery.hoverIntent.js:147-155` |
| 比べる | 前回の位置と今の位置の直線距離(`Math.sqrt(dx² + dy²)`)が `sensitivity` 未満なら、`mousemove` を外して `over` を呼ぶ。そうでなければ今の位置を覚え、また `interval` 後に比べる | `:66-84` |
| タイマーの作り方 | `setInterval` ではなく、`setTimeout` を毎回作り直す。比べる処理が遅れても、間隔が詰まらない | `:81-82` |
| 出たとき | `over` を呼んだあとなら、`timeout` 後に `out` を呼ぶ。`over` の前に出たなら何もしない(`out` は呼ばない) | `:156-163`, `:86-93` |
| また入ったとき | 待っているタイマー(`out` の予約を含む)を消す。`timeout` の間に戻れば、メニューは閉じない | `:140-141`, `:149` |
| 状態の置き場所 | 要素の `$.data('hoverIntent')` に、呼び出しごとの番号で状態を持つ。同じ要素に何回付けても混ざらない | `:53-54`, `:125-131` |
| マウスの位置 | 全インスタンスで共有する変数 `cX` / `cY` に持つ | `:56-63` |

**やっていないこと**: キーボード(`focus` / `blur`)にもタッチにも反応しない。扱うのは `mouseenter` / `mouseleave` / `mousemove` だけである(`:144`, `:167`)。

---

### 2. Spartacus の標準にあるか

**結論: 無い。** 「マウスの速さで判定する」「開くのを遅らせる」仕組みはどちらも無い。近いものとして、ナビゲーションのフライアウトがある。

#### 2.1 フライアウトの開き方

フライアウトは `NavigationUIComponent`(`sf/cms-components/navigation/navigation/navigation-ui.component.ts`)が描く。開き方は入力の種類で違う。

| 入力 | 開き方 | 場所 |
|---|---|---|
| マウス(デスクトップ) | CSS だけで開く。最上段の `li` の `:hover` で、直下の `.wrapper` を `display: none` から `display: initial` に切り替える。遅れは無い | `core-libs/styles/scss/components/content/navigation/_navigation-ui.scss:1-7`, `:385-399` |
| マウスが入ったとき(JS) | `(mouseenter)` で `onMouseEnter()` を呼ぶ。開く処理ではなく、フライアウトが画面の右からはみ出すなら左にずらす処理と、フォーカスの調整だけをする | `sf/cms-components/navigation/navigation/navigation-ui.component.html:91`、`navigation-ui.component.ts:308-311`, `:337-347`, `:356-372` |
| クリック | `toggleOpen()` で、開いたノードを `openNodes` に積み、`is-open` クラスと `aria-expanded="true"` を付ける | `navigation-ui.component.html:90`、`.ts:197-227`, `:381-393` |
| キーボード | Space / Enter で開いて最初の項目にフォーカス、上下の矢印で項目を移動、Esc で 1 段戻ってボタンにフォーカス | `navigation-ui.component.html:92-96`、`.ts:234-301` |
| フォーカス(デスクトップ) | 最上段の `li` が `:focus-within` で、かつ `is-open` のときだけ開く(クリックやキーで開いたあと) | `_navigation-ui.scss:401-409` |
| ページ遷移 | `NavigationEnd` で `openNodes` を空にする | `navigation-ui.component.ts:118-122` |
| デスクトップの判定 | `BreakpointService.isUp(BREAKPOINT.lg)` | `navigation-ui.component.ts:106-107` |

開くボタンには `aria-haspopup="true"`、`aria-expanded`、`aria-controls` が付く(`navigation-ui.component.html:83-86`)。

#### 2.2 hoverIntent との差

| 観点 | hoverIntent | Spartacus のフライアウト |
|---|---|---|
| マウスで開くまで | 止まりかけるまで待つ(既定で最低 100ms) | すぐ開く(CSS の `:hover`) |
| マウスが出たあと | `timeout` だけ待ってから閉じる | すぐ閉じる |
| キーボード | 扱わない | Space / Enter / Esc / 矢印 |
| タッチ | 扱わない | クリック(タップ)で開閉 |
| 状態の持ち方 | 要素の `$.data` | マウスは CSS の状態(`:hover`)。クリックとキーは `openNodes` の配列と `is-open` クラス |

#### 2.3 Spartacus の部品と組み合わせる例

3 節の方法を、Spartacus のナビゲーションに当てはめるときの注意をまとめる。

- **CSS で遅らせる(3.1 節)**: Spartacus のフライアウトは `display` の切り替えで開く(`core-libs/styles/scss/components/content/navigation/_navigation-ui.scss:385-409`)。3.1 節の `visibility` と `opacity` の書き方で上書きするときは、この `display` の切り替えと競合しないように、同じセレクタの組み立てに合わせる
- **キーボードとタップ(3.3 節)**: `NavigationUIComponent` は、開くボタン(`aria-expanded`)、Esc で閉じる処理、フォーカスの移動をすでに持っている(2.1 節)。Spartacus のナビゲーションを使うなら、3.3 節を自分で書く必要は無い
- **ディレクティブ(3.2 節)と Zone**: Spartacus はルートの `package.json` に `zone.js` を持ち(`package.json:197`)、サンプルのアプリは `provideZoneChangeDetection({ eventCoalescing: true })` で Zone を使う構成である(`projects/storefrontapp/src/app/app.config.ts:30`)。3.2 節の `NgZone.runOutsideAngular` が効く

---

### 3. Angular 標準で書くとどうなるか(Spartacus を使わない)

この節は、`@angular/*` とブラウザ標準(と RxJS)だけで書く。Spartacus の部品(`NavigationUIComponent` など)と組み合わせるときの注意は 2.3 節にまとめた。

#### 3.1 まず CSS で遅らせる

「横切っただけで開く」の多くは、開くのを 100〜200ms 遅らせれば防げる。CSS だけで書け、JS もサーバー側の配慮も要らない。`display` は `transition` で遅らせられないので、`visibility` と `opacity` で隠す。

```scss
.menu > li > .wrapper {
  visibility: hidden;
  opacity: 0;
  // 閉じるとき: 200ms 待ってから消す(hoverIntent の timeout にあたる)
  transition: opacity 0.15s, visibility 0s linear 0.2s;
}

// マウスがある環境でだけ、ホバーで開く
@media (hover: hover) and (pointer: fine) {
  .menu > li:hover > .wrapper {
    visibility: visible;
    opacity: 1;
    // 開くとき: 150ms 待ってから出す
    transition: opacity 0.15s 0.15s, visibility 0s 0.15s;
  }
}

// キーボードやクリックで開いたとき
.menu > li.is-open > .wrapper {
  visibility: visible;
  opacity: 1;
  transition: none;
}
```

- `(hover: hover) and (pointer: fine)` で、マウスのある環境に限る。タッチの端末では「最初のタップでホバー扱い」になる問題を避けられる
- `visibility: hidden` の要素は、フォーカスも読み上げもされない。閉じている間にキーボードで中へ入ってしまうことは無い

#### 3.2 速さで判定したいならディレクティブ

hoverIntent と同じ判定(一定間隔で位置を比べる)を、Angular のディレクティブで書く。

```ts
import {
  DestroyRef, Directive, ElementRef, NgZone, afterNextRender, inject, input, output,
} from '@angular/core';

@Directive({ selector: '[appHoverIntent]' })
export class HoverIntentDirective {
  sensitivity = input(6);    // px
  interval = input(100);     // ms
  timeout = input(0);        // ms
  hoverIn = output<void>();
  hoverOut = output<void>();

  private el = inject<ElementRef<HTMLElement>>(ElementRef).nativeElement;
  private zone = inject(NgZone);
  private destroyRef = inject(DestroyRef);

  constructor() {
    // ブラウザでだけ実行される(サーバーでは呼ばれない)
    afterNextRender(() => {
      let x = 0, y = 0, px = 0, py = 0;
      let timer: ReturnType<typeof setTimeout> | undefined;
      let active = false;

      const move = (e: PointerEvent) => { x = e.clientX; y = e.clientY; };
      const check = () => {
        if (Math.hypot(px - x, py - y) < this.sensitivity()) {
          this.el.removeEventListener('pointermove', move);
          active = true;
          this.zone.run(() => this.hoverIn.emit());
        } else {
          px = x; py = y;
          timer = setTimeout(check, this.interval());
        }
      };
      const enter = (e: PointerEvent) => {
        if (e.pointerType !== 'mouse') return;      // タッチとペンは対象外
        clearTimeout(timer);
        if (active) return;                          // 閉じる予約を取り消しただけ
        px = x = e.clientX; py = y = e.clientY;
        this.el.addEventListener('pointermove', move);
        timer = setTimeout(check, this.interval());
      };
      const leave = (e: PointerEvent) => {
        if (e.pointerType !== 'mouse') return;
        clearTimeout(timer);
        this.el.removeEventListener('pointermove', move);
        if (!active) return;
        timer = setTimeout(() => {
          active = false;
          this.zone.run(() => this.hoverOut.emit());
        }, this.timeout());
      };

      // pointermove のたびに変更検知が走らないよう、Angular の外で聞く
      this.zone.runOutsideAngular(() => {
        this.el.addEventListener('pointerenter', enter);
        this.el.addEventListener('pointerleave', leave);
      });
      this.destroyRef.onDestroy(() => {
        clearTimeout(timer);
        this.el.removeEventListener('pointerenter', enter);
        this.el.removeEventListener('pointerleave', leave);
        this.el.removeEventListener('pointermove', move);
      });
    });
  }
}
```

```html
<li appHoverIntent [timeout]="300" (hoverIn)="open.set(true)" (hoverOut)="open.set(false)"
    [class.is-open]="open()">
  <button type="button" [attr.aria-expanded]="open()" (click)="open.update((v) => !v)">カテゴリ</button>
  @if (open()) { <div class="wrapper">…</div> }
</li>
```

**ポイント**

- **状態は `signal` に持つ**: ホバー、クリック、キーボードのどれで開いても、同じ `open` を書き換える。見た目と `aria-expanded` は `open()` から決める
- **`pointerType` で分ける**: Pointer Events はマウス・タッチ・ペンを同じイベントで扱う。タッチではホバーが無いので、クリック(タップ)だけで開閉させる
- **`NgZone.runOutsideAngular`**: Zone を使う構成(`zone.js` を読み込み、`provideZoneChangeDetection()` を使うアプリ)では、`pointermove` を Angular の中で聞くと、マウスが動くたびに変更検知が走る。外で聞き、`over` / `out` のときだけ `zone.run` で中に戻す。Zone を使わない構成(`provideZonelessChangeDetection()`)では、`NgZone` は何もしない実装に置き換わるので、このコードはそのまま動く
- **キーボードの代わりにはならない**: ホバーは補助である。開くボタン(`aria-expanded`)、Esc で閉じる処理、フォーカスの移動は別に要る(3.3 節)

#### 3.3 キーボードとタップでも開閉する

ホバーは近道である。土台には「開閉するボタン + リンクの一覧」(ディスクロージャー)を置き、ホバーはその上に重ねる。

```ts
import { Component, signal } from '@angular/core';
import { HoverIntentDirective } from './hover-intent.directive';   // 3.2 節

@Component({
  selector: 'app-nav-item',
  imports: [HoverIntentDirective],
  template: `
    <div class="nav-item" appHoverIntent [timeout]="300" (hoverIn)="onHoverIn()" (hoverOut)="onHoverOut()"
        (keydown.escape)="close(btn)" (focusout)="onFocusOut($event)"
        [class.is-open]="open()">
      <button #btn type="button" aria-controls="nav-cat" [attr.aria-expanded]="open()"
              (click)="toggle()">カテゴリ</button>
      <ul id="nav-cat" class="wrapper" [hidden]="!open()">
        <li><a href="/c/1">…</a></li>
      </ul>
    </div>
  `,
})
export class NavItemComponent {
  open = signal(false);
  private byHover = false;   // ホバーで開いたか

  onHoverIn() {
    if (this.open()) return;
    this.byHover = true;
    this.open.set(true);
  }
  onHoverOut() {
    if (!this.byHover) return;   // クリックやキーで開いたものは、ホバーでは閉じない
    this.byHover = false;
    this.open.set(false);
  }
  toggle() {                     // マウスのクリック、タップ、Enter / Space のどれでも呼ばれる
    if (this.byHover) {          // ホバーで開いた直後のクリックは、閉じずに「開いたまま」にする
      this.byHover = false;
      return;
    }
    this.open.update((v) => !v);
  }
  close(btn: HTMLButtonElement) {   // Esc で閉じ、ボタンにフォーカスを戻す
    if (!this.open()) return;
    this.byHover = false;
    this.open.set(false);
    btn.focus();
  }
  onFocusOut(e: FocusEvent) {       // フォーカスが外へ出たら閉じる
    const box = e.currentTarget as HTMLElement;
    if (!box.contains(e.relatedTarget as Node | null)) {
      this.byHover = false;
      this.open.set(false);
    }
  }
}
```

- 使う側は `<ul class="menu"><li><app-nav-item /></li>…</ul>` のように、`li` の中に置く
- `aria-controls` が指す要素は、閉じている間も DOM に要る。`id` は項目ごとに別の値にする(例では固定にしている)。そのため、ここでは `@if` ではなく `[hidden]` で隠している
- **ホバーで開いた直後のクリック**: マウスで止まると開き、そのままボタンを押すと、何もしなければ閉じてしまう。上の例では、ホバーで開いたあとの最初のクリックを「開いたまま固定する」操作として扱う
- タップでは 3.2 節のディレクティブが反応しない(`pointerType` で除いている)ので、`click` だけで開閉する
- ページの別の場所をクリックしたら閉じたいなら、`DOCUMENT` の `click` を `afterNextRender` の中で聞き、`DestroyRef.onDestroy()` で外す
- 部品に任せたいなら、Angular チームの公式パッケージ `@angular/aria@21`(dist-tag `v21-lts`、`@angular/cdk@21` が要る、開発者プレビュー)がある。ただし、メニュー(`role="menu"`)の部品である点に注意する(4 節)

#### 3.4 SSR での注意

- サーバーにはマウスも `pointer` イベントも無い。イベントの登録は `afterNextRender` の中で行う(3.2 節の例)。`afterNextRender` はブラウザでだけ実行される
- サーバーで描く HTML では、フライアウトは閉じた状態にしておく。`open` の初期値を `false` にすれば、そのまま閉じた HTML になる
- 3.1 節の CSS だけの方法は、サーバーで描いた HTML にもそのまま効く
- `afterNextRender` を使わずに分けるなら、`isPlatformBrowser(inject(PLATFORM_ID))`(`@angular/common`)で判定する。`window` や `document` は、グローバルではなく `inject(DOCUMENT)`(とその `defaultView`)から取る

---

### 4. ほかの選択肢

| ライブラリ | バージョン | peerDependencies | Angular 21 で使えるか | 内容 |
|---|---|---|---|---|
| `hoverintent` | `2.2.1`(公開 2019-08-15) | なし | 使える(フレームワーク非依存) | jQuery を使わない hoverIntent。`sensitivity`(既定 7)、`interval`(100)、`timeout`(0)に加え、`handleFocus` でフォーカスにも反応できる。距離は縦と横の差の和で測る。更新は止まっている |
| `@angular/aria`(`ngMenu` の `expansionDelay`) | `21.2.14`(dist-tag `v21-lts`) | `@angular/cdk` `21.2.14`、`@angular/core` `^21.0.0 \|\| ^22.0.0` | 使える。ただし型定義に `@developerPreview 21.0` とある | ホバーでサブメニューを開くまでの遅れを指定できる。`latest` は 22.3.0(Angular 22 以降) |

- `@angular/aria` のメニューは、アプリケーションのメニュー(`role="menu"`)の振る舞いを作るものである。サイトのナビゲーションは、多くの場合「開閉するボタン + リンクの一覧」(ディスクロージャー)の形が合う。Spartacus のナビゲーションもこの形である。メニューの部品に置き換える前に、どちらの形が要るかを確かめる
- `@angular/aria` は `@angular/cdk` を peerDependencies に持つ。**Spartacus は `@angular/cdk` に依存していない**ので、使うなら CDK も足すことになる
- ブラウザ標準では、ホバーやフォーカスで要素を出す仕組み(Interest Invokers、`interestfor` 属性)の策定が進んでいる。本ノートでは、仕様の現状とブラウザの対応状況は確かめていない

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| Spartacus のナビゲーションをそのまま使う | 何もしない。ホバーは CSS、キーボードとタップは `NavigationUIComponent` が扱う |
| 横切っただけで開くのを防ぎたい | CSS の `transition-delay`(3.1 節)。Spartacus の SCSS を上書きする(2.3 節) |
| マウスが離れたあと、少しの間は閉じないでほしい | CSS の `transition-delay`(閉じる側)。JS が要るなら 3.2 節の `timeout` |
| マウスの速さで判定したい(hoverIntent と同じ) | 3.2 節のディレクティブ。フレームワーク非依存でよければ `hoverintent` |
| タッチの端末 | ホバーに頼らない。タップで開閉する(3.3 節)。CSS は `@media (hover: hover)` で分ける |
| Spartacus を使わない Angular のアプリでフライアウトを作る | 開くボタン + `signal` + Esc / `focusout` で閉じる(3.3 節)。ホバーは CSS の遅れ(3.1 節)か 3.2 節のディレクティブを重ねる |

---

### 6. コンピュータサイエンスの観点から

- **意図を、離散的な標本から推定する**: マウスの「意図」は直接は見えない。hoverIntent は 100ms ごとに位置を標本として取り、2 点の距離(つまり速さ)がしきい値を下回ったら「止まるつもりだ」と推定する。時間の遅れだけで判定する方法(CSS の `transition-delay`)よりも、ゆっくり動かす人と素早く動かす人の差に強い
- **ヒステリシス**: 開く条件(止まりかけた)と閉じる条件(出てから `timeout` 経った)を別にしている。境界の付近で開閉が小刻みに繰り返されるのを防ぐ、制御工学のヒステリシスと同じ考え方である。CSS で開く側と閉じる側の `transition-delay` を別にするのも同じ
- **ホバーは入力の一部にすぎない**: hoverIntent が作られた頃は、マウスが前提だった。今はタッチ、ペン、キーボード、スクリーンリーダーがある。Pointer Events は入力の種類を `pointerType` で区別でき、CSS の `(hover: hover)` は「ホバーできる環境か」を問える。ホバーは「あると便利な近道」として、ほかの操作の上に重ねる
