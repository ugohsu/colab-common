# SQL ガイド（SQLite / SQL 実践編）

本ドキュメントは、[`io_sql_basic.md`](./io_sql_basic.md) で紹介した SQLite / SQL の基礎を前提に、  
**SQL を「道具として使う」ための主要構文を体系的に整理したガイド**です。

ここでは、Google Colaboratory + SQLite 環境を想定し、
データ分析や前処理で頻出する SQL 構文を中心にまとめます。

---

## 1. SELECT 文の基本

### 1.1 全列の取得（基本形）

```sql
SELECT * FROM Students;
```

テーブルのすべての列・行を取得します。

---

### 1.2 射影（必要な列だけ取得）

```sql
SELECT id, height, birthday FROM Students;
```

---

### 1.3 選択（条件指定）

```sql
SELECT * FROM Attendances WHERE class = '04';
```

---

### 1.4 列名の変更（AS）

```sql
SELECT studentid AS id FROM Attendances;
```

---

### 1.5 射影 + 選択

```sql
SELECT name, gender, birthday
FROM Students
WHERE gender = 'm';
```

---

## 2. パターンマッチ（LIKE）

```sql
SELECT * FROM Students
WHERE name LIKE '%moto%';
```

---

## 3. 並び替え（ORDER BY）

```sql
SELECT * FROM Students ORDER BY id ASC;
SELECT * FROM Students ORDER BY id DESC;
```

---

## 4. 集計（GROUP BY）

```sql
SELECT
    month(birthday) AS birth_month,
    COUNT(id) AS n_students
FROM Students
GROUP BY month(birthday);
```

---

## 5. 重複の除去（DISTINCT）

```sql
SELECT DISTINCT name FROM Students;
```

---

## 6. 行数制限（LIMIT）

```sql
SELECT * FROM Tweets LIMIT 20;
```

---

## 7. テーブル結合（JOIN）

### 7.1 内部結合（INNER JOIN）

```sql
SELECT *
FROM Students
INNER JOIN Attendances
ON Students.id = Attendances.studentid;
```

---

### 7.2 左外部結合（LEFT JOIN）

```sql
SELECT *
FROM Students
LEFT JOIN Attendances
ON Students.id = Attendances.studentid;
```

---

### 7.3 複数テーブルの結合

```sql
SELECT *
FROM Students
INNER JOIN Student_Groups
    ON Students.id = Student_Groups.studentid
INNER JOIN Groups
    ON Student_Groups.groupid = Groups.id;
```

---

### 7.4 サブクエリを用いた結合

```sql
SELECT *
FROM Students
LEFT JOIN (
    SELECT *
    FROM Attendances
    WHERE class = '05'
) AS X
ON Students.id = X.studentid;
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
    gender,
    AVG(height) AS avg_height
FROM Students
GROUP BY gender;
```

---

## 9. pandas との併用（再掲）

```python
df = pd.read_sql(
    "SELECT * FROM Students WHERE gender = 'm'",
    con
)
```

---

## 10. まとめ

- SQL は **データを取り出すための道具**
- 全構文を覚える必要はない
- SELECT / WHERE / GROUP BY / JOIN を使えれば十分

必要になったときに、本ドキュメントを **辞書的に参照**してください。
