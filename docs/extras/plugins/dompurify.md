# DOMPurify: 信頼できない HTML から危険な部分を取り除く

> **この章が答える問い**: アクセラレータが読み込む `purify.min.js`(DOMPurify)は何をしているのか。Spartacus(Angular)には同じ役割の仕組みがあるのか。Spartacus がサニタイズを無効にしているのはどこで、なぜなのか。段落コンポーネントのそれはなぜ問題になり得るのか。DOMPurify を Angular に持ち込むなら、Trusted Types と SSR で何に気をつけるのか

> **根拠の取り方**:
> - **プラグイン**: npm の `dompurify@3.5.0`(2026-11-27 時点の `latest`。2026-11-22 公開)の tarball を展開し、`dist/purify.es.mjs`、`src/tags.ts`、`src/attrs.ts`、`README.md` を読んだ。アクセラレータのファイル名(`purify.min.js`)には版が無いので、最新版について書く。アクセラレータが実際に同梱している版とは違う可能性がある。以下 `pkg/` はパッケージのルート
> - **Angular**: npm の `@angular/core@21.2.26` の `fesm2022/_debug_node-chunk.mjs`(以下 `ng/`)。サニタイザの実装がここにある
> - **Spartacus**: SAP/spartacus `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`core/` は `core-libs/core/src/`、`il/` は `integration-libs/` を指す。`.spec.ts` は除いて grep した
> - 代替ライブラリのバージョンは 2026-11-27 に `npm view` で確認した

---

### 先に話し言葉で: Angular は「既定で消毒する」、DOMPurify は「自分で消毒する」

DOMPurify は、外から来た HTML 文字列を受け取り、`<script>` や `onerror` 属性のような危険な部分を取り除いて返すライブラリです。jQuery のプラグインではありません。jQuery の `.html()` は文字列をそのまま DOM に入れるので、アクセラレータでは DOMPurify を挟んで XSS を防いでいたと考えられます(アクセラレータ側の呼び出し箇所は確認していません)。

Angular では、`[innerHTML]` に文字列を渡すと、**Angular が自動でサニタイズします**。DOMPurify に当たるものが最初から組み込まれているので、多くの場面では何も足す必要がありません。

ただし Spartacus の段落コンポーネント(`CMSParagraphComponent`)は、`bypassSecurityTrustHtml` で **Angular のサニタイズをわざと切っています**。CMS の HTML を書き換えずにそのまま出すためです。CMS の編集者が書いた HTML を「信頼できる」とみなす設計です。この前提が成り立たない場合に、DOMPurify を使う意味が出てきます。

DOMPurify を Angular に持ち込むなら、「DOMPurify で消毒してから `bypassSecurityTrustHtml` で渡す」が基本形です。SSR では DOMPurify は DOM が無いと動きません。動かないときは**入力をそのまま返す**ので、サーバー側では特に注意が要ります(3.4 節)。

---

### 1. DOMPurify は何をするか

#### 1.1 主な API

| API | 内容 | 場所 |
|---|---|---|
| `DOMPurify.sanitize(dirty, cfg?)` | HTML 文字列(または DOM ノード)を消毒して返す。既定の戻り値は文字列 | `pkg/dist/purify.es.mjs:2543` |
| `DOMPurify(window)` | 指定した `window` に結び付いた新しいインスタンスを作る。サーバーで jsdom の `window` を渡すときに使う | `:1094-1096` |
| `DOMPurify.isSupported` | この環境で消毒できるか。DOM が無いと `false` | `:1100`, `:1179` |
| `DOMPurify.setConfig(cfg)` / `clearConfig()` | 既定の設定を固定する | `:2562` |
| `DOMPurify.addHook(name, fn)` | 要素や属性を処理する前後に、自分の処理を差し込む | `:2584` |
| `DOMPurify.removed` | 直前の `sanitize` で取り除いたものの一覧 | `:1098` |

主な設定(`cfg`)は次のとおりです(`pkg/README.md:211` 以降)。

| 設定 | 内容 |
|---|---|
| `ALLOWED_TAGS` / `ALLOWED_ATTR` | 許可する要素・属性を、既定の代わりに指定する |
| `ADD_TAGS` / `ADD_ATTR` | 既定の許可リストに足す(`:1420-1424`) |
| `FORBID_TAGS` / `FORBID_ATTR` | 許可リストから外す。例: `FORBID_ATTR: ['style']` |
| `USE_PROFILES` | `{ html: true }`、`{ svg: true }` などの組み合わせで許可リストを選ぶ |
| `RETURN_DOM` / `RETURN_DOM_FRAGMENT` | 文字列ではなく DOM を返す |
| `RETURN_TRUSTED_TYPE` | Trusted Types が使えれば `TrustedHTML` を返す(`:1369`) |
| `TRUSTED_TYPES_POLICY` | 内部で使う Trusted Types のポリシーを渡す。`null` で内部ポリシーを作らない(`:1441-1452`) |

#### 1.2 中でどう動いているか

| 処理 | 中身 | 場所 |
|---|---|---|
| 判定はブラウザのパーサに任せる | 文字列を自前の正規表現で解析しない。ブラウザの DOM パーサで実際に DOM を作り、木をたどって許可リストに無い要素と属性を消す。ブラウザが解釈するのと同じ形で判定するので、解析のずれを突く攻撃に強い | `pkg/README.md:39` |
| 許可リスト方式 | 既定の許可リストは HTML・SVG・MathML の要素と属性。`form`、`input`、`button`、`style` 要素、`style` 属性も既定で許可されている | `pkg/src/tags.ts:20`, `:48`, `:62`, `:102`、`pkg/src/attrs.ts:110` |
| DOM が無い環境では何もしない | `window` が無い、または `window.document` が無いと `isSupported = false` になる。そのとき `sanitize` は**入力をそのまま返す** | `pkg/dist/purify.es.mjs:1026-1028`, `:1100-1102`, `:2470` |
| Trusted Types のポリシーを自分で作る | `window.trustedTypes` があれば `dompurify` という名前のポリシーを作る。作れないと警告を出す | `:1037-1056` |

README は「消毒したあとに HTML を書き換えると、消毒の効果が消える」と注意しています(`pkg/README.md:80-82`)。消毒は**最後に**かけるのが原則です。

---

### 2. Spartacus の標準にあるか

結論: **一部ある**。Angular 標準のサニタイズが同じ役割を担う。DOMPurify 自体は使っていない。

`dompurify`、`sanitize-html`、`trustedTypes` は、`core-libs`、`feature-libs`、`integration-libs` のどこにも出てきません。

#### 2.1 Angular 標準のサニタイズ

`[innerHTML]` に文字列を渡すと、Angular は `ɵɵsanitizeHtml` を通します(`ng/_debug_node-chunk.mjs:3319-3330`)。中身は次のとおりです。

| 処理 | 中身 | 場所 |
|---|---|---|
| 不活性な DOM で解析する | `DOMParser` か `<template>` で解析する。スクリプトは実行されない | `ng/…:3016`, `:3036` |
| 結果が安定するまで解析し直す | 解析の前後で文字列が変わるあいだ繰り返す(最大 5 回)。mXSS への対策 | `:3196-3206` |
| 許可リスト方式 | 要素は `VALID_ELEMENTS`、属性は `VALID_ATTRS` だけ残す。`script`・`style`・`template` は中身ごと捨てる | `:3072-3083`, `:3131-3134` |
| URL 属性を検査する | `href`、`src` などは `SAFE_URL_PATTERN` で `javascript:` を落とす | `:3048-3051`, `:3136` |
| 開発時に警告する | 何か消したら `WARNING: sanitizing HTML stripped some content` を出す | `:3209-3211` |

DOMPurify との一番大きな違いは、**許可リストの広さ**です。

| 対象 | Angular 標準 | DOMPurify の既定 |
|---|---|---|
| `style` 属性 | 消す(`HTML_ATTRS` に無い。`ng/…:3080`) | 残す |
| `<style>` 要素 | 中身ごと捨てる(`:3083`) | 残す |
| `<form>`、`<input>`、`<button>` | 消す(`VALID_ELEMENTS` に無い。`:3072-3078`) | 残す |
| SVG、MathML | 消す | 残す(危険な属性は消す) |
| 設定の変更 | できない(`Sanitizer` を差し替えるしかない) | `ALLOWED_TAGS`、`FORBID_ATTR`、フックなどで細かく変えられる |

CMS の HTML に `style="color:red"` を書くと、Angular 標準では色が消えます。Spartacus がサニタイズを切っている箇所と、その理由は 2.2 節と 2.3 節にまとめました。

#### 2.2 Spartacus でサニタイズを切っている箇所

`bypassSecurityTrust` を使っているのは、本体のソースでは 4 ファイルです。

| 場所 | 何を信頼しているか |
|---|---|
| `sf/cms-components/content/paragraph/paragraph.component.ts:49-51`、テンプレート `paragraph.component.html:3` | **CMS の段落の `content`**。`cxSupplementHashAnchors` パイプで `#id` だけのリンクを書き換えたあと、`bypassSecurityTrustHtml` で渡す。`CMSParagraphComponent` と `CMSTabParagraphComponent` の両方に使われる(`paragraph.module.ts:24-29`) |
| `sf/cms-components/misc/icon/icon-loader.service.ts:44`, `:52` | アイコン。SVG の URL は先に `sanitize(SecurityContext.URL, …)` で検査し(`:35-38`)、テキストのアイコンは `textContent` 経由でエスケープしてから信頼する。外からの HTML ではない |
| `il/opf/checkout/components/opf-checkout-payment-wrapper/opf-checkout-payment-wrapper.component.ts:103-109`、テンプレート `:44`, `:88` | 決済サービス(OPF)から返る HTML と、`iframe` の URL |
| `il/opf/cta/components/opf-cta-element/opf-cta-element.component.ts:36-50` | 決済サービスの CTA の HTML。ブラウザでは `<script>` を取り除いてから信頼する。SSR では文字列のまま返し、Angular の標準サニタイズに任せる(コメント `:37`) |

段落のテンプレートはこうなっています。

```html
<!-- sf/cms-components/content/paragraph/paragraph.component.html:1-4 -->
<div
  *ngIf="component.data$ | async as data"
  [innerHTML]="bypassSecurityTrustHtml(data.content | cxSupplementHashAnchors)"
></div>
```

つまり、CMS の編集者が段落に `<img src=x onerror=…>` を書くと、そのまま実行されます。CMS の編集権限を持つ人を信頼できるなら、これは仕様です。信頼の範囲が広い場合(外部の制作会社、取り込んだデータなど)は、段落コンポーネントを差し替えて DOMPurify を挟みます(2.5 節)。

一方、次のような `[innerHTML]` はサニタイズを切っていないので、Angular 標準のサニタイズが効きます(`[innerHTML]` は本体の HTML テンプレートに 23 か所)。

| 場所 | 値 |
|---|---|
| `sf/cms-components/content/banner/banner.component.html:10`, `:16` | バナーの `headline`、`content` |
| `sf/cms-components/product/product-tabs/product-details-tab/product-details-tab.component.html:2` | 商品の `description` |
| `sf/cms-components/product/product-summary/product-summary.component.html:22` | 商品の `summary` |
| `sf/cms-components/product/product-list/product-list-item/product-list-item.component.html:29` | 検索結果の `nameHtml`(ハイライト付きの商品名) |

#### 2.3 サニタイズを切っている理由

2.2 節の 4 か所について、なぜサニタイズを切っているのかを 1 つずつ見ます。理由がソースのコメントに書かれているものと、書かれていないものがあります。書かれていないものは、「Angular の標準のサニタイズを通すと何が消えるか」から推測し、推測だと明記します。

`il/opf/` 配下の 2 か所は、決済の統合ライブラリ(Open Payment Framework。`@spartacus/opf`)のものです。このライブラリを入れたときだけ動きます。

##### まとめ

| 場所 | 渡す値の出どころ | 切っている理由 | 理由の根拠 | 代わりに何で守っているか |
|---|---|---|---|---|
| 段落 | CMS の編集者が書いた HTML | `style`、`id`、`name` 属性や、`<form>`、`<iframe>`、SVG を残すため | **推測**(コメントなし) | 守っていない。CMS の編集者を信頼する前提 |
| アイコン | Spartacus の設定(`IconConfig`) | `<svg><use xlink:href>` を出すため | **推測**(コードから明らか) | URL を先に `sanitize(SecurityContext.URL)`。文字は `textContent` でエスケープ |
| OPF 決済画面 | 決済サービスが返す HTML と URL | 決済サービスのフォームや入れ物を残すため。`iframe` の `src` は、bypass しないと必ず例外になるため | HTML は**推測**。URL は Angular の仕様 | `iframe` に `sandbox` 属性を設定で付けられる |
| OPF の CTA | 決済サービスが返す HTML | 決済ボタンの HTML を残すため | **コメントあり**(`<script>` を除くのは暫定) | ブラウザでは `<script>` を取り除く。SSR では bypass しない |

##### 段落コンポーネント(`CMSParagraphComponent`、`CMSTabParagraphComponent`)

```ts
// sf/cms-components/content/paragraph/paragraph.component.ts:49-51
public bypassSecurityTrustHtml(html: string = ''): SafeHtml {
  return this.sanitizer.bypassSecurityTrustHtml(html);
}
```

- **何を渡しているか**: CMS の段落の `content` に、`cxSupplementHashAnchors` パイプを通したもの(`paragraph.component.html:3`)
- **理由**: ソースにも、メソッドのコメントにも書かれていない。Angular の標準のサニタイズを通すと、次のものが消える(`ng/…:3072-3080`)。CMS の編集者が普通に書く HTML が崩れるのを避けるため、と考えられる(**推測**)
  - `style` 属性(文字の色、配置など)
  - `id`・`name` 属性。ページ内リンクの飛び先が消える。`cxSupplementHashAnchors` パイプが `#id` だけのリンクを補っている(`sf/shared/pipes/suplement-hash-anchors/supplement-hash-anchors.pipe.ts:10-20`)ことから、Spartacus は段落の中でページ内リンクが使われる前提でいる
  - `<form>`、`<input>`、`<iframe>`、`<svg>`(`VALID_ELEMENTS` に無い)。埋め込み動画や問い合わせフォームが消える
- **代わりの守り**: 無い。`cxSupplementHashAnchors` パイプは `<template>` 要素の `innerHTML` に代入して `<a>` を探す(`:36-49`)。`<template>` の中身は実行されないので、パイプ自体は安全である。ただし、危険な部分を取り除くことはしない。パイプが返した文字列は、そのまま bypass される
- **結果**: CMS の段落に書いた `<img src=x onerror=…>` や `<a href="javascript:…">` は、そのままページに入る。なお、`innerHTML` で入れた `<script>` は、ブラウザの仕様で実行されない

##### アイコン(`cx-icon`)

```ts
// sf/cms-components/misc/icon/icon-loader.service.ts:33-46(抜粋)
const url = this.sanitizer.sanitize(SecurityContext.URL, this.getSvgPath(type) || null);
if (url) {
  const useElement = this.winRef.document.createElement('use');
  useElement.setAttribute('xlink:href', url);
  const svgElement = this.winRef.document.createElement('svg');
  svgElement.appendChild(useElement);
  return this.sanitizer.bypassSecurityTrustHtml(svgElement.outerHTML);
}
```

- **何を渡しているか**: Spartacus 自身が組み立てた `<svg><use xlink:href="…"></use></svg>`、または文字のアイコン。テンプレートは `<i [outerHTML]="icon">`(`sf/cms-components/misc/icon/icon.component.html:2`)
- **理由**: Angular の標準のサニタイズでは `svg` と `use` が許可リストに無いので、SVG のアイコンが丸ごと消える(`ng/…:3072-3078`)。そのため bypass が要る(**推測**だが、コードから明らか)。文字のアイコンも bypass しているのは、戻り値の型を `SafeHtml` に揃えるためと考えられる(**推測**)
- **代わりの守り**: 外から来る HTML を信頼しているわけではない
  - SVG の URL は、bypass の前に `sanitize(SecurityContext.URL, …)` で検査する(`:35-38`)。`javascript:` などはここで落ちる
  - 文字のアイコンは `textContent` に入れてから `innerHTML` で取り出す(`:50-52`)。`<` などはエスケープされる
  - メソッドのコメントも「DOM に安全に足せる HTML 断片を返す」としている(`:30-32`)
- **結果**: 値の出どころが Spartacus の設定なので、危険は小さい。設定の `IconConfig` に外部の値を流し込まない限り問題にならない

##### OPF の決済画面(`cx-opf-checkout-payment-wrapper`)

```ts
// il/opf/checkout/components/opf-checkout-payment-wrapper/opf-checkout-payment-wrapper.component.ts:103-109
bypassSecurityTrustHtml(html: string): SafeHtml {
  return this.sanitizer.bypassSecurityTrustHtml(html);
}
bypassSecurityTrustResourceUrl(url: string): SafeResourceUrl {
  return this.sanitizer.bypassSecurityTrustResourceUrl(url);
}
```

ここでは 2 種類の値を信頼しています。

**`iframe` の URL**(テンプレート `:39-45`)

- **何を渡しているか**: 決済サービスの画面の URL(`paymentLink.destination.url`)
- **理由**: `iframe` の `src` は Angular の「リソース URL」の文脈で、ここだけは**サニタイズで安全にする方法が無い**。bypass していない値を渡すと、Angular は必ず例外を投げる(`ng/…:3352-3361` の `ɵɵsanitizeResourceUrl`。エラーは `unsafe value used in a resource URL context`)。外部の決済画面を `iframe` に出すには、bypass するしかない(Angular の仕様)
- **代わりの守り**: `cxOpfSandbox` ディレクティブで `iframe` に `sandbox` 属性を付けられる(`opf-iframe-sandbox.directive.ts:18-22`)。値は決済の選択肢ごとに、設定 `opf.paymentOption.iframeSandboxMap` で決める(`opf-checkout-payment-wrapper.component.ts:111-117`)。設定しなければ付かない

**決済サービスの HTML**(テンプレート `:87-89`)

- **何を渡しているか**: 決済セッションの `dynamicScript.html`。決済サービス(OPF のバックエンド経由)が返す HTML である(`opf-checkout-payment-wrapper.service.ts:284-305`)
- **理由**: ソースに書かれていない。決済サービスの HTML には、カード入力などのフォームや、決済サービスの JS が描き込む入れ物(`id` 付きの `<div>` など)が入る。Angular の標準のサニタイズでは `<form>`、`<input>`、`id` 属性が消えるので、決済画面が描けなくなるため、と考えられる(**推測**)
- **関連する処理**: `innerHTML` で入れた `<script>` は実行されない。そのため OPF は、HTML の中の最初の `<script>` の中身を取り出し、`Function(…)()` で実行する(`il/opf/base/root/services/opf-resource-loader.service.ts:174-184`)
  - これは bypass よりさらに強い信頼で、決済サービスの JS をそのまま動かす
  - SSR では実行しない(コメント「SSR mode not supported for security concerns」、`:175`)
  - 実行するのは、まだ決済の画面にいるときだけ(`opf-checkout-payment-wrapper.service.ts:74-93`)
  - `htmlContentMode` が `SEPARATE` のときは実行しない(`:307-313`。`il/opf/base/root/model/opf-base.model.ts:42-45`)

##### OPF の CTA(`cx-opf-cta-element`)

```ts
// il/opf/cta/components/opf-cta-element/opf-cta-element.component.ts:36-50
renderHtml(html: string): SafeHtml {
  // Display sanitized html in SSR for security concerns
  return this.windowRef.isBrowser()
    ? this.sanitizer.bypassSecurityTrustHtml(this.removeScriptTags(html))
    : html;
}

// Removing script tags on FE until BE fix: CXSPA-8572
protected removeScriptTags(html: string) { … }
```

- **何を渡しているか**: 決済サービスの「すぐ買う」ボタンなどの HTML(`dynamicScript.html`)
- **理由**: 決済サービスのボタンの HTML を、そのまま描くため。ソースのコメントから、次の 2 つが読み取れる
  - **SSR では bypass しない**: サーバーでは文字列のまま返し、Angular の標準のサニタイズに任せる(「Display sanitized html in SSR for security concerns」、`:37`)
  - **`<script>` を取り除くのは暫定措置**: 「バックエンドが直るまで、フロントで `<script>` を取り除く」とある(「Removing script tags on FE until BE fix: CXSPA-8572」、`:43`)。CXSPA-8572 は SAP 社内の課題番号で、中身は公開されていない
- **代わりの守り**: ブラウザでは、`DOMParser` で `<script>` を見つけ、その `outerHTML` を文字列から取り除いてから bypass する(`:44-50`)。`onerror` などのイベント属性や、`javascript:` の URL は取り除かない
- **関連する処理**: 取り除いた `<script>` の中身は、`OpfCtaScriptsService` が別途 `executeScriptFromHtml` で実行する(`il/opf/cta/components/opf-cta-scripts/opf-cta-scripts.service.ts:50-55`)。つまり `<script>` を消すのは、「`innerHTML` で入れない」ためであって、「実行しない」ためではない

##### 反対の例: あえてサニタイズを通している箇所

`ng-select-a11y` ディレクティブは、ng-select が描いた選択肢の文字を、`sanitize(SecurityContext.HTML, …)` に通してから入力欄の `value` に入れている(`sf/shared/components/ng-select-a11y/ng-select-a11y.directive.ts:225-231`, `:250-251`)。DOM を直接触る場面でも、Angular のテンプレートを通らない値は自分でサニタイズする、という書き方の例になる。

##### 段落とほかの 3 か所の違い

| 観点 | 段落 | アイコン | OPF の 2 か所 |
|---|---|---|---|
| 誰が値を書くか | CMS の編集者(人) | 開発者(設定) | 外部の決済サービス |
| 書ける人の範囲 | CMS の権限の持ち方で広くも狭くもなる | 開発者だけ | 決済サービスと、その通り道 |
| 切る前の検査 | 無い | URL の検査、エスケープ | `<script>` の除去(CTA だけ)、`sandbox`(設定したときだけ) |
| ライブラリを入れないと動かないか | 標準で動く | 標準で動く | `@spartacus/opf` を入れたときだけ |

段落だけは、標準の Spartacus で動き、外から来る値をまったく検査せずに信頼しています。DOMPurify を挟む候補になるのは、主にここです(2.5 節)。

#### 2.4 Trusted Types

Angular は Trusted Types に対応しています。ブラウザに `trustedTypes` があれば、`angular` と `angular#unsafe-bypass` の 2 つのポリシーを作ります(`ng/…:2892-2937`)。`bypassSecurityTrustHtml` で渡した値は、後者のポリシーで `TrustedHTML` になります。

Spartacus は Trusted Types の設定を持っていません(`trustedTypes`、`TrustedHTML` は grep で 0 件)。CSP の `require-trusted-types-for 'script'` を有効にする場合は、次の点に注意します。

- `trusted-types` の許可リストに `angular` と `angular#unsafe-bypass` が要る。DOMPurify を入れるなら `dompurify` も要る(または DOMPurify に `TRUSTED_TYPES_POLICY: null` を渡す。`pkg/README.md:180-205`)
- `cxSupplementHashAnchors` パイプは `<template>` の `innerHTML` に文字列を直接代入している(`sf/shared/pipes/suplement-hash-anchors/supplement-hash-anchors.pipe.ts:37-38`)。Trusted Types を強制すると、ここで例外になると考えられる(動かして確かめてはいない)

#### 2.5 Spartacus の部品と組み合わせる例

段落コンポーネントで DOMPurify を挟むには、CMS のマッピングで `CMSParagraphComponent` と `CMSTabParagraphComponent` を自作のコンポーネントに差し替えます。標準のマッピングは `sf/cms-components/content/paragraph/paragraph.module.ts:22-31` にあります。DOMPurify を呼ぶところは 3.2 節と同じです。

```ts
import { Component, inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { toSignal } from '@angular/core/rxjs-interop';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { CmsConfig, CmsParagraphComponent, provideConfig } from '@spartacus/core';
import { CmsComponentData, SupplementHashAnchorsPipe } from '@spartacus/storefront';
import DOMPurify from 'dompurify';

@Component({
  selector: 'app-safe-paragraph',
  imports: [SupplementHashAnchorsPipe],
  template: `<div [innerHTML]="purify(data()?.content | cxSupplementHashAnchors)"></div>`,
})
export class SafeParagraphComponent {
  protected readonly data = toSignal(
    inject<CmsComponentData<CmsParagraphComponent>>(CmsComponentData).data$
  );
  private readonly sanitizer = inject(DomSanitizer);
  private readonly isBrowser = isPlatformBrowser(inject(PLATFORM_ID));

  purify(html: string): SafeHtml | string {
    // リンクの書き換え(cxSupplementHashAnchors)を先に、DOMPurify を最後にかける
    return this.isBrowser
      ? this.sanitizer.bypassSecurityTrustHtml(DOMPurify.sanitize(html))
      : html; // サーバーでは Angular の標準サニタイズに任せる
  }
}

// アプリの providers に足す
export const safeParagraphProviders = [
  provideConfig(<CmsConfig>{
    cmsComponents: {
      CMSParagraphComponent: { component: SafeParagraphComponent },
      CMSTabParagraphComponent: { component: SafeParagraphComponent },
    },
  }),
];
```

- `CmsComponentData` は `sf/cms-structure/page/model/cms-component-data.ts:10-13`、`cxSupplementHashAnchors` パイプは `sf/shared/pipes/suplement-hash-anchors/supplement-hash-anchors.pipe.ts:21`, `:36`、`provideConfig` は `core/config/config-providers.ts:18-27` にある
- 標準の段落コンポーネントは、段落の中のリンクのクリックを拾い、同じホストへのリンクを `Router.navigateByUrl` で開く(`sf/cms-components/content/paragraph/paragraph.component.ts:29-42`)。差し替えると、この処理も無くなる。要るなら同じ `@HostListener('click')` を書き写す
- 「サーバーでは Angular の標準サニタイズに任せ、ブラウザで bypass する」形は、Spartacus の OPF の CTA と同じである(`il/opf/cta/components/opf-cta-element/opf-cta-element.component.ts:36-41`)

---

### 3. Angular 標準で書くとどうなるか(Spartacus を使わない)

この節は、`@angular/*` とブラウザ標準(と DOMPurify 本体)だけで書きます。Spartacus の部品と組み合わせる書き方は 2.5 節にあります。

#### 3.1 まずは何も足さない

外から来た HTML を出すだけなら、`[innerHTML]` に文字列を渡すだけです。Angular が消毒します。

```html
<div [innerHTML]="html()"></div>
```

文字として出したいなら `{{ html() }}` にします。こちらはエスケープされ、タグとして解釈されません。

#### 3.2 Angular 標準より広く許可したいとき: DOMPurify + bypass

`style` 属性などを残したいときは、DOMPurify で消毒してから `bypassSecurityTrustHtml` で渡します。Angular の消毒を二重にかけると、DOMPurify が残したものを Angular が消してしまうからです。

```ts
import { Component, computed, inject, input, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import DOMPurify from 'dompurify';

@Component({
  selector: 'app-rich-text',
  template: `<div [innerHTML]="safeHtml()"></div>`,
})
export class RichTextComponent {
  readonly html = input('');
  private readonly sanitizer = inject(DomSanitizer);
  private readonly isBrowser = isPlatformBrowser(inject(PLATFORM_ID));

  readonly safeHtml = computed<SafeHtml | string>(() => {
    if (!this.isBrowser) {
      // サーバーでは DOMPurify が動かない。Angular の標準サニタイズに任せる
      return this.html();
    }
    const clean = DOMPurify.sanitize(this.html(), {
      FORBID_TAGS: ['style', 'form'],
    });
    return this.sanitizer.bypassSecurityTrustHtml(clean);
  });
}
```

受け取った HTML のリンクを書き換えるなど、ほかの処理もかけるなら、**書き換えを先に、DOMPurify を最後に**かけます(1.2 節の README の注意)。

#### 3.3 何か所でも使うならパイプにする

同じ処理を多くのテンプレートで使うなら、パイプにまとめます。

```ts
import { inject, Pipe, PipeTransform, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import DOMPurify, { type Config } from 'dompurify';

@Pipe({ name: 'purify' })
export class PurifyPipe implements PipeTransform {
  private readonly sanitizer = inject(DomSanitizer);
  private readonly isBrowser = isPlatformBrowser(inject(PLATFORM_ID));

  transform(html: string | null | undefined, config: Config = {}): SafeHtml | string {
    const value = html ?? '';
    if (!this.isBrowser) {
      return value; // サーバーでは Angular の標準サニタイズに任せる
    }
    return this.sanitizer.bypassSecurityTrustHtml(DOMPurify.sanitize(value, config));
  }
}
```

```html
<div [innerHTML]="article.body | purify: { FORBID_ATTR: ['style'] }"></div>
```

- パイプは既定で純粋(pure)なので、`html` と `config` が変わったときだけ消毒し直す。テンプレートに書いたオブジェクトリテラル(`{ FORBID_ATTR: … }`)は、中の値が変わらない限り同じオブジェクトが渡されるので、変更検知のたびに消毒し直すことはない
- `Config` 型は DOMPurify の型定義から import できる(`pkg/dist/purify.es.d.mts:446`)
- `@taiga-ui/dompurify` の `dompurify` パイプ(4 節)も同じ形をとっている

#### 3.4 SSR での注意

- **DOMPurify は DOM が無いと何もしない**。Node.js で `import DOMPurify from 'dompurify'` すると、`window` が無いので `isSupported = false` のインスタンスができる。このとき `sanitize()` は例外を出さず、**入力をそのまま返す**(`pkg/dist/purify.es.mjs:1100-1102`, `:2470`)。サーバーで「消毒したつもり」になるのが一番危ない
- サーバーで消毒したいなら、jsdom の `window` を渡してインスタンスを作る(`pkg/README.md:94-133`)。README は最新の jsdom を強く勧め、happy-dom は安全ではないとしている(`:98-102`)
- Angular のサーバー用の `document`(`inject(DOCUMENT).defaultView`。`DOCUMENT` は `@angular/core` から import できる)を DOMPurify に渡したときに、`isSupported` が `true` になるか、安全に動くかは確認していない。DOMPurify の README はこの組み合わせに触れていない
- 3.2 節と 3.3 節の例のように、サーバーでは Angular の標準サニタイズに任せ、ブラウザで DOMPurify に切り替える方法もある。判定には `isPlatformBrowser(inject(PLATFORM_ID))` を使う。この場合、サーバーで描いた HTML とブラウザで描き直した HTML が違う(`style` 属性の有無など)ので、表示が一瞬変わることがある

---

### 4. ほかの選択肢

| ライブラリ | 版(2026-11-27) | peerDependencies | 内容 |
|---|---|---|---|
| `dompurify` | 3.5.0 | なし(`@types/trusted-types` を optional で持つ) | 本章の対象。型定義を同梱している |
| `@taiga-ui/dompurify` | 5.0.2 | `@angular/core` と `@angular/platform-browser` が `>=19.0.0`、`dompurify` が `^3.2.7` | DOMPurify を Angular のパイプ(`dompurify`)と `Sanitizer` として包む。インスタンスは `inject(DOCUMENT).defaultView` から作る |
| `isomorphic-dompurify` | 4.9.0 | なし(`jsdom@^31.0.1` と `dompurify@^3.5.0` に依存) | サーバーでは jsdom を内部で用意する。Node.js は `^22.22.2 \|\| ^24.15.0 \|\| >=26.0.0` |
| `sanitize-html` | 2.18.2 | なし | DOM を使わず `htmlparser2` で解析する。サーバーだけで消毒するときの候補 |
| `@tinkoff/ng-dompurify` | 4.0.0 | `@angular/core >=12.0.0` など | `@taiga-ui/dompurify` の旧名。2023-10 から更新されていない |

`@taiga-ui/dompurify` の注意点:

- README は `{ provide: Sanitizer, useClass: NgDompurifySanitizer }` で Angular のサニタイザごと差し替える方法を載せている。しかし `NgDompurifySanitizer.sanitize` は、受け取った値を `String(value)` にしてから DOMPurify に渡す(`fesm2022/taiga-ui-dompurify.mjs:65-72`)。Angular は `bypassSecurityTrustHtml` の結果(`SafeHtml`)もこのサニタイザに渡す(`ng/…:3324-3325`)。`SafeHtml` を文字列にすると `SafeValue must use [property]=binding: …` という文になる(`ng/…:2945-2946`)。ソースを読む限り、差し替えると Spartacus の段落コンポーネントの表示が壊れると考えられる(動かして確かめてはいない)。Spartacus では**パイプのほうを使う**のが無難
- パイプ(`value | dompurify`)は、消毒した結果を `bypassSecurityTrustHtml` で包んで返す(`:89-95`)。3.2 節と同じ形

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| 外から来た HTML を出すだけで、`style` などが消えてもよい | `[innerHTML]` に文字列を渡す。Angular 標準で足りる |
| 文字として出せばよい | `{{ }}` で出す |
| CMS の段落など、Spartacus が bypass している箇所で、HTML の書き手を信頼しきれない | `CMSParagraphComponent` を差し替え、DOMPurify で消毒してから bypass する(2.5 節) |
| Angular 標準より広く許可したい(`style` 属性、SVG など) | DOMPurify + `bypassSecurityTrustHtml`(3.2 節)。パイプにするなら自作の `purify` パイプ(3.3 節)か、`@taiga-ui/dompurify` の `dompurify` パイプ |
| Spartacus を使わない Angular アプリで、外から来た HTML を出す | まず `[innerHTML]` で Angular 標準に任せる(3.1 節)。足りなければ DOMPurify を `isPlatformBrowser` で包んだコンポーネントかパイプ(3.2〜3.3 節)。Spartacus 固有の差し替えは要らない |
| SSR でもサーバーで消毒したい | jsdom の `window` で DOMPurify を作る(`isomorphic-dompurify` でもよい)。または DOM を使わない `sanitize-html` |
| Trusted Types を強制したい | CSP の `trusted-types` に `angular`、`angular#unsafe-bypass` を入れる。DOMPurify を使うなら `dompurify` も入れるか、`TRUSTED_TYPES_POLICY: null` を渡す。Spartacus 側(Spartacus を使わないなら自分のコード)で文字列を `innerHTML` に代入している箇所を洗い出す |

---

### 6. コンピュータサイエンスの観点から

- **許可リストと拒否リスト**: Angular も DOMPurify も「安全と分かっているものだけ残す」許可リスト方式です。「危険なものを消す」拒否リスト方式は、新しい要素や属性が増えるたびに穴が開きます。HTML の仕様は増え続けるので、許可リストのほうが壊れにくい
- **パーサの差分を突く攻撃(mXSS)**: 消毒する側とブラウザとで HTML の解釈が違うと、消毒後の文字列をブラウザが別の形に組み立て直し、危険な要素が生まれることがあります。両者ともブラウザ自身のパーサで解析し、Angular は「結果が変わらなくなるまで解析し直す」ことで対策しています(`ng/…:3196-3206`)。サーバーで DOMPurify を使うときに DOM の実装(jsdom の版など)が重要になるのも同じ理由です
- **型で信頼を表す**: Angular の `SafeHtml` と、ブラウザの `TrustedHTML` は、どちらも「この文字列は検査済み」という情報を型で運ぶ仕組みです。ただの `string` を危険な代入先(`innerHTML`)に渡せないようにすることで、検査漏れを実行時やコンパイル時に見つけられます。`bypassSecurityTrust…` は、その型を手で作る「抜け道」です。grep で数えられるので、監査の起点になります
