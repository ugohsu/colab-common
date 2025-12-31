# データベース入出力（SQLite / SQL 基礎）

このドキュメントでは、Google Colab 上で **RDBMS（リレーショナルデータベース）と SQL の基本概念**を理解しながら、 **SQLite を Python（pandas）から利用する方法**を紹介します。

- 行数・列数が多いデータを扱いたい
- 条件を指定して一部だけ取り出したい
- 中間結果を保存して再利用したい

といった場面を想定しています。

---

## 1. RDBMS と SQL の基礎

### RDBMS とは

RDBMS（Relational DataBase Management System）は、**表（テーブル）形式でデータを管理するデータベース**です。

- 行（row）：1件のデータ
- 列（column）：項目（変数）
- テーブル：同じ構造をもつデータの集合

Excel や Google スプレッドシートの 1 枚のシートを、より厳密に・効率よく扱える仕組みだと考えるとよいでしょう。

### SQL とは

SQL（Structured Query Language）は、 RDBMS に対して **データの取得・検索・集計**を指示するための言語です。

本資料では、まず次の操作を中心に扱います。

- `SELECT`：データを取り出す
- `WHERE`：条件を指定する

---

## 2. SQLite とは（なぜ使うのか）

SQLite は、**1つのファイルとして扱える軽量な RDBMS**です。

- サーバーが不要
- Python 標準ライブラリ（`sqlite3`）で利用可能
- Google Colab と相性がよい

小〜中規模のデータ分析では、  
「最初に学ぶデータベース」として非常に適しています。

---

## 3. SQLite データベースに接続する

Python では、`sqlite3` モジュールを使って SQLite を操作します。

```python
import sqlite3

# データベースに接続（存在しなければ作成される）
con = sqlite3.connect("nlp_data.db")
```

- `"nlp_data.db"` はデータベースファイル名です
- Colab の作業ディレクトリ（`/content`）に保存されます

> ※ Google Drive 上に SQLite ファイルを保存したい場合は、
> 事前に Google Drive をマウントする必要があります。
> マウント方法については、
> [`io_text_basic.md`](./io_text_basic.md) を参照してください。

---

## 4. pandas DataFrame を SQLite に保存する

分析途中で作成した DataFrame を、そのままデータベースに保存できます。

```python
df_tok.to_sql(
    "tokens",
    con,
    if_exists="replace",  # 既存テーブルがあれば上書き
    index=False
)
```

- `"tokens"`：テーブル名
- `if_exists="append"` にすると追記も可能です

---

## 5. SQL を使ってデータを読み込む

SQLite の強みは、**必要なデータだけを SQL で指定して取り出せること**です。

### 全件を読み込む

```python
import pandas as pd

df_all = pd.read_sql(
    "SELECT * FROM tokens",
    con
)
```

### 条件を指定して読み込む

```python
df_noun = pd.read_sql(
    "SELECT * FROM tokens WHERE pos = '名詞'",
    con
)
```

### テーブル一覧・カラム (列名) 一覧の参照

SQL文の記述に際してテーブル名やカラム名が使用されます。
それらを簡単に閲覧するために、本リポジトリでは、テーブル一覧・カラム一覧を参照する関数を用意しています。

```python
## ライブラリのインポート
from colab_common import describe_sqlite_tables

## 実行
describe_sqlite_tables(con)
```

---

## 6. Google Colab での DataFrame 表示を改善する

Colab では、`data_table` を有効化すると検索・ソート可能なテーブルとして表示できます。

```python
from google.colab import data_table
data_table.enable_dataframe_formatter()

display(df_all)
```

---

## 7. pandas と SQL を併用する意味

pandas だけでも多くの処理は可能ですが、

- データを一時保存したい
- 巨大なデータから一部だけ使いたい
- 条件指定・集計を簡潔に書きたい

といった場合、SQL を使うと処理が整理されます。

---

## 8. 接続を閉じる（重要）

作業が終わったら、必ず接続を閉じます。

```python
con.close()
```

### with 文の使用

`con.close()` の実行忘れがしばしば生じるので、このリポジトリでは、以下のように `with` 文を使って SQL に接続することを基本としましょう。

```python
with sqlite3.connect("nlp_data.db") as con:
    df = pd.read_sql("SELECT * FROM tokens", con)
```

## 9. まとめ

- SQLite は **Colab で最初に使うデータベースとして最適**
- pandas DataFrame と自然に連携できる
- SQL は「分析を助ける道具」として少しずつ覚えればよい

次のステップとしては、

- `GROUP BY`
- `ORDER BY`
- 複数テーブルの結合（JOIN）

などを段階的に学ぶと、より柔軟なデータ分析が可能になります。
