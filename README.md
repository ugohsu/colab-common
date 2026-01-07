# Colab Common Utilities

このリポジトリは、**Google Colaboratory 上で Python を利用する際の共通基盤となるテンプレート・関数群**をまとめたリポジトリです。

ゼミ・演習・研究用途で頻繁に発生する、

- Google Sheets との I/O
- Colab 固有の実行環境を前提とした初期設定

といった処理について、

- **そのまま貼り付けて使うテンプレート**
- **import して使う最小限の共通関数**

を明確に分離して整理しています。

本リポジトリは、教材用ノートブックや他の教材リポジトリから参照される **Colab 用の共通ユーティリティ集**として利用されることを想定しています。

---

## 基本方針 (各ディレクトリの役割)

### templates（貼り付けて使う）

- Google Colab の **コードセルにそのままコピー＆ペースト**
- **一言一句変更せずに使うことを前提**
- import はしない
- 認証・初期設定・環境依存処理向け

### colab_common（import して使う）

- リポジトリを clone した後、**import して使用**
- ノートブック側のコードを簡潔に保つための共通関数群

### docs

- 各テンプレート・関数・分析手法の 背景・理由・注意点

---

## テンプレートおよび関数の一覧

### テンプレート一覧（貼り付けて使う）

| 内容 | テンプレート | 解説ドキュメント |
|---|---|---|
| matplotlib 日本語表示設定 | [`templates/matplotlib_japanese_font.py`](./templates/matplotlib_japanese_font.py) | [`docs/matplotlib_japanese_font.md`](./docs/matplotlib_japanese_font.md) |

> ※ templates 内のコードは **一言一句変更せず、そのままコピー＆ペーストして使用してください。**
> import して使うことは想定していません。

---

### 関数一覧（import して使う）

| 分類 | 関数名 | 内容 | 実装ファイル | 解説ドキュメント |
| :--- | :--- | :--- | :--- | :--- |
| **Google Sheets** | `get_gspread_client_colab` | gspread クライアント取得 | [`colab_common/gsheet_io.py`](./colab_common/gsheet_io.py) | [`docs/gsheet_io.md`](./docs/gsheet_io.md) |
| **Google Sheets** | `write_df_to_gsheet` | スプレッドシートへの書き込み | [`colab_common/gsheet_io.py`](./colab_common/gsheet_io.py) | [`docs/gsheet_io.md`](./docs/gsheet_io.md) |
| **SQLite** | `describe_sqlite_tables` | sqlite テーブルおよび列名一覧の取得 | [`colab_common/io_sql_utils.py`](./colab_common/io_sql_utils.py) | [`docs/io_sql_basic.md`](./docs/io_sql_basic.md) |

---

### ドキュメント一覧

| 分類 | 内容 | 解説ドキュメント |
| :--- | :--- | :--- |
| **Text I/O** | テキストファイルの読み込み (標準ライブラリ) | [`docs/io_text_basic.md`](./docs/io_text_basic.md) |
| **Google Sheets** | Google スプレッドシートの読み書き | [`docs/gsheet_io.md`](./docs/gsheet_io.md) |
| **SQLite** | SQLite の接続・保存・読込 (基本) | [`docs/io_sql_basic.md`](./docs/io_sql_basic.md) |
| **SQLite** | SQLite / SQL クイックガイド (実践) | [`docs/io_sql_guide.md`](./docs/io_sql_guide.md) |
| **Visualization** | 作図時の日本語表記 (Matplotlib) | [`docs/matplotlib_japanese_font.md`](./docs/matplotlib_japanese_font.md) |
| **Environment** | ローカル環境構築ガイド (WSL/Linux) | [`docs/local_setup_guide.md`](./docs/local_setup_guide.md) |

---

## ライブラリインポートの手順 (Google Colab)

### 1. リポジトリを clone

```python
!git clone https://github.com/ugohsu/colab-common.git

```

### 2. import 用のパスを追加

```python
import sys
sys.path.append("/content/colab-common")

```

### 3. 関数を import (例)

```python
from colab_common import write_df_to_gsheet

```

---

### 注意（Google Colab での git clone）

同一ノートブック内で `git clone` を **2 回以上実行しないでください**。

```
fatal: destination path 'colab-common' already exists

```

というエラーが発生し、そのセルでは、当該行以降のコードが実行されなくなります。

---

## ローカル環境での利用について (Advanced)

本ライブラリは基本的に Google Colaboratory での動作を前提としていますが、大規模データ処理などの目的で **ローカル環境 (WSL/Linux)** で利用することも可能です。

推奨されるディレクトリ構成や環境構築の手順については、以下のガイドを参照してください。

* **[ローカル環境構築ガイド](https://www.google.com/search?q=./docs/local_setup_guide.md)**

---

## ライセンス・利用について

* 教育・研究目的での利用を想定しています
* 講義資料・演習ノートへの組み込みも自由です
