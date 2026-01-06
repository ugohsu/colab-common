# SQL ガイド（SQLite / SQL 実践編）

本ドキュメントは、[`io_sql_basic.md`](./io_sql_basic.md) で紹介した SQLite / SQL の基礎を前提に、  
**SQL を「道具として使う」ための主要構文を体系的に整理したガイド**です。

ここでは、Google Colaboratory + SQLite 環境を想定し、
データ分析や前処理で頻出する SQL 構文を中心にまとめます。

> **例コードの前提（本プロジェクトの想定テーブル）**
>
> - `documents`：文書メタ情報（例：`doc_id`, `title`, `path`）
> - `tokens`：形態素解析結果（例：`doc_id`, `token_id`, `token`, `pos`）
> - `doc_topics`：文書×トピックの結果（例：`doc_id`, `topic_id`, `weight`）
>
> ※ 実際の列名は環境によって異なるので、手元の DB スキーマに合わせて読み替えてください。

---

## 1. SELECT 文の基本

### 1.1 全列の取得（基本形）

```sql
SELECT * FROM tokens;
```

テーブルのすべての列・行を取得します。

---

### 1.2 射影（必要な列だけ取得）

```sql
SELECT doc_id, token, pos FROM tokens;
```

---

### 1.3 選択（条件指定）

```sql
SELECT * FROM tokens
WHERE pos = '名詞';
```

---

### 1.4 列名の変更（AS）

```sql
SELECT doc_id AS id FROM tokens;
```

---

### 1.5 射影 + 選択

```sql
SELECT doc_id, token
FROM tokens
WHERE pos = '名詞';
```

---

## 2. パターンマッチ（LIKE）

```sql
SELECT *
FROM tokens
WHERE token LIKE '%本%';
```

---

## 3. 並び替え（ORDER BY）

> **⚠️ 重要：SQL の順序に関する大原則**
>
> SQL では `ORDER BY` を指定しない限り、**結果の順序は保証されません。**
> 「保存した順に出るだろう」と思っていても、データの追加・削除や処理タイミングによって、**ある日突然バラバラの順序で返ってくる**ことがあります。
>
> **N-gram や時系列データなど、「順序」が重要な分析では、必ず ORDER BY を記述してください。**

### 3.1 基本的なソート

```sql
SELECT * FROM tokens ORDER BY doc_id ASC;   -- 昇順（小さい順）
SELECT * FROM tokens ORDER BY doc_id DESC;  -- 降順（大きい順）

```

### 3.2 【必須】元の文脈を復元するソート

文章としての「語順」を正しく取り出したい場合は、必ず **`doc_id` と `token_id` の両方**を指定してソートしてください。

```sql
SELECT * FROM tokens
WHERE pos IN ('名詞', '動詞')
ORDER BY doc_id, token_id;
```

1. まず `doc_id` 順に並べ、
2. 同じ文書の中では `token_id`（通し番号）順に並べます。

これを行わないと、`compute_ngram` などに渡したときに「前の文書の末尾」と「次の文書の途中」が混ざったり、文中の単語が前後したりして、分析結果が破壊されます。

---

## 4. 集計（GROUP BY）

```sql
SELECT
    pos,
    COUNT(*) AS n_tokens
FROM tokens
GROUP BY pos
ORDER BY n_tokens DESC;
```

---

## 5. 重複の除去（DISTINCT）

```sql
SELECT DISTINCT token FROM tokens;
```

---

## 6. 行数制限（LIMIT）

```sql
SELECT * FROM tokens LIMIT 20;
```

---

## 7. テーブル結合（JOIN）

### 7.1 内部結合（INNER JOIN）

`documents` と `tokens` を `doc_id` で結合して、文書タイトル付きでトークンを確認します。

```sql
SELECT
    d.doc_id,
    d.title,
    t.token,
    t.pos
FROM documents AS d
INNER JOIN tokens AS t
ON d.doc_id = t.doc_id;
```

---

### 7.2 左外部結合（LEFT JOIN）

`documents` を基準にして、トークンが存在しない文書も含めて取得します。

```sql
SELECT
    d.doc_id,
    d.title,
    t.token,
    t.pos
FROM documents AS d
LEFT JOIN tokens AS t
ON d.doc_id = t.doc_id;
```

---

### 7.3 複数テーブルの結合

`documents`（文書）× `doc_topics`（文書トピック）× `tokens`（トークン）を結合する例です。  
（分析の目的に応じて、実際には JOIN するテーブルは取捨選択してください。）

```sql
SELECT
    d.doc_id,
    d.title,
    dt.topic_id,
    dt.weight,
    t.token,
    t.pos
FROM documents AS d
INNER JOIN doc_topics AS dt
    ON d.doc_id = dt.doc_id
INNER JOIN tokens AS t
    ON d.doc_id = t.doc_id;
```

---

### 7.4 サブクエリを用いた結合

「名詞のみ」に絞った `tokens` をサブクエリにして結合します。  
（X は任意の別名です）

```sql
SELECT
    d.doc_id,
    d.title,
    X.token,
    X.pos
FROM documents AS d
LEFT JOIN (
    SELECT *
    FROM tokens
    WHERE pos = '名詞'
) AS X
ON d.doc_id = X.doc_id;
```

---

## 8. よく使う演算子・関数

### 8.1 比較演算子

- `=` 等しい
- `!=` 等しくない
- `<`, `<=`, `>`, `>=`

---

### 8.2 論理演算子

- `AND`
- `OR`
- `NOT`

---

### 8.3 集計関数

```sql
SELECT
    pos,
    AVG(LENGTH(token)) AS avg_token_len
FROM tokens
GROUP BY pos
ORDER BY avg_token_len DESC;
```

- `COUNT`
- `SUM`
- `AVG`
- `MIN`
- `MAX`

---

## 9. pandas との併用（再掲）

```python
df = pd.read_sql(
    "SELECT doc_id, token FROM tokens WHERE pos = '名詞'",
    con
)
```

---

## 10. まとめ

- SQL は **データを取り出すための道具**
- 全構文を覚える必要はない
- SELECT / WHERE / GROUP BY / JOIN を使えれば十分

必要になったときに、本ドキュメントを **辞書的に参照**してください。
