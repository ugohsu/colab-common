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

| 関数名 | 内容 | 実装ファイル | 解説ドキュメント |
|---|---|---|---|
| `get_gspread_client_colab` | gspread クライアント取得 | [`colab_common/gsheet_io.py`](./colab_common/gsheet_io.py) | [`docs/gsheet_io.md`](./docs/gsheet_io.md) |
| `write_df_to_gsheet` | スプレッドシートへの書き込み | [`colab_common/gsheet_io.py`](./colab_common/gsheet_io.py) | [`docs/gsheet_io.md`](./docs/gsheet_io.md) |
| `describe_sqlite_tables` | sqlite テーブルおよび列名一覧の取得 | [`colab_common/io_sql_utils.py`](./colab_common/io_sql_utils.py) | [`docs/io_sql_basic.md`](./docs/io_sql_basic.md) |

### ドキュメント一覧

|内容|解説ドキュメント|
|---|---|
|基本的なテキスト読み込み方法|[`docs/io_text_basic.md`](./docs/io_text_basic.md)|
|Google スプレッドシートの読み書き|[`docs/gsheet_io.md`](./docs/gsheet_io.md)|
|SQLite の導入|[`docs/io_sql_basic.md`](./docs/io_sql_basic.md)|
|よく使う SQL 文|[`docs/io_sql_guide.md`](./docs/io_sql_guide.md)|
|作図時の日本語表記|[`docs/matplotlib_japanese_font.md`](./docs/matplotlib_japanese_font.md)|

---

## ライブラリインポートの手順

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

## ライセンス・利用について

- 教育・研究目的での利用を想定しています
- 講義資料・演習ノートへの組み込みも自由です
