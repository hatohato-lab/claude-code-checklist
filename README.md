# claude-code-checklist

Claude Code で、作業を要素に分け、フォルダーごとに1枚のチェックリスト（HTML）で進めるためのスキルです。
チェックリストの行ごとに、PlantUML の図が中心の設計書を1枚付けます。
プラグインとして入れることも、クローンしてワークスペースのスキルとして使うこともできます。

## 目次

1. 入っているもの（スキル1つと、点検のスクリプトと、設計書の見本）
2. 入れ方1（プラグインとして入れる）
3. 入れ方2（クローンして、ワークスペースのスキルとして使う）
4. 必要なもの（Python と、図を描くときの Java と plantuml.jar）
5. 更新のしかた（使う側と作る側）
6. ライセンス（MIT）

## 1. 入っているもの（スキル1つと、点検のスクリプトと、設計書の見本）

| ファイル | 何をするか |
|---|---|
| `skills/チェックリストの作成/SKILL.md` | 手順の本文。チェックリストと設計書の形、名前の付け方、点検、報告のしかた |
| `skills/チェックリストの作成/チェックリストを点検する.py` | チェックリストの6つの点検を数える。読むだけで、何も書き換えない |
| `skills/チェックリストの作成/設計書の見本.html` | 設計書の見た目と、図のクリック拡大の見本 |

呼び出す言葉は「チェックリストで」「チェックリストを作って」「タスクに分けて」「作業を分解して」などです。

## 2. 入れ方1（プラグインとして入れる）

Claude Code で、次の2行を順に実行します。

```
/plugin marketplace add hatohato-lab/claude-code-checklist
```

```
/plugin install checklist@claude-code-checklist
```

## 3. 入れ方2（クローンして、ワークスペースのスキルとして使う）

使うワークスペースのいちばん上のフォルダーで、次の1行を実行します。

```
git clone https://github.com/hatohato-lab/claude-code-checklist .claude/skills/claude-code-checklist
```

フォルダーに `.claude-plugin/plugin.json` があるので、Claude Code はこのフォルダーをプラグインとして読みます。
ワークスペースのフォルダーで読ませるには、ワークスペースを信頼する確認を先に済ませておきます。
更新は、クローンしたフォルダーで `git pull` を実行します。

プラグインとしてではなく、ふつうのスキルとして使うときは、`skills/チェックリストの作成` のフォルダーだけを、ワークスペースの `.claude/skills/` に写します。

## 4. 必要なもの（Python と、図を描くときの Java と plantuml.jar）

| 使う場面 | 必要なもの |
|---|---|
| チェックリストの点検 | Python 3 |
| 設計書の図を描く | Java と plantuml.jar |

図は、手元の plantuml.jar で SVG にして、設計書の HTML に埋め込みます。図の内容を、外のサーバーへ送って描くことはしません。
plantuml.jar の置き場所は決めていません。それぞれの環境の場所を使います。

## 5. 更新のしかた（使う側と作る側）

プラグインとして入れた場合は、次の1行で最新にします。

```
/plugin marketplace update claude-code-checklist
```

作る側は、中身を変えたら `.claude-plugin/plugin.json` の `version` を上げます。
上げないと、使う側に更新が届きません。

## 6. ライセンス（MIT）

MIT License です。詳しくは LICENSE を見てください。
