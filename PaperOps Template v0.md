以下は、**そのまま VS Code の Codex に「実装依頼」として投げられる形式**の「プロジェクト設計仕様（実装チケット）」です。
（狙い：**実験の前提踏襲漏れゼロ**＋**本文数値更新漏れゼロ**＋**再現性監査可能**）

---

# PaperOps Template v0 — 実装仕様（Codex投入用）

## 0. ゴール

* **Goal A（課題1）**：新しい実験を追加しても、初期実験のハード設定・共通パラメータ・seed規約が必ず踏襲される
* **Goal B（課題2）**：図表だけでなく、本文中の inline metrics（例：`98.5%`）が更新漏れしない（手入力を禁止）
* **Goal C**：各実験 run は「追試に必要な証拠」を自動保存（config解決済み・依存・ハード・git・コマンド等）

---

## 1. 技術選定（固定）

* Language: **Python 3.11+**
* Package manager: **uv**（`pyproject.toml` 管理）
* Config: **Hydra + OmegaConf**
* Pipeline DAG: **Snakemake**
* Lint/format: **ruff + black**
* Paper: **LaTeX**（`paper/auto/*.tex` を `\input` する）
* CI: **GitHub Actions**
* 実験ログ保存形式: **runs/** に run ディレクトリを作成し、スナップショットを保存

---

## 2. リポジトリ構成（生成する）

```
repo/
  pyproject.toml
  README.md
  Makefile
  Snakefile
  .github/workflows/ci.yml
  .github/copilot-instructions.md

  conf/
    base.yaml
    exp/
      example.yaml

  src/
    paperops/
      __init__.py
      cli.py
      runner.py
      snapshot.py
      registry.py
      utils.py
      checks/
        check_run_integrity.py
        check_paper_freshness.py
        check_no_manual_numbers.py
      experiments/
        __init__.py
        example_experiment.py
      analysis/
        aggregate.py
        figures.py

  paper/
    main.tex
    refs.bib
    auto/            # 生成物（git管理しない）
    figures/         # 生成物（git管理しない）
    tables/          # 生成物（git管理しない）

  runs/              # 実験成果（git管理しない）
  data/              # 任意（git管理しない or DVC）
```

### Git 管理方針

* `paper/auto`, `paper/figures`, `paper/tables`, `runs`, `data` は **.gitignore** 対象（ただし paper/auto の一部をコミットしたいなら方針変更可。v0では非コミット推奨）
* 代わりに **CIで再生成できる**のを前提にする

---

## 3. 重要な設計原則（絶対ルール）

### Rule 1: 実験の Single Source of Truth

* **共通設定は `conf/base.yaml`**
* **実験差分は `conf/exp/*.yaml`**
* 実験コード側は **Hydra で解決済み config を受け取るだけ**（ハードコード禁止）

### Rule 2: Run スナップショットの保存（再現性の中核）

各 run ディレクトリ `runs/<run_id>/` に必ず保存：

* `config_resolved.yaml`（base+override解決済み）
* `git_commit.txt`（dirty判定も保存）
* `command.txt`
* `env_freeze.txt`（`uv pip freeze` 相当）
* `hardware.json`（OS/CPU/RAM/GPU/CUDA/driver）
* `seeds.json`
* `metrics.json`（集計後の主要結果）
* `artifacts/`（生ログ・中間生成物）

### Rule 3: 本文中の数字は手入力禁止

* `paper/auto/variables.tex` を生成し、本文は `\input{auto/variables.tex}` のマクロ参照で書く
* 直書き数値（例：`0.123` や `98.5%`）は **checkで検知してCIで落とす（完全ではなく「危険域の検知」）**

### Rule 4: “古い auto” でビルドできない

* `paper/auto/MANIFEST.json` に「生成元データのハッシュ」を保存
* `make check` で元データと一致しない場合は失敗（更新漏れゼロ）

---

## 4. CLI 仕様（実装する）

### 4.1 `paperops run`

* Hydra config を読み込み、実験を実行し、run dir を作り、スナップショット保存し、metrics.json を出力
* 例：

```bash
uv run paperops run exp=example
```

### 4.2 `paperops build-paper-assets`

* `runs/` の最新または指定 run を入力に
* `paper/auto/variables.tex` と `paper/auto/MANIFEST.json`
* 図表（`paper/figures/*.pdf`）と表（`paper/tables/*.tex`）を生成

### 4.3 `paperops check`

* `check_run_integrity`（runsの必須ファイル揃っているか）
* `check_paper_freshness`（MANIFESTと元データ一致）
* `check_no_manual_numbers`（paper/main.tex の危険な直書き検知）

---

## 5. 設定スキーマ（Hydra）

### `conf/base.yaml`（例）

最低限このキーを持つ：

```yaml
project:
  name: paperops-template
  runs_dir: runs

runtime:
  device: cuda
  dtype: fp16
  deterministic: true
  seed: 1234

logging:
  save_code_snapshot: true
  save_env_snapshot: true
  save_hardware_snapshot: true

experiment:
  name: example
  output_subdir: "${now:%Y%m%d_%H%M%S}_${experiment.name}"
```

### `conf/exp/example.yaml`

```yaml
defaults:
  - override /base: base

experiment:
  name: example

example:
  n: 1000
```

---

## 6. 実験実装規約（BaseExperiment）

### `src/paperops/runner.py`

* `BaseExperiment` 抽象クラス

  * `setup(config, run_dir)`
  * `run() -> dict`（metrics dict）
  * `teardown()`

* Runner は必ず次を行う：

  1. run_dir作成
  2. snapshot保存（config/git/env/hardware/command/seeds）
  3. experiment.run 実行
  4. metrics.json 保存

### `src/paperops/experiments/example_experiment.py`

* 最小実験：乱数生成して平均などを metrics に保存するだけでOK

---

## 7. スナップショット収集（実装詳細）

### `src/paperops/snapshot.py`

関数を実装：

* `save_config_resolved(run_dir, cfg)`
* `save_git_status(run_dir)`
* `save_command(run_dir, argv)`
* `save_env_freeze(run_dir)`：`uv pip freeze` 相当を subprocess で
* `save_hardware_info(run_dir)`：

  * OS: `platform`, `uname`
  * CPU/RAM: `psutil`（依存追加）
  * GPU: `nvidia-smi --query-gpu=... --format=csv,noheader,nounits` があれば取得（無ければ空でOK）
  * CUDA: `torch.version.cuda` があれば保存（torchが無ければスキップ）
* `save_seeds(run_dir, seed_dict)`

---

## 8. Paper 自動生成物

### 8.1 `paper/auto/variables.tex`

* 例：

```tex
\newcommand{\BestAccuracy}{98.52\%}
\newcommand{\DatasetSize}{10000}
```

### 8.2 `paper/auto/MANIFEST.json`

* 例：

```json
{
  "source": {
    "runs_dir": "runs/...",
    "metrics_json_sha256": "..."
  },
  "generated": {
    "variables_tex_sha256": "...",
    "generated_at": "..."
  }
}
```

---

## 9. DAG（Snakemake）と Makefile

### 9.1 `Snakefile`

最低限ルール：

* `run_example`：`paperops run exp=example`
* `aggregate`：`paperops build-paper-assets`
* `paper`：LaTeXコンパイル（ローカルは `latexmk` があれば利用、無ければエラーでOK）
* `check`：`paperops check`

### 9.2 `Makefile`

* `make run` -> snakemake run_example
* `make assets` -> snakemake aggregate
* `make paper` -> snakemake paper
* `make check` -> snakemake check

---

## 10. CI（GitHub Actions）

### `.github/workflows/ci.yml`

* `uv` セットアップ
* `uv sync`
* `make run`
* `make assets`
* `make check`
* （オプション）LaTeX環境がある場合 `make paper`

※ v0は `make paper` を必須にしない（環境依存が重い）。ただし assets と check は必須。

---

## 11. Copilot/Codex ルール（強制）

`.github/copilot-instructions.md` を生成し、以下を明記：

* 新実験追加は **必ず `conf/exp/*.yaml` 追加**
* 実験コードは **BaseExperiment 継承**
* ハードコード禁止（device/seed/dtype/path など）
* 出力は **run_dir 配下のみ**
* metrics は dict で返し、runner が `metrics.json` に保存

---

## 12. チェック仕様（CIで落とす）

### 12.1 `check_run_integrity`

* runs配下の最新run（または指定run）に必須ファイルが揃っていること

### 12.2 `check_paper_freshness`

* `paper/auto/MANIFEST.json` の `metrics_json_sha256` と実データが一致すること
* 一致しないなら「assets再生成が必要」として失敗

### 12.3 `check_no_manual_numbers`

* `paper/main.tex` を走査して、危険な直書きパターンを検知したら失敗
  （例：`[0-9]+\.[0-9]+` や `%` 付き数値、ただし引用や年号など誤検知もあるので v0は「allowlist コメント」で抑制できる仕様にする）
* 仕様：`% paperops-allow-number` を行末に付けた数値は許可

---

## 13. 受け入れ条件（Definition of Done）

* `uv run paperops run exp=example` が動き、`runs/...` に snapshot が揃う
* `uv run paperops build-paper-assets` が `paper/auto/variables.tex` と `MANIFEST.json` を生成
* `uv run paperops check` が通る
* 故意に `paper/main.tex` に `98.5%` を直書きすると `check_no_manual_numbers` が落ちる
* 故意に metrics を更新して assets を再生成しないと `check_paper_freshness` が落ちる

---

# Codexへの実装依頼文（そのまま貼る）

以下を Codex に投入して実装させてください（コピペ可）：

```text
You are implementing the repository described in “PaperOps Template v0 — 実装仕様（Codex投入用）”.
Create all files and code. Use Python 3.11, uv, Hydra, Snakemake, ruff, black.

Implement:
- package src/paperops with cli.py providing commands: run, build-paper-assets, check
- BaseExperiment runner + registry
- snapshot saving (config/git/command/env_freeze/hardware/seeds)
- example experiment
- build-paper-assets to generate paper/auto/variables.tex and paper/auto/MANIFEST.json from runs metrics.json
- checks: run integrity, paper freshness with sha256, no-manual-numbers with allowlist comment
- Makefile, Snakefile, GitHub Actions CI, copilot-instructions.md
- Provide minimal paper/main.tex that inputs auto/variables.tex and uses at least one macro.

Ensure all commands run locally:
1) uv sync
2) uv run paperops run exp=example
3) uv run paperops build-paper-assets
4) uv run paperops check
```

---