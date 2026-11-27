# pstrength: パスワード入力欄の下に、強さを色と言葉で示すバーを出す

> **この章が答える問い**: アクセラレータの `jquery.pstrength.custom-1.2.0.js` は何をしていたのか。Spartacus にパスワードの強さを示す部品はあるのか。無いなら、Angular でどう書けばよいのか。そもそも「強さのメーター」は今も要るのか

> **根拠の取り方**:
> - **プラグイン**: Tane Piper 氏の「jQuery Password Strength Plugin (PStrength)」(MIT ライセンス)。npm には無い(npm の `pstrength` は別の作者の別のプラグインで、`jquery.pstrength` は 2024-12 に取り下げられている)。作者の配布元(digitalspaghetti.me.uk)も読めなかった。そこで、**GitHub の公開リポジトリに第三者が同梱している写し** を読んだ
>   - 1.2 系: `jquery.pstrength-min.1.2.js` などの名前の写し 4 本(AspxCommerce/AspxCommerce2.7、Orangescrum/opensource-community-edition、dixya/online-shopping-management-system、jbroadway/sitellite)。**4 本とも、それぞれの同梱先で手が入っている**(色、文言、挿入する場所など)。以下では 4 本に共通する部分だけを書く。行番号は、整形済みで手の入り方が小さい AspxCommerce の写し(`SageFrame/js/jquery.pstrength-min.1.2.js`)で示し、`v12/` と書く
>   - 1.4: phpvms_5.5.x の `lib/js/jquery.pstrength.js`(作者のヘッダーと変更履歴が残っている)。以下 `v14/`
> - **`.custom` について**: ファイル名に `.custom` が付いているので、アクセラレータ側で手が入っている。この章は元のプラグインについて書く。`.custom` での変更点は確認できない。ファイル名の `1.2.0` が上の 1.2 系と同じものかも、確かめられていない
> - **Spartacus**: SAP/spartacus `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`core/` は `core-libs/core/src/`、`fl/` は `feature-libs/` を指す
> - 代替ライブラリのバージョンは 2026-11-27 に npm で確認

---

### 先に話し言葉で: Spartacus には「メーター」は無く、「規則のチェック」がある

pstrength は、パスワードの入力欄の下に細いバーと「Weak」「Strong」などの言葉を出すプラグインです。キーを押すたびに点数を計算し、点数に応じてバーの幅と色を変えます。点数は、長さと文字の種類(大文字、数字、記号)の足し算です。

Spartacus に強さのメーターはありません。その代わり、**パスワードの規則をバリデーターで検査** し、満たしていない規則を `cx-form-errors` で 1 つずつ表示します。規則は「8 文字以上 128 文字以下」「大文字・数字・記号を 1 つ以上」「同じ文字を続けない」などです。パスワードを表示して確かめるボタン(`cxPasswordVisibilitySwitch`)もあります。

メーターがどうしても要るなら、Angular では `computed()` で点数を出し、`<meter>` 要素で描けば数行で書けます。Spartacus を使わないプロジェクトでも、規則の検査は `@angular/forms` のバリデーターで、表示の切り替えはボタン 1 つで書けます(3 節)。点数の計算には、文字の種類を数える方式ではなく、よく使われるパスワードや辞書の単語を見つける `zxcvbn` 系のライブラリを使うほうが、実際の強さに近くなります。

---

### 1. pstrength は何をするか

#### 1.1 使い方

```js
$('#password').pstrength();
$('#password').pstrength({ minchar: 8, common: ['password', 'qwerty'] });
```

入力欄の **`id` が必須** です。表示用の要素の `id` を、入力欄の `id` から作るからです(`v12/:13`)。

#### 1.2 オプション(1.2 系)

| オプション | 既定値 | 内容 | 場所 |
|---|---|---|---|
| `verdects` | `["Very weak","Weak","Medium","Strong","Very strong"]` | 5 段階の言葉。綴りは原文どおり(verdicts の誤り) | `v12/:5` |
| `colors` | `["#f00","#c06","#f60","#3c0","#3f0"]` | 5 段階の色 | `v12/:6` |
| `scores` | `[10, 15, 30, 40]` | 段階の境目の点数 | `v12/:7` |
| `common` | `["password","sex","god","123456","123","liverpool","letmein","qwerty","monkey"]` | 使ってはいけない単語。**完全一致** だけを見る | `v12/:8`、`:130-134` |
| `minchar` | `6` | 最低の文字数 | `v12/:9` |

1.4 では、`minChar` / `verdicts` に綴りが直され、文言(`tooShortMsg`、`unsafeMsg`、`minCharMsg`)と `powMax`、`displayMin` が加わっています(`v14/:43-54`)。アクセラレータのコードで使われているオプション名を見ると、どちらの系統が元なのか見当がつきます。

#### 1.3 中でどう動いているか

| 処理 | 中身 | 場所 |
|---|---|---|
| 表示の要素を足す | 入力欄の後ろ(`after()`)に `div.pstrength-bar`(`id="<id>_bar"`)と `div.pstrength-info`(`id="<id>_text"`)を足す。バーの見た目は `style` 属性に直書き。`v12/` は足す場所を親要素の末尾に変えている | `v12/:13-16` |
| 計算の契機 | `keyup` のたびに `runPassword` を呼ぶ。貼り付けや自動入力(`keyup` が起きない)では更新されない | `v12/:18-20` |
| 長さの点数 | `minchar` 未満なら −100。`minchar`〜+2 文字で +6、+3〜+4 で +12、+5 以上で +18 | `v12/:88-102` |
| 文字の種類の点数 | 小文字 +1、大文字 +5、数字 +5、数字 3 つ以上 +7、記号 +5、記号 2 つ以上 +7、大小の混在 +2、英字と数字の混在 +3、英数字と記号の混在 +3 | `v12/:103-129` |
| 禁止語 | 小文字にして `common` と完全一致なら −200 | `v12/:130-134` |
| 表示 | 点数を `scores` と比べて段階を決め、バーの `width`(10%〜)と `backgroundColor` を変え、言葉を `html()` で入れる | `v12/:23-83` |

1.4 では、長さの点数が `Math.pow(文字数, 1.4)` に変わっています(`v14/:135`)。

#### 1.4 弱いところ

- **点数が実際の強さと合わない**: `Password1!` は大文字・数字・記号があり 10 文字なので、点数が高くなる。実際にはよく使われる形で、すぐ破られる。禁止語は完全一致しか見ないので、`password1` は禁止語に引っかからない
- **記号の正規表現が雑**: `[!,@,#,$,%,^,&,*,?,_,~]` は区切りのつもりの `,` も文字の候補に入っている(`v12/:115`)。`.` で始まるので、先頭の 1 文字目の記号は数えない
- **読み上げに伝わらない**: バーは `style` の幅と色だけで、`role` も `aria-*` も無い。言葉も `aria-live` の無い `div` に入るので、スクリーンリーダーには変化が伝わらない
- **色だけで区別している部分がある**: バーは色と幅で段階を表す(言葉は別に出る)
- **グローバル変数を汚す**: `nPerc`、`strColor`、`strText` が `var` 無しで代入され、`window` に漏れる(`v12/:24`、`:28-29`)

---

### 2. Spartacus の標準にあるか

**結論: メーターは無い。規則を検査して、満たしていないものを言葉で示す仕組みがある。**

#### 2.1 パスワードの規則(バリデーター)

規則は `CustomFormValidators` にあります。正規表現は `core/util/regex-pattern.ts` です。

| バリデーター | 規則 | エラーのキー | 場所 |
|---|---|---|---|
| `minOneDigitValidator` | 数字を 1 つ以上 | `cxMinOneDigit` | `sf/shared/utils/validators/custom-form-validators.ts:87`、`core/util/regex-pattern.ts:15` |
| `minOneUpperCaseCharacterValidator` | 大文字を 1 つ以上 | `cxMinOneUpperCaseCharacter` | `custom-form-validators.ts:66-75`、`regex-pattern.ts:13` |
| `minOneSpecialCharacterValidator` | 記号 `!@#$%^*()_-+{};:.,` を 1 つ以上 | `cxMinOneSpecialCharacter` | `custom-form-validators.ts:108`、`regex-pattern.ts:17-18` |
| `minEightCharactersLengthValidator` | 8 文字以上 | `cxMinEightCharactersLength` | `custom-form-validators.ts:150`、`regex-pattern.ts:22` |
| `maxCharactersLengthValidator` | 128 文字以下 | `cxMaxCharactersLength` | `custom-form-validators.ts:160`、`regex-pattern.ts:24` |
| `noConsecutiveCharacters` | 同じ文字を続けない(`aa` など) | `cxNoConsecutiveCharacters` | `custom-form-validators.ts:181`、`regex-pattern.ts:26` |
| `mustEndWithLegalCharacter` | 最後の文字が英数字か上の記号 | `cxMustEndWithLegalCharacter` | `custom-form-validators.ts:336-345`、`regex-pattern.ts:35-36` |
| `passwordsMustMatch` | 確認用の入力と一致 | `cxPasswordsMustMatch` | `custom-form-validators.ts:245-254` |

これらをまとめた配列が `securePasswordValidators` です(`custom-form-validators.ts:209-216`)。6 文字以上の古い組み合わせ `passwordValidators` も残っています(`:201-206`)。

会員登録、パスワード変更、パスワード再設定は `securePasswordValidators` を使います。機能フラグ `useEnhancedSecurePasswordValidators`(既定で `true`。`core/features-config/feature-toggles/config/feature-toggles.ts:1082`)が有効なら、`mustEndWithLegalCharacter` も足します。

```ts
// fl/user/profile/components/register/register.component.ts:78-84、:103
protected passwordValidators = this.featureToggles.useEnhancedSecurePasswordValidators
  ? [...CustomFormValidators.securePasswordValidators, CustomFormValidators.mustEndWithLegalCharacter]
  : CustomFormValidators.securePasswordValidators;
…
password: ['', [Validators.required, ...this.passwordValidators]],
```

同じ書き方が `fl/user/profile/components/update-password/update-password-component.service.ts:34-40` と `fl/user/profile/components/reset-password/reset-password-component.service.ts:31-34` にあります。

#### 2.2 画面での見せ方

```html
<!-- fl/user/profile/components/register/register.component.html:134-158 -->
<input type="password" formControlName="password"
       aria-describedby="password-input-hint" cxPasswordVisibilitySwitch />
<p class="input-hint" id="password-input-hint">
  {{ 'register.passwordMinRequirements' | cxTranslate }}
</p>
<cx-form-errors [control]="registerForm.get('password')" … />
```

| 部品 | 役割 | 場所 |
|---|---|---|
| 入力の手引き | 「8 文字以上で、大文字・小文字・数字・記号を混ぜる」という文を、入力前から出す。`aria-describedby` で入力欄に結び付ける | `register.component.html:146-151`。英語の文言は `core-libs/assets/src/translations/en/myAccount.json:19` |
| `cx-form-errors` | コントロールの `errors` を、キーごとに翻訳して並べる。値が不正で、かつ入力したか触ったあと(`dirty` か `touched`)に出す。ホストに `aria-live="polite"` が付き、読み上げにも伝わる | `sf/shared/components/form/form-errors/form-errors.component.ts:34`、`:73-88`、`:135-142` |
| `cxPasswordVisibilitySwitch` | 入力欄の横に「表示 / 非表示」のボタンを付け、`type` を `password` と `text` で切り替える | `sf/shared/components/form/password-visibility-toggle/password-visibility-toggle.directive.ts:22`、`password-visibility-toggle.component.ts:20-42` |

#### 2.3 pstrength との差

| 項目 | pstrength | Spartacus |
|---|---|---|
| 表すもの | 点数(5 段階) | 規則を満たしているか(規則ごと) |
| いつ出るか | キーを押すたび | 入力を始めたら(`dirty`)、満たしていない規則を出す。送信時は `markAllAsTouched()` で全部出す |
| 送信を止めるか | 止めない(表示だけ) | 止める(`form.valid` が偽) |
| 長さ | `minchar: 6` | 8〜128 文字 |
| 同じ文字の連続 | 見ない | `noConsecutiveCharacters` で禁止 |
| よく使われるパスワード | `common` の完全一致だけ | 見ない |
| 読み上げ | 伝わらない | `cx-form-errors` の `aria-live="polite"` で伝わる |
| サーバー側 | — | 規則はフロントの検査。サーバー側の規則と合わせる必要がある |

#### 2.4 Spartacus の部品と組み合わせる例

Spartacus の会員登録の画面に、3.1 節のメーターを足すときの形です。規則の検査は 2.1 節の `securePasswordValidators` と `cx-form-errors` のまま残し、メーターは目安として並べます。

```html
<!-- 親のテンプレート(会員登録のフォームの中) -->
<input type="password" formControlName="password" cxPasswordVisibilitySwitch
       aria-describedby="password-input-hint pw-meter-text" />
<app-password-meter [password]="registerForm.controls.password.value ?? ''" />
<cx-form-errors [control]="registerForm.get('password')" />
```

---

### 3. Angular 標準で書くとどうなるか(Spartacus を使わない)

この節は `@angular/*` とブラウザ標準(と RxJS)だけで書きます。`CustomFormValidators`、`cx-form-errors`、`cxPasswordVisibilitySwitch` など、Spartacus の部品を使う書き方は 2 節(組み合わせ方は 2.4 節)です。

#### 3.1 強さのメーター

メーターは、パスワードの値から点数を `computed()` で出し、`<meter>` で描きます。`<meter>` は「範囲の中のどこにあるか」を表す標準の要素で、`low` / `high` / `optimum` を渡すと、ブラウザが良し悪しの色を付けます。

```ts
import { Component, computed, input } from '@angular/core';

@Component({
  selector: 'app-password-meter',
  template: `
    <meter id="pw-meter" min="0" max="4" low="2" high="3" optimum="4"
           [value]="score()" [attr.aria-describedby]="'pw-meter-text'"></meter>
    <!-- 言葉でも出す。aria-live で変化を伝える -->
    <p id="pw-meter-text" aria-live="polite">{{ labels[score()] }}</p>
  `,
})
export class PasswordMeterComponent {
  password = input('');                       // 親から渡す
  labels = ['とても弱い', '弱い', 'ふつう', '強い', 'とても強い'];

  score = computed(() => {
    const p = this.password();
    if (p.length < 8) return 0;
    let s = 1;
    if (p.length >= 12) s++;
    if (/[A-Z]/.test(p) && /[a-z]/.test(p)) s++;
    if (/\d/.test(p) && /[^A-Za-z0-9]/.test(p)) s++;
    return s;                                 // 0〜4
  });
}
```

#### 3.2 規則の検査: 自分のバリデーター

Spartacus の `securePasswordValidators` にあたるものは、`@angular/forms` の `ValidatorFn` で書きます。規則を 1 つの配列にまとめておくと、バリデーターと、画面のチェックリスト(3.3 節)の両方で同じ規則を使えます。

```ts
// password-rules.ts
import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

const COMMON = ['password', 'qwerty', 'letmein', '123456'];   // pstrength の common にあたる

export const PASSWORD_RULES = [
  { key: 'length', label: '8 文字以上 128 文字以下', test: (p: string) => p.length >= 8 && p.length <= 128 },
  { key: 'upper', label: '大文字を 1 つ以上', test: (p: string) => /[A-Z]/.test(p) },
  { key: 'digit', label: '数字を 1 つ以上', test: (p: string) => /\d/.test(p) },
  { key: 'symbol', label: '記号を 1 つ以上', test: (p: string) => /[^A-Za-z0-9]/.test(p) },
  { key: 'common', label: 'よく使われるパスワードではない', test: (p: string) => !COMMON.includes(p.toLowerCase()) },
];

export const passwordRules: ValidatorFn = (c: AbstractControl): ValidationErrors | null => {
  const p = String(c.value ?? '');
  const failed = PASSWORD_RULES.filter((r) => !r.test(p));
  return failed.length ? Object.fromEntries(failed.map((r) => [r.key, true])) : null;
};
```

- pstrength の `minchar` は `length` の規則に、`common` は `common` の規則になる。pstrength は点数を下げるだけだったが、ここでは送信を止める
- ここでは使っていないが、`Validators.minLength()` は空の値を通す(長さ 0 ならエラーにしない。`@angular/forms@21.2.26` の `fesm2022/forms.mjs:351-356`)。`passwordRules` は空の値も規則に照らすが、空の欄の文言を分けたいなら `Validators.required` を一緒に付ける(3.3 節)
- 禁止語は pstrength と同じく完全一致だけを見ている。漏えい済みのパスワードと照らすのは、サーバーの仕事にする(6 節)

#### 3.3 入力欄にまとめる: チェックリスト、表示の切り替え、メーター

```ts
import { Component, computed, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { PASSWORD_RULES, passwordRules } from './password-rules';
import { PasswordMeterComponent } from './password-meter.component';

@Component({
  selector: 'app-password-field',
  imports: [ReactiveFormsModule, PasswordMeterComponent],
  template: `
    <label for="pw">パスワード</label>
    <input id="pw" [type]="visible() ? 'text' : 'password'" [formControl]="pw"
           autocomplete="new-password" aria-describedby="pw-rules pw-meter-text"
           [attr.aria-invalid]="pw.invalid && (pw.dirty || pw.touched)" />
    <!-- cxPasswordVisibilitySwitch にあたる。ラベルは変えず、aria-pressed で状態を伝える -->
    <button type="button" aria-controls="pw" [attr.aria-pressed]="visible()"
            (click)="visible.set(!visible())">パスワードを表示</button>

    <ul id="pw-rules">
      @for (r of checks(); track r.key) {
        <!-- 色だけに頼らず、言葉でも「済」「未」を出す -->
        <li [class.ok]="r.ok">{{ r.ok ? '済' : '未' }}: {{ r.label }}</li>
      }
    </ul>

    <app-password-meter [password]="value()" />
  `,
})
export class PasswordFieldComponent {
  pw = new FormControl('', { nonNullable: true, validators: [Validators.required, passwordRules] });
  visible = signal(false);
  value = toSignal(this.pw.valueChanges, { initialValue: '' });
  checks = computed(() => PASSWORD_RULES.map((r) => ({ ...r, ok: r.test(this.value()) })));
}
```

| pstrength | このコンポーネント |
|---|---|
| `keyup` のたびに `runPassword` | `valueChanges` → `toSignal` → `computed`。値が変われば必ず計算し直す |
| バーの幅と色 | `<meter>`(3.1 節) |
| 段階の言葉(`verdects`) | `labels` と `aria-live="polite"` |
| `minchar`、`common` | `PASSWORD_RULES`(3.2 節)。送信も止める |
| 無い | 規則ごとのチェックリスト、表示の切り替え |

ポイント:

- **`keyup` ではなく値から計算する**: Reactive Forms の値は、貼り付けやパスワードマネージャーの自動入力でも変わる。pstrength のように `keyup` を見る必要はない
- **メーターは送信を止めない**: 送信の可否は、3.2 節のバリデーター(Spartacus なら 2.1 節)で決める。メーターは目安として並べる
- **読み上げ**: 段階の言葉を `aria-live="polite"` の要素に入れる。1 文字ごとに読まれてうるさい場合は、段階が変わったときだけ文を変える(`computed` の値が同じなら、テンプレートの文も変わらない)。チェックリストは `aria-live` にせず、`aria-describedby` で入力欄に結び付けるだけにする。打つたびに全部が読まれるのを避けるためである
- **表示の切り替え**: `type` を `password` と `text` で替える。ボタンのラベルを「表示」「隠す」と替える書き方もあるが、ここでは `aria-pressed` で押されているかを伝える

**SSR での注意**:

- 点数の計算と規則の検査は文字列の処理だけなので、サーバーで動いても問題ない。サーバーでは空のパスワードとして描かれ、チェックリストはすべて「未」になる
- 辞書を使うライブラリ(4 節)は、辞書が数 MB ある。サーバーでもブラウザでも、パスワード欄のある画面でだけ読み込むよう、動的 `import()` にする。読み込みをブラウザだけに限るなら、`afterNextRender()`(`@angular/core@21.2.26` の `types/core.d.ts:2576`)の中か、`isPlatformBrowser(inject(PLATFORM_ID))` で分けた中で読み込む

---

### 4. ほかの選択肢

| ライブラリ | 版 | peerDependencies | メモ |
|---|---|---|---|
| `@zxcvbn-ts/core` | 4.3.0 | 無い(依存は `fastest-levenshtein`) | Dropbox の zxcvbn を TypeScript で書き直したもの。よく使われるパスワード、辞書の単語、日付、キーボードの並び(`qwerty`)、繰り返しなどを見つけ、破るのに要る推測の回数から `score`(0〜4)を出す。`feedback.suggestions` で改善の手がかりも返す。v4 の使い方は `new ZxcvbnFactory(options).check(pw)`(`package/README.md` の Usage) |
| `@zxcvbn-ts/language-common` | 4.2.0 | 無い | 共通の辞書とキーボードの配列。展開後 約 1.9MB |
| `@zxcvbn-ts/language-ja` | 4.1.2 | 無い | 日本語の文言と辞書 |
| `check-password-strength` | 3.0.0 | 無い | 文字の種類と長さで 4 段階に分ける。pstrength と同じ考え方で、軽い |
| `zxcvbn` | 4.4.2(2017 年以降更新が無い) | 無い | 元の Dropbox 版。新しく使うなら `@zxcvbn-ts/core` |

どれもフレームワークに依存しないので、Angular 21 でそのまま使えます。

`@zxcvbn-ts/core` を使う場合の形:

```ts
score = signal(0);
private zxcvbn?: { check(p: string): { score: number } };

async ensureLoaded() {          // パスワード欄にフォーカスが来たときに呼ぶ
  if (this.zxcvbn) return;
  const [{ ZxcvbnFactory }, common, ja] = await Promise.all([
    import('@zxcvbn-ts/core'),
    import('@zxcvbn-ts/language-common'),
    import('@zxcvbn-ts/language-ja'),
  ]);
  this.zxcvbn = new ZxcvbnFactory({
    translations: ja.translations,
    graphs: common.adjacencyGraphs,
    dictionary: { ...common.dictionary, ...ja.dictionary },
  });
}
```

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| 規則を満たしているかを示せばよい | Spartacus 標準(`securePasswordValidators` + `cx-form-errors` + 入力の手引き) |
| 規則を変えたい(長さ、記号の種類) | 自分のバリデーターを書き、`FormGroup` の作成を差し替える。サーバー側の規則も同じにする |
| 規則ごとに「満たした / まだ」を一覧で見せたい | 規則を 1 つの配列にまとめ、値からチェックリストを描く(3.3 節。`cx-form-errors` は満たしていないものだけを出す) |
| Spartacus を使わない Angular のプロジェクト | 3.2 節の `ValidatorFn` + 3.3 節の入力欄(チェックリスト、表示の切り替え)。メーターは 3.1 節 |
| 強さのメーターが要る(見た目の目安) | 3.1 節の `computed()` + `<meter>` |
| 実際の強さに近い評価が要る | `@zxcvbn-ts/core` + `language-common` + `language-ja` を動的 `import()` で |
| pstrength の見た目をそのまま再現したい | 3.1 節のコンポーネントで、`scores` と `colors` を同じ値にする |

---

### 6. コンピュータサイエンスの観点から

- **構成規則とエントロピーは別物**: 「大文字・数字・記号を含む」という規則は、文字の種類を増やせば推測の空間が広がる、という考えに基づく。しかし人は規則を満たす形を予測しやすい方法で作る(先頭を大文字、末尾に `1!`)。そのため、規則を満たしていても推測の回数は少ない。NIST SP 800-63B は、構成規則を課すより、漏えい済みのパスワードや辞書の単語を拒むことを勧めている
- **推測の回数で測る**: zxcvbn は、パスワードを「辞書の単語」「日付」「キーボードの並び」「繰り返し」などの部品に分け、最も少ない推測で当てられる分け方を動的計画法で探す。その推測の回数の対数が強さになる。pstrength の足し算の点数より、攻撃する側のやり方に近い
- **クライアントの検査はサーバーの代わりにならない**: メーターもバリデーターも、ブラウザの中の表示にすぎない。OCC を直接呼べば素通りできる。規則の最終判断はサーバーが持ち、フロントは「送る前に気づかせる」役に徹する
