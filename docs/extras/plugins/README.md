# プラグイン別ノート: jQuery プラグインを Angular / Spartacus でどう代替するか

アクセラレータの `javaScript.tag` が読み込んでいる jQuery プラグインとライブラリを、1 つずつ取り上げたノートです。各ノートは次の順で書いています。

1. そのプラグインは何をするか(プラグイン本体のソースを根拠にする)
2. Spartacus の標準に同じ機能があるか(Spartacus のソースを根拠にする)。Spartacus の部品と組み合わせる例もここに置く
3. **Angular 標準で書くとどうなるか(Spartacus を使わない)**。`@angular/*`、RxJS、ブラウザ標準の API だけで書く
4. ほかの選択肢(Angular 向けライブラリ、フレームワークに依存しないライブラリ、Angular CDK など)
5. 選び方

jQuery 本体の置き換えの考え方は [番外 4](../replacing-jquery.md)、画面の幅の判定は [番外 3](../breakpoint-observer.md) にあります。

> **根拠**: Spartacus は SAP/spartacus `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。Angular は `@angular/*@21.2.26`。プラグインと代替ライブラリの版は、各ノートの冒頭に書いた(2026-11-27 に npm または GitHub で確認)。ファイル名に `.custom` が付くもの(アクセラレータ側で手が入っているもの)は、元のプラグインについて書いている
>
> 3 節のコード例は、TypeScript の部分だけを `@angular/*@21.2.26` と TypeScript 5.9(strict)で型チェックした。テンプレートのコンパイルと、ブラウザでの実行はしていない。前の節のコードに足す部分だけを書いた抜粋は、単体では型チェックが通らない

## 一覧

「Spartacus 標準」の列は各ノートの 2 節の結論、「Angular 標準での代替」の列は 3 節の中身です。

### 表示・レイアウト

| プラグイン | 何をするか | Spartacus 標準 | Spartacus での代替 | Angular 標準での代替 |
|---|---|---|---|---|
| [Owl Carousel](owl-carousel.md) | 要素を横に並べてスライドで送る | 一部ある | `cx-carousel`、`cx-carousel-scrolling`(自動再生・ループは無い) | CSS の `scroll-snap` + 前後ボタン・ドットのコンポーネント。自動再生は `effect` とタイマーで、停止ボタンと `prefers-reduced-motion` 付き |
| [slideViewer](jquery-slideviewer.md) | 画像を 1 枚ずつ送るギャラリー | 一部ある | `cx-product-images`(メイン画像とサムネイル) | `linkedSignal` で番号を持ち、CSS の `transform` で滑らせる。番号ボタン、矢印キー、`aria-live` |
| [jQuery Zoom](jquery-zoom.md) | 画像のホバーで拡大 | 一部ある | `@spartacus/product/image-zoom`(ダイアログ内で拡大) | Pointer Events + `transform: scale()` と `transform-origin`。大きい画像は `decode()` で先に読む |
| [waitForImages](jquery-waitforimages.md) | 画像の読み込み完了を待つ | 一部ある | `cx-media` の `loaded` | `aspect-ratio` で待つ必要自体を無くす。待つなら `(load)` / `(error)` を signal で数える、`decode()` |
| [syncHeight](jquery-syncheight.md) | 並んだ要素の高さを揃える | 無い(不要) | 商品一覧は flexbox で揃っている | CSS Grid、`subgrid`。最後の手段として `ResizeObserver` + `afterNextRender` |
| [enquire.js](enquire-js.md) | メディアクエリを JS で受ける | 一部ある | `BreakpointService` | CSS の `@media`。JS なら `matchMedia` を signal に包む関数。`register` と同じ呼ばれ方を再現する関数も |

### ダイアログ・UI の挙動

| プラグイン | 何をするか | Spartacus 標準 | Spartacus での代替 | Angular 標準での代替 |
|---|---|---|---|---|
| [Colorbox](jquery-colorbox.md) | ライトボックス、モーダル | 一部ある | `LaunchDialogService`、`cxFocus` | ブラウザ標準の `<dialog>` + `showModal()` を signal / `input()` / `output()` で包む。フォーカスは自分で戻す |
| [BlockUI](jquery-blockui.md) | 処理中に画面を膜で覆う | 一部ある | `cx-spinner`、`cx-progress-button`、`LaunchDialogService` | 処理中を signal で持ち、`inert` と `aria-busy`、`finalize` で必ず戻す。ページ全体は `<dialog>` |
| [タブ(jquery.tabs.custom)](jquery-tabs.md) | タブ切り替え | ある | `cx-tab`(アコーディオンにも切り替わる) | `role="tablist"` と矢印キーのタブを自作。アコーディオンは `<details name>` |
| [hoverIntent](jquery-hoverintent.md) | ホバーの誤判定を防ぐ | 無い | `NavigationUIComponent`(遅延なし) | CSS の `transition-delay`。速さで判定するなら Pointer Events のディレクティブ。キーボードとタップでも開閉する |

### フォーム

| プラグイン | 何をするか | Spartacus 標準 | Spartacus での代替 | Angular 標準での代替 |
|---|---|---|---|---|
| [jQuery UI](jquery-ui.md) | 入力補完・日付・ダイアログなどの詰め合わせ | 一部ある | ウィジェットごとに対応表あり。スライダー・並べ替えは無い | ウィジェットごとに自作の例(入力補完、`<dialog>`、`<input type="date/range">`、タブ、Popover API の吹き出し)。CDK を使う場合も |
| [jQuery Form Plugin](jquery-form.md) | フォームを Ajax で送る | 同じ部品は無い | Reactive Forms + Facade | Reactive Forms + `HttpClient`。`FormData`、アップロードの進み具合、インターセプター |
| [pstrength](jquery-pstrength.md) | パスワード強度メーター | メーターは無い | `CustomFormValidators` の規則、`cx-form-errors` | 自作の `ValidatorFn` + `computed()` と `<meter>`、規則のチェックリスト |

### テンプレート・セキュリティ・その他

| プラグイン | 何をするか | Spartacus 標準 | Spartacus での代替 | Angular 標準での代替 |
|---|---|---|---|---|
| [jQuery Templates](jquery-tmpl.md) | 文字列テンプレートで DOM を作る | ある | アウトレット、CMS のマッピング | Angular のテンプレート、`ngTemplateOutlet`、`<ng-content>`、`ViewContainerRef` |
| [DOMPurify](dompurify.md) | 危険な HTML を取り除く | 一部ある | 段落コンポーネントを差し替えて DOMPurify を挟む(標準の段落はサニタイズを切っている) | Angular 標準のサニタイズ(`[innerHTML]`)。広く許可したいときだけ DOMPurify + bypass、パイプにまとめる |
| [jquery.currencies](jquery-currencies.md) | 金額をブラウザで別通貨に換算する(と考えられる) | 無い | `CurrencyService`、OCC の `formattedValue` | `LOCALE_ID`、`DEFAULT_CURRENCY_CODE`、`registerLocaleData`、`CurrencyPipe`、`Intl.NumberFormat` |

## 対象外

`global_navigation/*.js` と `acc.*.js` は、プラグインではなくサイトごとのコードなので扱っていません。`acc.*.js` の読み方は [番外 4 の 5 節](../replacing-jquery.md) を参照してください。
