from pathlib import Path
from typing import Dict, List, Any


def _campo(linha: str, ini: int, fim: int) -> str:
    """Recorta campo de layout 1-indexado inclusive e remove quebra de linha."""
    return linha[ini - 1:fim].rstrip("\r\n")


def _strip(linha: str, ini: int, fim: int) -> str:
    return _campo(linha, ini, fim).strip()


def somente_digitos(valor: str) -> str:
    return "".join(ch for ch in str(valor or "") if ch.isdigit())


def formatar_data(valor: str) -> str:
    valor = somente_digitos(valor)
    if len(valor) != 8:
        return valor
    return f"{valor[6:8]}/{valor[4:6]}/{valor[0:4]}"


def formatar_procedimento(codigo: str) -> str:
    codigo = somente_digitos(codigo)
    if len(codigo) == 10:
        return f"{codigo[:9]}-{codigo[9]}"
    return codigo


def parse_header(linha: str) -> Dict[str, str]:
    return {
        "tipo_registro": _strip(linha, 1, 2),
        "identificador": _strip(linha, 3, 7),
        "competencia": _strip(linha, 8, 13),
        "quantidade_apacs": _strip(linha, 14, 19),
        "controle": _strip(linha, 20, 23),
        "orgao_origem": _strip(linha, 24, 53),
        "sigla_origem": _strip(linha, 54, 59),
        "cnpj_origem": _strip(linha, 60, 73),
        "orgao_destino": _strip(linha, 74, 113),
        "indicador_destino": _strip(linha, 114, 114),
        "data_geracao": _strip(linha, 115, 122),
        "versao": _strip(linha, 123, 137),
    }


def parse_registro_14(linha: str) -> Dict[str, Any]:
    dados = {
        "tipo_registro": _strip(linha, 1, 2),
        "competencia": _strip(linha, 3, 8),
        "numero_apac": _strip(linha, 9, 21),
        "uf_codigo": _strip(linha, 22, 23),
        "cnes_executante": _strip(linha, 24, 30),
        "data_processamento": _strip(linha, 31, 38),
        "data_inicio_validade": _strip(linha, 39, 46),
        "data_fim_validade": _strip(linha, 47, 54),
        "tipo_atendimento": _strip(linha, 55, 56),
        "tipo_apac": _strip(linha, 57, 57),
        "nome_paciente": _strip(linha, 58, 87),
        "nome_mae": _strip(linha, 88, 117),
        "logradouro": _strip(linha, 118, 147),
        "numero_endereco": _strip(linha, 148, 152),
        "complemento": _strip(linha, 153, 162),
        "cep": _strip(linha, 163, 170),
        "municipio_codigo": _strip(linha, 171, 177),
        "data_nascimento": _strip(linha, 178, 185),
        "sexo": _strip(linha, 186, 186),
        "medico_responsavel": _strip(linha, 187, 216),
        "procedimento_principal": _strip(linha, 217, 226),
        "motivo_saida": _strip(linha, 227, 228),
        "data_obito_alta": _strip(linha, 229, 236),
        "nome_autorizador": _strip(linha, 237, 266),
        "cns_paciente": _strip(linha, 267, 281),
        "cns_responsavel": _strip(linha, 282, 296),
        "cns_autorizador": _strip(linha, 297, 311),
        "cid_causas_associadas": _strip(linha, 312, 315),
        "numero_prontuario": _strip(linha, 316, 325),
        "cnes_solicitante": _strip(linha, 326, 332),
        "data_solicitacao": _strip(linha, 333, 340),
        "data_autorizacao": _strip(linha, 341, 348),
        "codigo_emissor": _strip(linha, 349, 358),
        "carater_atendimento": _strip(linha, 359, 360),
        "apac_anterior": _strip(linha, 361, 373),
        "raca_cor": _strip(linha, 374, 375),
        "nome_responsavel_paciente": _strip(linha, 376, 405),
        "nacionalidade": _strip(linha, 406, 408),
        "etnia": _strip(linha, 409, 412),
        "codigo_logradouro": _strip(linha, 413, 415),
        "bairro": _strip(linha, 416, 445),
        "ddd_telefone": _strip(linha, 446, 447),
        "telefone": _strip(linha, 448, 456),
        "email": _strip(linha, 457, 496),
        "cns_executante": _strip(linha, 497, 511),
        # Alguns arquivos da Prefeitura vêm com 11 dígitos extras após o fim do layout oficial.
        # Na prática, esse sufixo tem sido o CPF do paciente e será usado no campo CNS/CPF do PDF.
        "cpf_paciente": somente_digitos(linha[511:]).strip(),
        "procedimentos": [],
        "laudo_geral": {},
    }
    dados["procedimento_principal_formatado"] = formatar_procedimento(dados["procedimento_principal"])
    dados["data_nascimento_formatada"] = formatar_data(dados["data_nascimento"])
    dados["data_solicitacao_formatada"] = formatar_data(dados["data_solicitacao"])
    dados["data_autorizacao_formatada"] = formatar_data(dados["data_autorizacao"])
    dados["data_inicio_validade_formatada"] = formatar_data(dados["data_inicio_validade"])
    dados["data_fim_validade_formatada"] = formatar_data(dados["data_fim_validade"])
    dados["endereco_completo"] = montar_endereco(dados)
    return dados


def parse_registro_13(linha: str) -> Dict[str, str]:
    dados = {
        "tipo_registro": _strip(linha, 1, 2),
        "competencia": _strip(linha, 3, 8),
        "numero_apac": _strip(linha, 9, 21),
        "codigo_procedimento": _strip(linha, 22, 31),
        "cbo": _strip(linha, 32, 37),
        "quantidade": _strip(linha, 38, 44),
        "cnpj_cessao": _strip(linha, 45, 58),
        "nota_fiscal": _strip(linha, 59, 64),
        "cid_principal": _strip(linha, 65, 68),
        "cid_secundario": _strip(linha, 69, 72),
        "servico": _strip(linha, 73, 75),
        "classificacao": _strip(linha, 76, 78),
        "equipe_seq": _strip(linha, 79, 86),
        "equipe_area": _strip(linha, 87, 90),
    }
    dados["codigo_procedimento_formatado"] = formatar_procedimento(dados["codigo_procedimento"])
    try:
        dados["quantidade_int"] = int(dados["quantidade"] or "0")
    except ValueError:
        dados["quantidade_int"] = 0
    return dados


def parse_registro_06(linha: str) -> Dict[str, str]:
    return {
        "tipo_registro": _strip(linha, 1, 2),
        "competencia": _strip(linha, 3, 8),
        "numero_apac": _strip(linha, 9, 21),
        "cid_principal": _strip(linha, 22, 25),
        "cid_secundario": _strip(linha, 26, 29),
    }


def montar_endereco(dados: Dict[str, Any]) -> str:
    partes = [dados.get("logradouro", ""), dados.get("numero_endereco", "")]
    complemento = dados.get("complemento", "")
    bairro = dados.get("bairro", "")
    texto = ", ".join([p for p in partes if p])
    if complemento:
        texto += f" - {complemento}"
    if bairro:
        texto += f" - {bairro}"
    return texto.strip(" -,")


def ler_remessa(caminho: str | Path) -> Dict[str, Any]:
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    # latin-1 preserva arquivos TXT antigos do DATASUS sem quebrar acentuação.
    texto = caminho.read_text(encoding="latin-1", errors="ignore")
    linhas = [linha.rstrip("\n") for linha in texto.splitlines() if linha.strip()]

    header = {}
    apacs: Dict[str, Dict[str, Any]] = {}
    registros_sem_corpo: List[Dict[str, str]] = []

    for linha in linhas:
        tipo = linha[:2]
        if tipo == "01":
            header = parse_header(linha)
        elif tipo == "14":
            dados = parse_registro_14(linha)
            apacs[dados["numero_apac"]] = dados
        elif tipo == "06":
            laudo = parse_registro_06(linha)
            numero = laudo["numero_apac"]
            if numero in apacs:
                apacs[numero]["laudo_geral"] = laudo
            else:
                registros_sem_corpo.append(laudo)
        elif tipo == "13":
            procedimento = parse_registro_13(linha)
            numero = procedimento["numero_apac"]
            if numero in apacs:
                apacs[numero].setdefault("procedimentos", []).append(procedimento)
            else:
                registros_sem_corpo.append(procedimento)

    lista_apacs = list(apacs.values())
    for apac in lista_apacs:
        laudo = apac.get("laudo_geral") or {}
        apac["cid_principal"] = laudo.get("cid_principal") or primeiro_cid_dos_procedimentos(apac)
        apac["cid_secundario"] = laudo.get("cid_secundario", "")

    return {
        "header": header,
        "apacs": lista_apacs,
        "total_linhas": len(linhas),
        "registros_sem_corpo": registros_sem_corpo,
    }


def primeiro_cid_dos_procedimentos(apac: Dict[str, Any]) -> str:
    for proc in apac.get("procedimentos", []):
        if proc.get("cid_principal"):
            return proc["cid_principal"]
    return ""


def opcoes_cnes(apacs: List[Dict[str, Any]]) -> List[str]:
    return sorted({a.get("cnes_executante", "") for a in apacs if a.get("cnes_executante")})


def opcoes_procedimentos_principais(apacs: List[Dict[str, Any]]) -> List[str]:
    return sorted({a.get("procedimento_principal", "") for a in apacs if a.get("procedimento_principal")})
