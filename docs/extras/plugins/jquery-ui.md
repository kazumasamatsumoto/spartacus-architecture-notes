# jQuery UI: 入力補完、日付選択、ダイアログ、タブなどのウィジェットの詰め合わせ

> **この章が答える問い**: アクセラレータの `jquery-ui-1.12.1.min.js` は何をしていたのか。中のウィジェットごとに、Spartacus の標準に同じ部品があるのか。無いものは Angular でどう書けばよいのか

> **根拠の取り方**:
> - **プラグイン**: npm の `jquery-ui@1.12.1`(ファイル名の版)の tarball を展開し、`ui/widget.js` と `ui/widgets/*.js` を読んだ。以下 `pkg/` はパッケージのルート。アクセラレータの `.min.js` がどのウィジェットを含むビルドなのかは確認できない(jQuery UI はダウンロード時にウィジェットを選んでビルドできる)
> - **Spartacus**: SAP/spartacus `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`core/` は `core-libs/core/src/`、`fl/` は `feature-libs/` を指す
> - 代替ライブラリのバージョンと、`jquery-ui@1.12.1` の既知の脆弱性(`npm audit`)は 2026-11-27 に npm で確認

---

### 先に話し言葉で: 「jQuery UI を置き換える」ではなく「ウィジェットを 1 つずつ置き換える」

jQuery UI は 1 つの部品ではありません。入力補完、日付選択、ダイアログ、タブ、アコーディオン、スライダー、並べ替えなど、20 個ほどのウィジェットの詰め合わせです。置き換えは、アクセラレータが実際に使っているウィジェットを洗い出し、1 つずつ行います。

Spartacus には、半分ほどのウィジェットに相当する標準の部品があります。検索候補は `cx-searchbox`、日付は `cx-date-picker`、ダイアログは `LaunchDialogService`、タブとアコーディオンは `cx-tab`、セレクトは ng-select です。スライダーと並べ替え(ドラッグ)は Spartacus にありません。

標準に無いものは、まずブラウザの標準の要素を検討します。`<input type="range">`、`<dialog>`、`<details>`、`<progress>`、Popover API などで、多くのウィジェットが置き換わります。

なお 1.12.1 には、修正済みの XSS の脆弱性が 4 件あります(1.4 節)。jQuery UI を残す場合でも、この版のままにはできません。

---

### 1. jQuery UI は何をするか

#### 1.1 仕組み: ウィジェットファクトリ

すべてのウィジェットは、`$.widget()` という共通の仕組みで作られています(`pkg/ui/widget.js:50`)。

```js
$('#city').autocomplete({ source: '/search/autocomplete', minLength: 2 });
$('#city').autocomplete('option', 'delay', 500);  // あとから設定を変える
$('#city').autocomplete('close');                 // メソッドを呼ぶ
$('#city').on('autocompleteselect', fn);          // イベントは「ウィジェット名 + イベント名」
```

| 仕組み | 中身 | 場所 |
|---|---|---|
| 登録 | `$.widget('ui.名前', 親, プロトタイプ)` でクラスを作り、`$.fn.名前` に橋渡しする | `pkg/ui/widget.js:50`、`:210`(`$.widget.bridge`) |
| 生成 | 既定の `options` と渡された設定を混ぜ、インスタンスを要素の `data` に保存する | `:294`(`_createWidget`) |
| 設定の変更 | `option()` は `_setOption()` を呼ぶ | `:428` |
| イベント | `_on()` で DOM イベントを付け、`_trigger()` で `autocompleteselect` のような独自イベントを投げる | `:561`、`:659` |

DOM を探して書き換える作りです。状態は要素の `data` と `class`(`ui-state-active` など)に置かれます。

#### 1.2 主なウィジェット(1.12.1)

| ウィジェット | 主なオプション(既定値) | 中でやっていること | 場所 |
|---|---|---|---|
| Autocomplete | `source`、`minLength: 1`、`delay: 300`、`position` | `source` が配列なら手元で絞り込み、文字列なら `$.ajax` で JSON を取る。前の通信は `abort()` する。候補は Menu ウィジェットで描き、選んだ値を `liveRegion` に入れて読み上げる | `pkg/ui/widgets/autocomplete.js:42-61`、`:387-410`、`:276-280` |
| Datepicker | `dateFormat: "mm/dd/yy"`、`firstDay: 0`、`minDate` / `maxDate`、言語別の `regional` | ウィジェットファクトリを使わない古い作り(`Datepicker` という 1 つのオブジェクト)。カレンダーの表を HTML の文字列で組み立てる。`role` / `aria-*` は 1 つも出てこない。日本語は `i18n/datepicker-ja.js`(`dateFormat: "yy/mm/dd"`) | `pkg/ui/widgets/datepicker.js:70`、`:86-104`、`:2078`、`pkg/ui/i18n/datepicker-ja.js:28` |
| Dialog | `modal: false`、`autoOpen: true`、`closeOnEscape: true`、`buttons`、`draggable` / `resizable: true` | `body` の末尾に移して `z-index` で前に出す。`modal` のときは覆い(overlay)を作り、`focusin` を見てフォーカスを中に戻す。Tab キーは最初と最後の要素の間で回す。閉じたら開いた要素にフォーカスを戻す | `pkg/ui/widgets/dialog.js:48-80`、`:224`、`:245-284`、`:328-375`、`:869` |
| Tabs | `active`、`collapsible: false`、`event: "click"`、`heightStyle: "content"` | リンクの `href` が `#id` ならその要素を、URL なら Ajax で中身を読んで表示する(`beforeLoad` / `load`) | `pkg/ui/widgets/tabs.js:42-60` |
| Accordion | `active: 0`、`collapsible: false`、`header`、`heightStyle: "auto"` | 見出しと中身の組を見つけ、1 つだけ開く。`heightStyle: "auto"` は全パネルを一番高いものに揃える | `pkg/ui/widgets/accordion.js:41-60` |
| Slider | `min: 0`、`max: 100`、`step: 1`、`range: false`、`values` | 取っ手(`<span>`)をマウスで動かす。キーボードは Home / End / 矢印に対応。`range: true` で 2 つの取っ手 | `pkg/ui/widgets/slider.js:41-60`、`:673-678` |
| Sortable / Draggable / Droppable | `items: "> *"`、`connectWith`、`axis`、`handle`、`placeholder` | `ui/widgets/mouse.js` の `mousedown` から始まる。タッチとポインターイベントには対応しない(`mouse.js` に `touch` / `pointer` の文字が無い)。キーボードでは並べ替えられない | `pkg/ui/widgets/sortable.js:41-75`、`pkg/ui/widgets/mouse.js:44-48` |
| Tooltip | `items: "[title]:not([disabled])"`、`position`、`show` / `hide` | `title` 属性を外してブラウザ標準の吹き出しを止め、自前の吹き出しを出す | `pkg/ui/widgets/tooltip.js:40-56`、`:147-154` |
| Selectmenu | `width`、`position` | 元の `<select>` を隠し、ボタンと Menu で作り直す | `pkg/ui/widgets/selectmenu.js:44-47` |
| Spinner | `min` / `max`、`step`、`page` | 数値入力の横に上下ボタンを付ける | `pkg/ui/widgets/spinner.js:49-53` |
| Progressbar | `max: 100`、`value: 0` | `div` の幅を変える | `pkg/ui/widgets/progressbar.js:37-39` |
| Menu | `items`、`position` | 入れ子のリストをキーボードで操作できるメニューにする | `pkg/ui/widgets/menu.js:39-43` |
| `.position()`(ユーティリティ) | `my`、`at`、`of`、`collision` | ある要素を別の要素の横に置く。画面からはみ出したら反転・ずらす | `pkg/ui/position.js` |
| Effects | `fadeIn` などの拡張、`effect('highlight')` | JS でスタイルを少しずつ変える | `pkg/ui/effect.js`、`pkg/ui/effects/` |

ほかに Button、Checkboxradio、Controlgroup、Resizable、Selectable があります(`pkg/ui/widgets/`)。

#### 1.3 見た目: ThemeRoller の CSS

見た目は `pkg/themes/base/` の CSS(`ui-widget`、`ui-state-default`、`ui-corner-all` など)で決まります。アクセラレータの SCSS にこのクラスの上書きがあれば、それも置き換えの対象です。

#### 1.4 版の注意: 1.12.1 の既知の脆弱性

`jquery-ui@1.12.1` に `npm audit` をかけると、4 件の XSS が出ます(2026-11-27 時点)。

| 内容 | 修正版 | 勧告 |
|---|---|---|
| Datepicker の `altField` オプション | 1.13.0 | GHSA-9gj3-hwp5-pmwc |
| Datepicker の `*Text` オプション(`closeText` など) | 1.13.0 | GHSA-j7qv-pgf6-hvh4 |
| `.position()` の `of` オプション | 1.13.0 | GHSA-gpqq-952q-5327 |
| Checkboxradio のラベルを `refresh` したとき | 1.13.2 | GHSA-h6gj-6jjq-h8g9 |

最新は 1.14.2 で、依存は `jquery` の `>=1.12.0 <5.0.0` です。どれも「信頼できない文字列をオプションに渡したとき」の問題です。

---

### 2. Spartacus の標準にあるか

**結論: 一部ある。** 検索候補、日付、ダイアログ、タブ、アコーディオン、セレクト、数量の増減、吹き出しには標準の部品がある。スライダー、並べ替え、ドラッグ、リサイズは無い。

#### 2.1 ウィジェットごとの対応表

| jQuery UI | Spartacus の標準 | 場所 | 標準に無いとき |
|---|---|---|---|
| Autocomplete(商品検索) | `cx-searchbox`。商品と候補語を出す | `sf/cms-components/navigation/search-box/search-box.component.ts:76` | — |
| Autocomplete(一覧から選ぶ) | ng-select の `[searchable]="true"`(住所フォームの国など) | `fl/user/profile/components/address-book/address-form/address-form.component.html:34-44` | `<input list>` と `<datalist>` |
| Datepicker | `cx-date-picker`。中身はネイティブの `<input type="date">` | `sf/shared/components/form/date-picker/date-picker.component.html:1-13` | — |
| Dialog | `LaunchDialogService` と `[cxFocus]` | `sf/layout/launch-dialog/services/launch-dialog.service.ts:52` | `<dialog>` の `showModal()` |
| Tabs | `cx-tab`(`TAB_MODE.TAB`) | `sf/cms-components/content/tab/tab.component.ts:29` | — |
| Accordion | `cx-tab`(`TAB_MODE.ACCORDIAN`。綴りは原文どおり) | `sf/cms-components/content/tab/tab.model.ts:65-68` | `<details>` / `<summary>` |
| Selectmenu | ng-select(peer 依存)と `NgSelectA11yDirective` | `sf/shared/components/ng-select-a11y/ng-select-a11y.directive.ts:41` | ネイティブの `<select>` |
| Spinner | `cx-item-counter`(数量の − / + ) | `sf/shared/components/item-counter/item-counter.component.ts:32` | `<input type="number">` |
| Tooltip | `[cxPopover]`。クリックとキーボードで開く吹き出し | `sf/shared/components/popover/popover.directive.ts:32` | Popover API、`title` 属性 |
| Menu | `cx-navigation-ui`(CMS のナビゲーション) | `sf/cms-components/navigation/navigation/navigation-ui.component.ts:40` | — |
| `.position()` | `PositioningService`(`cxPopover` が使う) | `sf/shared/services/positioning/positioning.service.ts:27`、`:285` | `@floating-ui/dom` |
| Progressbar | 無い(読み込み中は `cx-spinner`、ボタンは `cx-progress-button`) | `sf/shared/components/spinner/spinner.component.ts:13`、`sf/shared/components/progress-button/progress-button.component.ts:11` | `<progress>` |
| Slider | **無い**。`sf/`、`fl/`、`integration-libs/` の `.html` に `type="range"` は出てこない | — | `<input type="range">`、`nouislider` |
| Sortable / Draggable / Droppable | **無い**。`draggable` / `dragstart` / `cdkDrag` は出てこない | — | HTML Drag and Drop API、`sortablejs`、CDK の DragDrop |
| Resizable / Selectable | 無い | — | CSS の `resize`、チェックボックス |
| Effects | 無い(Spartacus は `@angular/animations` も使っていない) | — | CSS の `transition`、`animate.enter` / `animate.leave`([番外 4](../replacing-jquery.md) 7 節) |

#### 2.2 Autocomplete と `cx-searchbox`

`cx-searchbox` は商品検索の専用部品です。何にでも付けられる入力補完ではありません。

| 項目 | jQuery UI Autocomplete | `cx-searchbox` |
|---|---|---|
| 何文字から探すか | `minLength: 1` | `minCharactersBeforeRequest: 1`(`sf/cms-components/navigation/search-box/search-box.component.ts:61-72`) |
| 件数 | 制限なし(`source` 次第) | `maxProducts: 5`、`maxSuggestions: 5`(同上) |
| 待ち時間 | `delay: 300` で間引く | 間引かない。`(input)` のたびに探す(`search-box.component.html:17`、`search-box.component.ts:377`)。`debounce` は search-box のフォルダに出てこない |
| 通信 | `$.ajax` で URL を叩く | `SearchboxService` 経由で商品と候補語を別々に取る(`search-box-component.service.ts:70`、`:95`、`:112`) |
| 候補の描き方 | Menu ウィジェット | `role="listbox"` の `ul`。一致部分を `cxHighlight` パイプで強調(`search-box.component.html:87-97`) |
| キーボード | 上下キー | 上下キーで候補、左右キーで候補語と商品のグループを移る(`search-box.component.ts:702-712`、`:720-791`) |
| 設定 | オプション | CMS のコンポーネントの属性(`displayProducts`、`displaySuggestions` など。`search-box.component.ts:257-259`) |

商品検索以外の入力補完(住所、店舗、社内の一覧など)は、Spartacus に汎用の部品がありません。一覧が手元にあるなら ng-select の `[searchable]="true"`、サーバーに問い合わせるなら 3.1 節のように自分で書きます。

#### 2.3 Datepicker と `cx-date-picker`

`cx-date-picker` は、ブラウザの日付入力をそのまま使います。カレンダーの見た目はブラウザと OS が決めます。

```html
<cx-date-picker [control]="form.get('date')" min="2026-01-01" max="2026-12-31" [required]="true" />
```

| 項目 | jQuery UI Datepicker | `cx-date-picker` |
|---|---|---|
| カレンダー | 自前の表 | ブラウザ標準(`type="date"`。`date-picker.component.html:3`) |
| 書式 | `dateFormat`、言語ごとの `regional` | 値は常に `yyyy-mm-dd`。表示の書式はブラウザの言語設定で決まる(`date-picker.service.ts:25-37`) |
| 範囲 | `minDate` / `maxDate` | `min` / `max`(`date-picker.component.ts:41-42`)。範囲外は `cx-form-errors` が表示 |
| 祝日を選べなくする、特定の日だけ色を変える | `beforeShowDay` | **できない**(ネイティブの入力では不可能) |
| 読み上げ | `aria-*` が無い | ブラウザ標準の部品なので、OS の読み上げに任せられる |

`cx-date-picker` は、納品希望日(`fl/requested-delivery-date/`)、予算(`fl/organization/administration/`)、見積もり機能(`fl/quote/`)、請求書の絞り込み(`fl/subscription-billing/`)などで使われています。

#### 2.4 Dialog と `LaunchDialogService`

Spartacus のダイアログは、設定で「どのコンポーネントを、どこに描くか」を登録し、`LaunchDialogService.openDialog()` で開きます。カート追加後のダイアログが典型例です。

```ts
// 登録(fl/cart/base/components/added-to-cart-dialog/default-added-to-cart-layout.config.ts:10-18)
export const defaultAddedToCartLayoutConfig: LayoutConfig = {
  launch: {
    ADDED_TO_CART: {
      inlineRoot: true,
      component: AddedToCartDialogComponent,
      dialogType: DIALOG_TYPE.DIALOG,
    },
  },
};

// 開く(added-to-cart-dialog-event.listener.ts:57-62)
this.launchDialogService.openDialog(LAUNCH_CALLER.ADDED_TO_CART, triggerElementRef, undefined, data);
```

```html
<!-- ダイアログ側(added-to-cart-dialog.component.html:1-6) -->
<div class="cx-modal-container" role="dialog" [cxFocus]="focusConfig" (esc)="dismissModal('Escape pressed')">
```

| 項目 | jQuery UI Dialog | Spartacus |
|---|---|---|
| 開く | `$('#x').dialog('open')` | `openDialog(caller, openElement, vcr, data)`(`sf/layout/launch-dialog/services/launch-dialog.service.ts:52-58`) |
| 閉じる | `dialog('close')` | `closeDialog(reason)`。`dialogClose` で理由を受け取る(`:134-139`) |
| 描く場所 | `body` の末尾 | `inline` / `inlineRoot` / `outlet` / ルーティング(`sf/layout/launch-dialog/config/launch-config.ts:38-67`) |
| 種類 | 1 種類 | `DIALOG`、`POPOVER`、`SIDEBAR_START` / `SIDEBAR_END` など(`launch-config.ts:81-88`) |
| フォーカスを閉じ込める | `modal: true` のとき | `[cxFocus]="{ trap: true, block: true, autofocus: …, focusOnEscape: true }"`(`fl/cart/base/components/added-to-cart-dialog/added-to-cart-dialog.component.ts:93-98`) |
| 閉じたらフォーカスを戻す | 開いた要素へ | `openElement` へ(`launch-dialog.service.ts:47-48` のコメント) |
| ドラッグ、リサイズ | あり | 無い |

#### 2.5 Tabs / Accordion と `cx-tab`

`cx-tab` は 1 つの部品で、タブとアコーディオンの両方になります。

```ts
tabConfig: TabConfig = {
  label: 'productDetails.tabs',
  mode: TAB_MODE.TAB,            // または TAB_MODE.ACCORDIAN
  breakpoint: BREAKPOINT.md,     // これより狭いとアコーディオン、広いとタブ
  openTabs: [0],
};
```

```html
<cx-tab [tabs]="tabs" [config]="tabConfig" />
```

| 項目 | jQuery UI | `cx-tab` |
|---|---|---|
| 設定 | `active`、`collapsible` | `openTabs`、`mode`、`breakpoint`、`restrictDirectionKeys`(`sf/cms-components/content/tab/tab.model.ts:39-63`) |
| タブとアコーディオンの切り替え | 別のウィジェット | `breakpoint` で自動で切り替わる(`tab.component.ts:263`。[番外 3](../breakpoint-observer.md) の `BreakpointService` を使う) |
| 開き方 | Tabs は 1 つ、Accordion は 1 つ(`collapsible` で 0 個) | タブは 1 つ、アコーディオンは複数開ける(`tab.component.ts:96-103`、`:196`) |
| キーボード | 矢印、Home、End | 矢印、Home、End(`tab.component.ts:131-165`) |
| ARIA | `role="tablist"` など | タブでは `role="tab"` と `aria-selected`、アコーディオンでは `role="button"` と `aria-expanded`(`tab.component.html:4`、`:12-17`) |
| Ajax で中身を読む | `href` が URL なら読む | 無い。中身は `TemplateRef` で渡す(`tab.model.ts:27`) |
| 高さを揃える | `heightStyle: "auto"` | 無い |

使われている場所は、商品詳細のタブ(`sf/cms-components/content/tab-paragraph-container/tab-paragraph-container.component.html:2`)、絞り込みのアコーディオン(`sf/cms-components/product/product-list/product-facet-navigation/facet-list/facet-list.component.ts:97`)などです。

#### 2.6 Tooltip と `cxPopover`

`cxPopover` はホバーではなく、クリックと Enter / Space で開きます(`sf/shared/components/popover/popover.directive.ts:83-115`)。表示位置は `cxPopoverOptions` の `placement`、`autoPositioning`、`appendToBody` で決めます(`popover.model.ts:46`、`:56`、`:78`)。マウスを乗せただけで出る吹き出しは、Spartacus にありません。

---

### 3. Angular で書くとどうなるか

#### 3.1 入力補完(サーバーに問い合わせる)

```ts
import { Component, inject, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { debounceTime, distinctUntilChanged, filter, switchMap } from 'rxjs';

@Component({
  selector: 'app-city-input',
  template: `
    <label for="city">市区町村</label>
    <input id="city" role="combobox" autocomplete="off"
           aria-controls="city-list" [attr.aria-expanded]="items().length > 0"
           (input)="term.set($any($event.target).value)" />
    @if (items().length) {
      <ul id="city-list" role="listbox">
        @for (c of items(); track c.code) {
          <li role="option" (click)="pick(c)">{{ c.name }}</li>
        }
      </ul>
    }
  `,
})
export class CityInputComponent {
  private api = inject(CityFacade);   // 通信は Facade に任せる(15 章)
  term = signal('');
  items = toSignal(
    toObservable(this.term).pipe(
      debounceTime(300),                 // jQuery UI の delay
      distinctUntilChanged(),
      filter((t) => t.length >= 2),      // jQuery UI の minLength
      switchMap((t) => this.api.search(t)) // 前の問い合わせを捨てる(jQuery UI の xhr.abort())
    ),
    { initialValue: [] }
  );
  pick(c: City) { /* 値を入れて閉じる */ }
}
```

`switchMap` が、jQuery UI の「前の通信を `abort()` する」(`pkg/ui/widgets/autocomplete.js:398-400`)にあたります。上下キーで候補を選ぶ処理と `aria-activedescendant` も要ります。手間を省くなら ng-select の `typeahead` を使います(4 節)。

一覧が小さく、手元にあるなら `<datalist>` で足ります。

```html
<input list="prefs" name="pref" />
<datalist id="prefs">
  @for (p of prefectures; track p) { <option [value]="p"></option> }
</datalist>
```

#### 3.2 ダイアログ

Spartacus の外で独自のダイアログが要るときは、ネイティブの `<dialog>` が使えます。`showModal()` で開くと、背景が操作できなくなり、Esc で閉じ、`::backdrop` で覆いを描けます。jQuery UI の `modal: true` が JS でやっていたこと(`pkg/ui/widgets/dialog.js:328-375`、`:869`)を、ブラウザが担います。

```ts
@Component({
  selector: 'app-confirm',
  template: `
    <button #opener type="button" (click)="dlg().nativeElement.showModal()">削除</button>
    <dialog #dlg aria-labelledby="t" (close)="opener.focus()">
      <h2 id="t">削除しますか</h2>
      <form method="dialog">
        <button value="cancel">やめる</button>
        <button value="ok">削除する</button>
      </form>
    </dialog>
  `,
})
export class ConfirmComponent {
  dlg = viewChild.required<ElementRef<HTMLDialogElement>>('dlg');
}
```

Spartacus のページの中では、フォーカスの扱いと見た目を揃えるため、`LaunchDialogService` を使うほうが無難です。

#### 3.3 アコーディオン、スライダー、進捗

```html
<!-- アコーディオン: name が同じ details は 1 つしか開かない -->
<details name="faq"><summary>送料は?</summary><p>…</p></details>
<details name="faq"><summary>返品は?</summary><p>…</p></details>

<!-- スライダー(取っ手 1 つ) -->
<label>価格の上限 <input type="range" min="0" max="50000" step="1000" [formControl]="max" /></label>
<output>{{ max.value }}</output>

<!-- 進捗 -->
<progress [value]="done()" [max]="total()"></progress>
```

取っ手が 2 つの範囲スライダー(jQuery UI の `range: true`)は、ネイティブの `<input type="range">` にはありません。2 本重ねて CSS で見た目を作るか、ライブラリを使います(4 節)。

#### 3.4 並べ替え(Sortable)

HTML の Drag and Drop API で書けますが、タッチ端末では動かないブラウザがあり、キーボードでは使えません。**並べ替えには、必ず「上へ」「下へ」のボタンも付けます**(WCAG 2.5.7 ドラッグ操作)。ボタンだけなら、配列を入れ替えるだけで済みます。

```ts
items = signal<Item[]>([]);
move(i: number, d: -1 | 1) {
  this.items.update((a) => {
    const b = [...a];
    [b[i], b[i + d]] = [b[i + d], b[i]];
    return b;
  });
}
```

**SSR での注意**:

- `showModal()`、`focus()`、ドラッグの処理はブラウザでだけ動かす。クリックなどのイベントの中で呼ぶなら、サーバーでは呼ばれないので問題ない。ページを開いた直後に呼ぶなら `afterNextRender()`(`@angular/core@21.2.26` の `types/core.d.ts:2576`)の中で呼ぶ
- `<details>`、`<dialog>`、`<input type="range">` は HTML なので、サーバーで描いてもそのまま動く。jQuery UI のように「ブラウザで JS が動くまで素の HTML が見える」ことが無い

---

### 4. ほかの選択肢

| ライブラリ | 版 | peerDependencies | Angular 21 で | 置き換えるウィジェット |
|---|---|---|---|---|
| `@ng-select/ng-select` | Spartacus は `~21.1.4`(Spartacus のルートの `package.json:180`)。最新は 24.2.1 | 21.1.4: `@angular/core` / `@angular/forms` / `@angular/common` `^21.0.0`。24.x は `^22.0.0` と `@angular/cdk` `^22.0.0` | Spartacus の版なら可 | Selectmenu、一覧からの Autocomplete(`typeahead` でサーバー検索も) |
| `@ng-bootstrap/ng-bootstrap` | 最新 21.0.0、Angular 21 向けは 20.0.0 | 20.0.0: `@angular/core` / `@angular/common` / `@angular/forms` / `@angular/localize` `^21.0.0`、`@popperjs/core` `^2.11.8` | 20.0.0 なら可 | Datepicker(祝日の無効化など)、Typeahead、Modal、Nav、Accordion、Tooltip、Popover。Spartacus と同じ Bootstrap 系の見た目 |
| `ngx-bootstrap` | 最新 22.0.0、21 系は 21.2.2 | 21.2.2: `@angular/core` / `@angular/forms` / `@angular/common` `^21.2.0` | 21.2.2 なら可 | Datepicker、Typeahead、Modal、Tabs、Accordion、Tooltip、Sortable |
| `@angular/cdk` | 最新 22.3.0、21 系は 21.2.14(dist-tag `v21-lts`) | 21.2.14: `@angular/core` ほか `^21.0.0 \|\| ^22.0.0` | 21.2.14 なら可 | DragDrop(Sortable)、Dialog、Overlay(`.position()`)、Accordion。**Spartacus は `@angular/cdk` に依存していない**ので、新しく入れることになる |
| `sortablejs` | 1.15.7 | 無い | フレームワーク非依存 | Sortable。タッチにも対応 |
| `nouislider` | 15.8.1 | 無い | フレームワーク非依存 | 取っ手 2 つの Slider |
| `@floating-ui/dom` | 1.8.0 | 無い | フレームワーク非依存 | `.position()`、Tooltip の位置合わせ |
| `jquery-ui` | 1.14.2 | 依存: `jquery` `>=1.12.0 <5.0.0` | jQuery を残す場合のみ | 残すなら少なくともこの版へ(1.4 節) |

`@angular/material@21.2.14` にも Datepicker、Dialog、Slider などがありますが、見た目が Material Design で、Spartacus の Bootstrap 系の見た目とは合いません。

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| 商品検索の候補 | `cx-searchbox`(標準) |
| 決まった一覧から選ぶ、絞り込みながら選ぶ | ng-select の `[searchable]="true"`(Spartacus にすでにある) |
| サーバーに問い合わせる入力補完 | 3.1 節の `debounceTime` + `switchMap`。手間を省くなら ng-select の `typeahead` |
| 日付を選ぶ | `cx-date-picker` |
| 祝日を選べなくする、営業日だけ選ばせる | `@ng-bootstrap/ng-bootstrap@20` の Datepicker(`markDisabled`)。またはサーバー側で検証し、`cx-form-errors` で知らせる |
| ダイアログ | `LaunchDialogService` と `[cxFocus]`。Spartacus の外なら `<dialog>` |
| タブ、アコーディオン | `cx-tab`。CMS の外の簡単な開閉は `<details>` |
| スライダー(取っ手 1 つ) | `<input type="range">` |
| 範囲スライダー(取っ手 2 つ) | `nouislider`、または `<input type="range">` を 2 本 |
| 並べ替え | 「上へ / 下へ」ボタン + 必要なら `sortablejs`。CDK を入れてよいなら `@angular/cdk@21` の DragDrop |
| 吹き出し | `[cxPopover]`。ホバーで出したいなら Popover API と CSS |
| jQuery UI を当面残す | 1.14.2 に上げる。テーマの CSS が Spartacus の SCSS とぶつからないか確かめる |

---

### 6. コンピュータサイエンスの観点から

- **ウィジェットファクトリは「DOM に状態を貼り付ける」クラスの仕組みだった**: `$.widget()` はプロトタイプ継承でクラスを作り、インスタンスを DOM 要素の `data` に保存する。状態の持ち主が DOM なので、Angular のテンプレートが同じ要素を描き直すと、インスタンスは消えるか食い違う。Angular のコンポーネントは、状態をクラスのフィールドに置き、DOM はその写しにする([番外 4](../replacing-jquery.md))
- **ブラウザの標準がウィジェットを吸収した**: 2012 年頃の jQuery UI の主な仕事は、ブラウザに無い部品を作ることだった。その後、`<input type="date">`、`<input type="range">`、`<progress>`、`<datalist>`、`<dialog>`、`<details name>`、Popover API が標準になった。標準の部品は、キーボード操作と読み上げをブラウザが受け持つ。jQuery UI の Datepicker に ARIA が 1 つも無い(1.2 節)ことと比べると差が大きい
- **入力補完は「競合状態」の問題**: 速く打つと、前の問い合わせの結果が後から届き、新しい結果を上書きすることがある。jQuery UI は前の `xhr` を `abort()` し、さらに `requestIndex` で古い応答を捨てる(`pkg/ui/widgets/autocomplete.js:64`、`:459-464`)。RxJS の `switchMap` は、これを「新しい値が来たら前の購読をやめる」という 1 つの演算子で表す
- **ドラッグは入力手段に依存する**: jQuery UI の Sortable はマウスのイベントだけで作られている。タッチ、ペン、キーボード、音声入力では使えない。Pointer Events は入力の種類を 1 つにまとめたが、キーボードと音声は残る。だから並べ替えには、ドラッグとは別の操作(ボタン)を用意する
