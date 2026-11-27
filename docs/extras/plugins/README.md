# プラグイン別ノート: jQuery プラグインを Angular / Spartacus でどう代替するか

アクセラレータの `javaScript.tag` が読み込んでいる jQuery プラグインとライブラリを、1 つずつ取り上げたノートです。各ノートは次の順で書いています。

1. そのプラグインは何をするか(プラグイン本体のソースを根拠にする)
2. Spartacus の標準に同じ機能があるか(Spartacus のソースを根拠にする)
3. Angular で書くとどうなるか
4. ほかの選択肢
5. 選び方

jQuery 本体の置き換えの考え方は [番外 4](../replacing-jquery.md)、画面の幅の判定は [番外 3](../breakpoint-observer.md) にあります。

> **根拠**: Spartacus は SAP/spartacus `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。プラグインと代替ライブラリの版は、各ノートの冒頭に書いた(2026-11-27 に npm または GitHub で確認)。ファイル名に `.custom` が付くもの(アクセラレータ側で手が入っているもの)は、元のプラグインについて書いている

## 一覧

「Spartacus 標準」の列は、各ノートの 2 節の結論です。

### 表示・レイアウト

| プラグイン | 何をするか | Spartacus 標準 | 主な代替 |
|---|---|---|---|
| [Owl Carousel](owl-carousel.md) | 要素を横に並べてスライドで送る | 一部ある | `cx-carousel`、`cx-carousel-scrolling`。自動再生・ループは無い |
| [slideViewer](jquery-slideviewer.md) | 画像を 1 枚ずつ送るギャラリー | 一部ある | `cx-product-images`(メイン画像とサムネイル) |
| [jQuery Zoom](jquery-zoom.md) | 画像のホバーで拡大 | 一部ある | `@spartacus/product/image-zoom`(ダイアログ内で拡大) |
| [waitForImages](jquery-waitforimages.md) | 画像の読み込み完了を待つ | 一部ある | `cx-media` の `loaded`。`aspect-ratio` で待つ必要自体を無くす |
| [syncHeight](jquery-syncheight.md) | 並んだ要素の高さを揃える | 無い(不要) | CSS(flexbox / Grid / `subgrid`) |
| [enquire.js](enquire-js.md) | メディアクエリを JS で受ける | 一部ある | `BreakpointService`、CSS のメディアクエリ、`matchMedia` |

### ダイアログ・UI の挙動

| プラグイン | 何をするか | Spartacus 標準 | 主な代替 |
|---|---|---|---|
| [Colorbox](jquery-colorbox.md) | ライトボックス、モーダル | 一部ある | `LaunchDialogService`、`cxFocus`、`<dialog>` |
| [BlockUI](jquery-blockui.md) | 処理中に画面を膜で覆う | 一部ある | `cx-spinner`、`cx-progress-button`、`disabled` / `inert` |
| [タブ(jquery.tabs.custom)](jquery-tabs.md) | タブ切り替え | ある | `cx-tab`(アコーディオンにも切り替わる) |
| [hoverIntent](jquery-hoverintent.md) | ホバーの誤判定を防ぐ | 無い | CSS の `transition-delay`、Pointer Events のディレクティブ |

### フォーム

| プラグイン | 何をするか | Spartacus 標準 | 主な代替 |
|---|---|---|---|
| [jQuery UI](jquery-ui.md) | 入力補完・日付・ダイアログなどの詰め合わせ | 一部ある | ウィジェットごとに対応表あり。スライダー・並べ替えは無い |
| [jQuery Form Plugin](jquery-form.md) | フォームを Ajax で送る | 同じ部品は無い | Reactive Forms + Facade |
| [pstrength](jquery-pstrength.md) | パスワード強度メーター | メーターは無い | `CustomFormValidators` の規則、`computed()` と `<meter>`、zxcvbn-ts |

### テンプレート・セキュリティ・その他

| プラグイン | 何をするか | Spartacus 標準 | 主な代替 |
|---|---|---|---|
| [jQuery Templates](jquery-tmpl.md) | 文字列テンプレートで DOM を作る | ある | Angular のテンプレート、`ngTemplateOutlet`、アウトレット |
| [DOMPurify](dompurify.md) | 危険な HTML を取り除く | 一部ある | Angular 標準のサニタイズ。段落コンポーネントはそれを無効にしている点に注意 |
| [jquery.currencies](jquery-currencies.md) | 金額をブラウザで別通貨に換算する(と考えられる) | 無い | 通貨の切り替えは `CurrencyService`、金額は OCC の `formattedValue`、`Intl.NumberFormat` |

## 対象外

`global_navigation/*.js` と `acc.*.js` は、プラグインではなくサイトごとのコードなので扱っていません。`acc.*.js` の読み方は [番外 4 の 5 節](../replacing-jquery.md) を参照してください。
