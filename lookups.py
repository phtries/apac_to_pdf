import csv
from pathlib import Path
from paths import DATA_DIR

# Dicionário interno mínimo. O arquivo data/procedimentos.csv complementa/sobrescreve estes nomes.
PROCEDIMENTOS = {
    "0905010035": "OCI AVALIACAO INICIAL EM OFTALMOLOGIA - A PARTIR DE 9 ANOS",
    "0905010019": "OCI AVALIACAO INICIAL EM OFTALMOLOGIA - 0 A 8 ANOS",
    "0211060020": "BIOMICROSCOPIA DE FUNDO DE OLHO",
    "0211060127": "MAPEAMENTO DE RETINA",
    "0211060232": "TESTE ORTOPTICO",
    "0211060259": "TONOMETRIA",
    "0301010072": "CONSULTA MEDICA EM ATENCAO ESPECIALIZADA",
    "0301010102": "CONSULTA PARA DIAGNOSTICO/REAVALIACAO DE GLAUCOMA",
    "0902010018": "OCI AVALIACAO DE RISCO CIRURGICO",
    "0211020036": "ELETROCARDIOGRAMA",
    "0214020010": "ELETROCARDIOGRAMA",
    "0201010010": "EXAME ESPECIAL DE RASTREAMENTO DE DOENCAS CARDIOVASCULARES",
}

RACA_COR = {
    "01": "BRANCA",
    "02": "PRETA",
    "03": "PARDA",
    "04": "AMARELA",
    "05": "INDIGENA",
    "99": "SEM INFORMACAO",
}

_procedimentos_cache = None
_medicos_cache = None
_estabelecimentos_cache = None
_cids_cache = None


def somente_digitos(valor: str) -> str:
    return "".join(ch for ch in str(valor or "") if ch.isdigit())


def _ler_csv_dict(caminho: Path, delimiter: str = ";") -> list[dict]:
    if not caminho.exists():
        return []
    # utf-8-sig funciona bem com CSV salvo pelo Excel; latin-1 entra como fallback.
    for enc in ("utf-8-sig", "latin-1"):
        try:
            with caminho.open("r", encoding=enc, newline="") as f:
                return list(csv.DictReader(f, delimiter=delimiter))
        except UnicodeDecodeError:
            continue
    return []


def _carregar_procedimentos() -> dict[str, str]:
    global _procedimentos_cache
    if _procedimentos_cache is not None:
        return _procedimentos_cache

    dados = dict(PROCEDIMENTOS)
    for row in _ler_csv_dict(DATA_DIR / "procedimentos.csv"):
        codigo = somente_digitos(row.get("codigo", ""))
        descricao = (row.get("descricao") or row.get("nome") or "").strip()
        if codigo and descricao:
            dados[codigo] = descricao

    _procedimentos_cache = dados
    return dados


def buscar_medico_por_cns(cns: str) -> str:
    global _medicos_cache
    cns = (cns or "").strip()
    if not cns:
        return ""
    if _medicos_cache is None:
        _medicos_cache = _ler_csv_dict(DATA_DIR / "medicos.csv")
    for row in _medicos_cache:
        if row.get("cartao_sus", "").strip() == cns:
            return row.get("nome_completo", "").strip()
    return ""


def buscar_estabelecimento(cnes: str) -> str:
    global _estabelecimentos_cache
    cnes = (cnes or "").strip()
    if not cnes:
        return ""
    if _estabelecimentos_cache is None:
        _estabelecimentos_cache = _ler_csv_dict(DATA_DIR / "estabelecimentos.csv")
    for row in _estabelecimentos_cache:
        if row.get("cod_solicitante", "").strip() == cnes:
            return row.get("desc_solicitante", "").strip()
    return ""


def buscar_cid(codigo: str) -> str:
    global _cids_cache
    codigo = (codigo or "").strip().upper()
    if not codigo:
        return ""
    if _cids_cache is None:
        _cids_cache = _ler_csv_dict(DATA_DIR / "cid_oftalmologia.csv")
    for row in _cids_cache:
        if row.get("codigo", "").strip().upper() == codigo:
            return row.get("descricao", "").strip()
    return ""


def descricao_procedimento(codigo: str) -> str:
    codigo = somente_digitos(codigo)
    return _carregar_procedimentos().get(codigo, "")
