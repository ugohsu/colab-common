# ============================================================
# Google スプレッドシート I/O（書き込み）
# ------------------------------------------------------------
# - Google Colab 前提（認証済み gspread client を受け取る）
# - gspread_dataframe.set_with_dataframe を使用
# - 「とりあえず df を出力して確認したい」用途を強く意識
#
# 改善点（2025-12）
# - sheet_name を省略できる（既定 "temporary"）
# - Series / value_counts() 由来のオブジェクトでも「良しなに」書き込む
#   （reset_index し忘れ、列名なし、MultiIndex などを自動で整形）
# - gc を省略できる（Colab 前提で自動認証・キャッシュ）
# - gspread_dataframe を optional dependency 化（import 時に落ちないように修正）
# ============================================================

from __future__ import annotations

from typing import Any, Iterable, Union, Optional, Sequence, Set

import pandas as pd

# 【修正】トップレベルでの import を削除し、関数内で遅延インポートします
# from gspread_dataframe import set_with_dataframe


# モジュール内キャッシュ（Colab の認証・初期化を毎回走らせない）
_GC = None


def get_gspread_client_colab(*, force: bool = False):
    """
    Google Colab 前提で、認証済み gspread client (gc) を返します。

    - 初回のみ認証・初期化を行い、以降はモジュール内にキャッシュします
    - force=True の場合はキャッシュを無視して再初期化します

    Notes
    -----
    Colab 以外（ローカル Python 等）では動作しない想定です。
    """
    global _GC
    if _GC is not None and not force:
        return _GC

    # Colab 認証
    from google.colab import auth

    auth.authenticate_user()

    import gspread
    from google.auth import default

    creds, _ = default()
    _GC = gspread.authorize(creds)
    return _GC


def _make_unique(names: Iterable[str]) -> list[str]:
    """列名を重複なしに整形する（例: a, a -> a, a_2）"""
    seen: dict[str, int] = {}
    out: list[str] = []
    for n in names:
        base = str(n)
        if base not in seen:
            seen[base] = 1
            out.append(base)
        else:
            seen[base] += 1
            out.append(f"{base}_{seen[base]}")
    return out


def _flatten_columns(cols: Any) -> list[str]:
    """
    MultiIndex columns を 1段の文字列にする。
    例: ('a','b') -> 'a|b'
    """
    if isinstance(cols, pd.MultiIndex):
        flat: list[str] = []
        for tup in cols.to_list():
            parts = [str(x) for x in tup if x is not None and str(x) != ""]
            flat.append("|".join(parts) if parts else "")
        return flat
    return [str(c) if c is not None else "" for c in list(cols)]


def normalize_for_gsheet(
    obj: Union[pd.DataFrame, pd.Series],
    *,
    include_index: bool = False,
    index_name_default: str = "index",
) -> pd.DataFrame:
    """
    Google Sheets に書き込みやすい形に整形する。

    想定する「よくある困りごと」
    - value_counts() の結果（Series）をそのまま渡してしまう
    - reset_index() を忘れて index が情報を持っているのに列に出ない
    - columns が None / 空文字 / 重複 / MultiIndex
    """
    if isinstance(obj, pd.Series):
        # value_counts() など：Series -> DataFrame（列名が無い場合は count）
        name = obj.name if obj.name is not None and str(obj.name) != "" else "count"
        df = obj.to_frame(name=name)
    else:
        df = obj.copy()

    # index を列として残したい場合：
    # - include_index=True のときは set_with_dataframe 側で index を出すので reset_index はしない
    # - include_index=False でも、index が RangeIndex 以外なら情報が落ちるので reset_index する
    if not include_index:
        if not isinstance(df.index, pd.RangeIndex) or (df.index.name is not None):
            df = df.reset_index()
            if df.columns[0] in ("index", None, ""):
                df = df.rename(columns={df.columns[0]: index_name_default})

    # columns をフラット化 & 文字列化
    cols = _flatten_columns(df.columns)

    # 空列名は col_1, col_2... に置換
    fixed: list[str] = []
    for i, c in enumerate(cols, start=1):
        c2 = c.strip()
        fixed.append(c2 if c2 != "" else f"col_{i}")

    fixed = _make_unique(fixed)
    df.columns = fixed

    return df


def write_df_to_gsheet(
    df,
    sheet_url: str,
    *,
    gc: Any = None,
    sheet_name: str = "temporary",
    clear_sheet: bool = True,
    include_index: bool = False,
    normalize: bool = True,
) -> None:
    """
    Pandas DataFrame / Series を Google スプレッドシートに書き込む（上書き保存）。

    この関数は「とりあえず df の中身を確認したい」用途を強く意識しています。

    Parameters
    ----------
    df:
        書き込みたいデータ。DataFrame だけでなく Series（value_counts など）も可。
        Series の場合は内部で DataFrame に変換して書き込みます（normalize=True 既定）。
    sheet_url:
        書き込み先スプレッドシートの URL（書き込み権限が必要）。
    gc:
        認証済みの gspread クライアント。
        省略（None）の場合は、Colab 前提で自動的に認証して取得します（get_gspread_client_colab）。
    sheet_name:
        書き込み先のシート名。既定は "temporary"。
    clear_sheet:
        True の場合、書き込み前にシートを消去します（上書き用途向け）。
    include_index:
        True の場合、DataFrame の index をシートに含めます（set_with_dataframe の機能）。
    normalize:
        True の場合、Sheets に書き込みやすい形に自動整形します（推奨）。
    """
    
    # 【修正】依存ライブラリのチェックとインポートをここで行います
    try:
        from gspread_dataframe import set_with_dataframe
    except ImportError:
        raise ImportError(
            "gspread_dataframe がインストールされていません。\n"
            "Google Colab では次を実行してください:\n"
            "  !pip install gspread-dataframe"
        )

    if gc is None:
        gc = get_gspread_client_colab()

    # 1) Open spreadsheet
    sh = gc.open_by_url(sheet_url)

    # 2) Worksheet を取得（無ければ作る）
    try:
        ws = sh.worksheet(sheet_name)
    except Exception:
        ws = sh.add_worksheet(title=sheet_name, rows=100, cols=26)

    # 3) シート消去（必要なら）
    if clear_sheet:
        ws.clear()

    # 4) DataFrame 整形（必要なら）
    df_out = normalize_for_gsheet(df, include_index=include_index) if normalize else (
        df.to_frame(name=(df.name or "count")) if isinstance(df, pd.Series) else df
    )

    # 5) 書き込み
    set_with_dataframe(
        ws,
        df_out,
        include_index=include_index,
        include_column_header=True,
        resize=True,
    )

    print("✅ DataFrame written to Google Sheets:", sheet_url, "/", sheet_name)

def _clean_columns_for_read(cols: Sequence[Any]) -> list[str]:
    """読み込み時の列名を整形（空・重複・前後空白など）"""
    cols2 = []
    for i, c in enumerate(cols, start=1):
        s = "" if c is None else str(c)
        s = s.strip()
        cols2.append(s if s != "" else f"col_{i}")
    # 重複を a, a_2... にする（write 側と同じ規約）
    return _make_unique(cols2)


def read_df_from_gsheet(
    sheet_url: str,
    *,
    gc: Any = None,
    sheet_name: str = "シート1",
    header: Union[int, None] = 0,
    usecols: Optional[Sequence[Union[int, str]]] = None,
    nrows: Optional[int] = None,
    dtype: Optional[dict[str, Any]] = None,
    parse_dates: Optional[Union[Sequence[str], bool]] = None,
    keep_default_na: bool = True,
    na_values: Optional[Sequence[str]] = None,
    evaluate_formulas: bool = True,
    empty_as_na: bool = True,
) -> pd.DataFrame:
    """
    Google Sheets -> pandas DataFrame（Colab 認証を自動化・キャッシュ可能）

    Parameters
    ----------
    sheet_url:
        読み込み元スプレッドシートURL
    gc:
        認証済み gspread client。None なら Colab 認証してキャッシュ（write と同様）
    sheet_name:
        ワークシート名（既定 "シート1"）
    header:
        0: 先頭行をヘッダとして扱う / None: ヘッダなしで連番列名
    usecols:
        取りたい列（列名 or 0-based の列番号）。None なら全列
    nrows:
        先頭から読む行数（ヘッダ行を除くデータ行に対して適用）
    dtype, parse_dates, keep_default_na, na_values:
        pandas 側での型変換・欠損処理
    evaluate_formulas:
        True: 数式セルは「計算結果」を取得（既定）
        False: 数式文字列（"=SUM(...)"）を取得
    empty_as_na:
        True: ""（空文字）を NA 扱いに寄せる（用途により有効）
    """
    if gc is None:
        gc = get_gspread_client_colab()

    # ここを追加（任意）
    try:
        import gspread  # noqa: F401
    except ImportError:
        raise ImportError(
            "gspread がインストールされていません。\n"
            "Google Colab では次を実行してください:\n"
            "  !pip install gspread"
        )

    sh = gc.open_by_url(sheet_url)
    ws = sh.worksheet(sheet_name)

    # gspread: get_all_values() は「表示値(文字列)」寄り。
    # value_render_option を使うと数式 or 計算結果を制御可能。
    value_render_option = "FORMATTED_VALUE" if evaluate_formulas else "FORMULA"
    rows = ws.get_all_values(value_render_option=value_render_option)

    if not rows:
        return pd.DataFrame()

    if header is None:
        data_rows = rows
        columns = [f"col_{i}" for i in range(1, (len(rows[0]) if rows else 0) + 1)]
    else:
        if header != 0:
            # 必要になったら拡張（今は write 側と合わせて 0 前提を強く推奨）
            raise ValueError("現在 header は 0 または None のみ対応です。")
        columns = _clean_columns_for_read(rows[0])
        data_rows = rows[1:]

    if nrows is not None:
        data_rows = data_rows[:nrows]

    df = pd.DataFrame(data_rows, columns=columns)

    # usecols（列名 or インデックス）
    if usecols is not None:
        if all(isinstance(c, int) for c in usecols):
            df = df.iloc[:, list(usecols)]
        else:
            df = df.loc[:, list(usecols)]

    # 空文字を NA 寄せしたい場合
    if empty_as_na:
        df = df.replace("", pd.NA)

    # na_values の反映（pandas 的に寄せる）
    if na_values is not None:
        df = df.replace(list(na_values), pd.NA)

    # 型変換（必要な列だけ確実に）
    if dtype:
        df = df.astype(dtype, errors="raise")

    # 日付パース（必要な列だけ）
    if parse_dates:
        if parse_dates is True:
            # 自動推定は誤爆しやすいので、基本は列名指定推奨
            pass
        else:
            for c in parse_dates:
                if c in df.columns:
                    df[c] = pd.to_datetime(df[c], errors="coerce")

    # keep_default_na は read_csv 的な概念なので、ここでは直接は使いにくい
    # （必要なら empty_as_na / na_values 側で制御するのが安全）
    _ = keep_default_na

    return df

def _to_num_safe(x):
    """
    安全に数値変換を試みる。
    - 変換できれば float を返す
    - できなければ元の値をそのまま返す
    """
    if x is None:
        return x

    s = str(x).strip()
    if s == "":
        return x

    # よくある表記ゆれ（汎用）
    s = s.replace(",", "")
    s = s.replace("▲", "-")
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]

    try:
        return float(s)
    except Exception:
        return x

def cast_numeric_schema(
    df: pd.DataFrame,
    *,
    exclude_cols: Iterable[str] | None = None,
    int_cols: Iterable[str] | None = None,
    date_cols: Iterable[str] | None = None,
    strict: bool = False,
) -> pd.DataFrame:
    """
    多くの列が数値であることを想定し、
    変換可能な列を自動的に数値型へ変換する。

    - 数値変換は try ベースで安全に実施
    - 変換に失敗した値があっても、既定では列を壊さない
    - 数値化できない列は object のまま残る

    Parameters
    ----------
    df : pd.DataFrame
        読み込み直後の DataFrame（多くは object 型）
    exclude_cols : iterable of str, optional
        数値変換を試みない列（ID、名称、カテゴリなど）
    int_cols : iterable of str, optional
        整数として扱いたい列（year, period など）
    date_cols : iterable of str, optional
        日付として変換する列
    strict : bool, default False
        True の場合、数値変換に失敗した値がある列で例外を投げる

    Returns
    -------
    pd.DataFrame
        数値中心のスキーマに変換された DataFrame
    """
    df = df.copy()

    exclude_cols: Set[str] = set(exclude_cols or [])
    int_cols: Set[str] = set(int_cols or [])
    date_cols: Set[str] = set(date_cols or [])

    # --- 自動数値変換 ---
    for col in df.columns:
        if col in exclude_cols or col in int_cols or col in date_cols:
            continue

        converted = df[col].map(_to_num_safe)

        # 少なくとも1つ float に変換できたら「数値列候補」
        has_numeric = converted.map(lambda x: isinstance(x, float)).any()

        if not has_numeric:
            continue

        if strict:
            bad = converted.map(
                lambda x: isinstance(x, float) or pd.isna(x)
            )
            if not bad.all():
                raise ValueError(
                    f"数値変換できない値があります: column='{col}'"
                )

        df[col] = converted

    # --- 整数列 ---
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # --- 日付列 ---
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df
