# ローカル環境構築ガイド

本リポジトリ（`colab-common`）および関連ライブラリ（`colab-nlp`）は、基本的に Google Colaboratory で動作させることを前提としています。

ただし、大規模なデータを扱う場合や、オフラインでの作業が必要な場合のために、**ローカル環境（Linux / WSL）** での環境構築手順を以下にまとめます。

> **対象者**: コマンドライン操作（ターミナル）に慣れている方
> **Windows ユーザーの方**: 本書末尾の **【付録：Windows ユーザー向け設定】** を先に参照し、WSL (Debian) 環境を用意してください。

---

## 1. 必要なツールのインストール

まず、Python 環境構築に必要な最小限のツールをインストールします。

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git

```

---

## 2. ディレクトリ構成の設計（重要）

ローカル環境では、**「分析ファイル（自分が書くコード）」** と **「環境（ライブラリ本体）」** の場所を分けることを推奨します。
これにより、分析ファイルだけを Dropbox や Google Drive で同期し、重たいライブラリや環境設定はローカルに留めることができます。

### 推奨ディレクトリ構成 (Tree)

以下のような構成を目指します。

```text
~ (ホームディレクトリ)
├── venvs/                  # 仮想環境置き場（同期しない）
│   └── nlp-env/            # ★今回作成する仮想環境
│
├── colab-utils/            # ライブラリ置き場（同期しない）
│   ├── colab-common/       # git clone したもの
│   └── colab-nlp/          # git clone したもの
│
└── Dropbox/                # クラウド同期フォルダ
    └── my_analysis/        # ★実際の分析作業場所
        ├── analysis.py     # 自分で書くスクリプト
        └── requirements.txt # ★ライブラリのリスト

```

* **`~/venvs`**: Python 仮想環境をまとめて置く場所です。
* **`~/colab-utils`**: 本リポジトリなどを clone しておく場所です。
* **`~/Dropbox/my_analysis`**: 実際にコードを書く場所です。ここだけをクラウド同期します。

---

## 3. 環境構築の手順

### 3-1. 仮想環境の作成

ホームディレクトリ直下に仮想環境用のフォルダを作り、プロジェクトごとの環境をそこに作成します。

```bash
# 仮想環境置き場を作成
mkdir -p ~/venvs

# 'nlp-env' という名前で仮想環境を作成
python3 -m venv ~/venvs/nlp-env

# 仮想環境の有効化 (Activate)
source ~/venvs/nlp-env/bin/activate

```

> **Point**: ターミナルの先頭に `(nlp-env)` と表示されていれば OK です。

### 3-2. ライブラリの配置とインストール

ライブラリ（リポジトリ）は、分析ディレクトリとは別の場所（`~/colab-utils`）に clone します。

```bash
# ライブラリ置き場を作成して移動
mkdir -p ~/colab-utils
cd ~/colab-utils

# 1. 共通ユーティリティ (colab-common) の clone
git clone https://github.com/ugohsu/colab-common.git

# 2. 自然言語処理ライブラリ (colab-nlp) の clone
#    ※ NLPを行わない場合は省略可能です
git clone https://github.com/ugohsu/colab-nlp.git

```

続いて、必要な Python パッケージをインストールします。

```bash
# 必須ライブラリ
pip install pandas matplotlib scikit-learn

# 自然言語処理用 (colab-nlp 利用時)
pip install sudachipy sudachidict_core

```

### 3-3. パスの設定（自動読み込み）

ダウンロードしたライブラリ（`~/colab-utils` 配下）を Python が自動的に認識できるように設定します。
作業の前に、以下の2つの準備を行ってください。

1. **仮想環境の有効化**:
必ず仮想環境（`nlp-env` 等）を activate した状態で作業してください。
```bash
source ~/venvs/nlp-env/bin/activate

```

2. **シンボリックリンクの作成**:
仮想環境の中からライブラリを参照できるように、リンクを作成します。
```bash
# 仮想環境のルートに 'colab-utils' へのリンクを作成
ln -s ~/colab-utils $VIRTUAL_ENV/colab-utils

```


**設定コマンドの実行**
準備ができたら、以下のコマンドをコピーし、ターミナルで実行してください。
Python の検索パス設定ファイル（`.pth`）を自動作成します。

```bash
# 1. site-packages の場所を自動取得
SITE_PKG=$(python3 -c "import site; print(site.getsitepackages()[0])")

# 2. パス設定ファイルを作成
#    ($VIRTUAL_ENV を使い、仮想環境からの相対位置でリンクします)
echo "$VIRTUAL_ENV/colab-utils/colab-common" > "$SITE_PKG/local_dev_links.pth"

# (オプション) 新しいリポジトリを追加する場合は以下のように追記します
# echo "$VIRTUAL_ENV/colab-utils/new-repository" >> "$SITE_PKG/local_dev_links.pth"

# 完了メッセージ
echo "設定完了: $SITE_PKG/local_dev_links.pth"

```

この設定を行うことで、以降は `sys.path.append` などを書かずに直接 `import` できるようになります。

**確認方法**
エラーが出なければ設定完了です。以下のコマンドでインポートできるか試してみましょう。

```bash
python3 -c "import colab_common; print('Setup OK!')"

```


### 3-4. パッケージ情報の保存と復元 (`requirements.txt`)

インストールしたライブラリの種類とバージョンを記録（フリーズ）しておくと、別の PC や将来の自分が同じ環境を再現できます。

**現状の保存**
環境構築が一通り終わったら、分析ディレクトリ（例: `~/Dropbox/my_analysis`）に移動し、リストを作成します。

```bash
cd ~/Dropbox/my_analysis
pip freeze > requirements.txt

```

**環境の復元**
別の環境で作業する際は、以下のコマンドで同じライブラリを一括インストールできます。

```bash
pip install -r requirements.txt

```

### 3-5. ライブラリの更新 (Maintenance)

ライブラリは日々更新されます。時々以下の手順で最新版にアップデートすることを推奨します。

1. **更新の確認**:
```bash
pip list --outdated

```


2. **更新の実行**:
* **個別更新**: `pip install --upgrade パッケージ名`
* **一括更新**: `pip-review` ツールを使うと便利です。
```bash
pip install pip-review
pip-review --local --interactive

```




3. **リストの更新**:
更新後は必ず `requirements.txt` を書き換えてください。
```bash
pip freeze > requirements.txt

```



---

## 4. 分析スクリプトからの読み込み

前項（3-3）の設定が完了していれば、`sys.path.append` に関する特別なコードを書く必要はありません。
通常のライブラリと同様にインポートして使用できます。

```python
import sys
import os

# 3-3 の設定を行っていない場合のみ、以下のパス設定が必要です
# utils_dir = os.path.expanduser("~/colab-utils")
# sys.path.append(os.path.join(utils_dir, "colab-common"))
# sys.path.append(os.path.join(utils_dir, "colab-nlp"))

# インポート確認
from colab_common import describe_sqlite_tables
from colab_nlp import tokenize_df

print("Import successful!")

```

> **Note**: `colab_common` は安全に設計されており、インポートしただけでは `google.colab` 固有の処理（認証など）は走りません。ローカル環境でもエラーなく読み込めます。

---

## 5. ローカル利用時の注意点

Colab 用のコードには、ローカル環境では動作しない機能が一部あります。

1. **Google Drive マウント**: `drive.mount()` は動きません。ローカルのパスを直接指定してください。
2. **Google 認証**: `get_gspread_client_colab()` は Colab 独自の認証機能を使っているため、ローカルでは動作しません。スプレッドシートを操作する場合は、GCP サービスアカウントキー等を使った認証コードに書き換える必要があります。
3. **日本語フォント**: Colab 用のフォントパス（`/usr/share/fonts/...`）は存在しない場合があります。`sudo apt install fonts-noto-cjk` 等でフォントを入れ、正しいパスを指定してください。

---

# 【付録：Windows ユーザー向け設定】

Windows で開発を行う場合は、**WSL (Windows Subsystem for Linux)** を使用して Linux 環境 (Debian) を構築することを強く推奨します。

## A-1. WSL (Debian) のインストール

PowerShell を「管理者として実行」し、以下のコマンドを入力してください。

```powershell
wsl --install -d Debian

```

インストール完了後、再起動してユーザー名・パスワードを設定したら、本ガイドの **「1. 必要なツールのインストール」** から作業を開始してください。

---

# 【付録：大規模データ処理の最適化】

`colab-nlp` の `CorpusDB` を使用して大規模なテキストデータを処理する場合、ファイルの配置場所がパフォーマンスに大きく影響します。

Windows + WSL 環境では、以下の **ハイブリッド配置** を推奨します。

1. **データベース (`corpus.db`)** → **WSL 側に置く** (例: `~/venvs/my-db/corpus.db`)
* 高速かつ安全に書き込みを行うため、必ず WSL 領域内に置いてください。


2. **元テキストデータ (`*.txt`)** → **Windows 側に置いたままでOK**
* Windows 側のフォルダ（`/mnt/c/...`）を直接参照することで、ディスク容量を節約できます。



```python
from colab_nlp import CorpusDB

# DBは WSL 側に作成 (高速)
db = CorpusDB("corpus.db")

# データは Windows 側を参照 (容量節約)
root_dir = "/mnt/c/Users/YourName/Documents/nlp_data"

db.register_files(root_dir)

```
