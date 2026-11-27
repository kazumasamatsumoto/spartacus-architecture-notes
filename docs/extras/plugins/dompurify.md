# DOMPurify: 信頼できない HTML から危険な部分を取り除く

> **この章が答える問い**: アクセラレータが読み込む `purify.min.js`(DOMPurify)は何をしているのか。Spartacus(Angular)には同じ役割の仕組みがあるのか。Spartacus の段落コンポーネントがサニタイズを無効にしているのはなぜ問題になり得るのか。DOMPurify を Angular に持ち込むなら、Trusted Types と SSR で何に気をつけるのか

> **根拠の取り方**:
> - **プラグイン**: npm の `dompurify@3.5.0`(2026-11-27 時点の `latest`。2026-11-22 公開)の tarball を展開し、`dist/purify.es.mjs`、`src/tags.ts`、`src/attrs.ts`、`README.md` を読んだ。アクセラレータのファイル名(`purify.min.js`)には版が無いので、最新版について書く。アクセラレータが実際に同梱している版とは違う可能性がある。以下 `pkg/` はパッケージのルート
> - **Angular**: npm の `@angular/core@21.2.26` の `fesm2022/_debug_node-chunk.mjs`(以下 `ng/`)。サニタイザの実装がここにある
> - **Spartacus**: SAP/spartacus `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`il/` は `integration-libs/` を指す。`.spec.ts` は除いて grep した
> - 代替ライブラリのバージョンは 2026-11-27 に `npm view` で確認した

---

### 先に話し言葉で: Angular は「既定で消毒する」、DOMPurify は「自分で消毒する」

DOMPurify は、外から来た HTML 文字列を受け取り、`<script>` や `onerror` 属性のような危険な部分を取り除いて返すライブラリです。jQuery のプラグインではありません。jQuery の `.html()` は文字列をそのまま DOM に入れるので、アクセラレータでは DOMPurify を挟んで XSS を防いでいたと考えられます(アクセラレータ側の呼び出し箇所は確認していません)。

Angular では、`[innerHTML]` に文字列を渡すと、**Angular が自動でサニタイズします**。DOMPurify に当たるものが最初から組み込まれているので、多くの場面では何も足す必要がありません。

ただし Spartacus の段落コンポーネント(`CMSParagraphComponent`)は、`bypassSecurityTrustHtml` で **Angular のサニタイズをわざと切っています**。CMS の HTML を書き換えずにそのまま出すためです。CMS の編集者が書いた HTML を「信頼できる」とみなす設計です。この前提が成り立たない場合に、DOMPurify を使う意味が出てきます。

DOMPurify を Angular に持ち込むなら、「DOMPurify で消毒してから `bypassSecurityTrustHtml` で渡す」が基本形です。SSR では DOMPurify は DOM が無いと動きません。動かないときは**入力をそのまま返す**ので、サーバー側では特に注意が要ります(3.3 節)。

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

CMS の HTML に `style="color:red"` を書くと、Angular 標準では色が消えます。Spartacus の段落コンポーネントがサニタイズを切っている理由の 1 つは、おそらくこれです(Spartacus のソースに理由は書かれていません)。

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

つまり、CMS の編集者が段落に `<img src=x onerror=…>` を書くと、そのまま実行されます。CMS の編集権限を持つ人を信頼できるなら、これは仕様です。信頼の範囲が広い場合(外部の制作会社、取り込んだデータなど)は、段落コンポーネントを差し替えて DOMPurify を挟みます(3.2 節)。

一方、次のような `[innerHTML]` はサニタイズを切っていないので、Angular 標準のサニタイズが効きます(`[innerHTML]` は本体の HTML テンプレートに 23 か所)。

| 場所 | 値 |
|---|---|
| `sf/cms-components/content/banner/banner.component.html:10`, `:16` | バナーの `headline`、`content` |
| `sf/cms-components/product/product-tabs/product-details-tab/product-details-tab.component.html:2` | 商品の `description` |
| `sf/cms-components/product/product-summary/product-summary.component.html:22` | 商品の `summary` |
| `sf/cms-components/product/product-list/product-list-item/product-list-item.component.html:29` | 検索結果の `nameHtml`(ハイライト付きの商品名) |

#### 2.3 Trusted Types

Angular は Trusted Types に対応しています。ブラウザに `trustedTypes` があれば、`angular` と `angular#unsafe-bypass` の 2 つのポリシーを作ります(`ng/…:2892-2937`)。`bypassSecurityTrustHtml` で渡した値は、後者のポリシーで `TrustedHTML` になります。

Spartacus は Trusted Types の設定を持っていません(`trustedTypes`、`TrustedHTML` は grep で 0 件)。CSP の `require-trusted-types-for 'script'` を有効にする場合は、次の点に注意します。

- `trusted-types` の許可リストに `angular` と `angular#unsafe-bypass` が要る。DOMPurify を入れるなら `dompurify` も要る(または DOMPurify に `TRUSTED_TYPES_POLICY: null` を渡す。`pkg/README.md:180-205`)
- `cxSupplementHashAnchors` パイプは `<template>` の `innerHTML` に文字列を直接代入している(`sf/shared/pipes/suplement-hash-anchors/supplement-hash-anchors.pipe.ts:37-38`)。Trusted Types を強制すると、ここで例外になると考えられる(動かして確かめてはいない)

---

### 3. Angular で書くとどうなるか

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

Spartacus の段落に入れるなら、`CMSParagraphComponent` のマッピングを自作のコンポーネントに差し替えます。`cxSupplementHashAnchors` のようにリンクを書き換える処理があるなら、**書き換えを先に、DOMPurify を最後に**かけます(1.2 節の README の注意)。

#### 3.3 SSR での注意

- **DOMPurify は DOM が無いと何もしない**。Node.js で `import DOMPurify from 'dompurify'` すると、`window` が無いので `isSupported = false` のインスタンスができる。このとき `sanitize()` は例外を出さず、**入力をそのまま返す**(`pkg/dist/purify.es.mjs:1100-1102`, `:2470`)。サーバーで「消毒したつもり」になるのが一番危ない
- サーバーで消毒したいなら、jsdom の `window` を渡してインスタンスを作る(`pkg/README.md:94-133`)。README は最新の jsdom を強く勧め、happy-dom は安全ではないとしている(`:98-102`)
- Angular のサーバー用の `document`(`inject(DOCUMENT).defaultView`)を DOMPurify に渡したときに、`isSupported` が `true` になるか、安全に動くかは確認していない。DOMPurify の README はこの組み合わせに触れていない
- 3.2 節の例のように、サーバーでは Angular の標準サニタイズに任せ、ブラウザで DOMPurify に切り替える方法もある。Spartacus の OPF の CTA も同じ形をとっている(`il/opf/cta/components/opf-cta-element/opf-cta-element.component.ts:36-41`)。この場合、サーバーで描いた HTML とブラウザで描き直した HTML が違う(`style` 属性の有無など)ので、表示が一瞬変わることがある

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
| CMS の段落など、Spartacus が bypass している箇所で、HTML の書き手を信頼しきれない | `CMSParagraphComponent` を差し替え、DOMPurify で消毒してから bypass する |
| Angular 標準より広く許可したい(`style` 属性、SVG など) | DOMPurify + `bypassSecurityTrustHtml`。パイプにするなら `@taiga-ui/dompurify` の `dompurify` パイプ |
| SSR でもサーバーで消毒したい | jsdom の `window` で DOMPurify を作る(`isomorphic-dompurify` でもよい)。または DOM を使わない `sanitize-html` |
| Trusted Types を強制したい | CSP の `trusted-types` に `angular`、`angular#unsafe-bypass` を入れる。DOMPurify を使うなら `dompurify` も入れるか、`TRUSTED_TYPES_POLICY: null` を渡す。Spartacus 側で文字列を `innerHTML` に代入している箇所を洗い出す |

---

### 6. コンピュータサイエンスの観点から

- **許可リストと拒否リスト**: Angular も DOMPurify も「安全と分かっているものだけ残す」許可リスト方式です。「危険なものを消す」拒否リスト方式は、新しい要素や属性が増えるたびに穴が開きます。HTML の仕様は増え続けるので、許可リストのほうが壊れにくい
- **パーサの差分を突く攻撃(mXSS)**: 消毒する側とブラウザとで HTML の解釈が違うと、消毒後の文字列をブラウザが別の形に組み立て直し、危険な要素が生まれることがあります。両者ともブラウザ自身のパーサで解析し、Angular は「結果が変わらなくなるまで解析し直す」ことで対策しています(`ng/…:3196-3206`)。サーバーで DOMPurify を使うときに DOM の実装(jsdom の版など)が重要になるのも同じ理由です
- **型で信頼を表す**: Angular の `SafeHtml` と、ブラウザの `TrustedHTML` は、どちらも「この文字列は検査済み」という情報を型で運ぶ仕組みです。ただの `string` を危険な代入先(`innerHTML`)に渡せないようにすることで、検査漏れを実行時やコンパイル時に見つけられます。`bypassSecurityTrust…` は、その型を手で作る「抜け道」です。grep で数えられるので、監査の起点になります
