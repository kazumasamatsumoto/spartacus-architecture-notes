# 番外 3. Angular CDK の BreakpointObserver と Spartacus の BreakpointService

> **この章が答える問い**: Angular の BreakpointObserver は今も使えるのか(古い記事しか見つからない)。どこに入っていて、どう動いているのか。Spartacus には同じ役割の仕組みがあるのか。Spartacus のプロジェクトでは、どちらを使えばよいのか

> **根拠の取り方**:
> - **Angular CDK**: npm の `@angular/cdk@22.3.0`(2026-11-27 時点の `latest`)の tarball を展開して読んだ。以下 `cdk/` はパッケージのルートを指す
> - **Spartacus**: [SAP/spartacus](https://github.com/SAP/spartacus) `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。README の調査対象(`b7b028f`)より新しい。以下 `sf/` は `core-libs/storefront/`、`core/` は `core-libs/core/src/` を指す

---

### 先に話し言葉で: 消えたのではなく、変わっていない

BreakpointObserver は今も現役です。ただし Angular 本体(`@angular/core`)ではなく、別パッケージの **Angular CDK**(`@angular/cdk/layout`)に入っています。2017 年頃の CDK 初期に登場してから API がほとんど変わっていないので、新しい記事が書かれにくく、古い記事ばかりが検索に出てきます。

Spartacus は CDK に依存していません。その代わりに、同じ役割の **`BreakpointService`** を自前で持っています。仕組みは違います。CDK はブラウザのメディアクエリ(`matchMedia`)に判定を任せます。Spartacus は `resize` イベントで画面の幅を読み、設定ファイルのしきい値と比べます。

Spartacus の中では `BreakpointService` を使うのが基本です。幅以外の条件(画面の向き、`prefers-reduced-motion` など)が要るときだけ、CDK か `matchMedia` を検討します。

---

### 1. Angular CDK の BreakpointObserver

#### 1.1 使い方

```ts
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';

private bo = inject(BreakpointObserver);

isHandset$ = this.bo.observe(Breakpoints.Handset).pipe(map((s) => s.matches));

// 今この瞬間だけ判定する
const wide = this.bo.isMatched('(min-width: 1024px)');
```

#### 1.2 公開 API

型定義は `cdk/types/layout.d.ts` にあります。公開されているのは次の 5 つです(`:87-88`)。

| API | 内容 | 場所 |
|---|---|---|
| `BreakpointObserver.observe(query)` | `Observable<BreakpointState>` を返す。値は `{ matches, breakpoints: { [query]: boolean } }`。クエリは配列でも渡せる | `cdk/types/layout.d.ts:45` |
| `BreakpointObserver.isMatched(query)` | 今一致しているかを同期で返す | `:38` |
| `Breakpoints` | 定義済みのメディアクエリ | `:52-67` |
| `MediaMatcher` | `window.matchMedia` の薄いラッパー | `:70` |
| `LayoutModule` | NgModule 時代の名残。`inject()` で使うなら不要 | `:5` |

`Breakpoints` の値は Material Design のしきい値で、Bootstrap とは違います(`cdk/fesm2022/layout.mjs:44-50`)。

| 名前 | メディアクエリ |
|---|---|
| `XSmall` | `(max-width: 599.98px)` |
| `Small` | `(min-width: 600px) and (max-width: 959.98px)` |
| `Medium` | `(min-width: 960px) and (max-width: 1279.98px)` |
| `Large` | `(min-width: 1280px) and (max-width: 1919.98px)` |
| `XLarge` | `(min-width: 1920px)` |
| `Handset` / `Tablet` / `Web` | 幅と画面の向き(`orientation`)の組み合わせ |

#### 1.3 仕組み

実装は `cdk/fesm2022/_breakpoints-observer-chunk.mjs` にあります。

| 処理 | 中身 | 場所 |
|---|---|---|
| 判定はブラウザに任せる | `window.matchMedia(query)` で `MediaQueryList` を作り、その `change` を購読する。CSS の `@media` と同じ基準で判定されるので、CSS と JS で判定がずれない | `:17`, `:117-123` |
| SSR では偽物を使う | `window` が無いときは `noopMatchMedia` に切り替える。`'all'` と空文字以外のクエリは常に「一致しない」 | `:17`, `:71-78` |
| 通知を間引く | 最初の値はすぐに出し、2 回目以降は `debounceTime(0)` で間引く。複数のクエリが同時に切り替わっても通知は 1 回 | `:97` |
| 変更検知に乗せる | 通知は `NgZone.run` の中で出す | `:119` |
| 同じクエリは共有する | クエリ文字列ごとに `MediaQueryList` を 1 つだけ作り、`Map` で使い回す | `:113-135` |
| WebKit / Blink 向けの回避策 | 空の `@media` ルールを `<style>` に足して、ブラウザが確実にクエリを評価するようにする。CSP の `nonce` にも対応 | `:20-21`, `:50-70` |

#### 1.4 バージョンの注意

CDK のメジャーバージョンは Angular と揃えます。22.x の peerDependencies は `@angular/core` の `^22.0.0 || ^23.0.0` です(`cdk/package.json:160-165`)。

Spartacus の `develop` は Angular `~21.2.23` を使っています(Spartacus のルートの `package.json:169`)。そのため、入れるなら **`@angular/cdk@21`**(dist-tag `v21-lts`。確認時点で 21.2.14)になります。

なお 22.x のビルド成果物では、`MediaMatcher` と `BreakpointObserver` のデコレータが `@Service` になっています(`:46`。以前の版では `@Injectable({ providedIn: 'root' })`)。使う側の書き方(`inject(BreakpointObserver)`)は変わりません。

---

### 2. Spartacus の BreakpointService

#### 2.1 使い方

```ts
import { BREAKPOINT, BreakpointService } from '@spartacus/storefront';

private bp = inject(BreakpointService);

isMobile$ = this.bp.isDown(BREAKPOINT.sm);   // sm 以下か
isDesktop$ = this.bp.isUp(BREAKPOINT.lg);    // lg 以上か
current$ = this.bp.breakpoint$;              // 'xs' | 'sm' | 'md' | 'lg' | 'xl'
```

#### 2.2 公開 API

すべて `sf/layout/breakpoint/breakpoint.service.ts` にあります。

| API | 内容 | 場所 |
|---|---|---|
| `breakpoint$` | 現在のブレークポイントを流す | `:40-46` |
| `isDown(bp)` | 指定したブレークポイント以下か | `:89-97` |
| `isUp(bp)` | 指定したブレークポイント以上か | `:106-114` |
| `isEqual(bp)` | 指定したブレークポイントと一致するか | `:119-121` |
| `getSize(bp)` | ブレークポイントの最大幅 | `:71-80` |
| `breakpoints` | 設定から読んだブレークポイントを、小さい順に並べたもの | `:60-65` |

#### 2.3 仕組み

| 処理 | 中身 | 場所 |
|---|---|---|
| `resize` イベントで幅を読む | `WindowRef.resize$` を購読し、`innerWidth` からブレークポイントを求める。`matchMedia` は使わない | `breakpoint.service.ts:40-46` |
| 300ms 間引く | `resize$` は `fromEvent(window, 'resize')` に `debounceTime(300)` を掛け、最初に 1 回だけ疑似的なイベントを流す | `core/window/window-ref.ts:97-107` |
| 幅とブレークポイントの対応 | 小さい順に見て、「幅 < 最大幅」を満たす最初のものを返す。どれにも当たらなければ一番大きいもの | `breakpoint.service.ts:192-199` |
| しきい値は設定で決まる | `LayoutConfig.breakpoints`。数値なら最大幅、`{ min, max }` でも書ける | `sf/layout/config/layout-config.ts:100`、`breakpoint.service.ts:161-180` |
| SSR では最小の画面とみなす | ブラウザでなければ、一番小さいブレークポイントを `of()` で返す(モバイルファースト) | `breakpoint.service.ts:46`, `:124-131` |
| 重複した通知を止める | `distinctUntilChanged()` と `shareReplay({ refCount: true, bufferSize: 1 })` | `:43-44` |

初期値は Bootstrap と同じです(`sf/layout/config/default-layout.config.ts:10-18`)。

```ts
breakpoints: {
  xs: 576,          // 576 未満
  sm: 768,          // 768 未満
  md: 992,          // 992 未満
  lg: 1200,         // 1200 未満
  xl: { min: 1200 },
}
```

値を変えるときや、ブレークポイントを足すときは、`provideConfig(<LayoutConfig>{ breakpoints: { … } })` で上書きします。SCSS 側のブレークポイント(Bootstrap の変数)も同じ値に揃えないと、CSS と JS で判定がずれます。

#### 2.4 Spartacus の中での使われ方

`BreakpointService` を使っているのは、本体を含めて 10 ファイルです。

| 使っている場所 | 用途 |
|---|---|
| `sf/cms-structure/page/page-layout/page-layout.service.ts:55-59` | ページに並べるスロットを、ブレークポイントごとに切り替える。`layoutSlots` に `lg: { slots: [...] }` のように書くと効く |
| `sf/cms-components/navigation/navigation/navigation-ui.component.ts` | ナビゲーションの開き方(モバイルとデスクトップで違う) |
| `sf/cms-components/navigation/search-box/search-box.component.ts` | 検索ボックスの表示 |
| `sf/cms-components/content/tab/tab.component.ts` | タブとアコーディオンの切り替え |
| `sf/cms-components/product/product-list/product-facet-navigation/product-facet-navigation.component.ts` | ファセットをダイアログで出すかどうか |
| `sf/shared/components/table/table.service.ts` | 表のレイアウトの切り替え |
| `sf/shared/components/split-view/split/split-view.component.ts` | 分割ビューの表示数 |
| `sf/shared/components/ng-select-a11y/ng-select-a11y.directive.ts` | ng-select のアクセシビリティ対応 |
| `feature-libs/product/image-zoom/…/product-image-zoom-view.component.ts` | 画像ズームの挙動 |

`matchMedia` を直接呼んでいる箇所は、`core-libs` と `feature-libs` には見つかりませんでした。

---

### 3. 比較と使い分け

| 観点 | CDK BreakpointObserver | Spartacus BreakpointService |
|---|---|---|
| 判定の方法 | `matchMedia`(CSS と同じ基準) | `resize` イベントと `innerWidth` |
| 反応の速さ | すぐに反応する | 300ms 遅れる |
| 指定できる条件 | 任意のメディアクエリ(向き、`prefers-reduced-motion`、`(hover: hover)`、`prefers-color-scheme` など) | 幅だけ |
| しきい値の管理 | クエリ文字列をコードに書く | `LayoutConfig` で一元管理し、ページのスロット構成と連動する |
| SSR での値 | 「一致しない」 | 一番小さいブレークポイント |
| 依存関係 | `@angular/cdk` の追加が必要 | 追加不要 |
| 既定のしきい値 | Material Design(600 / 960 / 1280 / 1920) | Bootstrap(576 / 768 / 992 / 1200) |

**推奨**

1. **見た目だけの切り替えなら、CSS のメディアクエリで済ませる**: JS が要らず、SSR でもちらつかない。一番軽い
2. **Spartacus の中で JS から幅を判定するなら、`BreakpointService` を使う**: しきい値が `LayoutConfig` の 1 か所にまとまり、ページのスロット構成と同じ基準で動く
3. **幅以外の条件が要るときだけ、`matchMedia` を検討する**: 数か所なら CDK を足さずに、`WindowRef` と `matchMedia` で小さなサービスを書けば足りる。多くの画面で使うなら CDK を足す(バージョンは Angular に揃える)

**注意**: CDK の `Breakpoints` 定数を Spartacus の画面でそのまま使うと、Spartacus の SCSS とブレークポイントがずれます(600 と 576 など)。CDK を使う場合も、クエリは Spartacus の `LayoutConfig` の値から組み立てます。

---

### 4. アクセラレータからの移行との関係

アクセラレータでは、`enquire.min.js` がこの役目を担っていました。`enquire.register('screen and (max-width: 767px)', { match, unmatch })` のように、`matchMedia` を使って JS で切り替えます。

Spartacus への移行では、`enquire` の呼び出し箇所を次のように振り分けます。

| アクセラレータでの使い方 | 移行先 |
|---|---|
| 要素を出し分けるだけ | CSS のメディアクエリ |
| 部品の振る舞いを変える(メニューの開き方など) | `BreakpointService` の `isUp()` / `isDown()` |
| スロットの並びを変える | `LayoutConfig` の `layoutSlots` にブレークポイント別の `slots` を書く |
| 幅以外の条件 | `matchMedia` の小さなサービス、または CDK |

---

### 5. コンピュータサイエンスの観点から

- **ポーリングとイベント駆動**: `resize` は、ドラッグ中に 1 秒間で数十回発生することがある。Spartacus は `debounceTime(300)` で「止まってから 300ms 後に 1 回」にまとめ、幅を読み直す。`matchMedia` は、ブラウザのレイアウトエンジンが「しきい値をまたいだ瞬間」にだけ通知する。後者のほうが通知の回数が少なく、判定の基準も CSS と一致する
- **SSR では「画面」が存在しない**: サーバーには画面の幅が無い。どちらの実装も「仮の答え」を決めて返している。CDK は「一致しない」、Spartacus は「一番小さい画面」。ブラウザで実際の値に切り替わったとき表示が変わるので、SSR で描いた HTML とずれる(ハイドレーション時のちらつき)。CSS で済む切り替えを CSS に任せるべき理由はここにある
- **共有と参照カウント**: CDK はクエリごとに 1 つの `MediaQueryList` を `Map` で共有する。Spartacus は `shareReplay({ refCount: true })` で、購読者が 0 になったら `resize` の購読を外す。どちらも「購読者の数だけイベントリスナーを増やさない」ための工夫
