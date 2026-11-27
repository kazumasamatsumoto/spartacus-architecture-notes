# jQuery Form Plugin: 普通の HTML フォームを Ajax で送信する

> **この章が答える問い**: アクセラレータの `jquery.form.min.js` は何をしていたのか。Spartacus ではフォームの送信をどう書いているのか。ファイルの添付や、送信の前後の処理はどこに移るのか

> **根拠の取り方**:
> - **プラグイン**: アクセラレータが読むファイル名にバージョンが無いので、npm の最新版 `jquery-form@4.6.0`(2026-11-26 公開)の tarball を展開し、`src/` を読んだ。以下 `pkg/` はパッケージのルート。4.6.0 は `src/` が 14 本のモジュールに分かれた新しい作りで、アクセラレータが同梱した当時の版(3.x か 4.2.x と思われるが確認できない)とは中身の書き方が違う。公開 API(`ajaxForm`、`ajaxSubmit` とそのオプション)は同じ名前で残っている
> - **Spartacus**: SAP/spartacus `develop` のコミット `2db8cb96f5361cb59c2d95ef80438df4630344f9`(2026-11-19)。以下 `sf/` は `core-libs/storefront/`、`core/` は `core-libs/core/src/`、`fl/` は `feature-libs/` を指す
> - 代替の方法はライブラリを使わないので、バージョンの確認は無い

---

### 先に話し言葉で: フォームの送信は Facade に頼む

jQuery Form Plugin は、普通の `<form>` の送信を横取りし、同じ中身を Ajax で送るプラグインです。入力値を集めて送り、返ってきた HTML を画面のどこかに差し込みます。ファイルの添付も扱えます。

Spartacus に同じプラグインはありませんし、要りません。フォームの値は Angular の Reactive Forms が持っています。送信は、コンポーネントが **Facade のメソッドを呼ぶ** だけです。会員登録なら `UserRegisterFacade.register()` です。その先で Connector と Adapter が `HttpClient` を使って OCC に送ります([15 章](../../15-facade-connector-adapter.md))。

置き換えで大きいのは、書き方より **送り先と返ってくるもの** です。アクセラレータの送り先は JSP のコントローラで、返ってくるのは HTML の断片でした。Spartacus では OCC の API に JSON を送り、JSON を受け取ります。ファイルの添付は `FormData` を `HttpClient` で送れば済みます。

---

### 1. jQuery Form Plugin は何をするか

#### 1.1 使い方

```js
// フォームの submit を横取りして、Ajax で送る
$('#addressForm').ajaxForm({
  target: '#addressBook',          // 返ってきた HTML をここに入れる
  beforeSubmit: validate,          // false を返すと送らない
  success: function () { ACC.address.refresh(); },
  resetForm: true,
});

// 自分の submit ハンドラから、今すぐ送る
$('#uploadForm').on('submit', function (e) {
  e.preventDefault();
  $(this).ajaxSubmit({ uploadProgress: showPercent });
});
```

#### 1.2 主な API とオプション

| API / オプション | 内容 | 場所 |
|---|---|---|
| `ajaxForm(options)` | フォームの `submit` に処理を付ける。押されたボタンの `name` / `value` も覚えておき、一緒に送る | `pkg/src/ajax-form.js:154`、`:11-31` |
| `ajaxSubmit(options)` | 今すぐ送る。中では「準備」「送信方法の選択」「送信」の順に進む | `pkg/src/jquery.form.js:134-171` |
| `formSerialize()` / `fieldSerialize()` / `formToArray()` | 送る値を集める(押されたボタン、`disabled` の除外など、ブラウザの送信と同じ規則) | `pkg/src/jquery.form.js:188-211`、`pkg/src/successful-controls.js` |
| `resetForm()` / `clearForm()` | 送信後にフォームを戻す、空にする | `pkg/src/jquery.form.js:309-369` |
| `url` / `type` | 既定はフォームの `action` / `method` | `pkg/src/options.js:41-53` |
| `beforeSerialize` / `beforeSubmit` | 値を集める前 / 送る前に呼ぶ。`false` で中止 | `pkg/src/submission.js:220-237` |
| `target` / `replaceTarget` | 応答の HTML を `html()` か `replaceWith()` で差し込む。`dataType` を指定しないときだけ | `pkg/src/submission.js:287-309` |
| `resetForm` / `clearForm` | 成功したらフォームを戻す、空にする | `pkg/src/submission.js:275-283` |
| `uploadProgress` | ファイル送信の進み具合(`xhr.upload` の `progress`) | `pkg/src/xhr-transport.js:60-87` |
| `iframe` | 隠した `<iframe>` に送る古い方法を強制する | `pkg/src/submission.js:372-381` |
| `requestFormat: "json"` | 4.x で加わった。値を JSON にして送る(ファイルは不可) | `pkg/src/submission.js:101-106`、`:385-387` |
| `delegation` | まだ無いフォームにも効くよう、`document` で受ける | `pkg/src/ajax-form.js:119-141` |

#### 1.3 中でどう動いているか

| 処理 | 中身 | 場所 |
|---|---|---|
| 送信方法を選ぶ | 値の入ったファイル入力があるか、`enctype` が `multipart/form-data` なら、`FormData` で送る。無ければ `$.ajax` で URL エンコードして送る。`FormData` が無い古いブラウザでは `<iframe>` に送る | `pkg/src/submission.js:347-381` |
| FormData で送る | フォームの値と `extraData` を `FormData` に積み、`$.ajax` に `processData: false` で渡す | `pkg/src/xhr-transport.js:31-104` |
| iframe で送る | 隠した `<iframe>` を作り、フォームの `target` をそこに向けて普通に送信し、iframe の中身を応答として読む。XHR でファイルを送れなかった時代の回避策 | `pkg/src/iframe-transport.js`、`pkg/src/iframe-post.js` |
| 機能の判定 | `<input type="file">` に `files` があるか、`window.FormData` があるか | `pkg/src/jquery.form.js:83-84` |
| 前提 | jQuery 1.7.2 以上。slim 版(`$.ajax` が無い)では動かない。jQuery 4 と組み合わせるなら 4.4.0 以上が要る(4.3.0 は jQuery 4 で消えた API を使う) | `pkg/src/jquery.form.js:143-148`、`pkg/README.md:76-80` |

README は、`target` で差し込む応答は HTML として入るので、信頼できる応答だけにするよう注意しています(`pkg/README.md:86`)。

---

### 2. Spartacus の標準にあるか

**結論: 同じ形の部品は無い。代わりに「Reactive Forms + Facade」という決まった形がある。**

#### 2.1 会員登録の例

```html
<!-- fl/user/profile/components/register/register.component.html:9 -->
<form (ngSubmit)="submitForm()" [formGroup]="registerForm">
  …
  <input type="password" formControlName="password" cxPasswordVisibilitySwitch />
  <cx-form-errors [control]="registerForm.get('password')" />
</form>
```

```ts
// fl/user/profile/components/register/register.component.ts:212-232
submitForm(): void {
  if (this.registerForm.valid) {
    this.registerUser();
  } else {
    this.registerForm.markAllAsTouched();   // エラーを表示させる
  }
}

registerUser(): void {
  this.isLoading$.next(true);
  this.registerComponentService
    .register(this.collectDataFromRegisterForm(this.registerForm.value))
    .subscribe({
      next: () => this.onRegisterUserSuccess(),
      error: () => this.isLoading$.next(false),
      …
    });
}
```

`RegisterComponentService.register()` は `UserRegisterFacade.register()` を呼ぶだけです(`fl/user/profile/components/register/register-component.service.ts:32-33`)。Facade の定義は `fl/user/profile/root/facade/user-register.facade.ts:29`、OCC への送信は `fl/user/profile/occ/adapters/occ-user-profile.adapter.ts:62` です。

#### 2.2 jQuery Form Plugin の役割はどこに移るか

| jQuery Form Plugin | Spartacus / Angular | 場所 |
|---|---|---|
| フォームの値を集める(`formSerialize`) | `FormGroup.value`。集める必要が無い | — |
| `beforeSubmit` で検証 | `Validators` と `form.valid`。エラーの表示は `cx-form-errors` | `sf/shared/components/form/form-errors/form-errors.component.ts:34`、`:73-88` |
| `$.ajax` で `action` に送る | Facade → Connector → Adapter → `HttpClient` | [15 章](../../15-facade-connector-adapter.md) |
| `target` に HTML を差し込む | 差し込まない。Facade の状態が変わり、それを見ている部品が描き直される | [番外 4](../replacing-jquery.md) 2.2 節 |
| `success` で別の部品を更新 | 要らない。または `EventService` のイベントを受ける | `core/event/event.service.ts:47` |
| エラー応答の表示 | 400 番台は `BadRequestHandler` などが `GlobalMessageService` に流す | `core/global-message/http-interceptors/handlers/bad-request/bad-request.handler.ts:21` |
| 送信中の表示 | `isLoading$` と `cx-spinner` / `cx-progress-button` | `sf/shared/components/progress-button/progress-button.component.ts:11` |
| `resetForm` / `clearForm` | `form.reset()` | — |
| ファイルを送る(`FormData`) | `cx-file-upload` で選び、Adapter で `FormData` を作って `HttpClient.post` | 2.3 節 |

#### 2.3 ファイルの添付

Spartacus にも、ファイルを送る処理があります。問い合わせ(カスタマーチケット)の添付です。

```ts
// fl/customer-ticketing/occ/adapters/occ-customer-ticketing.adapter.ts:206-226
uploadAttachment(customerId: string, ticketId: string, eventCode: string, file: File) {
  const formData: FormData = new FormData();
  formData.append('ticketEventAttachment', file);
  return this.http
    .post(this.getUploadAttachmentEndpoint(customerId, ticketId, eventCode), formData)
    .pipe(…);
}
```

ファイルを選ぶ部品は `cx-file-upload`(`sf/shared/components/form/file-upload/file-upload.component.ts:26`。`accept`、`multiple` は `:41`、`:45`)、サイズの検証は `FilesFormValidators.maxSize()`(`sf/shared/services/file/files-form-validators.ts:24`)です。

アップロードの進み具合(jQuery Form Plugin の `uploadProgress`)を出している箇所は、`sf/`、`fl/`、`integration-libs/` の `.ts` にありません(`reportProgress` と `HttpEventType.UploadProgress` で探した)。

---

### 3. Angular で書くとどうなるか

#### 3.1 普通のフォーム

```ts
@Component({
  selector: 'app-inquiry-form',
  imports: [ReactiveFormsModule, FormErrorsComponent],   // cx-form-errors は standalone
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()">
      <label>件名 <input formControlName="subject" /></label>
      <cx-form-errors [control]="form.controls.subject" />
      <button type="submit" [disabled]="busy()">送信</button>
    </form>
  `,
})
export class InquiryFormComponent {
  private facade = inject(InquiryFacade);   // 自作の Facade(15 章)
  busy = signal(false);
  form = inject(FormBuilder).nonNullable.group({
    subject: ['', [Validators.required, Validators.maxLength(100)]],
  });

  submit() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.busy.set(true);
    this.facade.send(this.form.getRawValue()).subscribe({
      next: () => this.form.reset(),          // jQuery Form Plugin の resetForm
      error: () => this.busy.set(false),
      complete: () => this.busy.set(false),
    });
  }
}
```

#### 3.2 ファイルと進み具合

```ts
// Adapter の中
upload(file: File): Observable<number> {
  const body = new FormData();
  body.append('file', file);
  return this.http
    .post(url, body, { reportProgress: true, observe: 'events' })
    .pipe(
      filter((e) => e.type === HttpEventType.UploadProgress),
      map((e) => Math.round((100 * e.loaded) / (e.total ?? e.loaded)))
    );
}
```

`FormData` を渡すと、`Content-Type: multipart/form-data` と境界文字列はブラウザが付けます。自分で `Content-Type` を指定しないようにします。

**SSR での注意**:

- フォームの送信はユーザーの操作で起きるので、サーバーでは走らない。送信の処理に `window` を使っていても、多くの場合は問題にならない
- ただし、ページを開いたときに Facade で何かを送る処理(初期値の保存など)は、サーバーでも動く。`File` や `FormData` はサーバーの Node.js にもあるが、ユーザーのファイルは無い。ファイルを扱う処理はイベントの中に閉じ込める
- サーバーで描いたフォームは、JS が動く前に送信されることがある。`action` の無い `<form>` は自分の URL に GET で送ってしまう。Spartacus のフォームも同じで、Angular の `ngSubmit` が動くまでは素の HTML のフォームとして振る舞う

---

### 4. ほかの選択肢

ライブラリは要りません。Angular の `HttpClient` と Reactive Forms で足ります。

フレームワークに依存しない方法としては、ブラウザ標準の `fetch(url, { method: 'POST', body: new FormData(form) })` があります。`new FormData(form)` は、jQuery Form Plugin の `formToArray()` と同じく、ブラウザの送信規則で値を集めます。ただし `fetch` はアップロードの進み具合を取れません(取るなら `XMLHttpRequest` か `HttpClient`)。Spartacus の中では、認証のヘッダーや言語・通貨のパラメータを付ける `HttpInterceptor` を通すため、`fetch` ではなく `HttpClient` を使います。

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| Spartacus にある機能(会員登録、住所、パスワード変更など)のフォーム | 標準のコンポーネント。見た目だけ変えるならテンプレートと SCSS |
| 標準に無いフォーム | Reactive Forms + 自作の Facade / Connector / Adapter([15 章](../../15-facade-connector-adapter.md)) |
| ファイルを送る | `cx-file-upload` + Adapter で `FormData` |
| 進み具合を出したい | `HttpClient` の `reportProgress: true, observe: 'events'` |
| 送り先が JSP のコントローラしか無い | フロントだけでは移せない。OCC に API を作る([12 章](../../12-backend-api-granularity.md)、[13 章](../../13-jsp-to-headless.md)) |
| サーバーが HTML の断片を返している | JSON を返す API に変え、HTML はコンポーネントで描く |

---

### 6. コンピュータサイエンスの観点から

- **プログレッシブエンハンスメント**: jQuery Form Plugin は「JS が無くても動くフォーム」に後から Ajax を足す作りだった。フォームの `action` と `method` がそのまま使われる。Spartacus は SPA なので、フォームは JS が動いて初めて意味を持つ。SSR はこの差を部分的に埋めるが、送信までは引き受けない
- **iframe トランスポートは、XHR が足りなかった時代の名残**: XHR でファイルを送れなかった頃、ページを移動させずにファイルを送る唯一の方法が、隠した `<iframe>` に普通の送信をさせることだった(`pkg/src/iframe-transport.js`)。XHR2 の `FormData` と `xhr.upload` が標準になり、4.6.0 では「`FormData` が無いときに自動で iframe を選ぶ」ことに非推奨の警告が出る(`pkg/src/submission.js:378-381`)
- **送る形式の違い**: HTML のフォームは `application/x-www-form-urlencoded` か `multipart/form-data` で送る。OCC の多くの API は JSON の本文を受け取る。jQuery Form Plugin も 4.x で `requestFormat: "json"` を足した(`pkg/src/submission.js:101-106`)。置き換えでは、送る形式が変わることを API の側でも確かめる
