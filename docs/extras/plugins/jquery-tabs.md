# タブ(jquery.tabs.custom.js): 見出しを押すと、対応するパネルだけを表示する

> **この章が答える問い**: アクセラレータが読み込んでいる `jquery.tabs.custom.js` は何をしているのか。Spartacus には同じ役割の部品があるのか。Angular では、タブやアコーディオンをどう書けばよいのか

> **根拠の取り方**:
> - **プラグイン**: `jquery.tabs.custom.js` の原典は**特定できなかった**。ファイル名に作者やバージョンが無く、`.custom` が付いている(アクセラレータ側で手が入っている)ためである。`.custom` での変更点も確認できない。そこで本ノートでは、一般的な jQuery のタブプラグインの機能として扱う。機能の裏付けには、jQuery のタブで一番広く使われている **jQuery UI Tabs** を代表例として読んだ(npm の `jquery-ui@1.14.2` の `ui/widgets/tabs.js`。以下 `pkg/` はパッケージのルート)。**アクセラレータのファイルが jQuery UI Tabs だという意味ではない**。なお、アクセラレータは `jquery-ui-1.12.1.min.js` も別に読み込んでいる(jQuery UI そのものについては [jQuery UI のノート](jquery-ui.md) を参照)
> - **Spartacus**: [SAP/spartacus](https://github.com/SAP/spartacus) `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`fl/` は `feature-libs/` を指す
> - 代替ライブラリのバージョンと peerDependencies は 2026-11-27 に npm で確認した

---

### 先に話し言葉で: Spartacus にはタブの部品がある

タブのプラグインは、見出しの並び(タブ)と中身の箱(パネル)を結び付け、選んだタブのパネルだけを見せます。どのタブのプラグインでも、だいたい「どのタブを開いておくか」「切り替えのアニメーション」「キーボード操作」「中身を Ajax で読む」あたりを持っています。

Spartacus には、標準のタブの部品 **`TabComponent`(`cx-tab`)** があります。商品詳細ページのタブ(CMS の `CMSTabParagraphContainer`)もこれで描いています。画面が狭いときはアコーディオンに切り替わります。`role="tab"` や `aria-selected`、矢印キーでの移動もそろっています。

Spartacus の画面の中なら、まず `cx-tab` を使います。独自のタブを書くときも、状態は「開いているタブの番号」の 1 つだけです。`signal` で持ち、`@if` で出し分ければ、プラグインは要りません。

---

### 1. タブのプラグインは何をするか

#### 1.1 使い方(一般的な形)

```html
<div class="js-tabs">
  <ul>
    <li><a href="#tab-1">詳細</a></li>
    <li><a href="#tab-2">仕様</a></li>
    <li><a href="/p/123/reviews">レビュー</a></li>   <!-- 中身を Ajax で読む -->
  </ul>
  <div id="tab-1">…</div>
  <div id="tab-2">…</div>
</div>
```

```js
$('.js-tabs').tabs({ active: 0 });
```

#### 1.2 主な機能

jQuery のタブプラグインに共通する機能を、jQuery UI Tabs のオプションで示す。オプションの一覧は `pkg/ui/widgets/tabs.js:43-62`。

| 機能 | jQuery UI Tabs での名前 | 内容 |
|---|---|---|
| 最初に開くタブ | `active` | 番号で指定する。URL の `#` があれば、それに合うタブを開く(`:114-140`) |
| すべて閉じられるか | `collapsible` | 開いているタブをもう一度押すと閉じる |
| 開くきっかけ | `event` | 既定は `click`。`mouseover` にもできる |
| パネルの高さ | `heightStyle` | 中身に合わせる、一番高いパネルに揃える、など |
| アニメーション | `show` / `hide` | 切り替えのときのフェードなど |
| 使えないタブ | `disabled` | 選べないタブを指定する |
| 中身を Ajax で読む | (タブの `href` がページ内の `#` でなければ自動) | `$.ajax` で取得してパネルに入れる。読み込み中は `aria-busy="true"`(`:858-870`) |
| 通知 | `beforeActivate` / `activate` / `beforeLoad` / `load` | 切り替えの前後、読み込みの前後 |

#### 1.3 中でどう動いているか(jQuery UI Tabs)

| 処理 | 中身 | 場所 |
|---|---|---|
| 役割を付ける | リストに `role="tablist"`、各見出しに `role="tab"`、パネルに `role="tabpanel"`。`aria-controls` と `aria-labelledby` で結ぶ | `pkg/ui/widgets/tabs.js:402-486` |
| 開いている状態 | 開いたタブに `aria-selected="true"` と `aria-expanded="true"`、パネルに `aria-hidden="false"` | `:685-708` |
| ページ内か Ajax か | タブの URL が今のページと同じで `#` があればページ内、そうでなければ Ajax | `:64-75`, `:858-862` |
| 矢印キー | 左右・上下で隣のタブへ、Home / End で最初・最後へ。フォーカスを移し、**300ms 後に**そのタブを開く(自動で開く方式)。Ctrl を押しながらならフォーカスだけ移す | `:42`, `:178-240` |
| Enter / Space | すぐに開く。Enter は開いているタブなら閉じる(`collapsible` のとき) | `:203-218` |

---

### 2. Spartacus の標準にあるか

**結論: ある。** `TabComponent`(`selector: 'cx-tab'`)である。

#### 2.1 使い方

```ts
import { Component } from '@angular/core';
import { TabComponent, Tab, TabConfig, TAB_MODE, BREAKPOINT } from '@spartacus/storefront';

@Component({
  selector: 'app-product-info',
  imports: [TabComponent],
  template: `
    <ng-template #details>詳細の中身</ng-template>
    <ng-template #specs>仕様の中身</ng-template>

    <cx-tab [tabs]="[
        { headerKey: 'productDetails.details', content: details, id: 0 },
        { headerKey: 'productDetails.specs',   content: specs,   id: 1 }
      ]"
      [config]="config" />
  `,
})
export class ProductInfoComponent {
  config: TabConfig = {
    label: 'productDetails.tabs',  // tablist の aria-label(翻訳キー)
    openTabs: [0],                 // 最初に開くタブ
    breakpoint: BREAKPOINT.md,     // md より広いとタブ、狭いとアコーディオン
  };
}
```

商品詳細ページのタブ(`TabParagraphContainerComponent`)は、CMS のコンポーネントを `ng-template` に描き、それを `cx-tab` に渡している。

| 部品 | 場所 |
|---|---|
| CMS のマッピング(`CMSTabParagraphContainer`) | `sf/cms-components/content/tab-paragraph-container/tab-paragraph-container.module.ts:33-34` |
| 既定の設定(`openTabs: [0]`、`breakpoint: BREAKPOINT.md`) | `tab-paragraph-container.component.ts:39-42` |
| タブの作り方(`headerKey`、`content`、`id: index`) | `tab-paragraph-container.component.ts:187-195` |
| `cx-tab` に渡すところ | `tab-paragraph-container.component.html:2` |
| ほかの利用 | ファセット(`sf/cms-components/product/product-list/product-facet-navigation/facet-list/facet-list.component.html:27`)、店舗受け取りの選択(`fl/pickup-in-store/components/presentational/pickup-options/pickup-options.component.html:7`) |

#### 2.2 入力と設定

| 項目 | 内容 | 場所 |
|---|---|---|
| `tabs` / `tabs$` | タブの配列。Observable でも渡せる | `sf/cms-components/content/tab/tab.component.ts:49-50` |
| `config` | `TabConfig` | `:51` |
| `disabled` | すべてのタブのボタンを使えなくする | `:52` |
| `Tab.headerKey` / `header` / `headerParams` | 見出し(翻訳キーか文字列) | `sf/cms-components/content/tab/tab.model.ts:11-23` |
| `Tab.content` | パネルの中身(`TemplateRef`) | `tab.model.ts:27` |
| `Tab.id` | タブとパネルを結ぶ番号 | `tab.model.ts:31` |
| `TabConfig.mode` | `TAB` か `ACCORDIAN`(綴りは原文のまま)。固定したいとき | `tab.model.ts:47`, `:65-68` |
| `TabConfig.breakpoint` | これより広いとタブ、狭いとアコーディオン | `tab.model.ts:53` |
| `TabConfig.openTabs` | 最初に開くタブの番号 | `tab.model.ts:57` |
| `TabConfig.restrictDirectionKeys` | タブは左右、アコーディオンは上下の矢印キーだけにする | `tab.model.ts:62` |

#### 2.3 仕組み

| 処理 | 中身 | 場所 |
|---|---|---|
| 状態 | 開いているタブの番号の配列を `BehaviorSubject<number[]>` で持つ | `tab.component.ts:62`, `:66-69` |
| タブとアコーディオンの切り替え | `mode` があればそれ。無ければ `BreakpointService.isUp(breakpoint)` で決める | `tab.component.ts:254-268` |
| 選ぶ | タブなら「その 1 つだけを開く」、アコーディオンなら「開閉を反転」 | `tab.component.ts:96-105`, `:196-205` |
| 矢印キー | 左上・右下で前後、Home / End で最初・最後。端では反対の端へ回る。**フォーカスを移すだけで、開くのは Enter / Space(ボタンの `click`)** | `tab.component.ts:117-125`, `:136-167` |
| roving tabindex | タブモードでは、開いているタブだけ `tabindex="0"`、ほかは `-1`。アコーディオンでは全部 `0` | `tab.component.ts:213-219` |
| 役割と状態 | タブモードでは `role="tablist"` / `role="tab"` / `aria-selected`。アコーディオンでは `role="button"` / `aria-expanded` | `sf/cms-components/content/tab/tab.component.html:3-22` |
| パネル | タブモードでは `role="tabpanel"`、アコーディオンでは `role="region"`。開いているパネルだけを `*ngIf` で描く | `tab.component.html:58-60`、`sf/cms-components/content/tab/panel/tab-panel.component.html:1-12` |
| パネルの Esc | パネルの中で Esc を押すと、パネルの枠にフォーカスが戻る(`cxFocus` の `focusOnEscape`) | `tab-panel.component.html:9` |

#### 2.4 プラグインとの差

| 観点 | jQuery のタブ(jQuery UI Tabs で確認) | Spartacus `cx-tab` |
|---|---|---|
| 中身の渡し方 | 既存の HTML(`#id` のパネル) | `TemplateRef` |
| 閉じているパネル | DOM に残して隠す | DOM に作らない(`*ngIf`) |
| Ajax で中身を読む | ある | 無い。中身のコンポーネントが自分でデータを取る |
| 矢印キーで開くか | フォーカスの 300ms 後に自動で開く | フォーカスだけ。Enter / Space で開く |
| アコーディオン | 別のウィジェット(jQuery UI Accordion) | 同じ部品で、ブレークポイントにより自動で切り替わる |
| 同時に複数開く | タブでは不可 | アコーディオンモードなら可 |
| URL の `#` と連動 | ある | 無い |
| 切り替えのアニメーション | `show` / `hide` | 無い |
| 翻訳 | 無い | 見出しは翻訳キーで書ける |

---

### 3. Angular で書くとどうなるか

状態は「開いているタブ」の 1 つだけである。`signal` で持ち、テンプレートで役割と状態を書く。

```ts
import { Component, ElementRef, signal, viewChildren } from '@angular/core';

@Component({
  selector: 'app-tabs',
  template: `
    <div role="tablist" aria-label="商品情報" (keydown)="onKey($event)">
      @for (t of tabs; track t.id; let i = $index) {
        <button #tabBtn type="button" role="tab"
                [id]="'tab-' + t.id"
                [attr.aria-controls]="'panel-' + t.id"
                [attr.aria-selected]="active() === i"
                [tabindex]="active() === i ? 0 : -1"
                (click)="active.set(i)">{{ t.label }}</button>
      }
    </div>
    @for (t of tabs; track t.id; let i = $index) {
      <div role="tabpanel" [id]="'panel-' + t.id" [attr.aria-labelledby]="'tab-' + t.id"
           tabindex="0" [hidden]="active() !== i">
        @if (active() === i) { {{ t.body }} }
      </div>
    }
  `,
})
export class TabsComponent {
  tabs = [
    { id: 'details', label: '詳細', body: '…' },
    { id: 'specs', label: '仕様', body: '…' },
  ];
  active = signal(0);
  private buttons = viewChildren<ElementRef<HTMLButtonElement>>('tabBtn');

  onKey(e: KeyboardEvent) {
    const n = this.tabs.length;
    const next = { ArrowRight: this.active() + 1, ArrowLeft: this.active() - 1, Home: 0, End: n - 1 }[e.key];
    if (next === undefined) return;
    e.preventDefault();
    this.active.set((next + n) % n);                       // 端では反対の端へ
    this.buttons()[this.active()].nativeElement.focus();   // ここでは「移したら開く」方式
  }
}
```

**ポイント**

- **開く方式を決める**: 上の例は「矢印で移したら開く」(自動)。Spartacus の `cx-tab` は「移すだけで、Enter / Space で開く」(手動)。パネルの中身が重い(描画や通信に時間がかかる)ときは手動が向く
- **閉じているパネル**: `@if` で DOM から消すと、中のコンポーネントは破棄され、入力中の値も消える。残したいなら `[hidden]` だけで隠す。上の例は枠を `[hidden]` で残し、中身を `@if` で消している
- **アコーディオンだけで足りるなら `<details>` / `<summary>`**: ブラウザ標準で開閉でき、JS が要らない。`name` 属性を揃えると、同じ名前の `<details>` は 1 つしか開かなくなる(「1 つだけ開く」アコーディオン)
- **タブとアコーディオンの切り替え**: Spartacus の画面なら `BreakpointService.isUp()` を使う([番外 3](../breakpoint-observer.md))。`cx-tab` の `breakpoint` はこれを使っている
- **アニメーション**: 切り替えの動きが要るなら CSS か、`@angular/core` の `animate.enter` / `animate.leave` で書く。`@angular/animations` は 20.2 で非推奨なので使わない([番外 4 の 7 節](../replacing-jquery.md))

**SSR での注意**

- タブは `signal` とテンプレートだけで書けるので、サーバーでもそのまま描ける。最初に開くタブの中身はサーバーの HTML に入るので、検索エンジンにも読まれる
- 閉じているタブの中身を `@if` で消すと、その中身はサーバーの HTML に入らない。検索エンジンに読ませたい中身なら、`[hidden]` で隠すだけにする
- URL の `#` で最初のタブを決めたいときは、`location.hash` を直接読まない。サーバーには `location` が無く、`#` はそもそもサーバーに送られない。Angular の `ActivatedRoute.fragment` を使い、ブラウザで切り替わる前提で書く

---

### 4. ほかの選択肢

| ライブラリ | バージョン | peerDependencies | Angular 21 で使えるか | 内容 |
|---|---|---|---|---|
| `@angular/aria`(`ngTabs` / `ngTabList` / `ngTab` / `ngTabPanel`) | `21.2.14`(dist-tag `v21-lts`) | `@angular/cdk` `21.2.14`、`@angular/core` `^21.0.0 \|\| ^22.0.0` | 使える。ただし型定義に `@developerPreview 21.0` とある | 見た目を持たない、アクセシビリティの振る舞いだけの部品。`selectionMode`(`follow` / `explicit`)で自動・手動を選べる。`latest` は 22.3.0(Angular 22 以降) |
| `@ng-bootstrap/ng-bootstrap`(`ngbNav`) | `20.0.0` | `@angular/core` `^21.0.0` ほか、`@angular/localize`、`@popperjs/core` | 20.x なら使える。`latest`(21.0.0)は Angular 22 が必要 | Bootstrap の見た目のタブ |
| `ngx-bootstrap`(`TabsModule`) | `21.2.2` | `@angular/core` `^21.2.0` | 21.x なら使える。`latest`(22.0.0)は Angular 22 が必要 | Bootstrap の見た目のタブ |

- `@angular/aria` は `@angular/cdk` を peerDependencies に持つ。**Spartacus は `@angular/cdk` に依存していない**ので、使うなら CDK も足すことになる。バージョンは Angular に揃える
- Spartacus の見た目(Bootstrap 由来の SCSS)に合わせるなら、ng-bootstrap か ngx-bootstrap は見た目が近い。ただし、`cx-tab` で足りる場面で足す理由は少ない

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| Spartacus の画面でタブを出す | `cx-tab`(`TabComponent`) |
| 狭い画面でアコーディオンに切り替えたい | `cx-tab` の `config.breakpoint` |
| アコーディオンだけでよく、JS を使いたくない | `<details>` / `<summary>`(1 つだけ開くなら `name` 属性) |
| `cx-tab` の見た目や振る舞いが合わない | `signal` と `@for` で自前のタブを書く(3 節)。アクセシビリティの振る舞いを任せたいなら `@angular/aria@21`(開発者プレビュー) |
| タブの中身を Ajax で読みたい | Ajax は使わない。パネルの中のコンポーネントが、Facade 経由でデータを取る([15 章](../../15-facade-connector-adapter.md)) |

---

### 6. コンピュータサイエンスの観点から

- **状態は 1 つの整数**: タブの UI がどれほど凝っていても、状態は「開いているタブの番号」だけである。jQuery のプラグインは、この状態を DOM のクラス(`.active` など)に持たせていた。そのため、状態を読むにも DOM を探す必要があった。Angular では状態を変数に持ち、DOM はその写像になる
- **フォーカスと選択を分けるか**: WAI-ARIA のタブの作法には、「矢印で移したら開く」と「移すだけで、Enter / Space で開く」の 2 通りがある。jQuery UI は前者に 300ms の遅延を入れて、素早く通り過ぎたタブを開かないようにしている。Spartacus の `cx-tab` は後者である。どちらも「選択のたびに重い処理を走らせない」ための工夫である
- **roving tabindex**: タブの並びは、Tab キーでは 1 回で通り過ぎ、中は矢印キーで動く。これを「選ばれた 1 つだけ `tabindex="0"`、ほかは `-1`」で実現する。部品の中の移動と、部品どうしの移動を分ける考え方で、ツールバーやメニューでも同じ形を使う
