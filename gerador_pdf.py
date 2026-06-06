from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from fpdf import FPDF

from lookups import (
    buscar_cid,
    buscar_estabelecimento,
    buscar_medico_por_cns,
    descricao_procedimento,
    RACA_COR,
)
from parser_remessa import formatar_procedimento

from paths import ASSETS_DIR

TEMPLATE_PATH = ASSETS_DIR / "template_apac.png"


def _txt(valor) -> str:
    return str(valor or "")


def _sexo_extenso(valor: str) -> str:
    valor = (valor or "").upper().strip()
    if valor == "M":
        return "MASCULINO"
    if valor == "F":
        return "FEMININO"
    return valor



def obter_documento_paciente(apac: Dict[str, Any]) -> str:
    procedimento = str(apac.get("procedimento_principal", "")).strip()
    cpf = str(apac.get("cpf_paciente", "")).strip()
    cns = str(apac.get("cns_paciente", "")).strip()

    if procedimento.startswith("09"):
        return cpf

    return cns or cpf

def preparar_dados_pdf(apac: Dict[str, Any]) -> Dict[str, str]:
    procedimentos = apac.get("procedimentos", [])
    proc_principal = apac.get("procedimento_principal", "")

    dados = {
        "NOME_ESTAB_SOLICITANTE": buscar_estabelecimento(apac.get("cnes_solicitante")) or apac.get("cnes_solicitante", ""),
        "CNES_SOLICITANTE": apac.get("cnes_solicitante", ""),
        "NOME_ESTABELECIMENTO": buscar_estabelecimento(apac.get("cnes_executante")) or apac.get("cnes_executante", ""),
        "CNES_ESTABELECIMENTO": apac.get("cnes_executante", ""),
        "NOME_PACIENTE": apac.get("nome_paciente", ""),
        "SEXO": _sexo_extenso(apac.get("sexo", "")),
        # Campo 6 do modelo físico.
        # Regra interna: procedimentos principais iniciados em 09 vêm com CPF no cadastro, não CNS.
        "CPF_PACIENTE": obter_documento_paciente(apac),
        "DATA_NASCIMENTO": apac.get("data_nascimento_formatada", ""),
        "RACA_COR": RACA_COR.get(apac.get("raca_cor", ""), apac.get("raca_cor", "")),
        "NOME_MAE": apac.get("nome_mae", ""),
        "NOME_RESPONSAVEL": apac.get("nome_responsavel_paciente", "") or apac.get("nome_paciente", ""),
        "ENDERECO": apac.get("endereco_completo", ""),
        "MUNICIPIO_RESIDENCIA": "FRANCA",
        "COD_IBGE_MUNICIPIO": apac.get("municipio_codigo", ""),
        "UF": "SP" if apac.get("uf_codigo") == "35" else apac.get("uf_codigo", ""),
        "CEP": apac.get("cep", ""),
        "PROC_PRINCIPAL_COD": formatar_procedimento(proc_principal),
        "PROC_PRINCIPAL_NOME": descricao_procedimento(proc_principal),
        "PROC_PRINCIPAL_QTD": "1",
        "DESC_DIAGNOSTICO": buscar_cid(apac.get("cid_principal", "")),
        "OBSERVACOES": "",
        "CID10_PRINCIPAL": apac.get("cid_principal", ""),
        "NOME_SOLICITANTE": buscar_medico_por_cns(apac.get("cns_responsavel", "")) or apac.get("medico_responsavel", ""),
        "DOC_SOLICITANTE": apac.get("cns_responsavel", ""),
        # Para a APAC física, usamos a data inicial de validade como data de solicitação.
        "DATA_SOLICITACAO": apac.get("data_inicio_validade_formatada", ""),
        "NOME_AUTORIZADOR": buscar_medico_por_cns(apac.get("cns_autorizador", "")) or apac.get("nome_autorizador", ""),
        "COD_ORGAO_EMISSOR": apac.get("codigo_emissor", ""),
        "DOC_AUTORIZADOR": apac.get("cns_autorizador", ""),
        "NUMERO_APAC": apac.get("numero_apac", ""),
        # Para a APAC física, usamos a data inicial de validade como data de autorização.
        "DATA_AUTORIZACAO": apac.get("data_inicio_validade_formatada", ""),
        "VALIDADE_INICIO": apac.get("data_inicio_validade_formatada", ""),
        "VALIDADE_FIM": apac.get("data_fim_validade_formatada", ""),
    }

    secundarios = [p for p in procedimentos if p.get("codigo_procedimento") != proc_principal]
    for i, proc in enumerate(secundarios[:5], start=1):
        cod = proc.get("codigo_procedimento", "")
        dados[f"PROC_SEC{i}_COD"] = formatar_procedimento(cod)
        dados[f"PROC_SEC{i}_NOME"] = descricao_procedimento(cod)
        qtd = proc.get("quantidade_int") or proc.get("quantidade") or ""
        dados[f"PROC_SEC{i}_QTD"] = str(int(qtd)) if str(qtd).isdigit() else str(qtd)

    return dados


class APACPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=5)

    def add_apac_page(self, data: Dict[str, str]):
        self.add_page()
        if TEMPLATE_PATH.exists():
            self.image(str(TEMPLATE_PATH), x=0, y=0, w=210, h=297)
        self.set_font("Arial", "", 9)
        self.set_text_color(0, 0, 0)

        self.set_xy(13, 32); self.cell(100, 5, txt=_txt(data.get("NOME_ESTAB_SOLICITANTE")))
        self.set_xy(168, 32); self.cell(50, 5, txt=_txt(data.get("CNES_SOLICITANTE")))
        self.set_xy(13, 46.5); self.cell(100, 5, txt=_txt(data.get("NOME_PACIENTE")))

        old_size = self.font_size_pt
        self.set_font_size(7)
        if data.get("SEXO") == "MASCULINO":
            self.set_xy(148.8, 47.5); self.cell(w=3, h=3, txt="X", border=0, align="C")
        elif data.get("SEXO") == "FEMININO":
            self.set_xy(160.8, 47.5); self.cell(w=3, h=3, txt="X", border=0, align="C")
        self.set_font_size(old_size)

        self.set_xy(13, 55.2); self.cell(90, 5, txt=_txt(data.get("CPF_PACIENTE")))
        self.set_xy(112, 55.2); self.cell(40, 5, txt=_txt(data.get("DATA_NASCIMENTO")))
        self.set_xy(148, 55.2); self.cell(40, 5, txt=_txt(data.get("RACA_COR")))
        self.set_xy(13, 62.7); self.cell(100, 5, txt=_txt(data.get("NOME_MAE")))
        self.set_xy(13, 72.5); self.cell(100, 5, txt=_txt(data.get("NOME_RESPONSAVEL")))
        self.set_xy(13, 80); self.cell(150, 5, txt=_txt(data.get("ENDERECO")))
        self.set_xy(13, 88.5); self.cell(50, 5, txt=_txt(data.get("MUNICIPIO_RESIDENCIA")))
        self.set_xy(130, 88.5); self.cell(50, 5, txt=_txt(data.get("COD_IBGE_MUNICIPIO")))
        self.set_xy(155, 88.5); self.cell(20, 5, txt=_txt(data.get("UF")))
        self.set_xy(167, 88.5); self.cell(40, 5, txt=_txt(data.get("CEP")))

        self.set_font("Arial", "", 8)
        self.set_xy(11.7, 103); self.cell(40, 5, txt=_txt(data.get("PROC_PRINCIPAL_COD")))
        self.set_xy(78, 103); self.cell(120, 5, txt=_txt(data.get("PROC_PRINCIPAL_NOME")))
        self.set_xy(180, 103); self.cell(10, 5, txt=_txt(data.get("PROC_PRINCIPAL_QTD")))
        for i, y in enumerate([118.5, 127.5, 136.5, 145.5, 154.5], start=1):
            self.set_xy(11.7, y); self.cell(40, 5, txt=_txt(data.get(f"PROC_SEC{i}_COD")))
            self.set_xy(78, y); self.cell(120, 5, txt=_txt(data.get(f"PROC_SEC{i}_NOME")))
            self.set_xy(182, y); self.cell(10, 5, txt=_txt(data.get(f"PROC_SEC{i}_QTD")))

        self.set_font("Arial", "", 9)
        self.set_xy(14, 173); self.cell(100, 5, txt=_txt(data.get("DESC_DIAGNOSTICO")))
        # Observações removidas a pedido: deixa o campo 40 em branco.
        self.set_xy(14, 185); self.cell(80, 5, txt=_txt(data.get("OBSERVACOES")))
        self.set_xy(125, 173); self.cell(80, 5, txt=_txt(data.get("CID10_PRINCIPAL")))

        self.set_xy(13, 222); self.cell(100, 5, txt=_txt(data.get("NOME_SOLICITANTE")))
        self.set_xy(55, 230); self.cell(60, 5, txt=_txt(data.get("DOC_SOLICITANTE")))
        self.set_xy(110, 222); self.cell(40, 5, txt=_txt(data.get("DATA_SOLICITACAO")))
        self.set_xy(18.8, 230.9); self.cell(w=2, h=2, txt="X", border=0, align="C")

        self.set_xy(13, 246); self.cell(60, 5, txt=_txt(data.get("NOME_AUTORIZADOR")))
        self.set_xy(105, 246); self.cell(60, 5, txt=_txt(data.get("COD_ORGAO_EMISSOR")))
        self.set_xy(55, 257.5); self.cell(60, 5, txt=_txt(data.get("DOC_AUTORIZADOR")))
        self.set_xy(140, 246); self.cell(60, 5, txt=_txt(data.get("NUMERO_APAC")))
        self.set_xy(13, 270); self.cell(60, 5, txt=_txt(data.get("DATA_AUTORIZACAO")))
        # Campo 53 - período de validade da APAC. O campo é estreito, então reduzimos a fonte
        # para garantir que apareçam a data inicial e a data final.
        tamanho_atual = self.font_size_pt
        self.set_font_size(7.5)
        periodo = f"{_txt(data.get('VALIDADE_INICIO'))} a {_txt(data.get('VALIDADE_FIM'))}"
        self.set_xy(145, 270); self.cell(58, 5, txt=periodo, align="C")
        self.set_font_size(tamanho_atual)
        self.set_xy(18.8, 257.9); self.cell(w=2, h=2, txt="X", border=0, align="C")

        self.set_xy(13, 283); self.cell(100, 5, txt=_txt(data.get("NOME_ESTABELECIMENTO")))
        self.set_xy(165, 283); self.cell(50, 5, txt=_txt(data.get("CNES_ESTABELECIMENTO")))


def gerar_pdf_unico(apacs: List[Dict[str, Any]], pasta_saida: str | Path, nome_base: str = "apacs_fisicas") -> Path:
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    pdf = APACPDF()
    for apac in apacs:
        pdf.add_apac_page(preparar_dados_pdf(apac))
    caminho = pasta_saida / f"{nome_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(str(caminho))
    return caminho


def gerar_pdf_separado_por_apac(apacs: List[Dict[str, Any]], pasta_saida: str | Path) -> List[Path]:
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    caminhos = []
    for apac in apacs:
        pdf = APACPDF()
        pdf.add_apac_page(preparar_dados_pdf(apac))
        nome = f"APAC_{apac.get('numero_apac','sem_numero')}_{apac.get('nome_paciente','paciente').strip().replace(' ', '_')[:40]}.pdf"
        caminho = pasta_saida / nome
        pdf.output(str(caminho))
        caminhos.append(caminho)
    return caminhos
