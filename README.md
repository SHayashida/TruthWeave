# PaperOps Template v1

Reproducible research workflow template for academic papers. Ensures experiments are traceable, paper metrics are automatically synced, and manual number updates are eliminated.

## Quickstart

```bash
uv sync
uv run paperops run exp=example
uv run paperops discover
uv run paperops build-paper-assets --paper example
uv run paperops check --paper example
```

## 使い方：論文執筆フロー（B運用・投稿先別TeX対応）

※未実装の場合は該当チケットを適用してください。

### メンタルモデル（流れ）

```
Experiment (conf/exp + src/paperops/experiments)
  -> runs/
  -> artifacts/
  -> papers/<paper_id>/auto
  -> PDF
```

### 0. 新しい論文（投稿先）を追加

```bash
uv run paperops create-paper <paper_id>
# ベース論文から複製する場合:
uv run paperops create-paper <paper_id> --from <base_paper_id>
```

- cls/sty は `papers/<paper_id>/styles/` に置く（TeXINPUTS で参照）

### 1. 新しい実験を追加（AIは中身だけ編集）

```bash
uv run paperops create-exp <exp_name>
```

AIに渡すテンプレ（編集許可ファイルを明示）:

```
このリポジトリの構成は固定です。
編集して良いファイル:
- conf/exp/<exp_name>.yaml
- src/paperops/experiments/<exp_name>.py
それ以外のファイル/ディレクトリは作成・変更しないでください。
```

```bash
uv run paperops run exp=<exp_name>
```

### 2. データを追加（必要なら）

```bash
uv run paperops create-dataset <dataset_id>
```

- 生データ配置先: `data/raw/<dataset_id>/`

### 3. 解析・集計・図表を追加（必要なら）

```bash
uv run paperops create-analysis <analysis_name>
make analysis NAME=<analysis_name>
# 直接実行する場合:
uv run python -m paperops.analysis.<analysis_name>
```

### 4. 論文に数値・表・図を反映（更新漏れ防止）

```bash
uv run paperops build-paper-assets --paper <paper_id>
```

- `papers/<paper_id>/auto/variables.tex` を `\input` し、本文の数値はマクロ参照にする

### 5. PDFビルド（任意）

```bash
uv run paperops build-paper --paper <paper_id>
```

- `latexmk` などの TeX ツールが必要（未インストールならエラー表示）

### 6. コミット前チェック（探索/dev と CI/ci）

```bash
uv run paperops check --paper <paper_id> --mode dev
uv run paperops check --paper <paper_id> --mode ci
```

- dev: STRUCTURE / PAPER_NUMBERS は警告のみ
- ci: STRUCTURE / PAPER_NUMBERS も失敗扱い

### トラブルシューティング（症状 / 原因 / 解決コマンド）

| 症状 | 原因 | 解決コマンド |
| --- | --- | --- |
| MANIFEST が stale | assets 未更新 | `uv run paperops build-paper-assets --paper <paper_id>` |
| No runs found | 実験未実行 | `uv run paperops run exp=<exp_name>` |
| Structure check fail | 配置ルール違反 | スキャフォールドを使い再配置 |
| Manual inline numbers detected | 本文直書き | マクロへ置換 or `% paperops-allow-number` |

### AIに依頼するときの鉄則

- まず `create-*` で雛形を作る
- AI には編集して良いファイルを明示し、それ以外は禁止

コピペ用テンプレ:

```
このリポジトリの構成は固定です。
編集して良いファイル:
- <create-* の出力で表示されたファイルのみ>
それ以外のファイル/ディレクトリは作成・変更しないでください。
```

## Paper workflow

- Papers live under `papers/<paper_id>/` with a `paperops.yml` configuration.
- `paperops discover` scans for `paperops.yml` and writes `artifacts/manifests/papers_index.json`.
- `paperops build-paper-assets --paper <paper_id>` writes `papers/<paper_id>/auto/variables.tex` and `papers/<paper_id>/auto/MANIFEST.json`.
- `paperops build-paper --paper <paper_id>` builds the LaTeX paper using the engine in `paperops.yml`.
- Make targets: `make assets PAPER=<paper_id>`, `make paper PAPER=<paper_id>`, `make assets-all`, `make paper-all`.

## How to add experiments (use create-exp)

```bash
uv run paperops create-exp myexp
uv run paperops run exp=myexp
```

## Workflow: add experiment

1) `uv run paperops create-exp myexp`
2) Ask AI to edit ONLY the created files
3) `uv run paperops run exp=myexp`

## Workflow: add analysis

1) `uv run paperops create-analysis my_analysis`
2) Ask AI to edit ONLY the created file
3) `make analysis NAME=my_analysis`

## Codex/AI Agent Skills

This repository includes structured skills for AI agents (Codex, GitHub Copilot, etc.) in `.codex/skills/`:

### Available Skills

#### `paperops-build-assets`
- **Purpose**: Rebuild paper assets (figures/tables/variables) deterministically for a paper_id
- **Usage**: Automatically invoked when AI needs to regenerate paper outputs
- **Key Commands**: `uv run paperops build-paper-assets --paper <paper_id>`
- **Constraints**: Never manually edit `papers/<paper_id>/auto/`

#### `paperops-check`
- **Purpose**: Run PaperOps CI checks, diagnose failures, and propose fixes
- **Usage**: Automatically invoked for validation and troubleshooting
- **Key Commands**: `uv run paperops check --paper <paper_id> --mode ci`
- **Capabilities**: Detects stale assets, missing metadata, structure violations

### Maintaining Skills

To add or modify skills:

1. Create/edit skill in `.codex/skills/<skill_name>/SKILL.md`
2. Follow the frontmatter format:
   ```yaml
   ---
   name: skill-name
   description: Brief description
   ---
   ```
3. Include: Inputs, Rules, Output format, Remediation playbook
4. Skills are automatically available to AI agents

See `AGENTS.md` for the agent contract and editing constraints.

## Workflow: add dataset

1) `uv run paperops create-dataset mydata`
2) Place raw files into `data/raw/mydata/`

## AI prompt template

```
You are editing this repo.
Allowed files to edit:
- <list paths from scaffold output>
Do not create new directories; CI will fail.
```

## Check modes

- `paperops check` defaults to dev mode (STRUCTURE/PAPER_NUMBERS warn only).
- `paperops check --mode ci` treats STRUCTURE/PAPER_NUMBERS as failures.

## B運用（投稿先ごと）最短手順

```bash
uv run paperops create-paper demo_paper
uv run paperops run exp=example
uv run paperops build-paper-assets --paper demo_paper
uv run paperops build-paper --paper demo_paper
uv run paperops check --paper demo_paper
make assets-all
make paper-all
make check-all
```

## Pipeline config

- `conf/pipeline.yaml` defines what counts as the latest run and which sources flow into assets.
