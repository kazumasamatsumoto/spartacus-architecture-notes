# 番外 2. GitHub Universe 2026 サマリー

> 作成日: 2026-11-24。共有された調査メモ 4 本を 1 枚にまとめたものです。リンクと引用はメモからそのまま取っており、各ページを開いて中身と一致するかは確かめていません。例外は 5 節の Chopin と Ace の状態で、公式のリポジトリとプロジェクトページを開いて確かめました。

GitHub Universe 2026(2026 年 10 月 28〜29 日)の主張は「実装はエージェントへ、人間は方向性・判断・センスへ」です。GitHub は「AGI」という言葉をほぼ使わず、「アンビエント・インテリジェンス」という言葉で未来を語っています。

## 1. 6 つの発表

6 つとも 10 月 28 日の Universe で発表されました。最初に読むなら、全体をテーマごとに整理した公式まとめ [GitHub Universe 2026: Evolving every layer of the stack](https://github.blog/news-insights/company-news/github-universe-2026-evolving-every-layer-of-the-stack/) です。

| 発表 | 何をするものか | 主な資料 |
| --- | --- | --- |
| Copilot app & Projects | ゴールを与えると、関連する作業をプロジェクトとしてまとめ、Copilot が調整する | [Changelog](https://github.blog/changelog/2026-10-28-github-copilot-app-universe-releases/)、[Docs: Working with projects](https://docs.github.com/en/copilot/how-tos/github-copilot-app/working-with-projects)、[発表時ブログ(日本語)](https://github.blog/jp/2026-06-04-github-copilot-app-the-agent-native-desktop-experience/) |
| Copilot Fusion | タスクごとに使うモデルを Copilot が選び、組み合わせて動かす。ローカルモデルも選べる。前身は HydraFusion | [Changelog](https://github.blog/changelog/2026-10-28-route-and-orchestrate-models-with-github-copilot-fusion/)、[ローカルモデル対応](https://github.blog/changelog/2026-10-28-github-copilot-fusion-now-supports-selection-of-local-models/)、[HydraFusion Docs](https://docs.github.com/en/early-access/copilot/hydrafusion) |
| GitHub Intelligence | GitHub 上のデータのグラフをもとにした、コンテキストと学習の層(4 節) | [Changelog](https://github.blog/changelog/2026-10-28-github-intelligence-puts-your-code-context-and-history-to-work) |
| Copilot Automations | API で外部から起動したり、GitHub のイベントに反応したり、自動化同士をつないで複数ステップにしたりできる。チームで共有もできる | [新しいツール・トリガー・コスト管理](https://github.blog/changelog/2026-10-28-new-tools-triggers-and-cost-controls-for-copilot-automations/)、[共有ワークフロー](https://github.blog/changelog/2026-10-28-build-shared-workflows-for-your-team-with-copilot-automations/)、[Docs(日本語)](https://docs.github.com/ja/copilot/concepts/agents/cloud-agent/about-automations) |
| AI Security & Agent Merge | Agent Merge は、PR のマージを止めている原因(失敗している Actions、コンフリクト)を Copilot が直す。AI Security は、エージェントの最初のコミットから本番までコードを守る | [Agent Merge のまとめ(SmartScope)](https://smartscope.blog/en/blog/github-copilot-app-updates-universe-projects-agent-merge-2026/)、[Docs: Secure code from commit to production](https://docs.github.com/en/code-security/tutorials/secure-code-from-commit-to-production)、[Risks and mitigations](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/risks-and-mitigations) |
| Platform | GitHub を動かしたまま、Git の基盤をエージェント規模の開発に耐えるよう作り直す。ストレージとコンピュートを分ける | [The New Stack: 月 74 億コミット、CPU 400 万コア追加](https://thenewstack.io/?p=22841892)、[CodeZine: Opening Keynote(日本語)](https://codezine.jp/article/detail/30168?p=3) |

ハーネスやランタイムに関心があるなら、Platform と Fusion を先に読むのがおすすめです。「GitHub がよく止まる」問題への GitHub 自身の答えは、Platform の記事にあります。

## 2. GitHub の思想

GitHub は「超知能」ではなく、開発者が中心にい続ける未来を語っています。中心になる言葉は次の 4 つです。

- **大事な成果物は「完成した仕事」**: 基調講演のキーメッセージです。増やすべきはコードの量ではない、という立場です([公式まとめ](https://github.blog/news-insights/company-news/github-universe-2026-evolving-every-layer-of-the-stack/))。
- **Beyond the first 1%**: 「人類がこれまでに書いた全コードは、これから作られるものの 1% にすぎないかもしれない」という話です。公式まとめは、開発者はかつてないほど重要だ、という一文で締めくくられています。
- **アンビエント・インテリジェンス**: 開発者向けの画面は背景に退き、細かい作業はエージェントが担います。開発者は方向を示し、結果を判断します。Developer Relations 担当 VP の Martin Woodward 氏が 10 月 15 日に書いたもので、「センス(taste)の価値を高める」という趣旨の一文があります([記事](https://github.blog/news-insights/company-news/the-next-developer-interface-is-ambient-intelligence/))。
- **AI は物語を書かない。あなたが書く**: Day 2 のクロージングキーノートです。AI が量産する低品質な成果物(AI slop)に向き合い、メンテナーを守る機能と人間の役割を語った回です([CodeZine レポート](https://codezine.jp/article/detail/30183?p=3))。登壇者は Woodward 氏で、東京版もこの流れを踏まえているとみられます。

「開発者はかつてないほど重要だ」という主張は、ユーザー単位で課金する GitHub のビジネスとも矛盾しません。

## 3. データで見る現状

エージェントから始まるプルリクエストは、3 月の 17% から 9 月には 40% 以上に増えました([Octoverse 2026](https://github.blog/news-insights/octoverse/octoverse-commits-pushes-reach-new-highs-in-2026-as-developers-build-with-agents/))。仕事の最初の一手はエージェントへの指示になり、レビューは「返ってきたものを形づくる手段」になりつつある、という整理です。

## 4. GitHub Intelligence

GitHub Intelligence は、エージェントにコンテキストを渡すための知識の層です([Changelog](https://github.blog/changelog/2026-10-28-github-intelligence-puts-your-code-context-and-history-to-work))。コンテキストが無いと、エージェントは既にある知識を探し直すのに時間を使い、チームの規約を見落とします。それを、GitHub 上のデータのグラフで補います。

| 機能 | 役割 |
| --- | --- |
| Memory | セッションをまたいで知識を引き継ぐ |
| Dreaming | コンテキストを最新の状態に保つ |
| Code search | 手元のチェックアウトの外まで検索する |

- **一番面白い資料**: [Building an agentic memory system for GitHub Copilot](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/)。難しいのは検索ではなく、ブランチや時間をまたいでコードが変わる中で、保存した知識が正しいままかを保証することだ、という話です。仕様は [Docs: About agentic memory](https://docs.github.com/en/copilot/concepts/agents/copilot-memory) にあります。
- **批判**: [Unblocked の記事](https://getunblocked.com/blog/github-agent-memory-only-knows-github/)は、Claude Code・Cursor・Codex も併用するとメモリがエージェントごとにでき、どれも部分的でばらばらに古くなる、と指摘しています。
- **限界**: 学習できるのは GitHub にあるデータだけです。現場の暗黙知や業務プロセスは拾えません。コンテキストを人が書くのではなく、GitHub 上の活動から自動で学習させる方式だからです。

## 5. GitHub Next

GitHub Next は GitHub 社内の研究開発チームで、Copilot を生んだチームです([githubnext.com](https://githubnext.com/))。リーダーは Idan Gazit 氏で、本人はチームを「Department of Fool Around and Find Out(いじってみて確かめる部署)」と紹介しています。エージェント時代の開発に関わるプロジェクトは次の 3 つです。

| プロジェクト | 段階 | 中身 | 資料 |
| --- | --- | --- | --- |
| GitHub Agentic Workflows(gh-aw) | 10 月 28 日に一般提供。MIT ライセンス | Markdown で書いた自然言語の指示を、制約付きの GitHub Actions にコンパイルする。Copilot・Claude・Codex を切り替えられる | [公式ドキュメント](https://github.github.com/gh-aw/)、[GA の Changelog](https://github.blog/changelog/2026-10-28-github-agentic-workflows-generally-available)、[セキュリティの仕組み](https://github.github.com/gh-aw/introduction/architecture/) |
| Chopin | 2026 年 9 月公開の研究プロトタイプ。MIT ライセンス。GitHub の正式な製品ではない | 人とエージェントが、実装計画・仕様・RFC・決定記録をリアルタイムに共同で書く場。エージェント「Planner」は選んだリポジトリを読んで文書の編集を提案し、コードで決められないことはチームに尋ねる。決めるのは人 | [リポジトリ githubnext/chopin](https://github.com/githubnext/chopin)、[プロジェクトページ](https://githubnext.com/projects/chopin/)、[発表の投稿(X)](https://twitter.com/GitHubNext/status/2095215736322953601) |
| Ace(Agent Collaboration Environment) | 研究プロトタイプ。公式ページでは「当面休止」 | 複数人と複数エージェントが同時に使う作業場。「Slack、GitHub、Claude/Copilot の間に生まれた子ども」と説明されている | [One Developer, Two Dozen Agents, Zero Alignment](https://githubnext.com/talks/one-developer-two-dozen-agents-zero-alignment/)、[Realtime Multiplayer Automation and You](https://githubnext.com/talks/realtime-multiplayer-automation-and-you/) |

- **Continuous AI**: gh-aw の背景にある考え方です。CI のジョブのようにリポジトリの中で動くエージェントが、ルールではなく推論が必要なタスクだけを担います([プロジェクトページ](https://githubnext.com/projects/continuous-ai/))。
- **Chopin が埋めようとしている穴**: 実装をエージェントが担うほど、計画とレビューが中心の仕事になります。ところが今の計画は、動かない文書で、1 人用の道具で書かれ、誰が決めたかも残りません。Chopin はこの穴を、次の仕組みで埋めようとしています([プロジェクトページ](https://githubnext.com/projects/chopin/))。
    - 共同編集できる文書: 他の人の位置とカーソルが見えます。
    - 横のチャット: `@chopin` で Planner を呼べます。
    - 決定の記録: 本文とは別に、決めた人の名前つきで残ります。後の編集で黙って上書きされません。
    - MCP サーバー: 計画を手元のコーディングエージェントへ持ち出せます。
- **Chopin の制約**: 標準の Planner は GitHub に書き込めず、編集するのは Chopin の文書だけです。読むのは開始時点のデフォルトブランチで、対応は GitHub.com だけです。一般向けの公開インスタンスは無く、自分で立てて使います([README](https://github.com/githubnext/chopin/blob/main/README.md))。
- **Ace との関係**: Chopin は Ace の「精神的な子ども」とされています。Ace は野心的ですが複雑すぎたため休止し、うまくいった考えを、計画づくりに絞った Chopin へ引き継いでいます([プロジェクトページ](https://githubnext.com/projects/chopin/))。
- **Ace の問題意識**: ローカルのエージェントの計画は共有されないまま終わります。ビジネス要件、社内政治、ユーザー調査、組織の経緯は人の頭の中にあり、エージェントには届きません。エージェントを増やすほど、人間側の合意形成が詰まります。
- **学ぶ教材として**: gh-aw は中身をすべて読め、エンジンも差し替えられます。ハーネスを外側から統制する仕組みを学ぶのに向いています。[番外. サブエージェントとスキルの分け方](../extra-agent-split-patterns.md)と並べて読むと、分け方と統制の両面が見えます。

Gazit 氏の考え方は、[WeAreDevelopers の講演](https://www.wearedevelopers.com/videos/1903-github-next-and-the-future-of-coding-idan-gazit)でも聞けます。

## 6. 批判的な視点と、読むときの視点

外部からは、信頼性と競合の 2 点が指摘されています。

- [Forrester: Lowering The Floor And Raising The Ceiling](https://www.forrester.com/blogs/github-universe-2026-lowering-the-floor-and-raising-the-ceiling/): 最初の課題として、GitHub はこの 12 か月あまり信頼できる状態ではなかった、と書いています。
- [The New Stack: GitHub のリーダーたちが新しいライバルをどう見ているか](https://thenewstack.io/github-agentic-infrastructure-rebuild/): 元 CEO の Dohmke 氏が作った新しいプラットフォーム「Entire」と対比しています。
- [Unblocked](https://getunblocked.com/blog/github-agent-memory-only-knows-github/): メモリが GitHub の中しか知らない点を批判しています(4 節)。

読むときは、思想としてだけでなく「誰がこの物語で得をするか」も見ると立体的になります。「開発者はかつてないほど重要」という言葉は、ユーザー単位の課金を支える言葉でもあります。一方で、登壇者が語らなかった「現場の暗黙知はリポジトリに無い」という課題を、GitHub Next は Ace と、その後を継いだ Chopin で正面から扱っています。

## 7. 未確認の点

- Chopin が今日(東京版)の講演でどう紹介されたかは、このページに入っていません。上の説明は公式のリポジトリとプロジェクトページによるものです。

- Agent Merge の公式 Changelog は、個別の URL が分かっていません。今は第三者のまとめ記事を参照しています。
- Platform の公式記事「Building Git infrastructure for agent-scale development」も、個別の URL が分かっていません。[github.blog](https://github.blog/) で検索してください。
- Fusion のローカルモデル対応の URL は、参考記事に引用されていたものです。
- GitHub Intelligence について、最初のメモでは「単独のページが無いテーマ」とされていました。その後、公式 Changelog が見つかり、コンテキストの層の名前だと分かったので、このページはそちらに合わせています。
- このページのリンクと引用は、すべて共有されたメモから取ったものです。各ページを開いて、中身と一致するかは確かめていません。

---

[← 番外. サブエージェントとスキルの分け方](../extra-agent-split-patterns.md) | [目次](../README.md)
