# 26. hybris と並行開発しながら移行するリポジトリ戦略: 保守の変更履歴を取り込み続ける条件

> **図**: 25 hybris と並行開発するリポジトリ戦略(`diagrams/spartacus-architecture.drawio`)。左: 保守 main から移行 migration へ一方向に merge するブランチの流れ。中: 保守の変更が種類ごとにどう届くか。右: 取り込み続けるための 6 条件と、戦略ごとの可否

![25 hybris と並行開発するリポジトリ戦略](diagrams/page25.png)

> **この章が答える問い**: hybris(アクセラレータ)の保守開発を止めずに Composable Storefront へ移行するとき、リポジトリとブランチをどう組めば、保守側の変更を移行側へ取り込み続けられるか。前提として何が同じでなければならないか(リポジトリか、フォルダ構成か)。どの戦略がその条件を満たし、どれが満たさないか

> **位置づけ**: 13 章と 25 章は「コードをどこへ移すか」を扱った。この章は「その作業をどのリポジトリ・ブランチでやるか」を扱う。25.6 の移行手順(まず Facade へ下ろす)を、保守と並行する制約の下で並べ直す

> **根拠の取り方**:
> - **CCv2 のリポジトリ構成**: SAP の公式サンプル [SAP-samples/cloud-commerce-sample-setup](https://github.com/SAP-samples/cloud-commerce-sample-setup) のコミット `546fe5b`(24 章で引いた `c3f81d1` より新しい)。以下 `sample/` と書く
> - **git の挙動**: 小さな hybris 風リポジトリで保守と移行を再現した実験スクリプト [`tools/git-sync-experiment.sh`](../tools/git-sync-experiment.sh)(実験 A〜F)と [`tools/git-layout-experiment.sh`](../tools/git-layout-experiment.sh)(実験 G。フォルダ構成を変えた場合)。git 2.50.1 で実行し、出力をそのまま載せる
> - **CCv2 のビルドとデプロイの細部**(接続できるリポジトリの数、ビルドに使うブランチの指定、js-storefront のビルドが失敗したときの扱い)は help.sap.com を確かめられていない。そこに頼る記述は「一般形・要確認」と書く

---

### 先に話し言葉で: 「取り込める」とは、git が共通の祖先を見つけられること

保守の変更を移行側で取り込めるかどうかは、結局 **`git merge` が通るかどうか** です。merge は、両側が共通の祖先を持っていて、そこから「どちらが何を変えたか」を比べられるときにだけ働きます。だから最初の条件は単純で、**移行側は保守リポジトリの履歴をそのまま持つ**こと。ブランチを切るか、履歴ごと複製する。ファイルをコピーして新しいリポジトリを作ると、その時点で取り込みの道は閉じます(26.2 実験 B)。

次に、保守の変更には 2 種類あることを押さえます。**core・facades・OCC のようなバックの変更は、merge すればそのまま Spartacus からも使えます。** 一方、**JSP・タグ・`web/src` の変更は、merge で届いても Spartacus では一度も実行されません**(25.1)。こちらは git では片付かないので、「移植が要る保守コミットの台帳」を作って Angular へ手で写します。

2 つ目の前提は、**保守が触るファイルが、移行側でも同じパスにあること**です。リポジトリそのものが同じである必要はなく、履歴ごと複製した別リポジトリでも取り込めます(実験 C)。フォルダ構成も、全部が同じである必要はありません。`js-storefront/` や新しい拡張を**足す**のは自由です。ただし、**既存のフォルダを動かすと取り込みが不安定になります**。git の「移動の検出」は推測なので、保守が新しいファイルを足したり、移行側で中身を書き換えたりすると外れます(26.3 実験 G)。オンプレの構成(`hybris/` 直下)から CCv2 の構成(`core-customize/hybris/`)へ移すような変更は、移行側ではなく**保守側で先にやって**、構成をそろえてから分かれます。

最後に、衝突を小さくする作法です。**移行側は足すだけにする。** 既存のファイル(Facade、`localextensions.xml`、設定)を変えたいときは、先に保守側に入れて流してもらう(upstream first)。ディレクトリを動かさない、整形し直さない、storefront を先に消さない。取り込みは保守リリースのたびに merge で行い、rebase や cherry-pick は使わない。これだけ守れば、保守のコミットは同じハッシュのまま移行側に並びます。

---

### 26.1 何を取り込むのか: 保守の変更を 4 種類に分ける

| 保守側で変わる場所 | 例 | 移行側での意味 | 取り込み方 |
|---|---|---|---|
| core・facades・service 拡張、`items.xml`、ImpEx、既存の OCC 拡張 | Facade の価格計算の修正 | Spartacus も OCC 経由で同じコードを使う | **merge で自動**。同じハッシュのまま届く(実験 A') |
| storefront・addon の web 層(`web/src`、JSP、タグ、`_ui`、`base_*.properties`) | 表示文言、数量の上限、BeforeViewHandler | merge で届くが、`/occ/v2` の通り道に無いので**実行されない**(25.1) | **台帳に載せて Angular へ移植**(26.5) |
| `localextensions.xml`、`manifest.json`、`*.properties` | 拡張の追加、プロパティ変更 | 両側が触るので衝突しやすい | 拡張・設定の追加は**先に main へ**(実験 A と A') |
| Backoffice で直したデータ(CMS、商品、設定) | ページの差し替え、文言 | git に無い | リポジトリ戦略の外。ImpEx に起こしたものだけ届く |

2 行目が、並行開発の本当のコストになる。保守で直した画面のふるまいは、merge では移行側に効かない。これを落とさない仕組みが要る(26.5)。

---

### 26.2 取り込み続けるための 6 条件と、それを確かめた実験

6 条件のうち **C1 と C2 は前提条件**で、満たしていないと取り込みの仕組みそのものが成り立たない。C3〜C6 は、前提を満たしたうえで衝突と漏れを小さくする運用の条件。

| 条件 | 内容 | 破るとどうなるか |
|---|---|---|
| **C1 共通の祖先**(前提) | 移行側は保守リポジトリの履歴を持つ(同じリポジトリのブランチか、履歴ごと複製したリポジトリ) | `refusing to merge unrelated histories`。無理に merge すると全ファイルが add/add 衝突(実験 B) |
| **C2 保守が触るファイルのパスが一致する**(前提) | 既存のファイルは保守と同じパスに置く。新しいディレクトリを足すのは自由。構成を変えるなら保守側で先に変える(26.3) | 移動と書き換えが重なると modify/delete 衝突(実験 D、G3)。保守が移動先に新しいファイルを足すたびに止まる(実験 G1b) |
| **C3 一方向の merge** | main → migration の向きだけ。merge コミットで取り込み、rebase・squash・cherry-pick しない | cherry-pick すると同じ変更が別ハッシュで 2 つ残り、「どこまで取り込んだか」を履歴で追えない(実験 E) |
| **C4 移行側は足すだけ** | 既存ファイルの変更(Facade の移動、拡張の追加、設定)は先に main へ入れる | 同じ箇所を両側が触って衝突する(実験 A) |
| **C5 web 層の変更は台帳で拾う** | 前回の取り込み以降の保守コミットのうち、web 層を触ったものを一覧にする | 保守で直した画面のふるまいが、移行後に元へ戻る |
| **C6 決まった間隔で取り込む** | 保守リリースのたび、など | 差が溜まるほど衝突が大きくなる。C5 の台帳も一度に膨らむ |

C1〜C4 は実験で確かめた。スクリプトは `T0`(移行開始時点)の小さなリポジトリを作り、保守側に次のコミットを積む。

- **MNT-101**: Facade の修正(バック)
- **MNT-102**: タグと `web/src` の修正(web 層)
- **MNT-103**: `localextensions.xml` に拡張を追加

そのうえで、移行側の作り方を変えて取り込みを試した。

**実験 A: 同じリポジトリの migration ブランチ。移行側も `localextensions.xml` の末尾に `xocc` を足した**

```
--- 取り込み前の移植台帳: migration にまだ無い保守コミットのうち web 層を触ったもの
4fad48f MNT-102 show currency, max qty 50 (storefront only)
--- merge main -> migration
CONFLICT (content): Merge conflict in core-customize/hybris/config/localextensions.xml
```

**実験 A': `xocc` の追加だけを先に保守 main へ入れた(upstream first)**

```
Merge made by the 'ort' strategy.
--- migration 側から見た Facade の履歴(保守のハッシュのまま)
f6e2e8b MNT-101 fix negative price in PriceFacade
cb76ebb initial
--- main2 の MNT-101 のハッシュ
f6e2e8b MNT-101 fix negative price in PriceFacade
```

**実験 B: T0 のファイルをコピーして新しいリポジトリを作った(履歴なし)**

```
fatal: refusing to merge unrelated histories
--- --allow-unrelated-histories
CONFLICT (add/add): Merge conflict in core-customize/hybris/bin/custom/xfacades/src/PriceFacade.java
CONFLICT (add/add): Merge conflict in core-customize/hybris/bin/custom/xstorefront/web/src/CartPageController.java
CONFLICT (add/add): Merge conflict in core-customize/hybris/bin/custom/xstorefront/web/webroot/WEB-INF/tags/price.tag
CONFLICT (add/add): Merge conflict in core-customize/hybris/config/localextensions.xml
```

**実験 C: 履歴ごと複製した別リポジトリ(clone して upstream を fetch)**

```
Merge made by the 'ort' strategy.
--- 取り込んだ MNT-104 のハッシュ(元リポジトリと同じ)
af488a3 MNT-104 min price 1 / max qty 40
af488a3 MNT-104 min price 1 / max qty 40
```

**実験 D: 移行側で `core-customize` を `backend` へ移動した**

```
--- 移動だけなら rename 検出で追従
Merge made by the 'ort' strategy.
--- 移動と同時に中身も書き換えると追従できない
CONFLICT (modify/delete): core-customize/hybris/bin/custom/xfacades/src/PriceFacade.java deleted in HEAD and modified in main3.
```

**実験 E: MNT-101 を cherry-pick で拾ってから、あとで merge した**

```
Merge made by the 'ort' strategy.
--- 同じ変更が別ハッシュで 2 つある
81ad1fd MNT-101 fix negative price in PriceFacade
9167e4b MNT-101 fix negative price in PriceFacade
```

**実験 F: 移行側で storefront 拡張を先に消した**

```
CONFLICT (modify/delete): core-customize/hybris/bin/custom/xstorefront/web/src/CartPageController.java deleted in HEAD and modified in main3.
CONFLICT (modify/delete): core-customize/hybris/bin/custom/xstorefront/web/webroot/WEB-INF/tags/price.tag deleted in HEAD and modified in main3.
```

ハッシュは実行のたびに変わる(コミット時刻を含むため)。変わらないのは「同じリポジトリでも別リポジトリでも、履歴を共有していれば保守のハッシュがそのまま届く」ことと、「衝突の有無」。

実験 D の前半が示すとおり、git の rename 検出は**移動だけ**なら追従する。ただしそれは、移動したファイルの中身が元と十分似ている間だけ。移行では Facade や OCC を書き換えるので、移動に頼らないほうがよい(C2)。実験 F は、保守の web 層の修正が来るたびに「消したファイルが変更された」衝突になることを示す。衝突は台帳の代わりにはなるが、毎回人手で解く必要があり、取り込みが重くなる。web 層は消さずに残し、台帳で拾うほうが軽い(26.6)。

---

### 26.3 前提の詳細: 何が同じでなければならないか

「リポジトリとフォルダ構成が同じであること」が前提に見えるが、git が実際に要求するのはもっと狭い 2 つ。

| 同じでなければならないもの | 同じでなくてよいもの | 根拠 |
|---|---|---|
| **履歴(共通の祖先)** | リポジトリそのもの。履歴ごと複製した別リポジトリでよい | 実験 B(コピーは不可)、実験 C(複製は可) |
| **保守が触るファイルのパス** | フォルダ構成の全体。`js-storefront/`、新しい拡張、移行専用の設定ファイルは足してよい | 実験 A'(足すだけなら自動 merge) |

2 つ目の「パス」が同じでないとき、git は**ファイルの中身が似ているかどうかから移動を推測**して、変更を移動先へ写す(rename 検出)。推測なので、当たる場合と外れる場合がある。CCv2 へ移る機会に、オンプレ構成(リポジトリ直下に `hybris/`)を CCv2 構成(`core-customize/hybris/`。`sample/README.md:46-47`)へ移す場合を、実験 G で試した。

| 実験 | 移行側でやったこと | 保守側でやったこと | 結果 |
|---|---|---|---|
| G1a | `hybris/` → `core-customize/hybris/` へ移動だけ | 既存の Facade を修正 | `Merge made`(移動先へ写った) |
| G1b | 同上 | **新しいファイルを追加** | `CONFLICT (file location): … added in main-work inside a directory that was renamed in HEAD`。毎回人が確認する必要がある |
| G2 | 移動 + Facade の別の行を少し修正 | Facade を修正 | `Merge made`(両方の変更が入った) |
| G3 | 移動 + Facade を大きく書き換え | Facade を修正 | `CONFLICT (modify/delete): hybris/…/PriceFacade.java deleted in HEAD and modified`。移動を見失う |
| G3' | 同上を `git merge -X subtree=core-customize` で取り込む | 同上 | `CONFLICT (content): Merge conflict in core-customize/…/PriceFacade.java`。パスの対応は戻り、残るのは本物の内容の衝突だけ |
| G4 | (構成変更は**保守 main で先に**行い、移行側はそこから分かれる) | 新しいパスで Facade を修正 | `Merge made` |

ここから言えること。

1. **構成変更は保守側で先にやり、構成をそろえてから分かれる(G4)。** これが一番確実。保守側も CCv2 で動かしているなら、構成はもともとそろっている
2. **保守側の構成を変えられないなら、移動は移行側で 1 コミットにまとめ、取り込みは毎回 `-X subtree=core-customize` を付ける(G3')。** プレフィックスが 1 つだけ付く単純な移動なら、パスの対応を git に教えられる。ただし移動の検出に頼るので、G1b のような新規ファイルの扱いは毎回確認する
3. **拡張の名前変更・分割・統合は、並行期間中はやらない。** プレフィックスでは表せない移動なので、`-X subtree` でも救えない

### 26.4 戦略の比較

| 戦略 | C1 祖先 | 保守のバック変更 | web 層変更の検知 | 未完成の移行コードが本番に入るか | CCv2 へのデプロイ | 判定 |
|---|---|---|---|---|---|---|
| **S1 同じリポジトリ + migration ブランチ + upstream first** | ○ | merge で自動 | 台帳(`git log migration..main -- …`) | 入らない(migration に置く)。upstream first で main に入れた追加は本番に出る | 移行環境は migration ブランチをビルド(一般形・要確認) | **推奨** |
| S2 同じリポジトリのトランク(main に js-storefront も置き、公開だけ止める) | ○(merge 不要) | 同じブランチなので常に最新 | 台帳(期間で区切る) | **入る**。JS Storefront を公開しない設定で止める | 保守のビルドに Node のビルドが加わる(失敗時の扱いは要確認) | ○。移行チームと保守チームの距離が近いとき |
| S3 履歴ごと複製した別リポジトリ + upstream remote | ○(実験 C) | `fetch upstream` + merge | 台帳 | 入らない | 移行側リポジトリを別のサブスクリプション/環境に接続する、または切替時に元へ戻す(要確認) | ○。権限やチームを分けたいとき |
| S4 フロントだけ別リポジトリ(バックは保守 main に upstream first) | バックは ○ / フロントは新規なので不要 | main に直接入るので常に最新 | 台帳 | フロントは入らない。バックの追加は入る | CCv2 は `core-customize/` と `js-storefront/` を同じリポジトリに置く構成(`sample/README.md:46-47`)。どこかで 1 つに揃える必要がある(要確認) | △ |
| S5 ファイルをコピーした新しいリポジトリ | ✕(実験 B) | 手で写す | 手で比べる | 入らない | — | **✕** |
| S6 保守のコミットを cherry-pick で拾う運用 | ○ | 拾い漏れ・二重化(実験 E) | 手で選ぶ | 入らない | — | **✕** |

**同じリポジトリに両方を置くのは、SAP の公式サンプルと同じ形**でもある。サンプルはリポジトリ直下に `core-customize/`(SAP Commerce)と `js-storefront/`(Spartacus)を並べる(`sample/README.md:46-47`)。`core-customize/manifest.json` はアクセラレータの `yacceleratorstorefront` と addon を残したまま(`sample/core-customize/manifest.json:8-18`、`accstorefront` アスペクト `:36-39`、`:320`)、SPA 用サイトの URL だけを JS Storefront に向けている(`website.electronics-spa.https` → `${ccv2.services.jsapps.url.0}`、`:132-163`)。つまり **1 つのリポジトリ・1 つのビルドで、アクセラレータのサイトと JS Storefront のサイトを同時に動かせる**。並行期間の構成として、そのまま使える形になっている。

S1 を推奨する理由は 3 つ。

1. **merge の起点が 1 つで済む。** 別リポジトリ(S3)だと remote の管理と、権限の二重管理が増える
2. **upstream first と相性がよい。** バックの追加(OCC 拡張、Facade への移動)は main に入れて保守のテストで守る。移行ブランチに残るのは、本番のふるまいを変えるもの(manifest の切替、storefront の削除)と、フロントだけになる
3. **未完成のフロントが保守のリリースを止めない。** S2 は、Node のビルドや依存の更新が保守のビルドに入り込む

---

### 26.5 推奨構成(S1)の運用

**置き場所の表**

| 変更 | 置く場所 | 理由 |
|---|---|---|
| `web/src` のロジックを Facade へ下ろす(25.6 の 1) | **main** | 両側が使う。アクセラレータのまま動作を変えずにでき、保守のテストで守れる |
| 新しい OCC 拡張・WsDTO・`fields`(24 章) | **main** | 追加だけなので保守に害は無い。ただし本番の `/occ/v2` に API が増えるので、`@Secured` と公開範囲は保守側でもレビューする |
| `localextensions.xml` への拡張追加 | **main** | 衝突点を 1 本にする(実験 A → A') |
| SPA 用のサイト・カタログの ImpEx | main(サイトを作るだけなら)/ migration(既存サイトを切り替えるなら) | 本番のふるまいが変わるかどうかで分ける |
| `js-storefront/` | migration | 未完成のフロントを保守のビルドに入れない |
| `manifest.json` の切替(SPA サイトの URL を jsapps へ、`storefrontAddons` の整理) | migration | 本番のふるまいが変わる |
| storefront・addon 拡張の削除 | **切替後の main** | 先に消すと、保守の修正がすべて modify/delete 衝突になる(実験 F) |
| 保守の web 層の修正 | main で修正 → 台帳 → migration で Angular へ移植 | merge では効かない(26.1) |
| 移行中に見つけたバックのバグ | **main** で修正 → merge で受け取る | 移行側だけで直すと、保守の同じ箇所の修正と衝突し、本番は直らない |

**取り込みの手順(保守リリースのたび)**

```bash
git switch migration
git fetch origin

# 1. 台帳: 前回の取り込み以降の保守コミットのうち、web 層を触ったもの
git log --format='%h %ad %s' --date=short migration..origin/main -- \
  'core-customize/hybris/bin/custom/*/web/*' \
  'core-customize/hybris/bin/custom/*/acceleratoraddon/*' \
  '*.jsp' '*.tag' '*.tld' '*base*.properties'

# 2. 取り込み: merge コミットで(--no-ff)。squash・rebase しない
git merge --no-ff origin/main -m "sync: main $(git rev-parse --short origin/main) into migration"

# 3. 取り込んだ地点に印(任意。merge-base でも分かる)
git tag sync/$(date +%Y%m%d) origin/main
```

1 の `migration..origin/main` は「main にあって migration に無いコミット」。取り込み直前に流すと、ちょうど今回入る分が出る(実験 A の台帳)。パスは自社の拡張名に合わせる。addon の web 層は `acceleratoraddon/web/` の下にある(25 章の OPF では `opfacceleratoraddon/acceleratoraddon/web/…`)。

**台帳の形**(Issue でも表でもよい)

| 保守コミット | 触ったもの | 25.2 の 8 つの形のどれか | Spartacus 側の行き先 | 移植チケット | 状態 |
|---|---|---|---|---|---|
| `4fad48f` MNT-102 | `price.tag`、`CartPageController.java` | タグ(整形)/ ページコントローラ(数量の上限) | フロントの整形パイプ / 上限はバックの検証が正、フロントは写し(25.5) | MIG-2 | 移植済み |

台帳を空にしてから切り替える。これが「保守の変更が移行後に消えない」ことの確認になる。

**main 側で守ること**

- main を rebase・force push しない。履歴を書き換えると、migration が持っている祖先が消える
- main への PR の squash merge は構わない。main 上で 1 コミットになるだけで、migration はそのコミットを merge で受け取る
- web 層のパスを触る PR には、CI か CODEOWNERS で移行チームをレビューに入れる(ラベル自動付与など。仕組みは一般形)。台帳の拾い漏れを PR の時点で減らせる
- 一括整形(フォーマッタ、改行コード、インデント)は、並行期間中はやらない。やるなら main で 1 コミットにまとめ、すぐ migration へ merge する

---

### 26.6 やってはいけないこと

| やりがちなこと | 何が起きるか | 代わりに |
|---|---|---|
| 「きれいに始めたい」と、ファイルをコピーして新しいリポジトリを作る | 以後の保守を merge で取れない(実験 B) | ブランチを切る。別リポジトリが要るなら履歴ごと複製(実験 C) |
| 保守の修正を cherry-pick で拾う | 同じ変更が別ハッシュで残る。どこまで取り込んだかが `git log` で分からない(実験 E) | 保守リリースごとに main 全体を merge |
| 移行側でディレクトリ構成を整理する(`core-customize` → `backend` など) | 移動と書き換えが重なると追従できない(実験 D、G3)。保守の新規ファイルで毎回止まる(G1b) | 構成変更は保守 main で先に(G4)、または切替後に |
| 移行側で storefront・addon を先に消す | 保守の web 層修正のたびに modify/delete 衝突(実験 F) | 切替後に main で消す。検知は台帳で |
| 移行側でバックのバグを直す | 本番は直らない。保守の修正と衝突する | main で直して流す |
| 移行側で Facade を書き換えて OCC 用にする | 保守の Facade 修正と衝突。アクセラレータとの共通部分が割れる | Facade の変更は main で(アクセラレータの動作を変えない形で)。OCC 専用の差は OCC 拡張の Populator / Controller に |
| 取り込みを切替直前にまとめてやる | 衝突と台帳が一度に膨らむ | C6: 保守リリースごと |

---

### 26.7 切り替えとその後

1. **台帳を空にする。** 最後の保守リリースまで取り込み、web 層の移植をすべて済ませる
2. **保守の凍結期間を決める。** 最後の merge から切替までに main に入った変更は、もう一度取り込む(期間を短くするほど楽)
3. **migration を main へ merge する。** 移行側の変更(js-storefront、manifest の切替)が main に入る。main のほうは migration に全部取り込み済みなので、こちら向きの merge で衝突は起きない(取り込みのたびに解いた結果が migration にある)
4. **切替後の main で、storefront・addon 拡張を消す。** `localextensions.xml`、`manifest.json` の `storefrontAddons` と `accstorefront` アスペクトを整理する。ここで初めて構成の整理(C2 の制約の解除)をしてよい
5. **migration ブランチを閉じる。** 以後は普通の 1 本の開発に戻る

---

### 26.8 まとめ

| 問い | 答え |
|---|---|
| 保守の変更を取り込める前提は | ① 移行側が保守の履歴を持つこと(共通の祖先。コピーは不可、履歴ごとの複製なら別リポジトリでも可)② 保守が触るファイルが移行側でも同じパスにあること(新しいフォルダを足すのは自由) |
| フォルダ構成を変えたいときは | 保守 main で先に変えてから分かれる。できなければ移動を 1 コミットにまとめ、`-X subtree=<prefix>` で取り込む |
| 推奨は | 同じリポジトリ + migration ブランチ + upstream first。SAP のサンプルも `core-customize/` と `js-storefront/` を 1 リポジトリに並べている |
| merge で届くもの | core・facades・OCC。同じハッシュのまま届き、Spartacus からもそのまま使える |
| merge では片付かないもの | web 層(JSP・タグ・`web/src`)。届いても実行されないので、台帳に載せて Angular へ移植 |
| 衝突を減らす作法 | 移行側は足すだけ。既存ファイルの変更は先に main へ。移動・整形・先行削除をしない。保守リリースごとに merge |
| 切替の完了条件 | 台帳が空。migration → main の merge のあとで storefront を消す |

---

[目次](README.md) | ← [25. JSP やタグから Java を呼んでいた処理はどうなるか、フロントとバックの責務をどう分けるか](25-jsp-java-calls-and-responsibilities.md) | [番外. サブエージェントとスキルの分け方](extra-agent-split-patterns.md) →
