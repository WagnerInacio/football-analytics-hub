import pandas as pd
from typing import List, Dict, Any

_DIAS_PT = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
_MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def build(fixtures_raw: List[Dict[str, Any]]) -> pd.DataFrame:
    """Gera dim_datas a partir das datas únicas das partidas."""
    if not fixtures_raw:
        return pd.DataFrame()

    dates = set()
    for item in fixtures_raw:
        date_str = item.get("fixture", {}).get("date")
        if date_str:
            dates.add(pd.Timestamp(date_str).normalize())

    if not dates:
        return pd.DataFrame()

    rows = []
    for dt in sorted(dates):
        rows.append({
            "data_id":          int(dt.strftime("%Y%m%d")),
            "data":             dt.date(),
            "dia":              dt.day,
            "mes":              dt.month,
            "ano":              dt.year,
            "trimestre":        dt.quarter,
            "dia_semana":       dt.dayofweek + 1,   # 1=Segunda … 7=Domingo
            "nome_dia_semana":  _DIAS_PT[dt.dayofweek],
            "nome_mes":         _MESES_PT[dt.month - 1],
            "is_fim_semana":    dt.dayofweek >= 5,
        })

    return pd.DataFrame(rows)
