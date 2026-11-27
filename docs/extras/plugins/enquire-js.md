# enquire.js: メディアクエリの一致・不一致を JS のコールバックで受け取る

> **この章が答える問い**: アクセラレータが読み込む `enquire.min.js` は何をしているのか。中ではどう動いているのか。Spartacus と Angular では何に置き換えるのか

> **根拠の取り方**:
> - **プラグイン**: npm の `enquire.js@2.1.6`(2026-11-27 時点の `latest`。2017-03-14 公開で、これが最後の版)の tarball を展開し、`src/` の 5 ファイルと `dist/enquire.min.js` の見出しを読んだ。アクセラレータのファイル名(`enquire.min.js`)には版が無いので、最新版について書く。以下 `pkg/` はパッケージのルート
> - **Spartacus**: SAP/spartacus `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`core/` は `core-libs/core/src/` を指す
> - 代替ライブラリのバージョンは 2026-11-27 に `npm view` で確認した
> - Spartacus の `BreakpointService` と Angular CDK の `BreakpointObserver` の詳しい比較は [番外 3](../breakpoint-observer.md) にある。本章では重ねて書かず、enquire.js から見た対応だけを書く

---

### 先に話し言葉で: `matchMedia` の薄い包み紙

enquire.js は、ブラウザの `window.matchMedia` を使いやすく包んだ小さなライブラリです。「このメディアクエリに入ったら `match`、外れたら `unmatch` を呼ぶ」という登録ができます。jQuery には依存していません。

Spartacus には、同じ役割の **`BreakpointService`** があります。ただし仕組みが違います。enquire.js はメディアクエリでブラウザに判定させます。`BreakpointService` は `resize` イベントで画面の幅を読み、設定のしきい値と比べます。そのため、幅以外の条件(画面の向き、`prefers-reduced-motion` など)は扱えません。

置き換えは 3 通りです。見た目の切り替えだけなら **CSS のメディアクエリ**、幅で振る舞いを変えるなら **`BreakpointService`**、幅以外の条件が要るなら **`matchMedia` を包んだ小さなサービス**(または Angular CDK)を使います。

---

### 1. enquire.js は何をするか

#### 1.1 主な API

```js
enquire.register('screen and (max-width: 767px)', {
  setup:   function () { /* 最初に 1 回だけ */ },
  match:   function () { /* クエリに入ったとき */ },
  unmatch: function () { /* クエリから外れたとき */ },
  destroy: function () { /* unregister されたとき */ },
  deferSetup: true,        // setup を最初に match するまで遅らせる
});

enquire.unregister('screen and (max-width: 767px)');
```

| API / オプション | 内容 | 場所 |
|---|---|---|
| `enquire.register(query, handler, shouldDegrade?)` | クエリにハンドラを登録する。`handler` はオブジェクト、関数、またはその配列。戻り値は `enquire` なので続けて書ける | `pkg/src/MediaQueryDispatch.js:37-60` |
| `enquire.unregister(query, handler?)` | ハンドラを外す。`handler` を省くと、そのクエリのハンドラをすべて外す | `:68-82` |
| `match` | クエリに一致したときに呼ばれる。登録した時点で一致していれば、すぐに呼ばれる | `pkg/src/MediaQuery.js:39-44`、`pkg/src/QueryHandler.js:37-40` |
| `unmatch` | 一致しなくなったときに呼ばれる | `QueryHandler.js:47-49` |
| `setup` | 最初に 1 回だけ呼ばれる。既定では登録した時点 | `QueryHandler.js:11-14`, `:25-30` |
| `deferSetup` | `true` なら、`setup` を最初に一致するまで遅らせる | `QueryHandler.js:13`, `:38` |
| `destroy` | `unregister` のときに呼ばれる。無ければ `unmatch` が呼ばれる | `QueryHandler.js:57-59` |
| `shouldDegrade` | メディアクエリを理解しない古いブラウザで、常に一致したとみなす | `MediaQueryDispatch.js:19`, `:39`、`MediaQuery.js:66-68` |

#### 1.2 中でどう動いているか

| 処理 | 中身 | 場所 |
|---|---|---|
| 読み込んだ時点でインスタンスを 1 つ作る | `module.exports = new MediaQueryDispatch()`。グローバルの `enquire` はこの 1 つ | `pkg/src/index.js:1-2` |
| `matchMedia` が無いと例外 | コンストラクタで `window.matchMedia` を確かめ、無ければ `throw` する | `MediaQueryDispatch.js:13-16` |
| クエリごとに `MediaQueryList` を 1 つ | 同じクエリ文字列を何度 `register` しても、`MediaQuery` は 1 つだけ作り、ハンドラを足していく | `MediaQueryDispatch.js:41-43` |
| 判定はブラウザに任せる | `window.matchMedia(query)` の `MediaQueryList` に `addListener` でリスナーを付ける。しきい値をまたいだときだけ呼ばれる | `MediaQuery.js:15-23` |
| 一致・不一致で全ハンドラを呼ぶ | 変化のたびに `assess()` が `matches` を見て、全ハンドラの `on()` か `off()` を呼ぶ | `MediaQuery.js:84-90` |
| 外すときは参照で比べる | `unregister(query, handler)` は、登録したオブジェクトか `match` 関数と同じ参照のものを外す | `QueryHandler.js:68-70` |

`addListener` は、`MediaQueryList` の古い書き方です。今は `addEventListener('change', …)` が標準です。主要なブラウザは今も `addListener` を受け付けますが、enquire.js は 2017 年から更新されていません。

---

### 2. Spartacus の標準にあるか

結論: **一部ある**。画面の幅による切り替えは `BreakpointService` がある。任意のメディアクエリを受ける仕組みは無い。

#### 2.1 `BreakpointService`

```ts
import { BREAKPOINT, BreakpointService } from '@spartacus/storefront';

private bp = inject(BreakpointService);

isMobile$ = this.bp.isDown(BREAKPOINT.sm);   // sm 以下か
isDesktop$ = this.bp.isUp(BREAKPOINT.lg);    // lg 以上か
```

| 項目 | 内容 | 場所 |
|---|---|---|
| `breakpoint$` | 現在のブレークポイント(`xs`〜`xl`)を流す。`WindowRef.resize$` と `innerWidth` から求める | `sf/layout/breakpoint/breakpoint.service.ts:40-46` |
| `isDown()` / `isUp()` / `isEqual()` | 指定したブレークポイント以下・以上・一致を `Observable<boolean>` で返す | `:89-121` |
| `resize$` | `fromEvent(window, 'resize')` に `debounceTime(300)` を掛け、最初に 1 回だけ疑似的なイベントを流す | `core/window/window-ref.ts:97-107` |
| SSR | 一番小さいブレークポイントを返す(モバイルファースト) | `breakpoint.service.ts:46`, `:129-131` |

しきい値の設定(`LayoutConfig.breakpoints`)、Spartacus の中での使われ方、CDK との比較は [番外 3](../breakpoint-observer.md) の 2〜3 節にあります。

#### 2.2 enquire.js との違い

| 観点 | enquire.js | `BreakpointService` |
|---|---|---|
| 判定の方法 | `matchMedia`(CSS と同じ基準) | `resize` イベントと `innerWidth` |
| 反応の速さ | しきい値をまたいだ瞬間 | `resize` が止まってから 300ms 後 |
| 指定できる条件 | 任意のメディアクエリ | 幅だけ |
| しきい値の管理 | クエリ文字列をコードに書く | `LayoutConfig` の 1 か所 |
| 受け取り方 | `match` / `unmatch` のコールバック | `Observable<boolean>`。テンプレートなら `async` パイプ |
| 最初の 1 回だけの処理 | `setup`、`deferSetup` | 無い。`take(1)` や `filter` で書く |
| 後片付け | `unregister` を自分で呼ぶ | 購読を外せば終わる(`async` パイプなら自動) |
| SSR | 読み込んだ時点で例外(3.6 節) | 一番小さいブレークポイント |

`core-libs` と `feature-libs` には、`matchMedia` を直接呼んでいる箇所がありません(2026-11-27 に grep で確認)。

#### 2.3 Spartacus の部品と組み合わせる例

**見た目だけなら Bootstrap の mixin**

Spartacus のスタイルは Bootstrap のブレークポイントに合わせてあるので、Bootstrap の `media-breakpoint-up` / `media-breakpoint-down` が使えます。Spartacus 自身も使っています(mixin は `core-libs/styles/vendor/bootstrap/scss/mixins/_breakpoints.scss:75`, `:88`。使用例は `core-libs/styles/scss/components/content/navigation/_navigation-ui.scss:29`)。

```scss
.cx-only-desktop { display: none; }
@include media-breakpoint-up(lg) { .cx-only-desktop { display: block; } }
```

**幅で振る舞いを変えるなら `BreakpointService` を signal で**

```ts
import { Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { BREAKPOINT, BreakpointService } from '@spartacus/storefront';

@Component({
  selector: 'app-menu',
  template: `
    @if (isMobile()) {
      <button (click)="open = !open">メニュー</button>
    } @else {
      <nav>…</nav>
    }
  `,
})
export class MenuComponent {
  private readonly bp = inject(BreakpointService);
  readonly isMobile = toSignal(this.bp.isDown(BREAKPOINT.sm), { initialValue: true });
  open = false;
}
```

enquire.js の `match` / `unmatch` で行っていた処理は、「`isMobile()` が `true` のときの状態」と「`false` のときの状態」としてテンプレートに書きます。コールバックで DOM を書き換える必要はありません。

`BreakpointService` のしきい値は `LayoutConfig.breakpoints` の 1 か所で決まります。3 節の `matchMedia` を使う書き方を Spartacus の中で使うなら、クエリの数値は `LayoutConfig` の値から組み立て、`BreakpointService` とずれないようにします([番外 3](../breakpoint-observer.md) の 3 節)。

---

### 3. Angular 標準で書くとどうなるか(Spartacus を使わない)

この節は、`@angular/core` と `@angular/common`、ブラウザ標準の `matchMedia` と CSS だけで書きます。Spartacus の `BreakpointService` や Bootstrap の mixin を使う書き方は 2.3 節にあります。

#### 3.1 見た目だけなら CSS

要素を出し分けるだけなら、JS は要りません。SSR でもちらつきません。

```css
.only-desktop { display: none; }
@media (min-width: 992px) {
  .only-desktop { display: block; }
}
```

CSS のカスタムプロパティ(`var(--bp-lg)`)は `@media` の条件の中では使えません。しきい値を 1 か所で管理したいなら、Sass の変数や mixin にまとめます。

#### 3.2 JS で一致を知りたいなら `matchMedia` を signal に包む

`matchMedia` を signal に包む小さな関数で、幅も幅以外の条件(`(orientation: landscape)`、`(prefers-reduced-motion: reduce)`、`(hover: hover)` など)も扱えます。

```ts
import { afterNextRender, DestroyRef, DOCUMENT, inject, signal, Signal } from '@angular/core';

/**
 * メディアクエリの一致を signal で返す。
 * サーバーと最初の描画では fallback を返し、描画のあとブラウザで本当の値に切り替える。
 */
export function mediaQuery(query: string, fallback = false): Signal<boolean> {
  const matches = signal(fallback);
  const win = inject(DOCUMENT).defaultView;
  const destroyRef = inject(DestroyRef);

  afterNextRender(() => {
    // afterNextRender はブラウザでだけ呼ばれる
    if (!win?.matchMedia) return;
    const mql = win.matchMedia(query);
    matches.set(mql.matches);
    const onChange = (e: MediaQueryListEvent) => matches.set(e.matches);
    mql.addEventListener('change', onChange);
    destroyRef.onDestroy(() => mql.removeEventListener('change', onChange));
  });

  return matches.asReadonly();
}
```

```ts
import { Component, signal } from '@angular/core';

@Component({
  selector: 'app-menu',
  template: `
    @if (isMobile()) {
      <button type="button" aria-controls="main-nav" [attr.aria-expanded]="open()"
              (click)="open.set(!open())">メニュー</button>
    }
    <nav id="main-nav" [hidden]="isMobile() && !open()">…</nav>
  `,
})
export class MenuComponent {
  readonly isMobile = mediaQuery('(max-width: 767.98px)', true);
  readonly reducedMotion = mediaQuery('(prefers-reduced-motion: reduce)');
  readonly open = signal(false);
}
```

- `mediaQuery()` は `inject()` を使うので、コンポーネントのフィールド初期化(注入コンテキスト)で呼ぶ
- `DOCUMENT` は `@angular/core` から import できる(`@angular/common` も同じものを再 export している)
- `afterNextRender` を使うのは、ハイドレーションのときにサーバーの HTML と最初の描画を揃えるためである。ハイドレーションを使わず、最初から本当の値で描きたいなら、`isPlatformBrowser(inject(PLATFORM_ID))` で分けて、ブラウザではその場で `mql.matches` を読んでもよい
- メニューのボタンには `aria-expanded` と `aria-controls` を付け、開閉の状態を支援技術に伝える。`<button>` なので Enter と Space で操作できる。`[hidden]` で隠したナビゲーションは、フォーカスも読み上げも受けない

#### 3.3 enquire.js の `register` をそのまま置き換える

`setup` や `deferSetup` も含めて、enquire.js と同じ呼ばれ方にしたいなら、コールバックを受ける関数にします。呼ばれる順序は enquire.js(1.1 節、`pkg/src/QueryHandler.js:11-59`)に合わせました。

```ts
import { afterNextRender, DestroyRef, DOCUMENT, inject } from '@angular/core';

export interface MediaQueryHandler {
  setup?: () => void;
  deferSetup?: boolean;
  match?: () => void;
  unmatch?: () => void;
  destroy?: () => void;
}

/** enquire.register に当たる。コンポーネントが破棄されると unregister に当たる処理が走る */
export function registerMediaQuery(query: string, h: MediaQueryHandler): void {
  const win = inject(DOCUMENT).defaultView;
  const destroyRef = inject(DestroyRef);

  afterNextRender(() => {
    if (!win?.matchMedia) return;
    const mql = win.matchMedia(query);
    let initialised = false;
    const setupOnce = () => {
      if (!initialised) { initialised = true; h.setup?.(); }
    };
    const on = () => { setupOnce(); h.match?.(); };
    const off = () => h.unmatch?.();

    if (!h.deferSetup) setupOnce();   // 既定では登録した時点で setup
    if (mql.matches) on();            // 登録した時点で一致していれば match
    const onChange = (e: MediaQueryListEvent) => (e.matches ? on() : off());
    mql.addEventListener('change', onChange);

    destroyRef.onDestroy(() => {
      mql.removeEventListener('change', onChange);
      h.destroy ? h.destroy() : off(); // destroy が無ければ unmatch
    });
  });
}
```

| enquire.js | 3.3 節の関数 | 違い |
|---|---|---|
| `enquire.register(query, handler)` | `registerMediaQuery(query, handler)` | 呼ぶのはコンポーネントの初期化の中。ブラウザで、最初の描画のあとに登録される |
| `enquire.unregister(query)` | コンポーネントの破棄 | `DestroyRef` に結び付くので、外し忘れが無い |
| 同じクエリを何度登録しても `MediaQueryList` は 1 つ | 登録ごとに `matchMedia` を呼ぶ | 数十か所で使うなら、クエリごとに 1 つにまとめるサービスにする |
| `shouldDegrade` | 無い | 今のブラウザはすべて `matchMedia` を持つ |

ただし、多くの場合は 3.2 節の signal で足ります。`match` / `unmatch` で DOM を書き換えていた処理は、signal の値に応じてテンプレートを書き分ける形に直すほうが、Angular らしく、SSR とも相性がよくなります。どうしても値の変化で処理を走らせたいなら、3.2 節の signal を `effect()` で見ます。

#### 3.4 しきい値を 1 か所で決める

```ts
export const BREAKPOINTS = { sm: 576, md: 768, lg: 992, xl: 1200 } as const;
export type Breakpoint = keyof typeof BREAKPOINTS;

export const up = (bp: Breakpoint) => `(min-width: ${BREAKPOINTS[bp]}px)`;
export const down = (bp: Breakpoint) => `(max-width: ${BREAKPOINTS[bp] - 0.02}px)`;

// 使う側
readonly isDesktop = mediaQuery(up('lg'));
```

上の数値は Bootstrap と同じ値の例です。CSS 側(Sass の変数)と同じ値を使います。`max-width` に 0.02px を引くのは、`min-width: 992px` と `max-width: 992px` が 992px ちょうどで両方とも一致するのを避けるためで、Bootstrap と同じ方法です(Spartacus が同梱する Bootstrap の `core-libs/styles/vendor/bootstrap/scss/mixins/_breakpoints.scss:49-59`)。

#### 3.5 Angular CDK を使う場合

Angular チームの公式パッケージ `@angular/cdk` の `BreakpointObserver`(`@angular/cdk/layout`)も、任意のメディアクエリを `Observable` で受けられます。3.2 節の関数で足りない(多くの画面で使い、クエリの共有や複数クエリの同時判定が欲しい)場合の候補です。Angular 21 には `@angular/cdk@21`(dist-tag `v21-lts`)を使います。詳しくは 4 節にあります。

#### 3.6 SSR での注意

- **enquire.js はサーバーでは読み込むだけで失敗する**。読み込んだ時点で `new MediaQueryDispatch()` が走り(`pkg/src/index.js:2`)、`window.matchMedia` を参照する(`MediaQueryDispatch.js:14`)。Node.js には `window` が無いので、ここで例外になる。Angular のコードから import するなら、ブラウザでだけ動的に読み込む必要がある
- サーバーには画面が無いので、どの方法でも「仮の答え」を決めて返すことになる。3.2 節の関数は `fallback`、Spartacus の `BreakpointService` は一番小さいブレークポイントを返す。ブラウザで本当の値に切り替わると表示が変わるので、CSS で済むものは CSS に任せる
- `window` は直接参照せず、`inject(DOCUMENT).defaultView` から取る。ブラウザでだけ動かす処理は `afterNextRender` の中に書くか、`isPlatformBrowser(inject(PLATFORM_ID))` で分ける。リスナーの後片付けは `DestroyRef` に任せる

---

### 4. ほかの選択肢

| ライブラリ | 版(2026-11-27) | peerDependencies | 内容 |
|---|---|---|---|
| `enquire.js` | 2.1.6 | なし | 本章の対象。2017-03 から更新されていない |
| `@angular/cdk`(`@angular/cdk/layout`) | `latest` は 22.3.0。Angular 21 向けは dist-tag `v21-lts` の 21.2.14 | 21.2.14 は `@angular/core` / `@angular/common` / `@angular/platform-browser` が `^21.0.0 \|\| ^22.0.0`、`rxjs` が `^6.5.3 \|\| ^7.4.0` | `BreakpointObserver.observe(query)` で任意のメディアクエリを `Observable` で受ける。SSR では「一致しない」を返す |

Angular CDK を使う場合の注意:

- **Spartacus は `@angular/cdk` に依存していない**。足すなら、Spartacus の Angular(`~21.2.23`)に合わせて `@angular/cdk@21` を入れる
- CDK の `Breakpoints` 定数は Material Design のしきい値(600 / 960 / 1280 / 1920)で、Spartacus(576 / 768 / 992 / 1200)と違う。クエリは Spartacus の `LayoutConfig` の値から組み立てる(詳しくは [番外 3](../breakpoint-observer.md) の 1.4 節と 3 節)

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| 要素を出し分けるだけ | CSS のメディアクエリ(Bootstrap の mixin) |
| 幅で部品の振る舞いを変える(メニューの開き方など) | `BreakpointService` の `isUp()` / `isDown()`。signal にするなら `toSignal`(2.3 節) |
| Spartacus を使わない Angular アプリで、幅や幅以外の条件で振る舞いを変える | `matchMedia` を signal に包んだ関数(3.2 節)。しきい値は 1 か所の定数にまとめる(3.4 節) |
| Spartacus を使わず、enquire.js の `setup` / `match` / `unmatch` の呼ばれ方をそのまま残したい | `afterNextRender` と `DestroyRef` で包んだ `registerMediaQuery`(3.3 節) |
| 幅でスロットの並びを変える | `LayoutConfig` の `layoutSlots` にブレークポイント別の `slots` を書く([番外 3](../breakpoint-observer.md) の 2.4 節) |
| 幅以外の条件が数か所 | `matchMedia` を包んだ小さな関数(3.2 節) |
| 幅以外の条件を多くの画面で使う | `@angular/cdk@21` の `BreakpointObserver` |
| enquire.js の `setup` / `deferSetup` に当たる「最初の 1 回だけ」 | コンポーネントの初期化で書く。一致したときだけなら `isUp(…).pipe(filter(Boolean), take(1))` |

---

### 6. コンピュータサイエンスの観点から

- **観察者パターンの小さな例**: enquire.js は、クエリ(観察される側)ごとにハンドラ(観察する側)の配列を持ち、状態が変わったら全員に知らせます(`MediaQuery.js:84-90`)。RxJS の `Observable` や Angular の signal は、同じ考え方を「値の流れ」として一般化したものです。`unregister` を呼び忘れるとリスナーが残る問題も、購読の寿命を `DestroyRef` や `async` パイプに結び付けることで解決されています
- **ブラウザ標準が追いついた**: enquire.js が登場した頃(2012 年頃)は、`matchMedia` の無いブラウザが残っていました。`shouldDegrade` はその名残です(`MediaQueryDispatch.js:19`)。今は `matchMedia` と `change` イベントがすべての主要なブラウザで使え、包み紙は十数行で書けます
- **CSS と JS で判定をそろえる**: `matchMedia` は CSS の `@media` と同じエンジンで判定します。`innerWidth` との比較は、スクロールバーの幅やズームの扱いで CSS とずれることがあります。CSS と JS の両方で切り替える部品では、どちらの基準を使うかを揃えることが、見た目の食い違いを防ぐ鍵になります
