# src/tools/csv_analyzer.py
 
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List
 
import math
import numpy as np
import pandas as pd
 
 
def sanitize_json(obj):
    """Converte NaN/inf e tipos numpy em valores JSON-safe (None, int, float)."""
    if obj is None:
        return None
 
    # numpy scalars (ex: np.float64, np.int64)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        x = float(obj)
        return x if math.isfinite(x) else None
 
    # floats normais
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
 
    # dict
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
 
    # listas/tuplos
    if isinstance(obj, (list, tuple)):
        return [sanitize_json(v) for v in obj]
 
    return obj
 
 
@dataclass
class CSVAnalysisResult:
    summary: Dict[str, Any]
    preview_rows: List[Dict[str, Any]]
    column_stats: Dict[str, Any]
 
 
def analyze_csv_bytes(csv_bytes: bytes, max_preview_rows: int = 10) -> CSVAnalysisResult:
    # Tentativas comuns de encoding
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            text = csv_bytes.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("Não consegui decodificar o CSV (tenta UTF-8).")
 
    # Lê CSV
    from io import StringIO
    df = pd.read_csv(StringIO(text))
 
    # Resumo
    summary = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "missing_values_total": int(df.isna().sum().sum()),
    }
 
    # Preview (amostra) - pode conter NaN
    preview = df.head(max_preview_rows).to_dict(orient="records")
 
    # Estatísticas simples por coluna
    column_stats: Dict[str, Any] = {}
    for col in df.columns:
        s = df[col]
        stats: Dict[str, Any] = {"dtype": str(s.dtype), "missing": int(s.isna().sum())}
 
        if pd.api.types.is_numeric_dtype(s):
            # min/max/mean podem dar NaN se a coluna tiver valores estranhos
            min_v = None if s.dropna().empty else s.min()
            max_v = None if s.dropna().empty else s.max()
            mean_v = None if s.dropna().empty else s.mean()
 
            stats.update(
                {
                    "min": sanitize_json(min_v),
                    "max": sanitize_json(max_v),
                    "mean": sanitize_json(mean_v),
                }
            )
        else:
            top = s.dropna().astype(str).value_counts().head(5)
            stats["top_values"] = [{"value": k, "count": int(v)} for k, v in top.items()]
 
        column_stats[col] = stats
 
    # ✅ Sanitizar tudo antes de devolver (resolve o erro do JSON/NaN)
    return CSVAnalysisResult(
        summary=sanitize_json(summary),
        preview_rows=sanitize_json(preview),
        column_stats=sanitize_json(column_stats),
    )
 