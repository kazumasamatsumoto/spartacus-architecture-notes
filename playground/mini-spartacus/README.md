# mini-spartacus: Spartacus の「CMS がページを組み立てる仕組み」を 15 ファイルで再現したもの

SAP Composable Storefront(Spartacus)のうち、次の 3 つの疑問に対応する部分だけを、本家と同じ名前・同じ構造で小さく作り直したものです。

1. ルートをほとんど書かないのに、なぜ URL ごとに違う画面が出るのか
2. ヘッダーやフッターを残して、どの DOM が描き直されるのか。誰がそれを決めているのか
3. ソート(クエリだけ変わる)と商品ページ遷移(パスが変わる)で、何が同じで何が違うのか

画面下に観測パネルがあり、NAV(遷移)/ HTTP / STATE / LIFE(生成・破棄)/ CD(その tick でテンプレートが評価された view)が時系列で出ます。右側は State の中身(Redux DevTools の代わり)です。

## 動かす

```bash
cd mini-spartacus
npm install          # 初回のみ
npx ng serve --port 4300
# → http://localhost:4300/
```

Angular 21、zone.js あり(本家と同じ `provideZoneChangeDetection`)。バックエンドは無く、`occ-fake-backend.ts` の JSON を 400ms 遅延で返します。

## ファイルと本家の対応

| このリポジトリ | 役割 | 本家(spartacus/core-libs/...) |
|---|---|---|
| `app.routes.ts` | ルート表。`product/:code` と `**` の 2 本だけ。どちらも `PageLayoutComponent` | `storefront/cms-structure/routing/cms-route/add-cms-route.ts:12-16`、`storefront/cms-pages/product-details-page/product-details-page.module.ts:17-23` |
| `cms/routing.service.ts` | URL → PageContext の変換規則(クエリは見ない) | `core/src/routing/store/reducers/router.reducer.ts:169-215` |
| `cms/cms-page.guard.ts` | Guard。PageContext を作り、ページを State に入れてから通す | `storefront/cms-structure/guards/cms-page.guard.ts:51-95` |
| `cms/routing-config.ts` | `loadStrategy`。既定 ALWAYS = 再訪でも `cms/pages` を取り直す | `core/src/routing/configurable-routes/config/routing-config.ts:11-44`、`routing-config.service.ts:45-47` |
| `cms/occ-fake-backend.ts` | OCC の代わり。**ここが CMS の管理画面で組んだページ** | `core/src/occ/adapters/cms/occ-cms-page.adapter.ts` |
| `cms/occ-cms-page.normalizer.ts` | API の形 → State の形(改名、配列→map、本体の分離) | `core/src/occ/adapters/cms/converters/occ-cms-page-normalizer.ts` |
| `cms/cms.service.ts` | NgRx の cms ストア + Facade を 1 クラスに畳んだもの | `core/src/cms/store/*`、`core/src/cms/facade/cms.service.ts` |
| `storefront.component.ts` | 固定の外枠。header / footer も `PageLayout` | `storefront/layout/main/storefront.component.html` |
| `cms/page-layout.component.ts` | 表②(LayoutConfig)を引いてスロット名の並びを出す | `storefront/cms-structure/page/page-layout/page-layout.component.ts` |
| `cms/layout-config.ts` | 表②。枠・テンプレート名 → スロット名の並び | `storefront/recipes/config/layout-config.ts:33-64` |
| `cms/page-slot.component.ts` | 表③。position → コンポーネント配列。uid の並びが同じなら流さない | `storefront/cms-structure/page/slot/page-slot.component.ts` |
| `cms/component-wrapper.directive.ts` | 表④を引いて `createComponent`。`CmsComponentData` を子 Injector で渡す | `storefront/cms-structure/page/component/component-wrapper.directive.ts`、`handlers/default-component.handler.ts` |
| `cms/cms-config.ts` | 表④。typeCode → Angular クラス | `core/src/cms/config/cms-config.ts`(各モジュールの `provideDefaultConfig`) |
| `cms/cms-component-data.ts` | コンポーネントが CMS データを受け取る入口(@Input ではなく DI) | `storefront/cms-structure/page/model/cms-component-data.ts` |
| `components/*.component.ts` | 描画クラス。Paragraph / Banner / ProductList / ProductSummary / Logo / SearchBox / FooterNav | `storefront/cms-components/...` |
| `components/product.services.ts` | 商品検索・商品の最小ストア。同じ条件なら呼ばない | `ProductSearchService`、`ProductService` |
| `debug/*` | 観測パネル(本家には無い) | なし |

省略したもの: NgRx(Action / Effect / Reducer は BehaviorSubject に畳んだ)、HttpClient、遅延ロード、アウトレット、SSR、i18n。

## 実験メニュー(ログを見ながら)

### 1. 初回ロード
`http://localhost:4300/` を開く。順番に注目:
`CmsPageGuard: / → ContentPage-homepage` → `hasPage = false` → `GET cms/pages` → 応答 → `State 更新` → `NavigationEnd` → `PageLayout[header/footer/main]` が表②∩ページのスロットを計算 → 各 `PageSlot ← [uid...]` → `created Banner/Paragraph/Logo...` → `CD tick`。
ヘッダーとフッターも、この 1 回の `cms/pages` 応答から引いている。

### 2. ホーム → 一覧(/search)→ ホーム
ヘッダーの「商品を探す」→ ロゴ、の順にクリック。
- /search では `cms/pages?...pageLabelOrId=search` が 1 回。`destroyed Banner/Paragraph`、`created ProductList`。**Logo / SearchBox / FooterNav は destroyed も created も出ない**(uid の並びが同じで PageSlot が流さない)。
- ホームへ戻ると `hasPage(ContentPage-homepage) = true だが loadStrategy=ALWAYS → cms/pages を取り直す`。**既定では一度見たページでも `cms/pages` は毎回飛ぶ**(本家も同じ。CMS の編集やログイン状態による出し分けを次の遷移で反映するため)。ただし応答の uid の並びは同じなので、Logo / SearchBox / FooterNav / Paragraph は作り直されず、State の中身が同じ値で上書きされるだけ。
- `cms/routing-config.ts` を `'ONCE'` にすると `hasPage(...) = true → HTTP なし` になり、再訪で飛ばなくなる。

### 3. ソート(クエリだけ変わる)
/search で並び替えを変える。
- `router.navigate([], { queryParams })` → `NavigationEnd /search?sortCode=...`。**CmsPageGuard の行が出ない**(ガードはパスやパラメータが変わったときしか走らない)。`cms/pages` も出ない。
- `GET products/search?sort=...` だけ出る。
- `CD tick` の行: `App › Storefront › PageLayout[main] › PageSlot[ProductListSlot] › ProductList › Tile...`。**PageLayout[header] は出てこない**。OnPush で dirty でないので評価を飛ばされている。App と Storefront は Default なので毎回出る。
- `created Tile` ×5 と `destroyed Tile` ×5。`@for (...; track p)` が同一性で比較しているので、新しい配列が来ると行を作り直す。`product-list.component.ts` の `track p` を `track p.code` に変えると、作り直しが消えて並び替えだけになる。

### 4. 商品 A → 商品 B(同じルート、:code だけ変わる)
商品ページ下の「他の商品へ」をクリック。
- `CmsPageGuard` は走る(パラメータが変わったので)。`hasPage(ProductPage-<B>) = false` → **`cms/pages` がもう 1 回呼ばれる**(index のキーが `ProductPage-<code>` なので商品ごとに別扱い。既定の ALWAYS ではどのみち毎回)。本家も同じ挙動。
- `created PageLayout[main]` は出ない(Angular がルートコンポーネントを再利用)。`created ProductSummary` も出ない。`PageSlot[Summary]` の uid が同じなので作り直されず、`product$` の値だけ変わる。
- `GET products/<B>`。2 回目以降同じ商品に戻ると `State にある → 呼ばない`。

### 5. 存在しない URL
`http://localhost:4300/nothing/here` を開く。`cms/pages?...pageLabelOrId=nothing/here` が「該当なし」→ `notFound ページを表示(URL は変えない)`。

### 6. CMS 側だけを変える(フロントのコードは触らない)
`cms/occ-fake-backend.ts` を編集して保存(自動リロード):
- homepage の `Section1` と `Section2A` のコンポーネントを入れ替える → 画面の順番は **変わらない**(順番を決めるのは表②)。中身は入れ替わる。
- `Section2A` の typeCode を `CMSParagraphComponentX` にする → その場所に何も出ず、ログに `flexType "..." は cmsComponents に無い → 何も描かない`。エラーにならない。
- homepage に新しいスロット `Section3` を足す → 表②に無いので **出ない**。`layout-config.ts` の `LandingPage2Template` に `'Section3'` を足すと出る。これが「バックエンドが新しいスロットを作ったらフロントに頼むこと」の正体。

### 7. フロント側だけを変える
- `cms/routing-config.ts` の `loadStrategy` を `'ONCE'` にする → 一度見たページに戻っても `cms/pages` が飛ばなくなる。代わりに CMS 側の変更はリロードまで反映されない。
- `layout-config.ts` の `LandingPage2Template` を `['Section2A', 'Section1']` にする → 順番が入れ替わる。
- `cms-config.ts` の 1 行を消す → その typeCode のコンポーネントが全ページから消える。
- `paragraph.component.ts` の `OnPush` を外す → ソートのたびに `CD tick` の行に Paragraph が出るようになる(Default は毎回評価される)。

## 読むときの地図

「URL → 画面」の一本道は、ファイルをこの順に読むと追えます。

```
app.routes.ts → cms-page.guard.ts → routing.service.ts(URL→PageContext)
  → cms.service.ts getPage(index に無ければ occ-fake-backend → normalizer → State)
  → storefront.component.ts(外枠)→ page-layout.component.ts(表②)
  → page-slot.component.ts(表③)→ component-wrapper.directive.ts(表④ + createComponent + CmsComponentData)
  → components/*.component.ts(data$ | async)
```

表①〜④の持ち主: ① `cms/pages` 応答の `template` と `slots` = CMS、② LayoutConfig = フロント設定、③ スロットの中身 = CMS、④ typeCode → クラス = フロント設定。
