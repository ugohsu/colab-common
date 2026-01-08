# Google スプレッドシートの入出力

本ドキュメントでは、Google Colaboratory での Google スプレッドシートの読み込みについて説明します。その後、Google スプレッドシート入出力を支援するツールを導入します。

---

## 想定利用環境

- Google Colaboratory
- Google スプレッドシート
- Pandas を用いたデータ分析・前処理

---

## Google スプレッドシートの読み込み手順 (基本形)

本節で解説する手順はあくまで基本です。実際の運用においては、本リポジトリでは後述する `read_df_from_gsheet` の使用を推奨します。

### 1. 読み込み対象の指定

まずは読み込みの対象としたい Google スプレッドシートの URL とシート名を調べます。以下のように変数に代入しておくとよいでしょう。


```python
SHEET_URL = ""
SHEET_NAME = ""
```

- `SHEET_URL`  
    - 読み込みたい Google スプレッドシートの URL を指定します。対象スプレッドシートには **「閲覧可」以上の権限**が必要です。
    - (例) `SHEET_URL = "https://docs.google.com/spreadsheets/d/..."` のように記述します。
- `SHEET_NAME`  
    - スプレッドシート内の **ワークシート（タブ）の名前**を指定します。表示されているタブ名と完全一致している必要があります。
    - (例) `SHEET_NAME = "シート1"` のように記述します。

---

### 2. Google アカウント認証

```python
from google.colab import auth
auth.authenticate_user()
```

- Google Colab から Google Drive / Spreadsheet にアクセスするために必要な処理です。
- **Colab セッションごとに 1 回だけ実行**すれば十分です。
- 実行時に、ブラウザ上で Google アカウントへのログインが求められます。

---

### 3. ライブラリの import

```python
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe
from google.auth import default
```

- `gspread`  
  Google スプレッドシートを操作するためのライブラリ
- `gspread_dataframe.get_as_dataframe`  
  ワークシートの内容を Pandas DataFrame に変換するために使用します

※ Google Colab では、これらは **標準で利用可能**です (Google Colab の仕様変更などで必要が生じた場合は、別途 !pip install... してください)。

---

### 4. 認証情報の取得とクライアント作成

```python
creds, _ = default()
gc = gspread.authorize(creds)
```

- `google.auth.default()` により、Colab 環境に紐づいた認証情報を自動取得します。
- 取得した認証情報を使って、`gspread` のクライアントを作成します。

---

### 5. スプレッドシート → DataFrame

```python
worksheet = gc.open_by_url(SHEET_URL).worksheet(SHEET_NAME)
df = get_as_dataframe(worksheet, header=0)
```

- `open_by_url()`  
  URL を指定してスプレッドシート全体を開きます。
- `worksheet()`  
  その中から、指定したワークシート（タブ）を取得します。
- `get_as_dataframe()`  
  ワークシートの内容を Pandas DataFrame に変換します。

`header=0` は  
**「1 行目を列名として扱う」**ことを意味します。

---

### よくあるエラーと注意点

#### 権限エラーが出る場合

- スプレッドシートの共有設定を確認してください。
- **「閲覧可」以上の権限**が付与されていないと読み込めません。

#### シート名エラーが出る場合

- `SHEET_NAME` は **タブ名と完全一致**する必要があります。
- 全角・半角、スペースの違いにも注意してください。

---

## 認証を関数でまとめる（`get_gspread_client_colab`）

認証の手続きをひとつの関数にまとめました。以下のコードを実行することで、gspread 認証を一括でおこないます。

```python
## 本リポジトリで定義するライブラリのインポート
from colab_common import get_gspread_client_colab

## 認証手続き
gc = get_gspread_client_colab()
```

---

## Google スプレッドシートの読み込み

本リポジトリでは、Google スプレッドシートから pandas DataFrame を読み込む際に、`read_df_from_gsheet` の使用を推奨します。

この関数は、

- Colab 環境での認証を自動化
- 認証情報のキャッシュ
- Sheets 特有の空文字・列名問題への対処
- pandas 的な引数設計（usecols / nrows / parse_dates など）

をまとめて提供します。

### クイックスタート

```python
from colab_common import read_df_from_gsheet

df = read_df_from_gsheet(SHEET_URL)
```

### 主な引数

- `sheet_name`  
  読み込み対象のワークシート名（既定 `"シート1"`）

- `usecols`  
  読み込む列を指定します（列名または 0-based index）

- `nrows`  
  先頭から読み込む行数（デバッグ用途など）

- `parse_dates`  
  日付として読み込む列名のリスト

- `dtype`  
  列の型を明示的に指定します
  （指定した型に変換できない場合はエラーになります）

- `empty_as_na`  
  空文字 `""` を欠損値（NA）として扱います

- `evaluate_formulas`  
  - True（既定）：数式セルは「計算結果」を取得  
  - False：数式文字列（`=SUM(...)`）を取得
```

### 具体例

```python
df = read_df_from_gsheet(
    SHEET_URL,
    sheet_name="temporary",
    usecols=["doc_id", "date", "price"],
    dtype={"doc_id": "int64"},
    parse_dates=["date"],
    empty_as_na=True,
)
```

---

## Google スプレッドシートへの書き込み (`write_df_to_gsheet`)

pandas データフレーム形式のデータを Google スプレッドシートへ書き込みます。書き込みは考慮すべき事項が多いため、本リポジトリでは、`gspread_dataframe/set_with_dataframe` のラッパー関数である、`write_df_to_gsheet` を用意しています。

### クイックスタート

Google Colab 上では、`write_df_to_gsheet` を **そのまま呼ぶだけ**で Google スプレッドシートに書き込めます。

```python
from colab_common import write_df_to_gsheet

write_df_to_gsheet(df, SHEET_URL)
```

- `gc`（gspread client）は **省略可能**です  
  → Colab 前提で、自動的に認証・取得されます
- `sheet_name` を省略した場合は `"temporary"` が使われます
- `df` には `DataFrame` だけでなく  
  `value_counts()` などの **Series もそのまま渡せます**

---

### gc を明示的に使いたい場合（複数回書き込み）

同じノートブックで何度も書き込む場合は、 `gc` を一度だけ用意して使い回すほうが効率的です。

```python
from colab_common import get_gspread_client_colab, write_df_to_gsheet

gc = get_gspread_client_colab()

write_df_to_gsheet(
    df,
    SHEET_URL,
    gc=gc,
)
```

- `get_gspread_client_colab()` は内部でキャッシュされるため、
  何度呼んでも再認証は行われません

---

### sheet_name（書き込み先シート名）

```python
write_df_to_gsheet(
    df,
    SHEET_URL,
    sheet_name="result",
)
```

- `sheet_name` を省略すると `"temporary"` が使われます
- シートが存在しない場合は自動的に作成されます
- 既存シートがある場合は、既定で **上書き**されます

---

### Series（value_counts など）を書き込む場合

```python
pos_counts = df_tok["pos"].value_counts()

write_df_to_gsheet(
    pos_counts,
    SHEET_URL,
)
```

`write_df_to_gsheet` は内部で自動的に整形を行うため、

- `Series` → `DataFrame` への変換
- `reset_index()` の自動適用
- 列名の補完・重複解消
- MultiIndex のフラット化

などを **ユーザーが意識せずに**書き込めます。

