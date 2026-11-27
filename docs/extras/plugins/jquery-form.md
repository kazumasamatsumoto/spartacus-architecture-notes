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

Spartacus を使わない Angular のプロジェクトなら、Facade を挟まず、コンポーネントから `HttpClient` を直接呼ぶ形で足ります(3 節)。進み具合の表示、送信の中止、共通のヘッダーも Angular の標準の機能で書けます。

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

#### 2.4 Spartacus の部品と組み合わせる例

Spartacus の中で、標準に無いフォームを足すときの形です。値は Reactive Forms で持ち、エラーの表示は `cx-form-errors` に任せ、送信は自作の Facade に頼みます([15 章](../../15-facade-connector-adapter.md))。Spartacus を使わない書き方は 3 節です。

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

ファイルの送信と進み具合は、Adapter の中で `HttpClient` を使って書きます。2.3 節の `uploadAttachment` に `reportProgress` を足した形です。

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

Spartacus の中では、ページを開いたときに Facade が何かを送る処理(初期値の保存など)は、SSR のサーバーでも動きます。ファイルを扱う処理は、ユーザーのイベントの中に閉じ込めます。

---

### 3. Angular 標準で書くとどうなるか(Spartacus を使わない)

この節は `@angular/*` とブラウザ標準(と RxJS)だけで書きます。Facade / Connector / Adapter の形や `cx-form-errors` など、Spartacus の部品を使う書き方は 2.4 節です。ここでは、コンポーネントが `HttpClient` を直接使います。

#### 3.1 準備: `HttpClient` を使えるようにする

```ts
// app.config.ts
import { ApplicationConfig } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { requestedWith } from './requested-with.interceptor';   // 3.5 節

export const appConfig: ApplicationConfig = {
  providers: [provideHttpClient(withInterceptors([requestedWith]))],
};
```

- `@angular/common@21.2.26` の `HttpClient` は `providedIn: 'root'` なので、`provideHttpClient()` を書かなくても `inject(HttpClient)` できる(`fesm2022/_module-chunk.mjs:1748-1756`)。そのときの送信は `XMLHttpRequest` で行う(`HttpBackend` の既定が `HttpXhrBackend`。`:1476-1483`)。インターセプターを足すなら `provideHttpClient()` を書く
- `withFetch()` を足すと、送信に `fetch` を使う。ただし **`fetch` ではアップロードの進み具合が取れない**(`types/http.d.ts:4209-4218` の注記)。3.4 節の進み具合が要るなら付けない。SSR との関係は、この節の最後に書いた

#### 3.2 普通のフォームを JSON で送る

jQuery Form Plugin の `ajaxForm` + `beforeSubmit` + `success` + `resetForm` を、1 つのコンポーネントで書くと次の形です。エラーの文言と、送信の結果の読み上げも自分で書きます。

```ts
import { Component, ElementRef, inject, signal } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';

@Component({
  selector: 'app-inquiry-form',
  imports: [ReactiveFormsModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()">
      <label for="subject">件名</label>
      <input id="subject" formControlName="subject"
             [attr.aria-invalid]="shows('subject')"
             [attr.aria-describedby]="shows('subject') ? 'subject-error' : null" />
      @if (shows('subject')) {
        <p id="subject-error">
          @if (form.controls.subject.hasError('required')) { 件名を入れてください }
          @else { 100 文字以内にしてください }
        </p>
      }

      <label for="email">メールアドレス</label>
      <input id="email" type="email" formControlName="email" autocomplete="email"
             [attr.aria-invalid]="shows('email')"
             [attr.aria-describedby]="shows('email') ? 'email-error' : null" />
      @if (shows('email')) {
        <p id="email-error">メールアドレスの形で入れてください</p>
      }

      <button type="submit" [disabled]="busy()">送信</button>
      <!-- role="status" は aria-live="polite" と同じ働き。最初から DOM に置いておく -->
      <p role="status">{{ message() }}</p>
    </form>
  `,
})
export class InquiryFormComponent {
  private http = inject(HttpClient);
  private host = inject<ElementRef<HTMLElement>>(ElementRef);
  busy = signal(false);
  message = signal('');
  form = inject(FormBuilder).nonNullable.group({
    subject: ['', [Validators.required, Validators.maxLength(100)]],
    email: ['', [Validators.required, Validators.email]],
  });

  shows(name: 'subject' | 'email') {
    const c = this.form.controls[name];
    return c.invalid && (c.dirty || c.touched);
  }

  submit() {
    if (this.form.invalid) {                  // beforeSubmit で false を返すのと同じ
      this.form.markAllAsTouched();           // エラーを全部出す
      this.host.nativeElement
        .querySelector<HTMLElement>('input.ng-invalid, select.ng-invalid, textarea.ng-invalid')
        ?.focus();                            // 最初の誤りへフォーカスを移す
      return;
    }
    this.busy.set(true);
    this.message.set('');
    this.http
      .post<{ id: string }>('/api/inquiries', this.form.getRawValue())   // JSON で送る
      .pipe(finalize(() => this.busy.set(false)))
      .subscribe({
        next: (r) => {
          this.form.reset();                  // resetForm。nonNullable なので初期値の '' に戻る
          this.message.set(`受け付けました(番号 ${r.id})`);
        },
        error: (e: HttpErrorResponse) =>
          this.message.set(e.status === 400 ? '入力を確かめてください' : '送信できませんでした'),
      });
  }
}
```

| jQuery Form Plugin | このコンポーネント |
|---|---|
| `url` / `type`(既定はフォームの `action` / `method`) | `http.post(url, body)` に書く |
| `beforeSubmit` で検証し、`false` で中止 | `Validators` と `form.invalid` |
| 値を集める(`formSerialize`) | `form.getRawValue()`。集める処理は要らない |
| `success` / `error` | `subscribe` の `next` / `error` |
| `resetForm` | `form.reset()` |
| `target` に HTML を差し込む | 差し込まない。結果は signal に入れ、テンプレートで描く(3.6 節) |
| 二重送信の防止(プラグインには無い) | 送信中はボタンを `disabled` にする |

`ng-invalid` のクラスは、Reactive Forms がコントロールの状態に合わせて付けます。最初の描画の時点で付いているので、`markAllAsTouched()` の直後でも探せます。

#### 3.3 フォームの形式のまま送る

送り先が JSON ではなく、HTML のフォームと同じ形式(`application/x-www-form-urlencoded`)を待っている場合は、本文を `HttpParams` にします。`HttpClient` が `Content-Type: application/x-www-form-urlencoded;charset=UTF-8` を付けます(`@angular/common@21.2.26` の `fesm2022/_module-chunk.mjs:557-558`)。jQuery Form Plugin が `$.ajax` で送っていたときと同じ形式です。

```ts
import { HttpParams } from '@angular/common/http';

const body = new HttpParams({ fromObject: this.form.getRawValue() });
this.http.post('/contact', body).subscribe(…);
```

フォームの要素から、ブラウザの規則のまま値を集めることもできます。`new FormData(form)` は、jQuery Form Plugin の `formToArray()` と同じく、`name` のある欄だけを集め、`disabled` の欄を除きます。第 2 引数に `submitter` を渡すと、押されたボタンの `name` / `value` も入ります(`ajaxForm` が押されたボタンを覚えていたのと同じ)。

```ts
@Component({
  selector: 'app-legacy-form',
  template: `
    <form #f action="/my-account/address" method="post" (submit)="send($event, f)">
      <input name="town" required />
      <button name="action" value="save">保存</button>
      <button name="action" value="saveAndNext">保存して次へ</button>
    </form>
  `,
})
export class LegacyFormComponent {
  private http = inject(HttpClient);

  send(e: SubmitEvent, f: HTMLFormElement) {
    e.preventDefault();                                     // ページの移動を止める
    const body = new FormData(f, e.submitter);              // multipart/form-data で送る
    this.http.post(f.action, body).subscribe(…);            // url の既定は action(jQuery Form Plugin と同じ)
  }
}
```

この例は `FormsModule` / `ReactiveFormsModule` を読み込みません。どちらかを読み込むと、`<form>` に Angular のフォームのディレクティブが付きます。`FormData` で送るのは `multipart/form-data` なので、送り先がそれを受け取れるかを確かめます。

#### 3.4 ファイルを送り、進み具合を出す

```ts
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { HttpClient, HttpEventType } from '@angular/common/http';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-upload',
  template: `
    <label for="file">添付ファイル(5MB まで)</label>
    <input id="file" type="file" accept=".pdf,image/*" (change)="pick($event)" />
    @if (percent() !== null) {
      <progress max="100" [value]="percent() ?? 0" aria-label="送信の進み具合">{{ percent() }}%</progress>
    }
    <button type="button" (click)="upload()" [disabled]="!file() || percent() !== null">送る</button>
    <button type="button" (click)="cancel()" [disabled]="percent() === null">やめる</button>
    <p role="status">{{ message() }}</p>
  `,
})
export class UploadComponent {
  private http = inject(HttpClient);
  file = signal<File | null>(null);
  percent = signal<number | null>(null);
  message = signal('');
  private sub?: Subscription;

  constructor() {
    inject(DestroyRef).onDestroy(() => this.sub?.unsubscribe());   // 画面を離れたら送信もやめる
  }

  pick(e: Event) {
    const f = (e.target as HTMLInputElement).files?.[0] ?? null;
    const tooBig = !!f && f.size > 5 * 1024 * 1024;
    this.file.set(tooBig ? null : f);
    this.message.set(tooBig ? '5MB 以下のファイルにしてください' : '');
  }

  upload() {
    const f = this.file();
    if (!f) return;
    const body = new FormData();
    body.append('file', f);
    this.percent.set(0);
    this.sub = this.http
      .post('/api/attachments', body, { reportProgress: true, observe: 'events' })
      .subscribe({
        next: (e) => {
          if (e.type === HttpEventType.UploadProgress && e.total) {
            this.percent.set(Math.round((100 * e.loaded) / e.total));   // uploadProgress
          } else if (e.type === HttpEventType.Response) {
            this.percent.set(null);
            this.message.set('送りました');
          }
        },
        error: () => {
          this.percent.set(null);
          this.message.set('送れませんでした');
        },
      });
  }

  cancel() {
    this.sub?.unsubscribe();     // 購読をやめると、送信中の XHR も abort() される
    this.percent.set(null);
    this.message.set('送信をやめました');
  }
}
```

- `FormData` を渡すと、`Content-Type: multipart/form-data` と境界文字列はブラウザが付ける(`HttpClient` は `FormData` のときに `Content-Type` を決めない。`fesm2022/_module-chunk.mjs:545-546`)。自分で `Content-Type` を指定しない
- 購読をやめたとき、`HttpXhrBackend` は終わっていない XHR を `abort()` する(`fesm2022/_module-chunk.mjs:1242-1244`)。jQuery Form Plugin には「送信をやめる」API が無かった
- `e.total` は、ブラウザが全体の大きさを知らないときに `undefined` になる。そのときは割合を出さない

#### 3.5 送信の前後に共通の処理を挟む: インターセプター

jQuery Form Plugin では、共通の処理を各フォームの `beforeSubmit` や `error` に書いていました。Angular では `HttpInterceptorFn` に 1 回書けば、`HttpClient` のすべての送信に効きます。

```ts
// requested-with.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';

// jQuery の $.ajax は、同じオリジンへの送信に X-Requested-With: XMLHttpRequest を自動で付けていた。
// サーバーがこのヘッダーで Ajax かどうかを見分けているなら、HttpClient でも付ける
export const requestedWith: HttpInterceptorFn = (req, next) =>
  req.url.startsWith('/')
    ? next(req.clone({ setHeaders: { 'X-Requested-With': 'XMLHttpRequest' } }))
    : next(req);
```

- jQuery が付けていたことは、npm の `jquery@3.5.1` の `src/ajax/xhr.js:59-66` で確かめた。`HttpClient` は付けない
- CSRF の対策: `HttpClient` には、クッキー `XSRF-TOKEN` の値をヘッダー `X-XSRF-TOKEN` に写す仕組みが最初から入っている。`GET` / `HEAD` と、別のオリジンへの送信には付けない(`fesm2022/_module-chunk.mjs:1283-1292`、`:1371-1400`)。名前が違うなら `withXsrfConfiguration({ cookieName, headerName })` で変える。サーバー側がこの名前で受け取れるかは、別に確かめる

#### 3.6 応答の HTML を差し込む(`target`)は避ける

応答の HTML をそのまま画面に入れる形は、Angular では勧めません。JSON を受け取り、テンプレートで描きます。

どうしても HTML の断片を受け取るなら、`responseType: 'text'` で受け、`[innerHTML]` に渡します。Angular は、入れる前に `<script>` や `on*` 属性などを取り除きます(取り除くと、開発時に `WARNING: sanitizing HTML stripped some content` と出る。`@angular/core@21.2.26` の `fesm2022/_debug_node-chunk.mjs:3210`)。ただし、差し込んだ HTML の中のボタンには、Angular のイベントは付きません。

```ts
fragment = signal('');
load() {
  this.http.get('/cart/rollover', { responseType: 'text' }).subscribe((h) => this.fragment.set(h));
}
// <div [innerHTML]="fragment()"></div>
```

**SSR での注意**:

- フォームの送信はユーザーの操作で起きるので、サーバーでは走らない。ただし `HttpClient` そのものはサーバーでも動く。ページを開いたときに送る処理(初期値の読み込みなど)はサーバーでも実行される
- `File`、`FileReader`、`focus()` など、ブラウザでしか意味が無い処理は、イベントの中に閉じ込める。ページを開いた直後に使うなら `afterNextRender()`(`@angular/core@21.2.26` の `types/core.d.ts:2576`)の中に置くか、`isPlatformBrowser(inject(PLATFORM_ID))`(`@angular/common@21.2.26` の `types/common.d.ts:823`)で分ける
- `withFetch()` を付けずに SSR を動かすと、開発時に「SSR では `fetch` を使うよう強く勧める」という警告が出る(`fesm2022/_module-chunk.mjs:1508-1512`)。一方で、`fetch` ではアップロードの進み具合が取れない(3.1 節)。進み具合の表示と、この警告への対応は両立しないので、どちらを取るかを決める
- **ハイドレーションの前に押された送信**: サーバーで描いたフォームは、JS が動く前にも押せる。押されると、ブラウザは素の HTML のフォームとして送る(`action` の無い `<form>` は自分の URL に GET で送る)。`provideClientHydration(withEventReplay())`(`@angular/platform-browser@21.2.26` の `types/platform-browser.d.ts:694`、`:760`)はハイドレーション前のイベントを記録してあとで再生するが、既定の動作を止める処理は `<a>` のクリックにしか無い(`@angular/core@21.2.26` の `fesm2022/primitives-event-dispatch.mjs:491-493`)。送信ボタンを最初は `disabled` で描き、ブラウザで有効にすれば防げる

```ts
ready = signal(false);                                  // サーバーでは false のまま描かれる
constructor() { afterNextRender(() => this.ready.set(true)); }
// <button type="submit" [disabled]="busy() || !ready()">送信</button>
```

---

### 4. ほかの選択肢

ライブラリは要りません。Angular の `HttpClient` と Reactive Forms で足ります。

フレームワークに依存しない方法としては、ブラウザ標準の `fetch(url, { method: 'POST', body: new FormData(form) })` があります。`new FormData(form)` は、jQuery Form Plugin の `formToArray()` と同じく、ブラウザの送信規則で値を集めます。ただし `fetch` はアップロードの進み具合を取れません(取るなら `XMLHttpRequest` か、`withFetch()` を付けない `HttpClient`)。Spartacus の中では、認証のヘッダーや言語・通貨のパラメータを付ける `HttpInterceptor` を通すため、`fetch` ではなく `HttpClient` を使います。

---

### 5. 選び方

| 条件 | 方法 |
|---|---|
| Spartacus にある機能(会員登録、住所、パスワード変更など)のフォーム | 標準のコンポーネント。見た目だけ変えるならテンプレートと SCSS |
| 標準に無いフォーム | Reactive Forms + 自作の Facade / Connector / Adapter([15 章](../../15-facade-connector-adapter.md)、2.4 節) |
| Spartacus を使わない Angular のプロジェクトのフォーム | Reactive Forms + コンポーネントから `HttpClient` を直接(3.2 節) |
| 送り先がフォームの形式(urlencoded / multipart)しか受けない | `HttpParams` か `new FormData(form, submitter)`(3.3 節) |
| ファイルを送る | Spartacus の中なら `cx-file-upload` + Adapter で `FormData`。使わないなら `<input type="file">` + `FormData`(3.4 節) |
| 進み具合を出したい | `HttpClient` の `reportProgress: true, observe: 'events'`(3.4 節)。`withFetch()` は付けない |
| 全部の送信に同じヘッダーや処理を付けたい | `HttpInterceptorFn` + `withInterceptors()`(3.5 節) |
| 送り先が JSP のコントローラしか無い | フロントだけでは移せない。OCC に API を作る([12 章](../../12-backend-api-granularity.md)、[13 章](../../13-jsp-to-headless.md)) |
| サーバーが HTML の断片を返している | JSON を返す API に変え、HTML はコンポーネントで描く |

---

### 6. コンピュータサイエンスの観点から

- **プログレッシブエンハンスメント**: jQuery Form Plugin は「JS が無くても動くフォーム」に後から Ajax を足す作りだった。フォームの `action` と `method` がそのまま使われる。Spartacus は SPA なので、フォームは JS が動いて初めて意味を持つ。SSR はこの差を部分的に埋めるが、送信までは引き受けない
- **iframe トランスポートは、XHR が足りなかった時代の名残**: XHR でファイルを送れなかった頃、ページを移動させずにファイルを送る唯一の方法が、隠した `<iframe>` に普通の送信をさせることだった(`pkg/src/iframe-transport.js`)。XHR2 の `FormData` と `xhr.upload` が標準になり、4.6.0 では「`FormData` が無いときに自動で iframe を選ぶ」ことに非推奨の警告が出る(`pkg/src/submission.js:378-381`)
- **送る形式の違い**: HTML のフォームは `application/x-www-form-urlencoded` か `multipart/form-data` で送る。OCC の多くの API は JSON の本文を受け取る。jQuery Form Plugin も 4.x で `requestFormat: "json"` を足した(`pkg/src/submission.js:101-106`)。置き換えでは、送る形式が変わることを API の側でも確かめる
